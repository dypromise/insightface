import shutil
import os


def rename_celebrity():
    val_dir = '/home/xmmtyding/data1/celebrity_val_aligned/'
    for _dir in os.listdir(val_dir):
        _id = _dir
        cnt = 0
        this_dir = os.path.join(val_dir, _dir)
        for file in os.listdir(this_dir):
            _idx = "{:0>4d}".format(cnt)
            name = _id + '_' + _idx + '.jpg'
            cnt += 1

            src = os.path.join(this_dir, file)
            dst = os.path.join(this_dir, name)
            os.rename(src, dst)

    print("All done.")
