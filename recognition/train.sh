export MXNET_CPU_WORKER_NTHREADS=6
export MXNET_ENGINE_TYPE=ThreadedEnginePerDevice

export PATH="/home/dingyang/anaconda2/bin:$PATH"
export LD_LIBRARY_PATH="/home/dingyang/anaconda2/lib/:/home/dingyang/anaconda3/lib:$LD_LIBRARY_PATH"

python2 -u train.py \
    --network r50 \
    --loss arcface \
    --dataset emore \
    --pretrained /home/dingyang/r50-arcface-emore_ckpt_wo_fc7/model \
    --pretrained-epoch 1 \
    --verbose 2 \
    --per-batch-size 64 \
    --lr 0.05 \
#    > train.log 2>&1
