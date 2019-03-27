export MXNET_CPU_WORKER_NTHREADS=16
export MXNET_ENGINE_TYPE=ThreadedEnginePerDevice

#export PATH="/home/dingyang/anaconda2/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/cuda-9.0/lib64:$LD_LIBRARY_PATH"
python2 -u train.py \
    --network r50 \
    --loss arcface \
    --dataset emore \
    --pretrained /home/xmmtyding/model-r50-am-lfw/model \
    --pretrained-epoch 0 \
    --verbose 1000 \
    --per-batch-size 100 \
    --lr 0.0001 \
    > train_paper_model_goon_lr0.0001.log 2>&1
