"""图片处理管线 · enhance→generate→refine · 依赖 ark_client"""
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

from server.ark_client import ArkClient, ArkResult, get_client
from server.makeup_config import build_prompt

log = logging.getLogger("virtual-makeup.pipeline")

UPLOAD_DIR = Path(__file__).parent.parent / "public" / "uploads"


@dataclass
class PipelineResult:
    """管线执行结果"""
    success: bool
    enhanced_path: str = ""
    generated_url: str = ""
    generated_urls: list = field(default_factory=list)  # 多张变体
    refined_url: str = ""
    error_stage: str = ""
    error_message: str = ""
    tokens_used: int = 0


class Pipeline:
    """试妆图片处理管线"""

    def __init__(self, client: Optional[ArkClient] = None):
        self.client = client or get_client()

    # ── 完整流程 ──

    def run(self, image: Image.Image,
            intensity: str = "标准妆",
            extra: str = "",
            ref_image_url: Optional[str] = None,
            do_refine: bool = False,
            size: str = "1024x1024", n: int = 1) -> PipelineResult:
        """
        执行完整试妆管线。

        Args:
            image: 用户上传的素颜照（PIL Image）
            category: 分类——日常妆/新娘妆/晚宴妆/其他
            intensity: 浓度——lighter/same/stronger
            extra: 额外描述（自备参考图时用户手写）
            ref_image_url: 参考妆容图的公开 URL
            do_refine: 是否执行精修

        Returns:
            PipelineResult
        """
        # Step 1: 增强
        enhanced = self.enhance(image)
        enhanced_path = str(self._save_upload(enhanced, prefix="enhanced"))
        log.info("增强完成: %s", enhanced_path)

        # Step 2: 生成
        gen_result = self.generate(
            intensity=intensity, extra=extra,
            image_urls=[ref_image_url] if ref_image_url else None,
            size=size, n=n)
        if not gen_result.success:
            return PipelineResult(success=False, enhanced_path=enhanced_path,
                                  error_stage="generate", error_message=gen_result.error_message)
        tokens = gen_result.tokens_used

        # Step 3: 精修（可选）
        refined_url = ""
        if do_refine and gen_result.image_url:
            ref_result = self.refine(gen_result.image_url)
            if ref_result.success:
                refined_url = ref_result.image_url
                tokens += ref_result.tokens_used
            else:
                log.warning("精修失败·降级使用生成原图: %s", ref_result.error_message)

        return PipelineResult(
            success=True,
            enhanced_path=enhanced_path,
            generated_url=gen_result.image_url,
            generated_urls=gen_result.image_urls,
            refined_url=refined_url,
            tokens_used=tokens,
        )

    # ── 各阶段 ──

    def enhance(self, image: Image.Image) -> Image.Image:
        """
        照片预处理——清晰度增强 + 背景优化。
        不修改原图，返回新 Image。
        """
        img = image.copy()

        # 锐化
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

        # 对比度微调
        img = ImageEnhance.Contrast(img).enhance(1.15)

        # 亮度微调
        img = ImageEnhance.Brightness(img).enhance(1.05)

        return img

    def generate(self, intensity: str = "标准妆", extra: str = "",
                 image_url: Optional[str] = None,
                 image_urls: Optional[list[str]] = None,
                 size: str = "1024x1024", n: int = 1) -> ArkResult:
        prompt = build_prompt(intensity, extra)
        return self.client.generate(prompt,
            image_url=image_url, image_urls=image_urls,
            size=size, n=n)

    def refine(self, image_url: str) -> ArkResult:
        prompt = (
            "enhance photo quality, natural skin texture, professional makeup photography, "
            "soft bokeh background, high-end retouching, keep facial identity unchanged"
        )
        return self.client.generate(prompt, image_url=image_url)

    # ── 辅助 ──

    def _save_upload(self, image: Image.Image, prefix: str = "img") -> Path:
        """将 PIL Image 保存到 public/uploads 目录"""
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        import uuid
        filename = f"{prefix}_{uuid.uuid4().hex[:12]}.png"
        path = UPLOAD_DIR / filename
        image.save(path, format="PNG")
        return path
