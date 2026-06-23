"""数据层——TemplateStore + LeadStore · 不依赖其他模块"""
import sqlite3
import logging
from pathlib import Path
from typing import Optional

log = logging.getLogger("virtual-makeup.db")

DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "virtual-makeup.db"
SCHEMA_SQL = Path(__file__).parent / "schema.sql"


def _get_conn() -> sqlite3.Connection:
    """获取数据库连接。调用方负责关闭。"""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """初始化数据库——幂等，已存在则跳过。"""
    conn = _get_conn()
    try:
        if SCHEMA_SQL.exists():
            conn.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
            conn.commit()
            log.info("数据库初始化完成: %s", DB_PATH)
        else:
            log.warning("schema.sql 不存在，跳过建表")
    except sqlite3.Error as e:
        log.error("数据库初始化失败: %s", e)
        raise
    finally:
        conn.close()


# ── TemplateStore ──

class TemplateStore:
    """妆容模板 CRUD"""

    @staticmethod
    def list_all(category: Optional[str] = None, published_only: bool = True) -> list[dict]:
        """列出模板。可按分类筛选，默认只返回已发布。"""
        conn = _get_conn()
        try:
            sql = "SELECT * FROM templates WHERE 1=1"
            params: list = []
            if published_only:
                sql += " AND is_published = 1"
            if category:
                sql += " AND category = ?"
                params.append(category)
            sql += " ORDER BY sort_order DESC, created_at DESC"
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def get(template_id: int) -> Optional[dict]:
        """获取单个模板"""
        conn = _get_conn()
        try:
            row = conn.execute("SELECT * FROM templates WHERE id = ?", (template_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    @staticmethod
    def create(name: str, category: str, image_url: str = "", description: str = "",
               makeup_style: str = "日常", color_tone: str = "暖调",
               prompt_template: str = "", thumbnail_url: str = "") -> int:
        """创建模板，返回 id"""
        conn = _get_conn()
        try:
            cur = conn.execute(
                """INSERT INTO templates (name, category, description, makeup_style, color_tone,
                   image_url, thumbnail_url, prompt_template, is_published)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)""",
                (name, category, description, makeup_style, color_tone,
                 image_url, thumbnail_url, prompt_template))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    @staticmethod
    def update(template_id: int, **kwargs) -> bool:
        """更新模板字段。kwargs 只含允许更新的列。"""
        allowed = {"name", "category", "description", "makeup_style", "color_tone",
                   "image_url", "thumbnail_url", "prompt_template", "is_published", "sort_order"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return False
        conn = _get_conn()
        try:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            set_clause += ", updated_at = CURRENT_TIMESTAMP"
            values = list(updates.values()) + [template_id]
            conn.execute(f"UPDATE templates SET {set_clause} WHERE id = ?", values)
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()

    @staticmethod
    def delete(template_id: int) -> bool:
        """删除模板"""
        conn = _get_conn()
        try:
            conn.execute("DELETE FROM templates WHERE id = ?", (template_id,))
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()


# ── LeadStore ──

class LeadStore:
    """留资管理 CRUD"""

    @staticmethod
    def list_all(status: Optional[str] = None) -> list[dict]:
        """列出全部留资。可按状态筛选。"""
        conn = _get_conn()
        try:
            sql = "SELECT * FROM leads WHERE 1=1"
            params: list = []
            if status:
                sql += " AND status = ?"
                params.append(status)
            sql += " ORDER BY created_at DESC"
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def create(phone: str, wechat: str = "", name: str = "",
               preferred_date: str = "", template_id: Optional[int] = None,
               source_channel: str = "web") -> int:
        """创建留资记录，返回 id"""
        conn = _get_conn()
        try:
            cur = conn.execute(
                """INSERT INTO leads (phone, wechat, name, preferred_date, source_channel, template_id)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (phone, wechat, name, preferred_date, source_channel, template_id))
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    @staticmethod
    def update_status(lead_id: int, status: str, notes: str = "") -> bool:
        """更新留资状态"""
        conn = _get_conn()
        try:
            conn.execute(
                "UPDATE leads SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, notes, lead_id))
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()

    @staticmethod
    def delete(lead_id: int) -> bool:
        """删除留资记录"""
        conn = _get_conn()
        try:
            conn.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
            conn.commit()
            return conn.total_changes > 0
        finally:
            conn.close()
