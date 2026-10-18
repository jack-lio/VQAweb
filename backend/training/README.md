# Model A (Taiwan): training

`/api/predict` with `model_name=A` uses `aqi_model/taiwan_v1.pt`, trained here.
Training and serving compute features with the same module, `aqi_features.py`:

- image: MobileNetV2 with fixed ImageNet weights, pooled to 1280 values,
  reduced to 64 by PCA
- weather: RH, rainfall, temperature, wind direction (sin, cos), wind speed
- classifier: linear, class-weighted (most hours are Good)

PCA, standardisation and the classifier are stored in the `.pt` file.

## Why it was retrained (2026-10)

The previous models (A–E) were trained on features from a `CNN()` and a
`TabularMLP()` that were randomly initialised, never trained and never saved,
and serving used yet another random `mobilenet_v2(weights=None)`. Their inputs
can't be reproduced, so their predictions changed on every restart and didn't
mean anything. B–E are still served for the web UI with a fixed seed: their
output is now repeatable, but still not meaningful (`"model_version": "legacy"`).

## Data

Station images with hourly labels, `<labels csv>:<image folder>`:

| Station | Period | Images |
|---|---|---|
| 001 基隆 | 2022, 2024-01..06 | 6,467 + 1,352 |
| 042 嘉義 | 2022, 2024-01..06 | 7,285 + 1,372 |
| 045 安南 | 2024-01..06 | 1,378 |

The CSVs (`*_converted_v6.csv`, `*_converted_v7.csv`) have `Filename`, `Year`,
`Month`, `Day`, `Hour`, `RH`, `RAINFALL`, `Temperature`, `WD_HR`, `WS_HR` and
`AQI_Class`.

## Results (`aqi_model/taiwan_v1.json`)

Trained on 2022 and tested on 2024-01..06, which includes station 045 that the
model never saw:

| | Accuracy | Macro-F1 | Within one class |
|---|---|---|---|
| Always "Good" | 62.0% | – | – |
| Weather only | 53.2% | 0.305 | 72.4% |
| **Image + weather** | **72.1%** | **0.364** | **94.4%** |

Recall per class: Good 0.92, Moderate 0.50, USG 0.17, Unhealthy 0.15. The model
mostly separates clean from polluted air; it can't yet tell USG from
Moderate reliably. The deployed model is refitted on all of the data above.

## Retrain

Run inside the app image so library versions match serving (`D` = data root):

```bash
docker run --rm --entrypoint python -v "$PWD/backend:/code" -v "$D:/data:ro" -w /code \
  ghcr.io/jack-lio/vqaweb:<tag> training/extract_features.py --out /code/data/features.npz \
  /data/2022/001_2022_converted_v6.csv:/data/2022/001_clean \
  /data/2022/042_2022_converted_v6.csv:/data/2022/042_clean \
  /data/AirTW/001_2024_converted_v7.csv:/data/AirTW/001_24_clean \
  /data/AirTW/042_2024_converted_v7.csv:/data/AirTW/042_24_clean \
  /data/AirTW/045_2024_converted_v7.csv:/data/AirTW/045_24_clean

docker run --rm --entrypoint python -v "$PWD/backend:/code" -w /code \
  ghcr.io/jack-lio/vqaweb:<tag> training/train.py \
  --features data/features.npz --out aqi_model/taiwan_v1.pt
```

Feature extraction takes about 17 minutes for 17,854 images on 14 CPUs;
training takes seconds. After retraining, update the expected prediction in
`.github/workflows/ci-cd.yml` (step "Predict on a sample image").
