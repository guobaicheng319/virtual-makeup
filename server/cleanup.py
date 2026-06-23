"""定时清理模块 · 删除超过 24h 的增强图 · 独立运行"""
import os
import sys
import time
import logging
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] cleanup: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("virtual-makeup.cleanup")

UPLOAD_DIR = PROJECT_ROOT / "public" / "uploads"
MAX_AGE_SECONDS = 24 * 60 * 60  # 24 小时


def clean_old_files(dry_run: bool = False) -> dict:
    """
    删除 public/uploads 中超过 24 小时的文件。
    返回: {"deleted": int, "kept": int, "errors": int}
    """
    if not UPLOAD_DIR.exists():
        log.info("uploads 目录不存在·跳过")
        return {"deleted": 0, "kept": 0, "errors": 0}

    now = time.time()
    deleted = 0
    kept = 0
    errors = 0

    for f in UPLOAD_DIR.iterdir():
        if not f.is_file():
            continue
        try:
            age = now - f.stat().st_mtime
            if age > MAX_AGE_SECONDS:
                age_hours = age / 3600
                if dry_run:
                    log.info("[DRY-RUN] 将删除: %s (%.1f 小时前)", f.name, age_hours)
                else:
                    f.unlink()
                    log.info("已删除: %s (%.1f 小时前)", f.name, age_hours)
                deleted += 1
            else:
                kept += 1
        except OSError as e:
            log.error("删除失败 %s: %s", f.name, e)
            errors += 1

    log.info("清理完成: 删除=%d 保留=%d 错误=%d", deleted, kept, errors)
    return {"deleted": deleted, "kept": kept, "errors": errors}


def run_forever(interval: int = 3600):
    """以守护模式运行·每 interval 秒清理一次"""
    log.info("清理守护启动·间隔=%ds·最大保留=%dh", interval, MAX_AGE_SECONDS // 3600)
    while True:
        clean_old_files()
        time.sleep(interval)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="试妆助手·定时清理")
    parser.add_argument("--dry-run", action="store_true", help="预览模式·不实际删除")
    parser.add_argument("--daemon", type=int, default=0, metavar="SECONDS",
                        help="守护模式·每隔 SECONDS 秒清理一次")
    args = parser.parse_args()

    if args.daemon:
        run_forever(args.daemon)
    else:
        result = clean_old_files(dry_run=args.dry_run)
        sys.exit(0 if result["errors"] == 0 else 1)
