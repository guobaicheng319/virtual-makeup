# L-009 关键技术分歧 · 试妆助手

> 铁椅 v3.4 外部搜索发现·2026-06-23

## 分歧 1：面部检测库选择

face-api.js 被我推荐时假设其"成熟稳定"——外部搜索爆出其已停更 6 年。

| 维度 | face-api.js | MediaPipe Face Mesh |
|------|------------|-------------------|
| 最近发布 | v0.22.2 / 2020年 | 持续更新 / Google维护 |
| 关键点 | 68点 | 478点（含唇形/眼睑细节） |
| WASM体积 | ~2MB (tiny face) + ~6MB (ssd mobilenet) | ~6MB |
| 维护状态 | 🔴 停更·453 open issues | 🟢 活跃·Google官方 |
| Chrome 119+ | 🔴 WebGL texImage2D黑屏未修 | 🟢 兼容 |
| 微信WebView | ❓ 无人验证 | ❓ 需实测 |
| 许可证 | MIT | Apache 2.0 |
| 文档 | 单README | 完整文档+examples |

### 决策

```
选择：先用 face-api.js 交付，通过 FaceDetector 接口隔离
原因：
  1. MediaPipe 的 478 点妆容定位是过度设计——68 点足够嘴唇/眼影/腮红/眉毛定位
  2. face-api.js 的 WASM 体积更小（~2MB vs ~6MB），冷启动加载更快
  3. 切换到 MediaPipe 的成本 = 写一个 MediaPipeFaceDetector adapter（~200行）——不改 M3/M4/M5

切换触发条件（满足任一）：
  - Chrome 更新后 WebGL 黑屏且无法降级绕过
  - 微信 WebView 上 face-api.js 完全不可用
  - 需要 478 点精度做唇形妆容（目前不需要）

隔离方式：
  interface FaceDetector {
    detect(image: ImageSource): Promise<DetectionResult>
  }
  → 当前: FaceApiDetector implements FaceDetector
  → 未来: MediaPipeDetector implements FaceDetector
  → M3/M4/M5 只依赖 FaceDetector 接口，不 import face-api.js 具体类
```

---

## 分歧 2：Canvas 渲染——Canvas 2D vs WebGL

| 维度 | Canvas 2D | WebGL (Three.js/PixiJS) |
|------|----------|------------------------|
| 学习曲线 | 低·标准API | 高·需Shader知识 |
| 性能 | 30fps at 720p | 60fps at 1080p |
| 微信兼容 | 🟢 微信WebView支持 | 🟡 部分支持·texImage2D黑屏 |
| 妆容效果 | globalCompositeOperation 14种blend | 自定义shader·任意blend |
| 复杂度 | 50行叠加一层 | 200行+ 初始化+shader编译 |

### 决策

```
选择：Canvas 2D · blend mode：multiply（口红/腮红）·overlay（眼影）
原因：
  1. 面部关键点定位→缩放图层PNG→globalCompositeOperation合成——14种blend够妆容效果
  2. 微信WebView对WebGL支持不稳定，Canvas 2D是安全基线
  3. 1个月时间窗不允许Shader开发+调试
  4. 30fps at 720p 对"预览妆容→决定是否预约"足够——不是实时美颜App

切换条件：化妆师反馈"效果不够真"且确认是blend mode限制（不是图层模板质量问题）
```

---

## 分歧 3：前端部署——Vercel vs 微信小程序

| 维度 | Vercel/Netlify Web | 微信小程序 |
|------|-------------------|-----------|
| 开发成本 | 低·标准Vue3 | 高·WXML+WXSS+JS |
| 分发 | QR码·链接·公众号菜单 | 微信搜索+附近的小程序 |
| 摄像头权限 | getUserMedia直接调 | wx.chooseMedia/wx.createCameraContext |
| 分享 | Web Share API / 长按保存 | 原生分享按钮 |
| 留资 | 填表单 | 微信一键授权手机号 |
| 审核 | 无 | 需审核·类目"化妆"需要资质 |

### 决策

```
选择：Web 优先——1个月内上线
原因：
  1. 小程序需要营业执照+类目审核——新工作室可能没走完注册
  2. Web开发速度是小程序的3倍——标准Vue3，无需学WXML
  3. 微信内打开Web = 同样QR码+同样微信内置浏览器
  4. 留资表单填手机号 vs 微信授权——表单更简单，先跑通转化链路

切换条件：工作室营业执照就绪 + Web版跑通验证了"试妆→留资"转化率 > 考虑小程序
```

---

*铁椅 v3.4 外部搜索+变化椅分析 · 2026-06-23*
