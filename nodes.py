"""
PhotoStylePrompts - 照片/图片风格提示词节点
============================================
一个针对照片或图片风格的 ComfyUI 自定义节点：

- 从模板库(photo_style_templates.json)中选择风格模板（可自定义添加）
- 可选附加文本(additional_text)与模板合并（固定：模板在前，附加文本在后）
- 输出合并后的完整正向提示词(prompt)，可接入 CLIP Text Encode 正向，
  或接入其他文本拼接节点（如 Comfyroll 的「展示文本 / 文本联结」）查看与组合。

注：本节点不再内置节点卡预览；查看提示词请直接连接「展示文本」等文本输出节点。
"""

import json
import os

# 模板库文件路径（与 nodes.py 同目录）
NODE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(NODE_DIR, "photo_style_templates.json")

# 内置默认模板：当模板文件缺失或损坏时使用
DEFAULT_TEMPLATES = {
    "人像-日系清新": "模拟35毫米胶片摄影，日系清新胶片模拟风格，轻盈细腻颗粒；顺光与柔光漫射，通透空气感；色调是低饱和的青绿白与粉肤，带有轻微褪色，整体充满清新治愈的日常感，且具备自然的胶片质感。",
    "人像-港风复古": "模拟35毫米胶片摄影，港风复古电影感胶片模拟风格，细腻颗粒；逆光与低照度霓虹光，光线氤氲迷离；色调是青绿阴影与暖肤色的低饱和碰撞，带有柔光与暗角，整体充满内敛疏离的情绪氛围，且具备自然的胶片质感。",
    "人像-法式胶片": "模拟35毫米胶片摄影，柯达Portra 400胶片模拟风格，法式慵懒质感，细腻柔焦颗粒；窗光与黄金时刻柔光，光线柔和温暖；色调是奶油色与淡粉的低饱和暖调，带有轻微柔光与暗角，整体充满慵懒浪漫的氛围，且具备自然的胶片质感。",
    "人像-CCD复古数码": "模拟CCD数码相机直出，千禧复古风格，低像素颗粒与柔焦；自然光下的轻微泛光；色调是暖调的粉嫩低饱和，带有柔和暗角，整体充满千禧年的怀旧氛围感，且具备真实的CCD质感。",
    "人像-黑白纪实": "模拟35毫米胶片摄影，柯达Tri-X 400黑白胶片模拟风格，明显有性格的颗粒；高反差自然光，阴影利落；纯黑白影调，浓黑深影与利落高光，整体充满纪实与情绪冲击力，且具备粗犷自然的胶片质感。",
    "人像-赛博朋克": "模拟35毫米胶片摄影，Cinestill 800T赛博朋克胶片模拟风格，细腻电影颗粒；钨丝灯冷光与霓虹光交织，灯源周围有红色辉光晕染；色调是冷蓝钨丝调与霓虹红的碰撞，带有轻微暗角，整体充满赛博夜色与迷离氛围，且具备自然的胶片质感。",
    "人像-赛博东方": "模拟数码电影摄影，赛博东方风格，未来感细腻质感；霓虹冷光与暖金光影交织，数字光晕与东方元素辉映；色调是青蓝冷光与朱红金箔的碰撞，带有柔和辉光与暗角，整体充满东方神秘与未来科技交织的氛围。",
    "人像-韩系柔光": "模拟数码相机直出，韩系氧气感风格，清透细腻；柔和顺光与通透窗光；色调是干净柔和的粉白与莫兰迪低饱和色，几乎无暗角，整体充满清透干净的氧气氛围感，且具备自然的清透质感。",
    "人像-私房氛围": "模拟35毫米胶片摄影，唯美柔光风格，细腻颗粒；低照度的暖光漫射，人物轮廓被柔和光线轻轻包裹；色调是低饱和的奶白与淡米、暖棕，带有轻微柔光与暗角，整体充满静谧私密治愈的氛围，且具备自然的胶片质感。",
    "风光-水墨意境": "模拟35毫米胶片摄影，新中式水墨风格，细腻颗粒；柔光与侧光，留白意境；色调是低饱和的水墨灰、淡青与素白，带有轻柔墨韵，整体充满东方静谧的意境，且具备自然的胶片质感。",
    "风光-赛博城市夜景": "模拟35毫米胶片摄影，Cinestill 800T夜景霓虹胶片模拟风格，细腻电影颗粒；低照度城市霓虹光，湿漉地面倒映彩光；色调是冷蓝钨丝调与霓虹红的碰撞，带有轻微暗角，整体充满未来城市的迷离夜色感，且具备自然的胶片质感。",
    "风光-富士胶片": "模拟35毫米胶片摄影，富士Velvia 100反转片模拟风格，极细颗粒；明亮日光，色彩通透浓郁；色调是超高饱和的蓝天、翠绿与通透金，整体充满鲜活浓烈之感，且具备锐利清透的胶片质感。",
    "风格-莫兰迪": "模拟数码相机直出，莫兰迪低饱和风格，细腻颗粒；柔和中性光，光线克制；色调是褪色的低饱和高级灰与哑光莫兰迪色，整体充满冷静克制的高级氛围，且具备自然的质感。",
    "风格-电影感": "模拟电影摄影调色，青橙对比风格，轻微胶片颗粒；低照度电影光，高光与阴影对比利落；色调是阴影偏青、高光偏橙的经典电影配色，带有轻微暗角，整体充满商业大片感与戏剧张力，且具备自然的电影胶片质感。",
    "风格-复古胶片颗粒": "模拟35毫米胶片摄影，柯达Gold 200胶片模拟风格，细腻微颗粒；黄金时刻的暖阳，光线温暖柔和；色调是暖金与奶白的怀旧色，带有轻微褪色与暖调暗角，整体充满复古怀旧的日常感，且具备自然的胶片质感。",
    "风格-极简白": "模拟数码棚拍，极简高调风格，少阴影、画面明亮；大面积柔和光，光线轻盈通透；色调是干净明亮的浅白与浅灰，几乎无暗角，整体充满纯净、简约、通透的氛围。"
}


def load_templates():
    """读取模板库 json；文件缺失或解析失败时回退到内置默认模板。"""
    try:
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            # 归一化：兼容 {"name": "string"} 简写 与 {"name": {"positive": ...}} 结构
            normalized = {}
            for name, value in data.items():
                if isinstance(value, str):
                    normalized[name] = value.strip()
                elif isinstance(value, dict):
                    pos = (value.get("positive") or "").strip()
                    if pos:
                        normalized[name] = pos
                else:
                    continue
            if normalized:
                return normalized
    except Exception:
        pass
    return dict(DEFAULT_TEMPLATES)


class PhotoStylePrompts:
    """照片/图片风格提示词节点（详细说明见 DESCRIPTION，节点右上角 ? 可查看）。"""

    DESCRIPTION = """照片/图片风格提示词节点

从内置风格模板库(photo_style_templates.json)中选择照片/图片风格，
与手动输入的附加文本合并，输出可直接接入 CLIP Text Encode 正向的完整提示词。

── 版权 / 信息 ──────────────────────────
节点   : PhotoStylePrompts（显示名：PhotoStyle 照片风格提示词）
版本   : 1.0
作者   : Dragonbro的日常（B站）
许可   : 个人使用，可自由修改模板与源码

── 修改提示词：改哪个文件 ────────────────
所有提示词模板都存放在【一个文件】里，改它即可，不用改任何代码：
  节点目录下：photo_style_templates.json（与 nodes.py 同目录）
打开方式：双击节点目录下「编辑模板.bat」，会自动用记事本打开该文件。
改已有模板内容 → 保存后直接点 Run 生效（无需重启）；
新增模板名     → 需重启 ComfyUI 才能在下拉中看到。
"""

    @classmethod
    def INPUT_TYPES(cls):
        templates = load_templates()
        names = list(templates.keys())
        return {
            "required": {
                "template_name": (names, {"default": names[0] if names else ""}),
                "enable_template": ("BOOLEAN", {"default": True}),
                "additional_text": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                        "placeholder": "手动输入提示词",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "build"
    CATEGORY = "提示词/照片风格"
    OUTPUT_NODE = False

    def build(self, template_name, additional_text="", enable_template=True):
        add = (additional_text or "").strip()

        # 开关关闭：不合并模板提示词，仅输出附加文本
        if not enable_template:
            return (add,)

        # 每次直接从 json 文件读取，确保合并使用最新模板内容
        maps = load_templates()

        # 兼容两种结构：{"name": "text"} 或 {"name": {"positive": "text"}}
        raw = maps.get(template_name, "")
        if isinstance(raw, dict):
            positive = (raw.get("positive") or "").strip()
        else:
            positive = (raw or "").strip()

        if add and positive:
            # 固定：模板在前，输入在后（模板以句号结尾，直接拼接）
            full = positive + add
        elif add:
            full = add
        else:
            full = positive

        return (full,)


NODE_CLASS_MAPPINGS = {
    "PhotoStylePrompts": PhotoStylePrompts,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PhotoStylePrompts": "PhotoStyle 照片风格提示词",
}

# ---------------------------------------------------------------------------
# 预览图服务：供前端节点卡显示当前模板的预览图。
# 规则：把预览图放到节点目录下 previews/，文件名 = 模板名（含前缀）。
#       支持 png/jpg/jpeg/webp；无预览图的模板由前端显示占位。
# 访问：/psp/preview/<模板名>  （img 直接请求，不走 fetchApi）
# ---------------------------------------------------------------------------
PREVIEW_DIR = os.path.join(NODE_DIR, "previews")
PREVIEW_EXTS = (".png", ".jpg", ".jpeg", ".webp")


def _has_preview(name):
    """判断某模板是否有预览图。"""
    for ext in PREVIEW_EXTS:
        if os.path.isfile(os.path.join(PREVIEW_DIR, name + ext)):
            return True
    return False


# ---------------------------------------------------------------------------
# 星标置顶：单独存于 stars.json（不改动模板库文件）
# ---------------------------------------------------------------------------
STAR_FILE = os.path.join(NODE_DIR, "stars.json")


def load_stars():
    """读取星标映射 {模板名: True}。"""
    try:
        with open(STAR_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}


def save_stars(stars):
    """保存星标映射。"""
    try:
        with open(STAR_FILE, "w", encoding="utf-8") as f:
            json.dump(stars, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


try:
    from aiohttp import web
    from server import PromptServer

    @PromptServer.instance.routes.get("/psp/preview/{name}")
    async def psp_preview(request):
        name = request.match_info.get("name", "")
        # 取纯文件名，防止路径穿越；兼容带扩展名与不带扩展名
        safe = os.path.basename(name)
        if not safe:
            return web.Response(status=404, text="empty name")

        # 1) 文件名已带扩展名
        p = os.path.join(PREVIEW_DIR, safe)
        if os.path.isfile(p):
            return web.FileResponse(p)

        # 2) 文件名未带扩展名，尝试各支持格式
        for ext in PREVIEW_EXTS:
            p = os.path.join(PREVIEW_DIR, safe + ext)
            if os.path.isfile(p):
                return web.FileResponse(p)

        return web.Response(status=404, text="preview not found")

    @PromptServer.instance.routes.get("/psp/preview_map")
    async def psp_preview_map(request):
        """返回 {模板名: {preview, starred}}，按模板库顺序，供前端渲染缩略图网格。"""
        maps = load_templates()
        stars = load_stars()
        result = {}
        for name in maps.keys():
            result[name] = {
                "preview": _has_preview(name),
                "starred": bool(stars.get(name)),
            }
        return web.json_response(result)

    @PromptServer.instance.routes.get("/psp/stars")
    async def psp_stars(request):
        """返回星标映射。"""
        return web.json_response(load_stars())

    @PromptServer.instance.routes.post("/psp/toggle_star")
    async def psp_toggle_star(request):
        """切换某模板的星标状态，返回切换后状态。"""
        try:
            data = await request.json()
            name = (data or {}).get("name", "")
        except Exception:
            return web.Response(status=400, text="bad request")
        if not name:
            return web.Response(status=400, text="empty name")
        stars = load_stars()
        new_val = not bool(stars.get(name))
        if new_val:
            stars[name] = True
        else:
            stars.pop(name, None)
        save_stars(stars)
        return web.json_response({"name": name, "starred": new_val})
except Exception:
    # 环境无 aiohttp / PromptServer 时（如纯脚本测试）跳过路由注册
    pass
