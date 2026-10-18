"""Compute image and weather features for every labelled station image.

Usage (inside the vqaweb image, so library versions match serving):
    python training/extract_features.py --out features.npz \
        DATA_ROOT/2022/042_2022_converted_v6.csv:DATA_ROOT/2022/042_clean ...

Each argument is <labels csv>:<image folder>. The CSVs have Filename, Year,
Month, Day, Hour, RH, RAINFALL, Temperature, WD_HR, WS_HR and AQI_Class.
"""
import argparse
import csv
import os
import sys
import time

import numpy as np
import torch
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from aqi_features import ImageEncoder, weather_vector  # noqa: E402

CLASS_NAMES = ["Good", "Moderate", "Unhealthy for Sensitive Groups",
               "Unhealthy", "Very Unhealthy", "Severe"]


def rows(sources):
    for source in sources:
        csv_path, image_dir = source.rsplit(":", 1)
        with open(csv_path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                path = os.path.join(image_dir, row["Filename"])
                if os.path.exists(path):
                    yield path, row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--batch", type=int, default=64)
    parser.add_argument("sources", nargs="+")
    args = parser.parse_args()

    torch.set_num_threads(os.cpu_count() or 4)
    encoder = ImageEncoder()
    items = list(rows(args.sources))
    print(f"{len(items)} labelled images")

    img_feats, weather, labels, names, times = [], [], [], [], []
    start = time.time()
    for i in range(0, len(items), args.batch):
        chunk = items[i:i + args.batch]
        img_feats.append(encoder.encode([Image.open(p) for p, _ in chunk]))
        for path, r in chunk:
            weather.append(weather_vector(float(r["RH"]), float(r["RAINFALL"]),
                                          float(r["Temperature"]), float(r["WD_HR"]),
                                          float(r["WS_HR"])))
            labels.append(CLASS_NAMES.index(r["AQI_Class"]))
            names.append(r["Filename"])
            times.append(f'{int(r["Year"]):04d}-{int(r["Month"]):02d}-{int(r["Day"]):02d}T{int(r["Hour"]):02d}')
        done = i + len(chunk)
        if done % (args.batch * 20) == 0 or done == len(items):
            print(f"{done}/{len(items)} images, {done / (time.time() - start):.1f}/s", flush=True)

    np.savez_compressed(
        args.out,
        img=np.concatenate(img_feats).astype(np.float32),
        weather=np.stack(weather),
        label=np.array(labels, dtype=np.int64),
        name=np.array(names),
        time=np.array(times),
    )
    print(f"saved {args.out}")


if __name__ == "__main__":
    main()
