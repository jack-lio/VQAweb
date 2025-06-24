import pickle

with open("fd4afbf0-7afc-44d9-9f9d-542257a341c7.pkl", "rb") as f:
    data = pickle.load(f)

print(type(data))

if isinstance(data, dict):
    print("🔑 包含的 keys:", data.keys())
    for k in data:
        print(f"{k}: {type(data[k])}")
elif hasattr(data, "eval"):  # 是模型
    print("✅ 是模型類型:", type(data))
    print("模型結構：")
    print(data)