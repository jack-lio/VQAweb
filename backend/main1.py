from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
from PIL import Image
import numpy as np
import torch
import io

from model_A import MultimodalNet
#from sky_test_v1 import validate_image

app = FastAPI()

model = MultimodalNet(tabular_input_size=5)
model.load_state_dict(torch.load("model_A.pkl", map_location="cpu"))
model.eval()

@app.post("/api/predict")
async def upload_data(
    image: UploadFile = File(...),
    rh: float = Form(...),
    rainfall: float = Form(...),
    temperature: float = Form(...),
    wd_hr: float = Form(...),
    ws_hr: float = Form(...)
):
    try:
        # 圖片預處理
        image_content = await image.read()
        pil_image = Image.open(io.BytesIO(image_content)).convert("RGB").resize((128, 128))
        img_array = np.array(pil_image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        img_tensor = torch.tensor(img_array).permute(0, 3, 1, 2).float()

        # 圖片驗證
        #if not validate_image(img_array):
        #    return {"response": "❌ 這張圖片不是天空，請重新上傳。"}

        # sensor 輸入
        sensor_array = np.array([[rh, rainfall, temperature, wd_hr, ws_hr]], dtype=np.float32)
        sensor_tensor = torch.tensor(sensor_array)

        # 模型推論
        with torch.no_grad():
            output = model(img_tensor, sensor_tensor)
            pred_class = torch.argmax(output, dim=1).item()
            class_names = ['Good', 'Moderate', 'USG', 'Unhealthy', 'Very Unhealthy', 'Severe']
            predicted_label = class_names[pred_class]

        # 回傳結果給前端
        return {
            "response": predicted_label,
            
        }

    except Exception as e:
        return {"error": str(e)}
