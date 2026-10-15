#!/usr/bin/env bash
# Linux/macOS launcher. Usage: ./run.sh [--smoke | --limit N | --report-only | --yes]
set -euo pipefail
IMAGE=blender-llm-bench
docker build -t "$IMAGE" .
if [[ " $* " != *" --smoke "* && " $* " != *" --report-only "* && -z "${AI_GATEWAY_API_KEY:-}" ]]; then
  read -rsp "Paste your Vercel AI Gateway API key: " AI_GATEWAY_API_KEY; echo
  export AI_GATEWAY_API_KEY
fi
mkdir -p results
docker run --rm -it --user "$(id -u):$(id -g)" -e HOME=/tmp -e AI_GATEWAY_API_KEY -v "$PWD/results:/work/results" "$IMAGE" "$@"
