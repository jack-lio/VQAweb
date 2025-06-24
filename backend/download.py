from minio import Minio
import os

# ======= 替換這些資訊 =======
endpoint = "storage.ccu01.footprint-ai.com"
access_key = "Cs50JE8TMIDnmQBb"
secret_key = "XGM6tCKn9I98taQa8eJ3EuLbok4MVQZA"
bucket_name = "project-4-social-patriot"

object_names = [
    "fd4afbf0-7afc-44d9-9f9d-542257a341c7.pkl",
    "7909a945-7a51-456f-9f4f-e99e1af44466.pkl",
    "f697991e-e233-44a7-91b3-5cd6324547b7.pkl",
    "e1c98025-6701-4ab0-8e80-f28beb1a0828.pkl",
    "91cbedea-5e82-4d19-bb80-0d44f14ae95e.pkl"
]

client = Minio(
    endpoint=endpoint,
    access_key=access_key,
    secret_key=secret_key,
    secure=True
)

# 下載檔案
for obj in object_names:
    client.fget_object(bucket_name, obj, f"./{obj}")
    print(f"✅ 已下載: {obj}")
