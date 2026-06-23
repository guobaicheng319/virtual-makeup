"""探测可用的模型名变体"""
import os
import sys
import requests
from pathlib import Path

ENV_FILE = Path(__file__).parent.parent / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

API_KEY = os.environ.get("ARK_API_KEY", "")
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# 用户给的名字 + 常见变体
candidates = [
    "doubao-seededit-3-0-i2i-250628",
    "doubao-seededit-3.0-i2i-250628",
    "Doubao-SeedEdit-3.0-i2i-250628",
    "doubao-seededit-3-0-i2i",
    "Doubao-SeedEdit-3.0",
    "doubao-seedream-3-0-t2i",
    "Doubao-Seedream-3.0-t2i",
    "doubao-seedream-3.0-t2i-250628",
]

print("探测模型名变体...")
print(f"API Key: {API_KEY[:8]}...\n")

for name in candidates:
    body = {"model": name, "prompt": "test", "n": 1, "size": "512x512"}
    try:
        resp = requests.post(BASE_URL, json=body, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            print(f"  ✅ {name} → 200 OK!")
        elif resp.status_code == 401:
            print(f"  🔴 {name} → 401 鉴权失败")
        elif resp.status_code == 404:
            print(f"  ⬜ {name} → 404 不存在")
        elif resp.status_code == 400:
            print(f"  🟡 {name} → 400 参数问题（模型名有效！）: {resp.text[:120]}")
        else:
            print(f"  ❓ {name} → {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        print(f"  ❌ {name} → {e}")
