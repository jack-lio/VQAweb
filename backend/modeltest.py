import torch
import pickle
import numpy as np
from torchvision import models, transforms
from feature_manager import FeatureManager  # ← 換成簡化版
from mm_models import ImageTextClassifier

# Step 1: 設定參數
img_args = {
    'feature_type': 'mobilenet_v2',
    'dataset': 'custom_aqi',
    'output_dir': './output',
    'raw_data_dir': './your_images'
}
fm_img = FeatureManager(img_args)

# 表格模型：tabular_mlp
tab_args = {
    'feature_type': 'tabular_mlp',
    'input_size': 5,
    'dataset': 'custom_aqi',
    'output_dir': './output',
    'raw_data_dir': './your_images'
}
fm_tab = FeatureManager(tab_args)

# Step 2: 圖像特徵擷取
img_feat = fm_img.extract_img_features("pic.jpg")
img_feat = torch.tensor(img_feat[:, :128])

x_img = img_feat.unsqueeze(1).repeat(1, 32, 1).float()  # ➜ [1, 32, 128]

# Step 3: 數值特徵擷取
tabular = [80.2, 0.5, 28, 180, 3.2]  # RH, Rainfall, Temp, WindDir, WindSpeed
tabular_feat = fm_tab.extract_tabular_feature(np.array(tabular))  # ➜ [512]
x_text = torch.tensor(tabular_feat).unsqueeze(0).unsqueeze(1).repeat(1, 32, 1).float()  # [1, 32, 512]

# Step 4: 載入模型
with open("fd4afbf0-7afc-44d9-9f9d-542257a341c7.pkl", "rb") as f:
    model = pickle.load(f)['global_model']
model.eval()

# Step 5: 推論
with torch.no_grad():
    pred, _ = model(x_img, x_text)

print("AQI 預測結果:", pred.item())