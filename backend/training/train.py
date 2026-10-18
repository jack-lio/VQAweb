"""Train the Taiwan AQI model (model A) on features from extract_features.py.

Time split, so the test set comes after everything the model trained on:
    train  2022-01 .. 2022-10
    val    2022-11 .. 2022-12   (picks the number of epochs)
    test   2024-01 .. 2024-06   (all stations; 045 has no 2022 data at all)
Accuracy alone is misleading here (62% of test hours are Good), so the report
also has macro-F1, per-class recall and an always-Good baseline.

The saved model is then refitted on ALL data (2022 + 2024) with the chosen
number of epochs; the test report above is its expected quality.

Usage: python training/train.py --features features.npz --out aqi_model/taiwan_v1.pt
"""
import argparse
import json
import os
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from aqi_features import AqiModel  # noqa: E402

CLASSES = ["Good", "Moderate", "USG", "Unhealthy", "Very Unhealthy", "Severe"]
VAL_FROM, TEST_FROM = "2022-11", "2024-01"
PCA_DIM = 64
MAX_EPOCHS = 60


def metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    recall, f1 = {}, []
    for c in sorted(set(y_true.tolist())):
        tp = int(((y_pred == c) & (y_true == c)).sum())
        p = tp / max(int((y_pred == c).sum()), 1)
        r = tp / int((y_true == c).sum())
        recall[CLASSES[c]] = round(r, 3)
        f1.append(0.0 if p + r == 0 else 2 * p * r / (p + r))
    return {
        "n": int(len(y_true)),
        "accuracy": round(float((y_true == y_pred).mean()), 3),
        "macro_f1": round(float(np.mean(f1)), 3),
        "within_one_class": round(float((np.abs(y_true - y_pred) <= 1).mean()), 3),
        "recall": recall,
    }


def fit(img, weather, y, epochs, weather_only=False, val=None):
    """Fit PCA, standardisation and the classifier on the given rows.

    With val=(img, weather, y) also returns the epoch with the best val macro-F1.
    """
    torch.manual_seed(0)
    model = AqiModel(pca_dim=PCA_DIM, num_classes=len(CLASSES))
    img_t, wea_t = torch.tensor(img), torch.tensor(weather)
    with torch.no_grad():
        model.pca_mean.copy_(img_t.mean(0))
        _, _, vt = torch.linalg.svd(img_t - model.pca_mean, full_matrices=False)
        model.pca_components.copy_(vt[:PCA_DIM])
        raw = model.inputs(img_t, wea_t)          # mean 0 / std 1 still unset
        model.mean.copy_(raw.mean(0))
        model.std.copy_(raw.std(0) + 1e-6)
        if weather_only:                          # image inputs become constant 0
            model.std[:PCA_DIM] = float("inf")

    counts = np.bincount(y, minlength=len(CLASSES)).astype(np.float32)
    weights = np.where(counts > 0, 1 / np.maximum(counts, 1), 0)
    loss_fn = torch.nn.CrossEntropyLoss(
        weight=torch.tensor(weights / weights[counts > 0].mean(), dtype=torch.float32))
    opt = torch.optim.AdamW(model.linear.parameters(), lr=1e-3, weight_decay=1e-2)
    x = model.inputs(img_t, wea_t).detach()
    yt = torch.tensor(y)

    best = (-1.0, 0)
    for epoch in range(1, epochs + 1):
        perm = torch.randperm(len(x))
        for i in range(0, len(x), 256):
            idx = perm[i:i + 256]
            opt.zero_grad()
            loss_fn(model.linear(x[idx]), yt[idx]).backward()
            opt.step()
        if val is not None:
            best = max(best, (metrics(val[2], predict(model, *val[:2]))["macro_f1"], epoch))
    return model, best[1]


def predict(model, img, weather):
    with torch.no_grad():
        return model(torch.tensor(img), torch.tensor(weather)).argmax(1).numpy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    d = np.load(args.features)
    img, wea, y, t = d["img"], d["weather"], d["label"], d["time"]
    tr, va, te = t < VAL_FROM, (t >= VAL_FROM) & (t < TEST_FROM), t >= TEST_FROM
    print(f"train {tr.sum()}  val {va.sum()}  test {te.sum()}")

    report = {"split": f"train <{VAL_FROM}, val <{TEST_FROM}, test >={TEST_FROM}"}
    report["always_good"] = metrics(y[te], np.zeros(te.sum(), dtype=int))
    for name, weather_only in [("weather_only", True), ("image_and_weather", False)]:
        _, epochs = fit(img[tr], wea[tr], y[tr], MAX_EPOCHS, weather_only, (img[va], wea[va], y[va]))
        model, _ = fit(img[tr | va], wea[tr | va], y[tr | va], epochs, weather_only)
        pred = predict(model, img[te], wea[te])
        report[name] = {"epochs": epochs, **metrics(y[te], pred)}
        print(name, json.dumps(report[name], ensure_ascii=False))

    confusion = np.zeros((len(CLASSES), len(CLASSES)), dtype=int)
    np.add.at(confusion, (y[te], pred), 1)
    report["image_and_weather"]["confusion_rows_true"] = confusion.tolist()

    # Deployed model: same recipe on all data.
    model, _ = fit(img, wea, y, report["image_and_weather"]["epochs"])
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    torch.save({
        "state_dict": model.state_dict(),
        "pca_dim": PCA_DIM,
        "classes": CLASSES,
        "features": "mobilenet_v2 IMAGENET1K_V1 pooled + weather (aqi_features.py)",
        "trained_on": f"{len(y)} images, 2022 + 2024-01..06, stations 001 042 045",
        "report": report,
    }, args.out)
    with open(os.path.splitext(args.out)[0] + ".json", "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"saved {args.out}")


if __name__ == "__main__":
    main()
