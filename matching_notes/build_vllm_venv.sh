#!/bin/bash
# Build the vLLM venv on the LOGIN node (internet access), for use on GPU nodes.
set -e
VENV=/scratch/$USER/venvs/vllm
mkdir -p "$(dirname "$VENV")"
rm -rf "$VENV"
/usr/bin/python3.12 -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip wheel
"$VENV/bin/pip" install vllm
"$VENV/bin/python" -c "import vllm; print('vllm OK:', vllm.__version__)"
echo "venv ready: $VENV"
