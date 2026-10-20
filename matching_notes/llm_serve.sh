#!/bin/bash
#SBATCH --job-name=llm-serve
#SBATCH --partition=work1
#SBATCH --account=cuuser_cpsc_ads_s27
#SBATCH --gres=gpu:h100:2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=1-00:00:00
#SBATCH --output=/scratch/%u/llm_serve_%j.out
#
# Serve an open-weight code model via vLLM's OpenAI-compatible API for the
# decompilation pipeline. The endpoint stays on the node's internal network;
# llm_decomp.py targets http://<node>:8000/v1.
#
# Env vars:
#   MODEL_PATH=/scratch/tsranso/models/<dir>   (required: safetensors weights)
#   PORT=8000
#
# First run: builds a venv with vllm (python 3.10+; the system 3.6 is unusable).
# Subsequent runs reuse it.
set -eu
MODEL_PATH=${MODEL_PATH:?set MODEL_PATH to the weights directory}
PORT=${PORT:-8000}
VENV=/scratch/$USER/venvs/vllm

mkdir -p "$VENV"
if [ ! -x "$VENV/bin/python" ]; then
    echo "building vllm venv (one-time)..."
    module load python/3.11 2>/dev/null || true
    python3 -m venv "$VENV"
fi
export PATH="$VENV/bin:$PATH"
if ! python -c "import vllm" 2>/dev/null; then
    pip install --quiet vllm
fi

echo "node: $(hostname)  model: $MODEL_PATH  port: $PORT"
exec python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_PATH" \
    --served-model-name decomp \
    --port "$PORT" \
    --tensor-parallel-size $SLURM_GPUS_ON_NODE \
    --max-model-len 16384 \
    --gpu-memory-utilization 0.92 \
    --disable-log-requests
