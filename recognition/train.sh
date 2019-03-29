export MXNET_CPU_WORKER_NTHREADS=16
export MXNET_ENGINE_TYPE=ThreadedEnginePerDevice

export LD_LIBRARY_PATH="/usr/local/cuda-9.0/lib64:$LD_LIBRARY_PATH"

# need to activate virtual env py27
python2 -u train.py \
    --network r50 \
    --loss arcface \
    --dataset emore_celebasian \
    --pretrained /data1/xmmtyding/r50_arcface_emore_finetune_lr0.0001fc7mul10_wofc7/model \
    --pretrained-epoch 1 \
    --verbose 1000 \
    --per-batch-size 96 \
    --lr 0.0001 \
    > train_emore_celebasian_finetune.log 2>&1
