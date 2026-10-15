# Headless Blender + Python evaluation pipeline (CPU only, no GPU needed)
FROM python:3.11-slim-bookworm

ARG BLENDER_VERSION=4.2.3
ARG BLENDER_SERIES=4.2

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/hf \
    XDG_CACHE_HOME=/opt/cache

# Libraries Blender needs even in --background mode
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl xz-utils fonts-dejavu-core \
        libx11-6 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libsm6 libice6 \
        libgl1 libegl1 libglib2.0-0 libgomp1 libxext6 libwayland-client0 libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fSL "https://download.blender.org/release/Blender${BLENDER_SERIES}/blender-${BLENDER_VERSION}-linux-x64.tar.xz" \
        -o /tmp/blender.tar.xz \
    && mkdir -p /opt/blender \
    && tar -xJf /tmp/blender.tar.xz -C /opt/blender --strip-components=1 \
    && rm /tmp/blender.tar.xz \
    && /opt/blender/blender -b --factory-startup --version

# CPU-only PyTorch first (much smaller than the CUDA build), then the rest
COPY requirements.txt /app/requirements.txt
# torch + torchvision MUST come from the same CPU index in one command, otherwise open_clip
# pulls a mismatched torchvision from PyPI ("operator torchvision::nms does not exist")
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install -r /app/requirements.txt \
    && python -c "import torch, torchvision; print('torch', torch.__version__, 'torchvision', torchvision.__version__)"

# Bake the CLIP weights into the image so runs are offline-reproducible
RUN python -c "import open_clip; open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')"

COPY . /app
WORKDIR /app

# LLM-written code runs as an unprivileged user
RUN useradd -m runner \
    && mkdir -p /work/results /opt/cache /opt/hf \
    && chown -R runner /work /app /opt/cache /opt/hf
USER runner

ENTRYPOINT ["python", "-m", "src.run_experiment", "--out", "/work/results"]
