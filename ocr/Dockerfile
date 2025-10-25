# Enable BuildKit features like RUN --mount=type=cache automatically in recent Docker
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Minimal system deps (OpenCV needs libgl1 + glib)
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3 python3-pip libgl1 libglib2.0-0 libgomp1\
    && rm -rf /var/lib/apt/lists/*

# Speed up pip (persisted only across builds, not in the image layers)
# (Requires BuildKit, which Docker Desktop enables by default.)
RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install -U pip setuptools wheel

# PaddlePaddle GPU (CUDA 11.8 wheel) + PaddleX
ARG PADDLE_INDEX=https://www.paddlepaddle.org.cn/packages/stable/cu118/
RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install paddlepaddle-gpu==3.2.0 -i ${PADDLE_INDEX} \
 && python3 -m pip install "paddlex[ocr]==3.2.0"

# PaddleX Serving (plugin)
RUN paddlex --install serving

EXPOSE 8080

CMD ["paddlex", "--serve", "--pipeline", "OCR", "--host", "0.0.0.0", "--port", "8080"]
