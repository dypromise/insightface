# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys

import mxnet as mx
import argparse
import cv2
import time
from easydict import EasyDict as edict
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
import face_preprocess

try:
    import multiprocessing
except ImportError:
    multiprocessing = None


def read_list(path_in):
    with open(path_in) as fin:
        identities = []
        last = [-1, -1]
        _id = 1

        # second part in record, idx: 1~ len(faces)
        while True:
            line = fin.readline()
            if not line:
                break
            item = edict()
            item.flag = 0
            (item.image_path, label, item.bbox,
             item.landmark, item.aligned
             ) = face_preprocess.parse_lst_line(line)
            if not item.aligned and item.landmark is None:
                continue
            item.id = _id
            item.label = [label, item.aligned]
            yield item
            if label != last[0]:
                if last[1] >= 0:
                    identities.append((last[1], _id))
                last[0] = label
                last[1] = _id
            _id += 1
        identities.append((last[1], _id))

        # head in record, idx: 0
        item = edict()
        item.flag = 2
        item.id = 0
        item.label = [float(_id), float(_id + len(identities))]
        yield item

        # third part, idx: len(faces)+1 ~ len(faces)+1+len(identities)
        for identity in identities:
            item = edict()
            item.flag = 2
            item.id = _id
            _id += 1
            item.label = [float(identity[0]), float(identity[1])]
            yield item


def image_encode(args, i, item, q_out):
    oitem = [item.id]
    if item.flag == 0:
        fullpath = item.image_path
        header = mx.recordio.IRHeader(item.flag, item.label, item.id, 0)
        if item.aligned:
            with open(fullpath, 'rb') as fin:
                img = fin.read()
            s = mx.recordio.pack(header, img)
            q_out.put((i, s, oitem))
        else:
            img = cv2.imread(fullpath, args.color)
            assert item.landmark is not None
            img = face_preprocess.preprocess(
                img, bbox=item.bbox, landmark=item.landmark,
                image_size='%d,%d' % (args.image_h, args.image_w))

            # AFTER PACK BUG!!!!! after pack, header.flag is set to len(label)
            # print("before pack:", header.flag, header.label, header.id)
            s = mx.recordio.pack_img(
                header, img, quality=args.quality, img_fmt=args.encoding)
            # h, _ = mx.recordio.unpack_img(s)
            # print("after pack:", h.flag, h.label, header.id)
            q_out.put((i, s, oitem))
            # print(header)
    else:
        header = mx.recordio.IRHeader(item.flag, item.label, item.id, 0)
        # print('write', item.flag, item.id, item.label)
        s = mx.recordio.pack(header, '')
        q_out.put((i, s, oitem))


def read_worker(args, q_in, q_out):
    while True:
        deq = q_in.get()
        if deq is None:
            break
        i, item = deq
        image_encode(args, i, item, q_out)


def write_worker(q_out, fname, output_dir):
    pre_time = time.time()
    count = 0
    fname = os.path.basename(fname)
    fname_rec = os.path.splitext(fname)[0] + '.rec'
    fname_idx = os.path.splitext(fname)[0] + '.idx'
    record = mx.recordio.MXIndexedRecordIO(
        os.path.join(output_dir, fname_idx),
        os.path.join(output_dir, fname_rec), 'w')
    buf = {}
    more = True
    while more:
        deq = q_out.get()
        if deq is not None:
            i, s, item = deq
            # h, _ = mx.recordio.unpack(s)
            # print(h.flag)
            buf[i] = (s, item)
        else:
            more = False
        while count in buf:
            s, item = buf[count]
            del buf[count]
            if s is not None:
                record.write_idx(item[0], s)

            if count % 1000 == 0:
                cur_time = time.time()
                print('time:', cur_time - pre_time, ' count:', count)
                pre_time = cur_time
            count += 1


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Create an image list or make a record database by \
reading from an image list')

    parser.add_argument('--lst', help='lst file path')
    parser.add_argument('--output_dir', help='output_dir')
    parser.add_argument('--property', help='property file path')

    rgroup = parser.add_argument_group('Options for creating database')
    rgroup.add_argument('--num-thread', type=int, default=1,
                        help='number of thread to use for encoding. rder \
of images will be different from the input list if >1. the input list will \
be modified to match the resulting order.')

    rgroup.add_argument('--quality', type=int, default=95,
                        help='JPEG quality for encoding, 1-100; or PNG \
compression for encoding, 1-9')

    rgroup.add_argument('--color', type=int, default=1, choices=[-1, 0, 1],
                        help='specify the color mode of the loaded image.\
1: Loads a color image. Any transparency of image will be neglected. It \
is the default flag. 0: Loads image in grayscale mode. -1:Loads image as \
such including alpha channel.')

    rgroup.add_argument('--encoding', type=str, default='.jpg',
                        choices=['.jpg', '.png'],
                        help='specify the encoding of the images.')

    rgroup.add_argument('--pack-label', type=bool, default=False,
                        help='Whether to also pack multi dimensional label \
in the record file')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    output_dir = args.output_dir
    args.image_h = 112
    args.image_w = 112
    fname = args.lst
    if fname.endswith('.lst'):
        print('Creating .rec file from', fname, 'in', output_dir)
        image_list = read_list(fname)
        # -- write_record -- #
        if args.num_thread > 1 and multiprocessing is not None:
            q_in = [multiprocessing.Queue(1024)
                    for i in range(args.num_thread)]
            q_out = multiprocessing.Queue(1024)
            read_process = [multiprocessing.Process(
                target=read_worker, args=(args, q_in[i], q_out))
                for i in range(args.num_thread)]
            for p in read_process:
                p.start()
            write_process = multiprocessing.Process(
                target=write_worker, args=(q_out, fname, output_dir))
            write_process.start()

            for i, item in enumerate(image_list):
                q_in[i % len(q_in)].put((i, item))
            for q in q_in:
                q.put(None)
            for p in read_process:
                p.join()

            q_out.put(None)
            write_process.join()
        else:
            print('multiprocessing not available, fall back to single threaded \
                encoding')
            try:
                import Queue as queue
            except ImportError:
                import queue
            q_out = queue.Queue()
            fname = os.path.basename(fname)
            fname_rec = os.path.splitext(fname)[0] + '.rec'
            fname_idx = os.path.splitext(fname)[0] + '.idx'
            record = mx.recordio.MXIndexedRecordIO(
                os.path.join(output_dir, fname_idx),
                os.path.join(output_dir, fname_rec), 'w')
            cnt = 0
            pre_time = time.time()
            for i, item in enumerate(image_list):
                image_encode(args, i, item, q_out)
                # print(item.flag)
                if q_out.empty():
                    continue
                _, s, item = q_out.get()

                record.write_idx(item[0], s)
                if cnt % 1000 == 0:
                    h, _ = mx.recordio.unpack(s)
                    print(h.flag, item[0])

                    cur_time = time.time()
                    print('time:', cur_time - pre_time, ' count:', cnt)
                    pre_time = cur_time
                cnt += 1
