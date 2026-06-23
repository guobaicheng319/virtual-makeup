"""M0 V2 · 照片预处理管线测试 · 清晰度增强 + 背景优化"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

# ── Step 1: 生成合成测试图（模拟素颜照）──
print("=" * 50)
print("Step 1: 生成合成测试图")
print("=" * 50)

test_img = Path(__file__).parent / "img" / "test_face.png"
test_img.parent.mkdir(exist_ok=True)

# 512x512 肤色底 + 粗糙五官轮廓
img = Image.new("RGB", (512, 512), color=(230, 200, 180))
draw = ImageDraw.Draw(img)
# 脸型
draw.ellipse([120, 60, 392, 460], fill=(245, 220, 195), outline=(200, 160, 130), width=2)
# 眼睛
for x, y in [(190, 200), (310, 200)]:
    draw.ellipse([x-22, y-10, x+22, y+10], fill=(255, 255, 255))
    draw.ellipse([x-10, y-5, x+10, y+5], fill=(50, 50, 50))
# 眉毛（淡淡的）
for x, y in [(190, 170), (310, 170)]:
    draw.arc([x-25, y-5, x+25, y+8], 180, 360, fill=(80, 60, 40), width=3)
# 鼻子
draw.ellipse([248, 240, 264, 280], fill=(220, 190, 160))
# 嘴巴
draw.arc([220, 300, 292, 340], 0, 180, fill=(190, 100, 110), width=4)
# 头发
draw.ellipse([90, 20, 422, 200], fill=(60, 40, 30))
# 杂色背景
for i in range(20):
    import random
    random.seed(i)
    x, y = random.randint(0, 512), random.randint(0, 100)
    draw.rectangle([x, y, x+random.randint(5,30), y+random.randint(5,30)],
                   fill=(random.randint(180, 240), random.randint(180, 240), random.randint(180, 240)))

img.save(test_img)
print(f"   合成测试图: {test_img} ({img.size})")

# ── Step 2: 清晰度增强 ──
print()
print("=" * 50)
print("Step 2: 清晰度增强")
print("=" * 50)

original = Image.open(test_img)

# 2a. 锐化
sharpened = original.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
print(f"   锐化: UnsharpMask(radius=2, percent=150) ✓")

# 2b. 对比度增强（让面部特征更清晰）
enhancer = ImageEnhance.Contrast(sharpened)
contrasted = enhancer.enhance(1.2)
print(f"   对比度: 1.2x ✓")

# 2c. 亮度微调
brightness = ImageEnhance.Brightness(contrasted)
brightened = brightness.enhance(1.05)
print(f"   亮度: 1.05x ✓")

enhanced_path = test_img.parent / "test_face_enhanced.png"
brightened.save(enhanced_path)
print(f"   结果: {enhanced_path}")

# ── Step 3: 背景优化 ──
print()
print("=" * 50)
print("Step 3: 背景优化")
print("=" * 50)

# 简单策略：将边缘区域统一为纯色，减少背景噪音干扰AI生成
# 实际场景会用rembg或MediaPipe分割——这里验证流程骨架

bg_optimized = brightened.copy()
draw = ImageDraw.Draw(bg_optimized)
# 边缘模糊过渡带
for i in range(20):
    draw.rectangle([0, i, 511, i+1], fill=(240, 240, 240))
    draw.rectangle([0, 511-i-1, 511, 511-i], fill=(240, 240, 240))
    draw.rectangle([i, 0, i+1, 511], fill=(240, 240, 240))
    draw.rectangle([511-i-1, 0, 511-i, 511], fill=(240, 240, 240))

# 上半部（头顶以上）统一白底
draw.rectangle([0, 0, 512, 40], fill=(240, 240, 240))
print(f"   边缘清洗: 20px过渡带 + 顶部白底 ✓")

bg_path = test_img.parent / "test_face_preprocessed.png"
bg_optimized.save(bg_path)
print(f"   结果: {bg_path}")

# ── 汇总 ──
print()
print("=" * 50)
print("✅ V2 照片预处理管线通过")
print(f"   输入: {test_img}")
print(f"   增强: {enhanced_path}")
print(f"   成品: {bg_path}")
print("=" * 50)
