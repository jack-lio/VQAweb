import io
import pickle
import traceback

import numpy as np
import torch
from fastapi import FastAPI, File, Form, UploadFile
from PIL import Image

from feature_manager import FeatureManager
from mm_models import ImageTextClassifier

app = FastAPI()

img_args = {
    "feature_type": "mobilenet_v2",
    "dataset": "custom_aqi",
    "output_dir": "./output",
    "raw_data_dir": "./your_images",
}
tab_args = {
    "feature_type": "tabular_mlp",
    "input_size": 5,
    "dataset": "custom_aqi",
    "output_dir": "./output",
    "raw_data_dir": "./your_images",
}

fm_img = FeatureManager(img_args)
fm_tab = FeatureManager(tab_args)

model_files = {
    "A": "e1c98025-6701-4ab0-8e80-f28beb1a0828.pkl",
    "B": "f697991e-e233-44a7-91b3-5cd6324547b7.pkl",
    "C": "7909a945-7a51-456f-9f4f-e99e1af44466.pkl",
    "D": "91cbedea-5e82-4d19-bb80-0d44f14ae95e.pkl",
    "E": "fd4afbf0-7afc-44d9-9f9d-542257a341c7.pkl",
}

models = {}

for name, file in model_files.items():
    with open(file, "rb") as f:
        obj = pickle.load(f)

    if "global_model" in obj:
        model = obj["global_model"]
    elif "model" in obj:
        state_dict = obj["model"]
        img_input_dim = state_dict["img_proj.0.weight"].shape[1]
        text_input_dim = state_dict["text_proj.0.weight"].shape[1]

        model = ImageTextClassifier(
            num_classes=6,
            img_input_dim=img_input_dim,
            text_input_dim=text_input_dim,
        )
        model.load_state_dict(state_dict)
    else:
        raise ValueError(f"Model format unknown in {file}")

    model.eval()
    models[name] = model

class_names = ["Good", "Moderate", "USG", "Unhealthy", "Very Unhealthy", "Severe"]
class_descriptions = {
    "Good": "Air quality is considered satisfactory, and air pollution poses little or no risk.",
    "Moderate": "Air quality is acceptable; however, some pollutants may be a moderate health concern.",
    "USG": "Members of sensitive groups may experience health effects.",
    "Unhealthy": "Everyone may begin to experience health effects.",
    "Very Unhealthy": "Health alert: everyone may experience more serious health effects.",
    "Severe": "Health warnings of emergency conditions. The entire population is more likely to be affected.",
}


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/predict")
async def upload_data(
    image: UploadFile = File(...),
    rh: float = Form(...),
    rainfall: float = Form(...),
    temperature: float = Form(...),
    wd_hr: float = Form(...),
    ws_hr: float = Form(...),
    model_name: str = Form("A"),
):
    try:
        image_content = await image.read()
        pil_image = Image.open(io.BytesIO(image_content)).convert("RGB").resize((128, 128))

        img_feat = fm_img.extract_img_features(pil_image)
        img_feat = torch.tensor(img_feat[:, :128])
        x_img = img_feat.unsqueeze(1).repeat(1, 32, 1).float()

        tabular = [rh, rainfall, temperature, wd_hr, ws_hr]
        tabular_feat = fm_tab.extract_tabular_feature(np.array(tabular))
        x_text = torch.tensor(tabular_feat).unsqueeze(0).unsqueeze(1).repeat(1, 32, 1).float()

        if model_name not in models:
            return {"error": f"Unknown model name: {model_name}"}

        with torch.no_grad():
            pred, _ = models[model_name](x_img, x_text)
            pred_value = pred.item()
            pred_class = int(np.clip(round(pred_value), 0, 5))

        predicted_label = class_names[pred_class]
        return {
            "AQI": predicted_label,
            "pred_class": pred_class,
            "regression_value": round(pred_value, 3),
            "description": class_descriptions[predicted_label],
        }

    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}
