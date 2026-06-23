"""试妆助手 · Flask 后端入口 · 阶段 2"""
import os
import sys
import time
import uuid
import logging
import sqlite3
from pathlib import Path
from io import BytesIO

# 确保项目根目录在 Python 路径上
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from flask import Flask, jsonify, request, send_from_directory, send_file
from PIL import Image

# ── 日志 ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("virtual-makeup")

# ── 初始化数据库 ──
from server.db.store import init_db
init_db()

# ── 导入业务模块 ──
from server.db.store import TemplateStore, LeadStore
from server.pipeline import Pipeline
from server.makeup_config import get_config, update_config

pipeline = Pipeline()

# ── 项目路径 ──
PROJECT_ROOT = Path(__file__).parent.parent
PUBLIC_DIR = PROJECT_ROOT / "public"
UPLOAD_DIR = PUBLIC_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_IMG_DIR = PUBLIC_DIR / "images"
TEMPLATE_IMG_DIR.mkdir(parents=True, exist_ok=True)

IMG_EXPIRY_SECONDS = 86400  # 24h


def create_app() -> Flask:
    app = Flask(__name__, static_folder=str(PUBLIC_DIR), static_url_path="/static")

    # L-005: 密钥从环境变量
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-change-in-production")

    # ── 静态文件 ──
    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        return send_from_directory(str(PUBLIC_DIR / "assets"), filename)

    @app.route("/images/<path:filename>")
    def serve_template_img(filename):
        return send_from_directory(str(TEMPLATE_IMG_DIR), filename)

    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(str(UPLOAD_DIR), filename)

    # ── 图片上传（管理后台用）──
    @app.route("/api/upload", methods=["POST"])
    def api_upload():
        if "file" not in request.files:
            return jsonify({"error": {"code": "NO_FILE", "message": "请选择文件"}}), 400
        file = request.files["file"]
        try:
            img = Image.open(file.stream)
            img.verify()
        except Exception:
            return jsonify({"error": {"code": "INVALID_IMAGE", "message": "无法解析图片"}}), 400

        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "png"
        if ext not in ("png", "jpg", "jpeg", "webp"):
            ext = "png"
        filename = f"tmpl_{uuid.uuid4().hex[:12]}.{ext}"
        file.seek(0)
        img = Image.open(file.stream).convert("RGB")
        img.save(str(TEMPLATE_IMG_DIR / filename))

        url = f"/images/{filename}"
        log.info("模板图片上传: %s", filename)
        return jsonify({"url": url, "filename": filename})

    # ── SPA 入口 ──
    @app.route("/")
    def serve_index():
        index_html = PUBLIC_DIR / "index.html"
        if index_html.exists():
            return send_from_directory(str(PUBLIC_DIR), "index.html")
        return jsonify({"status": "ok", "message": "前端尚未构建"})

    # ── 管理后台 ──
    @app.route("/admin")
    def serve_admin():
        admin_html = PUBLIC_DIR / "admin.html"
        if admin_html.exists():
            return send_from_directory(str(PUBLIC_DIR), "admin.html")
        return jsonify({"error": {"code": "NOT_FOUND", "message": "管理后台页面不存在"}}), 404

    # ── 健康检查 ──
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "virtual-makeup", "stage": "2"})

    # ═══════════════════════════════════════
    # 试妆管线 API
    # ═══════════════════════════════════════

    @app.route("/api/enhance", methods=["POST"])
    def api_enhance():
        """上传照片 → 清晰度增强 → 返回增强图 URL"""
        if "image" not in request.files:
            return jsonify({"error": {"code": "NO_IMAGE", "message": "请上传照片"}}), 400

        file = request.files["image"]
        try:
            img = Image.open(file.stream).convert("RGB")
        except Exception:
            return jsonify({"error": {"code": "INVALID_IMAGE", "message": "无法解析图片，请上传 JPG/PNG 格式"}}), 400

        enhanced = pipeline.enhance(img)
        filename = f"enhanced_{uuid.uuid4().hex[:12]}.png"
        enhanced.save(str(UPLOAD_DIR / filename), format="PNG")

        url = f"/uploads/{filename}"
        log.info("增强完成: %s (%dx%d)", filename, enhanced.width, enhanced.height)
        return jsonify({"url": url, "width": enhanced.width, "height": enhanced.height})

    @app.route("/api/generate", methods=["POST"])
    def api_generate():
        """调用 Doubao 生成妆容图"""
        data = request.get_json(silent=True) or {}
        prompt = data.get("prompt", "").strip()
        if not prompt:
            return jsonify({"error": {"code": "NO_PROMPT", "message": "请填写妆容描述"}}), 400

        ref_url = data.get("ref_image_url", "") or None

        result = pipeline.generate(prompt, image_url=ref_url)
        if not result.success:
            return jsonify({"error": {"code": result.error_code, "message": result.error_message}}), 502

        return jsonify({
            "result_url": result.image_url,
            "tokens_used": result.tokens_used,
        })

    @app.route("/api/refine", methods=["POST"])
    def api_refine():
        """妆后精修——对生成图做二次优化"""
        data = request.get_json(silent=True) or {}
        image_url = data.get("image_url", "").strip()
        if not image_url:
            return jsonify({"error": {"code": "NO_URL", "message": "请提供待精修的图片 URL"}}), 400

        result = pipeline.refine(image_url)
        if not result.success:
            return jsonify({"error": {"code": result.error_code, "message": result.error_message}}), 502

        return jsonify({
            "result_url": result.image_url,
            "tokens_used": result.tokens_used,
        })

    @app.route("/api/try-on", methods=["POST"])
    def api_try_on():
        """一键试妆——上传照片+妆容描述 → 返回生成结果"""
        if "image" not in request.files:
            return jsonify({"error": {"code": "NO_IMAGE", "message": "请上传照片"}}), 400

        # 新方案：intensity 替代手写 prompt
        intensity = request.form.get("intensity", "标准妆")
        extra = request.form.get("extra", "").strip()

        template_id = request.form.get("template_id")

        do_refine = request.form.get("refine", "0") == "1"
        size = request.form.get("size", "1024x1024")
        n = int(request.form.get("n", "1"))

        # 参考图：优先用模板效果图 URL，其次用上传的参考图文件
        ref_url = request.form.get("ref_image_url", "").strip() or None
        if not ref_url and "ref_image" in request.files:
            ref_file = request.files["ref_image"]
            ref_filename = f"ref_{uuid.uuid4().hex[:12]}.png"
            ref_img = Image.open(ref_file.stream).convert("RGB")
            ref_img.save(str(UPLOAD_DIR / ref_filename), format="PNG")
            ref_url = f"/uploads/{ref_filename}"

        # 相对路径 → 完整公网 URL（Doubao 需要公网可访问）
        if ref_url and ref_url.startswith("/"):
            scheme = request.headers.get("X-Forwarded-Proto", "https")
            host = request.headers.get("X-Forwarded-Host", request.host)
            ref_url = f"{scheme}://{host}{ref_url}"

        try:
            file = request.files["image"]
            img = Image.open(file.stream).convert("RGB")
        except Exception:
            return jsonify({"error": {"code": "INVALID_IMAGE", "message": "无法解析图片"}}), 400

        result = pipeline.run(img, intensity=intensity, extra=extra,
                              ref_image_url=ref_url, do_refine=do_refine, size=size, n=n)
        if not result.success:
            return jsonify({
                "error": {"code": "GENERATION_FAILED", "message": result.error_message},
                "enhanced_url": f"/uploads/{Path(result.enhanced_path).name}"
            }), 502

        return jsonify({
            "enhanced_url": f"/uploads/{Path(result.enhanced_path).name}",
            "generated_url": result.generated_url,
            "generated_urls": result.generated_urls,
            "refined_url": result.refined_url,
            "tokens_used": result.tokens_used,
        })

    # ═══════════════════════════════════════
    # 妆容模板 API
    # ═══════════════════════════════════════

    @app.route("/api/templates", methods=["GET"])
    def api_templates_list():
        category = request.args.get("category")
        published_only = request.args.get("published_only", "true") != "false"
        templates = TemplateStore.list_all(category=category, published_only=published_only)
        return jsonify(templates)

    @app.route("/api/templates/<int:tid>", methods=["GET"])
    def api_templates_get(tid):
        tmpl = TemplateStore.get(tid)
        if not tmpl:
            return jsonify({"error": {"code": "NOT_FOUND", "message": "模板不存在"}}), 404
        return jsonify(tmpl)

    @app.route("/api/templates", methods=["POST"])
    def api_templates_create():
        data = request.get_json(silent=True) or {}
        name = data.get("name", "").strip()
        category = data.get("category", "").strip()
        if not name or not category:
            return jsonify({"error": {"code": "MISSING_FIELDS", "message": "name 和 category 为必填"}}), 400

        tid = TemplateStore.create(
            name=name, category=category,
            description=data.get("description", ""),
            makeup_style=data.get("makeup_style", "日常"),
            color_tone=data.get("color_tone", "暖调"),
            image_url=data.get("image_url", ""),
            thumbnail_url=data.get("thumbnail_url", ""),
            prompt_template=data.get("prompt_template", ""),
        )
        return jsonify({"id": tid, "name": name}), 201

    @app.route("/api/templates/<int:tid>", methods=["PUT"])
    def api_templates_update(tid):
        data = request.get_json(silent=True) or {}
        ok = TemplateStore.update(tid, **data)
        if not ok:
            return jsonify({"error": {"code": "NOT_FOUND", "message": "模板不存在或无有效字段"}}), 404
        return jsonify({"id": tid, "updated": True})

    @app.route("/api/templates/<int:tid>", methods=["DELETE"])
    def api_templates_delete(tid):
        ok = TemplateStore.delete(tid)
        if not ok:
            return jsonify({"error": {"code": "NOT_FOUND", "message": "模板不存在"}}), 404
        return jsonify({"id": tid, "deleted": True})

    # ═══════════════════════════════════════
    # 留资 API
    # ═══════════════════════════════════════

    @app.route("/api/leads", methods=["GET"])
    def api_leads_list():
        status = request.args.get("status")
        leads = LeadStore.list_all(status=status)
        return jsonify(leads)

    @app.route("/api/leads", methods=["POST"])
    def api_leads_create():
        data = request.get_json(silent=True) or {}
        phone = data.get("phone", "").strip()
        if not phone:
            return jsonify({"error": {"code": "MISSING_PHONE", "message": "请填写手机号"}}), 400

        lid = LeadStore.create(
            phone=phone,
            wechat=data.get("wechat", ""),
            name=data.get("name", ""),
            preferred_date=data.get("preferred_date", ""),
            template_id=data.get("template_id"),
            source_channel=data.get("source_channel", "web"),
        )
        return jsonify({"id": lid}), 201

    @app.route("/api/leads/<int:lid>", methods=["PUT"])
    def api_leads_update(lid):
        data = request.get_json(silent=True) or {}
        status = data.get("status", "")
        notes = data.get("notes", "")
        ok = LeadStore.update_status(lid, status, notes)
        if not ok:
            return jsonify({"error": {"code": "NOT_FOUND", "message": "记录不存在"}}), 404
        return jsonify({"id": lid, "updated": True})

    # ═══════════════════════════════════════
    # 全局配置 API
    # ═══════════════════════════════════════

    @app.route("/api/config", methods=["GET", "PUT"])
    def api_config():
        if request.method == "PUT":
            data = request.get_json(silent=True) or {}
            cfg = update_config(data)
            return jsonify(cfg)
        return jsonify(get_config())

    # ═══════════════════════════════════════
    # 错误处理
    # ═══════════════════════════════════════

    @app.errorhandler(500)
    def handle_500(e):
        log.error("内部错误: %s", e)
        return jsonify({"error": {"code": "INTERNAL", "message": "服务器内部错误"}}), 500

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": {"code": "NOT_FOUND", "message": "接口不存在"}}), 404

    return app


if __name__ == "__main__":
    log.info("启动试妆助手 Flask 后端 (阶段 2)")
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False)
