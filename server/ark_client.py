"""火山方舟 API 封装 · Doubao-Seedream-4.0 · 不依赖其他模块"""
import os
import time
import logging
import requests
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

log = logging.getLogger("virtual-makeup.ark")

# ── 加载 .env ──
_ENV_FILE = Path(__file__).parent.parent / ".env"
if _ENV_FILE.exists():
    for _line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())


@dataclass
class ArkResult:
    """API 调用结果"""
    success: bool
    image_url: str = ""
    image_urls: list = field(default_factory=list)  # 多张生成结果
    raw_response: dict = field(default_factory=dict)
    error_code: str = ""
    error_message: str = ""
    tokens_used: int = 0


class ArkClient:
    """火山方舟 Doubao-Seedream-4.0 客户端"""

    BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
    MAX_RETRIES = 2
    RETRY_DELAY = 2  # seconds

    def __init__(self, api_key: Optional[str] = None, endpoint_id: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ARK_API_KEY", "")
        self.endpoint_id = endpoint_id or os.environ.get("ARK_ENDPOINT_ID", "")
        if not self.api_key:
            raise ValueError("ARK_API_KEY 未设置——请在 .env 或环境变量中配置")
        if not self.endpoint_id:
            raise ValueError("ARK_ENDPOINT_ID 未设置——请在 .env 或环境变量中配置")

    # ── 公开方法 ──

    def generate(self, prompt: str, image_url: Optional[str] = None,
                 image_urls: Optional[list[str]] = None,
                 size: str = "1024x1024", n: int = 1,
                 watermark: bool = False) -> ArkResult:
        """
        调用 Seedream-4.0 生成图片。

        Args:
            prompt: 图片描述
            image_url: 单张参考图 URL（i2i 模式）
            image_urls: 多张参考图 URL 数组（最多 10 张）
            size: 输出尺寸 1024x1024 / 2K / 4K
            n: 生成张数 1-4
            watermark: 是否加水印

        Returns:
            ArkResult——success=True 时 image_url 有值（多张时仅返回第一张 URL）
        """
        body = {
            "model": self.endpoint_id,
            "prompt": prompt,
            "n": max(1, min(n, 4)),
            "size": size,
            "response_format": "url",
            "watermark": watermark,
        }
        if image_urls:
            body["image_urls"] = [u for u in image_urls[:10] if u]
        elif image_url:
            body["image_urls"] = [image_url]

        return self._call_with_retry(body)

    # ── 内部 ──

    def _call_with_retry(self, body: dict) -> ArkResult:
        """带重试的 API 调用"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        last_error = ""

        for attempt in range(1 + self.MAX_RETRIES):
            try:
                # L-015: 显式超时——保护调用方不被卡死
                resp = requests.post(
                    self.BASE_URL, json=body, headers=headers,
                    timeout=(10, 60)  # (connect, read)
                )

                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("data", [])
                    img_url = items[0].get("url", "") if items else ""
                    img_urls = [it.get("url", "") for it in items if it.get("url")]
                    tokens = data.get("usage", {}).get("total_tokens", 0)
                    log.info("API 调用成功·tokens=%s·images=%d", tokens, len(img_urls))
                    return ArkResult(success=True, image_url=img_url,
                                     image_urls=img_urls, raw_response=data, tokens_used=tokens)

                if resp.status_code == 429:
                    log.warning("API 限流·attempt=%d/%d", attempt + 1, 1 + self.MAX_RETRIES)
                    if attempt < self.MAX_RETRIES:
                        time.sleep(self.RETRY_DELAY * (attempt + 1))
                    last_error = "请求过于频繁，请稍后重试"
                    continue

                if resp.status_code >= 500:
                    log.warning("服务端错误 %d·attempt=%d/%d", resp.status_code, attempt + 1, 1 + self.MAX_RETRIES)
                    if attempt < self.MAX_RETRIES:
                        time.sleep(self.RETRY_DELAY * (attempt + 1))
                    last_error = f"服务器错误 ({resp.status_code})"
                    continue

                # 4xx 不重试
                err_data = resp.json() if resp.text else {}
                err_msg = err_data.get("error", {}).get("message", resp.text[:200])
                log.error("API 请求错误 %d: %s", resp.status_code, err_msg)
                return ArkResult(success=False, error_code=str(resp.status_code),
                                 error_message=err_msg)

            except requests.exceptions.Timeout:
                log.warning("API 超时·attempt=%d/%d", attempt + 1, 1 + self.MAX_RETRIES)
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                last_error = "AI 服务响应超时，请稍后重试"

            except requests.exceptions.ConnectionError as e:
                log.error("API 连接失败: %s", e)
                return ArkResult(success=False, error_code="CONNECTION",
                                 error_message="无法连接到 AI 服务，请检查网络")

        return ArkResult(success=False, error_code="RETRY_EXHAUSTED", error_message=last_error)


# ── 模块级便捷函数 ──
_default_client: Optional[ArkClient] = None


def get_client() -> ArkClient:
    global _default_client
    if _default_client is None:
        _default_client = ArkClient()
    return _default_client
