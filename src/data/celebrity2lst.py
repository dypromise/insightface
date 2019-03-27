
import sys
import os
import numpy as np


data_root = sys.argv[1]
input_lmk = sys.argv[2]
target_lst = sys.argv[3]

lmap = {}

# image_dir = os.path.join(input_dir, ds)
lmk_file = input_lmk
idx = 0
fo = open(target_lst, 'w')
for line in open(lmk_file, 'r'):
    idx += 1
    vec = line.strip().split(' ')
    if len(vec) != 12 and len(vec) != 11:
        raise RuntimeError("vec length wrong!")
    image_file = os.path.join(data_root, vec[0])
    assert image_file.endswith('.jpg')
    vlabel = -1  # test mode
    if len(vec) == 12:
        label = int(vec[1])
        if label in lmap:
            vlabel = lmap[label]
        else:
            vlabel = len(lmap)
            lmap[label] = vlabel
        lmk = np.array([float(x) for x in vec[2:]], dtype=np.float32)
    else:
        lmk = np.array([float(x) for x in vec[1:]], dtype=np.float32)
    lmk = lmk.reshape((5, 2)).T
    lmk_str = "\t".join([str(x) for x in lmk.flatten()])
    fo.write("0\t%s\t%d\t0\t0\t0\t0\t%s\n" % (image_file, vlabel, lmk_str))

fo.close()
