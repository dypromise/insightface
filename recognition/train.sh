export MXNET_CPU_WORKER_NTHREADS=16
export MXNET_ENGINE_TYPE=ThreadedEnginePerDevice

export LD_LIBRARY_PATH="/usr/local/cuda-9.0/lib64:$LD_LIBRARY_PATH"

# need to activate virtual env py27
python2 -u train.py \
    --network r50 \
    --loss arcface \
    --dataset emore \
    --pretrained /home/xmmtyding/model-r50-am-lfw/model \
    --pretrained-epoch 1 \
    --verbose 1000 \
    --per-batch-size 64 \
    --lr 0.0001
#    > train.log 2>&1
