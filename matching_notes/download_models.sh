#!/bin/bash
# Download open-weight code models for the decompilation pipeline.
# Runs on the login node; weights land in /scratch/tsranso/models/.
set -e
cd /scratch/tsranso/models

if [ ! -f qwen25-coder-7b/model.safetensors ] && [ ! -f qwen25-coder-7b/model-00001-of-00002.safetensors ]; then
    echo "downloading Qwen2.5-Coder-7B-Instruct (~15GB)..."
    rm -rf qwen25-coder-7b
    git clone https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct.git qwen25-coder-7b
    echo "7B done"
else
    echo "7B already present"
fi

if [ ! -f qwen25-coder-32b/model-00001-of-00007.safetensors ]; then
    echo "downloading Qwen2.5-Coder-32B-Instruct (~65GB)..."
    rm -rf qwen25-coder-32b
    git clone https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct.git qwen25-coder-32b
    echo "32B done"
else
    echo "32B already present"
fi
echo "all downloads complete"
du -sh qwen25-coder-7b qwen25-coder-32b
