@echo off
rem ============================================
rem  PhotoStyle 提示词模板编辑工具
rem  双击本文件，用记事本打开模板库即可编辑
rem
rem  规则：
rem   1) 修改【已有模板】的内容 -> 保存后，
rem      直接回 ComfyUI 点 Run（运行）即生效，无需重启
rem   2) 新增【新模板名】 -> 保存后需重启 ComfyUI，
rem      才能在下拉框里看到新名字
rem ============================================
notepad "E:\ComfyUI-aki-v1.6\ComfyUI\custom_nodes\ComfyUI-PhotoStylePrompts\photo_style_templates.json"
