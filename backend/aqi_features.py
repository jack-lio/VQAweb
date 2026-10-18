"""Features for the AQI model, shared by training (training/) and serving (main.py).

Both sides must compute features with exactly this code: the previous models
were trained on features from randomly initialised networks whose weights
were never saved, so serving could not reproduce them.

Image: MobileNetV2 with fixed ImageNet weights, global-pooled to 1280 values.
Weather: RH, rainfall, temperature, wind direction as sin/cos, wind speed.
"""
import math

import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from torchvision.models import MobileNet_V2_Weights, mobilenet_v2

IMG_DIM = 1280
WEATHER_NAMES = ["rh", "rainfall", "temperature", "wd_sin", "wd_cos", "ws_hr"]

_TRANSFORM = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


class ImageEncoder:
    def __init__(self):
        model = mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)
        model.classifier = torch.nn.Identity()
        self.model = model.eval()

    @torch.no_grad()
    def encode(self, images: list[Image.Image]) -> np.ndarray:
        batch = torch.stack([_TRANSFORM(img.convert("RGB")) for img in images])
        return self.model(batch).numpy()


def weather_vector(rh: float, rainfall: float, temperature: float,
                   wd_hr: float, ws_hr: float) -> np.ndarray:
    """Wind direction in degrees becomes sin/cos so that 359 and 1 are close."""
    rad = math.radians(wd_hr)
    return np.array([rh, rainfall, temperature, math.sin(rad), math.cos(rad), ws_hr],
                    dtype=np.float32)


class AqiModel(torch.nn.Module):
    """Image features -> PCA -> standardise with weather -> linear classifier.

    PCA, standardisation and the classifier are all fitted by
    training/train.py and stored in the state dict, so serving only loads it.
    """

    def __init__(self, pca_dim: int = 64, num_classes: int = 6):
        super().__init__()
        n = pca_dim + len(WEATHER_NAMES)
        self.register_buffer("pca_mean", torch.zeros(IMG_DIM))
        self.register_buffer("pca_components", torch.zeros(pca_dim, IMG_DIM))
        self.register_buffer("mean", torch.zeros(n))
        self.register_buffer("std", torch.ones(n))
        self.linear = torch.nn.Linear(n, num_classes)

    def inputs(self, img: torch.Tensor, weather: torch.Tensor) -> torch.Tensor:
        x = torch.cat([(img - self.pca_mean) @ self.pca_components.T, weather], dim=1)
        return (x - self.mean) / self.std

    def forward(self, img: torch.Tensor, weather: torch.Tensor) -> torch.Tensor:
        return self.linear(self.inputs(img, weather))
