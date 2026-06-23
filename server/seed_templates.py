"""种子数据——添加初始妆容模板"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.db.store import TemplateStore, init_db

init_db()

templates = [
    {
        "name": "夏日蜜桃妆",
        "category": "日常妆",
        "makeup_style": "韩系",
        "color_tone": "暖调",
        "description": "清透水光肌+蜜桃色腮红+珊瑚唇，适合日常出街、约会。淡雅不浓，显气色。",
        "prompt_template": "Korean peach makeup style, dewy glass skin, soft coral peach blush on cheeks, coral pink gradient lips, subtle brown eyeliner, natural straight brows, light shimmer on eyelids, fresh and youthful summer look, professional makeup photography, soft natural lighting",
    },
    {
        "name": "气质新娘妆",
        "category": "新娘妆",
        "makeup_style": "日常",
        "color_tone": "暖调",
        "description": "经典新娘造型，自然光泽底妆+玫瑰色唇+柔和眼妆，端庄大方，适合婚礼当天。",
        "prompt_template": "elegant bridal makeup, luminous natural skin, soft rose pink lips, champagne shimmer eyeshadow, defined but soft eyeliner, natural arched brows, subtle highlighter on cheekbones, romantic and timeless bridal look, professional bridal photography, soft diffused studio lighting",
    },
    {
        "name": "烟熏晚宴妆",
        "category": "晚宴妆",
        "makeup_style": "欧美",
        "color_tone": "冷调",
        "description": "深邃烟熏眼妆+裸色唇，气场全开，适合年会、派对、晚宴场合。",
        "prompt_template": "glamorous smokey eye makeup, sophisticated dark grey and brown blended eyeshadow, winged eyeliner, voluminous lashes, nude matte lips, sculpted cheekbones with contour, defined brows, evening party look, professional beauty photography, dramatic soft lighting",
    },
    {
        "name": "纯欲白开水妆",
        "category": "日常妆",
        "makeup_style": "纯欲",
        "color_tone": "中性",
        "description": "伪素颜裸妆感，清透底妆+淡粉唇+若有似无的眼妆，适合上学、通勤。",
        "prompt_template": "clean girl aesthetic makeup, barely-there natural look, ultra-fresh dewy skin, very subtle pink blush, tinted lip balm natural pink, light brown mascara no eyeliner, brushed up natural brows, minimalist fresh-faced beauty, soft natural daylight, professional portrait",
    },
    {
        "name": "日系元气妆",
        "category": "日常妆",
        "makeup_style": "日系",
        "color_tone": "暖调",
        "description": "日杂风橙色系，大面积腮红+水润唇蜜+圆眼妆，元气满满，减龄可爱。",
        "prompt_template": "Japanese igari makeup style, flushed orange-pink draped blush across cheeks and nose bridge, glossy juicy lips, rounded doll-like eyes with brown liner, curled lashes, light peachy eyeshadow, soft matte skin, cute and energetic youthful look, Harajuku inspired, professional beauty photography, bright soft lighting",
    },
]

print("正在添加模板...\n")
for t in templates:
    tid = TemplateStore.create(
        name=t["name"],
        category=t["category"],
        makeup_style=t["makeup_style"],
        color_tone=t["color_tone"],
        description=t["description"],
        prompt_template=t["prompt_template"],
    )
    # 发布
    TemplateStore.update(tid, is_published=1)
    print(f"  ✅ #{tid} {t['name']} ({t['category']}·{t['makeup_style']})")

print(f"\n🎉 {len(templates)} 套模板已添加并发布")
