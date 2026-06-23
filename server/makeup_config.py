"""妆容全局配置——基准提示词 + 浓度调节 · 从 JSON 读取"""
import json
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent / "makeup_config.json"

_DEFAULTS = {
    "global_prompt": (
        "professional makeup photography, natural skin texture, soft studio lighting, "
        "high quality portrait, keep facial features and identity fully recognizable"
    ),
    "intensity_modifier": {
        "淡妆": "light natural makeup, barely-there look",
        "自然妆": "natural everyday makeup, fresh and clean",
        "标准妆": "balanced makeup matching reference intensity",
        "浓妆": "bold dramatic makeup, richer and more defined",
        "精致浓妆": "ultra-refined glam makeup, maximum definition and saturation",
    },
}


def _load_config() -> dict:
    if _CONFIG_PATH.exists():
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            merged = {**_DEFAULTS, **cfg}
            for key in ("intensity_modifier",):
                if key in cfg and key in _DEFAULTS:
                    merged[key] = {**_DEFAULTS[key], **cfg[key]}
            return merged
        except (json.JSONDecodeError, OSError):
            pass
    _save_config(_DEFAULTS)
    return dict(_DEFAULTS)


def _save_config(cfg: dict) -> None:
    with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def get_config() -> dict:
    return _load_config()


def update_config(data: dict) -> dict:
    """仅允许更新 global_prompt——浓度从 JSON 文件直接编辑"""
    cfg = _load_config()
    if "global_prompt" in data and data["global_prompt"]:
        cfg["global_prompt"] = data["global_prompt"]
    _save_config(cfg)
    return cfg


_config = _load_config()
GLOBAL_PROMPT = _config["global_prompt"]
INTENSITY_MODIFIER = _config["intensity_modifier"]


def build_prompt(intensity: str = "标准妆", extra: str = "") -> str:
    """组装最终 prompt·支持 {intensity} 占位符替换"""
    cfg = _load_config()
    prompt = cfg["global_prompt"]
    mod = cfg["intensity_modifier"].get(intensity, "")

    # 占位符替换
    if "{intensity}" in prompt:
        prompt = prompt.replace("{intensity}", mod)
    elif mod:
        # 兼容：无占位符则追加到末尾
        prompt = prompt + "。" + mod

    if extra:
        prompt = prompt + "。" + extra

    return prompt
