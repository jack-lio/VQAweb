FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ImageNet weights for the feature extractor (aqi_features.py), downloaded at
# build time so the container starts without network access.
ENV TORCH_HOME=/opt/torch
RUN python -c "from torchvision.models import mobilenet_v2, MobileNet_V2_Weights; mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)"

# docker-compose.yml still mounts ./backend over /app for development;
# Kubernetes runs this copy.
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
