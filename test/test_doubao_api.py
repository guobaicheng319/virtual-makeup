"""M0 V1 · 豆包 API 连通性测试 · doubao-seededit-3-0-i2i-250628"""
import os
import sys
import time
import base64
import requests
from pathlib import Path
from io import BytesIO
from PIL import Image

# ── 加载 .env ──
ENV_FILE = Path(__file__).parent.parent / ".env"
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

API_KEY = os.environ.get("ARK_API_KEY", "")
MODEL_ID = os.environ.get("ARK_MODEL_ID", "doubao-seededit-3-0-i2i-250628")
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"

print(f"🔑 API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
print(f"🤖 Model:   {MODEL_ID}")
print(f"🌐 Endpoint: {BASE_URL}")
print()

# ── Step 1: 鉴权测试（不带参数，看 401 还是其他错误）──
print("=" * 50)
print("Step 1: 鉴权测试")
print("=" * 50)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# 最小请求体——验证 API Key 是否被接受
minimal_body = {
    "model": MODEL_ID,
    "prompt": "test",
    "n": 1,
    "size": "512x512",
}

try:
    resp = requests.post(BASE_URL, json=minimal_body, headers=headers, timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")

    if resp.status_code == 401:
        print("\n❌ 鉴权失败——API Key 无效或过期")
        sys.exit(1)
    elif resp.status_code == 200:
        print("\n✅ API Key 有效，调用成功！")
    elif resp.status_code in (400, 422):
        print(f"\n✅ API Key 有效（服务端返回参数错误而非鉴权错误）")
        print("   需要调整请求参数格式")
    else:
        print(f"\n⚠️  未预期的状态码: {resp.status_code}")
except requests.exceptions.Timeout:
    print("\n❌ 请求超时（30s）——检查网络")
    sys.exit(1)
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ 连接失败: {e}")
    sys.exit(1)

# ── Step 2: 创测试图 + 调用 i2i ──
print()
print("=" * 50)
print("Step 2: 图生图测试（合成测试图）")
print("=" * 50)

# 生成一张 512x512 纯色测试图作为"素颜照"
test_img = Image.new("RGB", (512, 512), color=(255, 220, 200))  # 肤色底
buf = BytesIO()
test_img.save(buf, format="PNG")
img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

i2i_body = {
    "model": MODEL_ID,
    "image": img_b64,
    "prompt": "add light natural makeup, soft lipstick, subtle eyeshadow, keep face recognizable",
    "n": 1,
    "size": "512x512",
}

try:
    resp = requests.post(BASE_URL, json=i2i_body, headers=headers, timeout=60)
    print(f"Status: {resp.status_code}")

    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ 图生图调用成功！")
        print(f"   data keys: {list(data.keys())}")
        # 保存结果
        if "data" in data and len(data["data"]) > 0:
            img_url = data["data"][0].get("url", "")
            img_b64_resp = data["data"][0].get("b64_json", "")

            out_dir = Path(__file__).parent / "img"
            out_dir.mkdir(exist_ok=True)

            if img_url:
                print(f"   图片URL: {img_url[:80]}...")
                # 下载结果图
                img_resp = requests.get(img_url, timeout=30)
                if img_resp.status_code == 200:
                    out_path = out_dir / "test_result.png"
                    out_path.write_bytes(img_resp.content)
                    print(f"   ✅ 已保存: {out_path}")
            elif img_b64_resp:
                out_path = out_dir / "test_result.png"
                out_path.write_bytes(base64.b64decode(img_b64_resp))
                print(f"   ✅ 已保存: {out_path}")
    elif resp.status_code == 400:
        print(f"❌ 参数错误: {resp.text[:500]}")
    elif resp.status_code == 422:
        print(f"❌ 请求格式错误: {resp.text[:500]}")
    else:
        print(f"⚠️  状态码 {resp.status_code}: {resp.text[:500]}")

except requests.exceptions.Timeout:
    print("⚠️  图生图请求超时（60s）——模型可能需更长时间")
except Exception as e:
    print(f"❌ 异常: {e}")
