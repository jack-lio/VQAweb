import pickle
import torch

# 讀入模型
with open("fd4afbf0-7afc-44d9-9f9d-542257a341c7.pkl", "rb") as f:
    data = pickle.load(f)

model = data["global_model"]
model.eval()

# 自動推斷正確的 input dim
img_input_dim = model.img_proj[0].weight.shape[1]
text_input_dim = model.text_proj[0].weight.shape[1]

# 準備正確維度的輸入
x_img = torch.randn(1, 32, img_input_dim)
x_text = torch.randn(1, 32, text_input_dim)

# 推論
with torch.no_grad():
    preds, _ = model(x_img, x_text)

print("預測結果:", preds)