# face-api.js vs MediaPipe Face Mesh · 技术对比

> M0 V4 纸面对比 · 铁椅 v3.4 要求 · 2026-06-23

---

## 1. 关键点数量与精度

| 维度 | face-api.js | MediaPipe Face Mesh |
|------|------------|-------------------|
| 关键点数 | **68点** (dlib标准) | **478点** (Face Mesh) |
| 覆盖区域 | 眉毛·眼睛·鼻子·嘴唇·脸型 | 同上 + 眼睑·瞳孔·唇内外轮廓 |
| 3D坐标 | ❌ 仅2D (x,y) | ✅ 3D (x,y,z) |
| 妆容定位足够？| ✅ 口红·眼影·腮红·眉毛·粉底——68点够用 | ✅ 更精细——可做唇彩渐变·双眼皮贴 |
| 过度设计？| — | ⚠️ 478点对"预览妆容→预约"是过度设计——精确到瞳孔坐标但对口红定位帮助不大 |

**结论：68 点够用。478 点的额外精度不转化为用户价值。**

---

## 2. WASM 体积与加载性能

| 维度 | face-api.js | MediaPipe Face Mesh |
|------|------------|-------------------|
| 核心库 | ~200KB (face-api.js) | ~500KB (@mediapipe/face_mesh) |
| 模型文件 | 2选项: tiny_face (~2MB) / ssd_mobilenetv1 (~6MB) | ~6MB (face_landmark.tflite) |
| **最小加载** | **~2.2MB** (tiny face) | **~6.5MB** |
| 4G网络加载 | ~5-8秒 | ~12-18秒 |
| 首次加载体验 | 可接受 (配合loading进度条) | 偏长——用户可能放弃 |

**结论：face-api.js 2.2MB 冷启动更快。新媒体环境下这 4MB 差距 = 用户等不等。**

---

## 3. 维护状态与生态

| 维度 | face-api.js | MediaPipe Face Mesh |
|------|------------|-------------------|
| 最后发布 | **2020年** (v0.22.2) | **持续更新** (Google 官方) |
| GitHub Stars | 16.5k (但 453 open issues) | 27k+ (MediaPipe 整体) |
| Issue 解决率 | 极低——核心维护者已离开 | 高——Google 团队维护 |
| Chrome 119+ | 🔴 **WebGL texImage2D 黑屏** | 🟢 兼容 |
| 文档质量 | 单 README + 零散 examples | 完整文档 + 官方 examples + 社区 |
| TypeScript | ✅ 内置类型 | ✅ 内置类型 |
| 社区活跃度 | 🔴 已死 | 🟢 活跃 |
| 保险性 | ❌ 出 bug 没法修——源码在但无人 review PR | ✅ Google 会修 |

**结论：face-api.js 已死。但这不改变我们的选择——因为我们用接口隔离它。**

---

## 4. 微信 WebView 兼容性

| 维度 | face-api.js | MediaPipe Face Mesh |
|------|------------|-------------------|
| WebGL 依赖 | ✅ 有 WebGL 加速路径 (但 Chrome 119+ 黑屏) | ✅ WebGL + WASM |
| Canvas 2D 降级 | ✅ 可降级到 CPU (慢但能跑) | ❓ 不确定 |
| 微信 X5 内核 | ❓ **无人验证过** | ❓ **无人验证过** |
| 微信内置浏览器 | ❓ 未知 | ❓ 未知 |

**结论：两个库在微信 WebView 的兼容性都是未知数。这是 V5 要验证的。**

---

## 5. Canvas Blend Mode 性能

| 维度 | face-api.js 定位 + Canvas 2D | MediaPipe 定位 + Canvas 2D |
|------|------|------|
| 渲染帧率 (720p) | 25-30fps | 25-30fps |
| 关键点抖动 | 需要时序滤波 (M4)  | 本身更稳定——468点自带平滑 |
| CPU 占用 | 中等 (检测 30-50ms/帧) | 较高 (检测 40-70ms/帧) |
| 实时预览 | ✅ 勉强够用 | ⚠️ 更慢——478点计算量更大 |

**结论：face-api.js 在性能上反而更适配我们的场景（轻量·快速·够用）。**

---

## 最终决策

```
选择：face-api.js · tiny_face 模型 · Canvas 2D 渲染

理由排序（按重要性）：
  1. 2.2MB vs 6.5MB——冷启动快 3 倍，对引流场景至关重要
  2. 68 点够用——478 点对"预览妆容→预约"不转化为用户价值
  3. CPU 占用更低——移动端体验更好
  4. 接口隔离（FaceDetector）——死了也不怕，切换成本 = 200 行 adapter

切换条件（满足任一即触发）：
  ● V5 实测 face-api.js 在微信 WebView 完全不可用且 MediaPipe 可用
  ● Chrome 更新后 WebGL 黑屏无法通过降级绕过
  ● 化妆师反馈需要更精细的唇形定位（478 点才能满足）

切换成本：~200 行 MediaPipeFaceDetector adapter——不改 M3/M4/M5/M6/M7
```

---

## 验证状态

- [ ] V5 微信 WebView 实测 face-api.js 能否加载
- [ ] V1 本地 Chrome 加载 face-api.js tiny_face 模型
- [ ] 降级路径验证：WebGL 黑屏 → Canvas 2D CPU 模式

---

*M0 V4 纸面对比 · 铁椅 v3.4 · 2026-06-23*
