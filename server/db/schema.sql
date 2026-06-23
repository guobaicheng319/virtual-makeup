-- 试妆助手 · 数据库 Schema v3 · AI生成方案 · 2026-06-23
-- L-017: Schema 变更是代码的一部分——此文件与代码一起版本化

-- ═══════════════════════════════════════
-- 妆容模板表
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,                      -- 日常妆/新娘妆/晚宴妆/其他
    description TEXT DEFAULT '',
    makeup_style TEXT NOT NULL DEFAULT '日常',    -- 甜酷/纯欲/欧美/日系/韩系/日常
    color_tone TEXT NOT NULL DEFAULT '暖调',      -- 暖调/冷调/中性

    -- 参考妆容图（AI 生成的 prompt 参考）
    image_url TEXT NOT NULL DEFAULT '',
    -- 缩略图
    thumbnail_url TEXT NOT NULL DEFAULT '',

    -- 生成 prompt 模板（给 Doubao 的描述）
    prompt_template TEXT NOT NULL DEFAULT '',

    is_published INTEGER NOT NULL DEFAULT 0,
    sort_order INTEGER NOT NULL DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════
-- 留资表
-- ═══════════════════════════════════════
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT NOT NULL,
    wechat TEXT NOT NULL DEFAULT '',
    name TEXT DEFAULT '',
    preferred_date TEXT DEFAULT '',
    source_channel TEXT DEFAULT 'web',
    template_id INTEGER DEFAULT NULL,

    status TEXT NOT NULL DEFAULT 'new'
        CHECK(status IN ('new','contacted','booked','completed','cancelled')),

    notes TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════
-- 索引
-- ═══════════════════════════════════════
CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);
CREATE INDEX IF NOT EXISTS idx_templates_published ON templates(is_published);
CREATE INDEX IF NOT EXISTS idx_templates_style ON templates(makeup_style);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created ON leads(created_at);
