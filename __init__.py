"""
ComfyUI-PhotoStylePrompts
照片/图片风格提示词节点

前端扩展（web/）：在节点卡下方显示当前选中模板的预览图（小格子，512×512/1:1）。
预览图放在节点目录 previews/ 文件夹，文件名须与模板名一致。
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
