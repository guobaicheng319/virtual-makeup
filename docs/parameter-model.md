# 妆容参数模型 · 混合方案 C

> 快椅 v2.0 分析输出 · 57 参数→三档分流 · 2026-06-23

---

## 产品决策

```
用户操作流: 选模板(化妆师预设) → 调关键slider(个性化) → 看效果 → 预约

模板 = 化妆师在后台配好 42 个预设参数 + 上传 PNG 图层
Slider = 用户在前端调 10 个关键参数 (实时 Canvas 叠加)
风格 = 5 个全局枚举 (整体切换)
```

---

## 一、参数三档分流

### 🎚️ Slider（10 个·用户前端可调·实时 Canvas 叠加）

| # | 参数 | 类型 | 范围 | 默认 | 实现方式 |
|:--:|------|------|------|------|------|
| 1 | `lipColor` | hex color | 色盘 | 模板预设 | Canvas α+color 叠加嘴唇区域 |
| 2 | `lipSaturation` | float | 0.0-1.0 | 0.8 | Canvas saturation filter |
| 3 | `eyeColor` | hex color | 色盘 | 模板预设 | Canvas α+color 叠加眼睑区域 |
| 4 | `blushColor` | hex color | 色盘 | 模板预设 | Canvas α+color 叠加脸颊区域 |
| 5 | `blushOpacity` | float | 0.0-1.0 | 0.5 | 腮红 PNG 图层 globalAlpha |
| 6 | `foundationColor` | hex color | 色盘 | 模板预设 | Canvas α+color 全脸覆盖 |
| 7 | `foundationOpacity` | float | 0.0-1.0 | 0.3 | 粉底 PNG 图层 globalAlpha |
| 8 | `contourIntensity` | float | 0.0-1.0 | 0.5 | 修容 PNG 图层 globalAlpha |
| 9 | `highlightIntensity` | float | 0.0-1.0 | 0.5 | 高光 PNG 图层 globalAlpha |
| 10 | `noseShadowDepth` | float | 0.0-1.0 | 0.5 | 鼻影 PNG 图层 globalAlpha |

### 🏷️ Style（5 个·全局枚举选择·整体切换）

| # | 参数 | 类型 | 选项 | 实现方式 |
|:--:|------|------|------|------|
| 1 | `makeupStyle` | enum | 甜酷/纯欲/欧美/日系/韩系/日常 | 切换整套模板预设 |
| 2 | `colorTone` | enum | 暖调/冷调/中性 | 全局色温滤镜 |
| 3 | `intensity` | float (0-1) | 0.3淡妆→0.7日常→1.0浓妆 | 全局 alpha 缩放 |
| 4 | `lipFinish` | enum | 哑光matte/镜面glossy/丝绒velvet | 唇部 PNG 换图 |
| 5 | `glitter` | bool | on/off | 叠加亮片 PNG 层 |

### 🔒 Preset（42 个·化妆师后台配置·存模板 JSON·用户不可调）

| 类别 | 参数 | 类型 | 范围 |
|------|------|------|------|
| 底妆 | `coverageStrength` | float | 0.0-1.0 |
| 底妆 | `coverageArea` | enum | 全脸/局部/斑点 |
| 底妆 | `skinSmooth` | float | 0.0-1.0 |
| 眉毛 | `browShape` | enum | 平眉/弯眉/剑眉/柳叶眉/自然 |
| 眉毛 | `browHeadColor` | hex | 色盘 |
| 眉毛 | `browTailColor` | hex | 色盘 |
| 眉毛 | `browThickness` | float | 0.0-1.0 |
| 眉毛 | `browLength` | float | 0.0-1.0 |
| 眉毛 | `browHeight` | float | 0.0-1.0 |
| 眉毛 | `browMist` | float | 0.0-1.0 |
| 眼妆 | `eyeSecondaryColor` | hex | 色盘 |
| 眼妆 | `eyeShimmer` | float | 0.0-1.0 |
| 眼妆 | `eyelinerThickness` | float | 0.0-1.0 |
| 眼妆 | `eyelinerType` | enum | 内眼线/外眼线/全开 |
| 眼妆 | `lashDensity` | float | 0.0-1.0 |
| 眼妆 | `lashLength` | float | 0.0-1.0 |
| 眼妆 | `aegyoSal` | float | 0.0-1.0 (卧蚕) |
| 腮红 | `blushPosition` | enum | 苹果肌/颧骨/太阳穴 |
| 腮红 | `blushArea` | float | 0.0-1.0 |
| 腮红 | `blushShape` | enum | 圆形/椭圆/横扫 |
| 腮红 | `blushFinish` | enum | 哑光/珠光 |
| 修容 | `contourColor` | hex | 色盘 |
| 修容 | `highlightColor` | hex | 色盘 |
| 修容 | `highlightArea` | enum | T区/全脸/局部 |
| 眼线细节 | `wingAngle` | float | 0.0-1.0 |
| 眼线细节 | `eyelinerGradient` | float | 0.0-1.0 |
| 眼线细节 | `innerLinerStrength` | float | 0.0-1.0 |
| 眼线细节 | `lowerLinerOn` | bool | on/off |
| 眼线细节 | `lowerLinerDepth` | float | 0.0-1.0 |
| 睫毛 | `upperLashDensity` | float | 0.0-1.0 |
| 睫毛 | `lowerLashOn` | bool | on/off |
| 睫毛 | `lashCurl` | float | 0.0-1.0 |
| 睫毛 | `lashRootDarkness` | float | 0.0-1.0 |
| 鼻影 | `noseShadowWidth` | float | 0.0-1.0 |
| 鼻影 | `noseTipHighlight` | float | 0.0-1.0 |
| 唇形 | `lipLineClarity` | float | 0.0-1.0 |
| 唇形 | `lipPeakHeight` | float | 0.0-1.0 |
| 唇形 | `lipThickness` | float | 0.0-1.0 |
| 唇形 | `mouthCornerLift` | float | 0.0-1.0 |
| 唇部 | `lipOpacity` | float | 0.0-1.0 |
| 特效 | `freckleOn` | bool | on/off |
| 特效 | `beautyMarkOn` | bool | on/off |

---

## 二、数据库字段设计（templates 表）

```sql
-- templates 表核心字段
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,              -- "夏日蜜桃妆"
    category TEXT NOT NULL,          -- 日常妆/新娘妆/晚宴妆
    description TEXT DEFAULT '',
    thumbnail_url TEXT NOT NULL,

    -- 🔒 预设参数 (JSON·42字段)
    preset_params_json TEXT NOT NULL DEFAULT '{}',
    -- 结构见下方 PRESET_PARAMS_SCHEMA

    -- 🎚️ slider 默认值 (JSON·10字段)
    slider_defaults_json TEXT NOT NULL DEFAULT '{}',
    -- 结构见下方 SLIDER_DEFAULTS_SCHEMA

    -- PNG 图层列表 (JSON数组)
    layers_json TEXT NOT NULL DEFAULT '[]',
    -- [{region, image_url, blend_mode}]

    -- 🏷️ 风格标签
    makeup_style TEXT NOT NULL DEFAULT '日常',
    color_tone TEXT NOT NULL DEFAULT '暖调',

    is_published INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### PRESET_PARAMS_SCHEMA

```json
{
  "coverageStrength": 0.7,
  "coverageArea": "全脸",
  "skinSmooth": 0.5,
  "browShape": "自然",
  "browHeadColor": "#8b5a3c",
  "browTailColor": "#6b3a2e",
  "browThickness": 0.5,
  "browLength": 0.5,
  "browHeight": 0.5,
  "browMist": 0.3,
  "eyeSecondaryColor": "#c49a7c",
  "eyeShimmer": 0.4,
  "eyelinerThickness": 0.5,
  "eyelinerType": "外眼线",
  "lashDensity": 0.6,
  "lashLength": 0.5,
  "aegyoSal": 0.3,
  "blushPosition": "苹果肌",
  "blushArea": 0.5,
  "blushShape": "椭圆",
  "blushFinish": "哑光",
  "contourColor": "#8b7355",
  "highlightColor": "#f5e6d3",
  "highlightArea": "T区",
  "wingAngle": 0.3,
  "eyelinerGradient": 0.5,
  "innerLinerStrength": 0.7,
  "lowerLinerOn": false,
  "lowerLinerDepth": 0.3,
  "upperLashDensity": 0.5,
  "lowerLashOn": false,
  "lashCurl": 0.5,
  "lashRootDarkness": 0.5,
  "noseShadowWidth": 0.4,
  "noseTipHighlight": 0.6,
  "lipLineClarity": 0.6,
  "lipPeakHeight": 0.5,
  "lipThickness": 0.5,
  "mouthCornerLift": 0.0,
  "lipOpacity": 0.8,
  "freckleOn": false,
  "beautyMarkOn": false
}
```

### SLIDER_DEFAULTS_SCHEMA (10 个前端可调参数·模板预设默认值)

```json
{
  "lipColor": "#cc0033",
  "lipSaturation": 0.8,
  "eyeColor": "#9b6b4a",
  "blushColor": "#e8b4b4",
  "blushOpacity": 0.5,
  "foundationColor": "#f5e6d3",
  "foundationOpacity": 0.3,
  "contourIntensity": 0.5,
  "highlightIntensity": 0.5,
  "noseShadowDepth": 0.5
}
```

---

## 三、API 设计（行业标准三元组简化）

> 腾讯特效/BytePlus/Visage SDK 共性：`color(hex) + intensity(0-1) + finish(enum)` 三元组

### GET /api/templates?category=新娘妆

```json
{
  "templates": [{
    "id": 1,
    "name": "夏日蜜桃妆",
    "category": "日常妆",
    "thumbnail_url": "/static/thumbs/peach.jpg",
    "makeup_style": "日常",
    "color_tone": "暖调",
    "slider_defaults": {
      "lipColor": "#cc0033",
      "eyeColor": "#9b6b4a",
      "blushColor": "#e8b4b4",
      "blushOpacity": 0.5,
      "foundationColor": "#f5e6d3",
      "foundationOpacity": 0.3,
      "contourIntensity": 0.5,
      "highlightIntensity": 0.5,
      "noseShadowDepth": 0.5,
      "lipSaturation": 0.8
    }
  }]
}
```

### POST /api/makeup/preview（试妆预览·核心端点）

```json
// Request: 用户选择模板 + 调节 slider 后
{
  "template_id": 1,
  "sliders": {
    "lipColor": "#d4466a",    // 用户换了豆沙粉
    "lipSaturation": 0.6,      // 调淡一点
    "blushOpacity": 0.7        // 腮红加重
  }
}

// Response: 前端用 template.layers + sliders 本地渲染
// 不传图到服务器——M1 FaceDetectionEngine 浏览器本地跑
{ "status": "ok" }
```

### POST /admin/templates（管理后台·创建模板）

```json
{
  "name": "夏日蜜桃妆",
  "category": "日常妆",
  "preset_params": { /* 42字段见上方SCHEMA */ },
  "slider_defaults": { /* 10字段见上方SCHEMA */ },
  "makeup_style": "日常",
  "color_tone": "暖调",
  "layers": [
    {"region": "foundation", "image": "@file: foundation.png", "blend_mode": "normal"},
    {"region": "lips", "image": "@file: lips_peach.png", "blend_mode": "multiply"},
    {"region": "blush", "image": "@file: blush_peach.png", "blend_mode": "multiply"}
  ]
}
```

---

## 四、简化统计

| 档位 | 参数数 | 谁配置 | 实现方式 |
|------|:--:|------|------|
| 🔒 Preset | 42 | 化妆师·管理后台 | 存 JSON → 选模板即应用 |
| 🎚️ Slider | 10 | 用户·前端滑块 | Canvas globalAlpha + fillStyle |
| 🏷️ Style | 5 | 用户·枚举选择 | 全局滤镜 + 图层替换 |
| **合计** | **57** | | |

**独立字段数（去重后）：~25 个**
- 颜色字段统一为 hex（唇色=眼影色=腮红色=粉底色 —— 结构相同，值不同）
- 强度字段统一为 0-1 float
- 枚举字段统一为预定义选项

---

*快椅 v2.0 + 用户决策 · 2026-06-23*
