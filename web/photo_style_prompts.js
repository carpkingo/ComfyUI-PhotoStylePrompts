import { app } from "../../scripts/app.js";

console.log("[PhotoStylePrompts] 前端 v8.6（风格文字字号10→8px）");

/**
 * PhotoStylePrompts 缩略图网格选择器 —— DOM 方案
 * 预览网格置顶 → enable_template → additional_text。
 * 关键修复：去掉 computeLayoutSize（它会让 ComfyUI 压缩预览区分配高度导致容器溢出），
 * 只保留 computeSize 返回 GRID_H，让节点严格按 GRID_H 给预览区高度。
 */
app.registerExtension({
    name: "PhotoStylePrompts.ThumbGrid",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "PhotoStylePrompts") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
            const node = this;

            let tpl = node.widgets.find((w) => w.name === "template_name");
            if (tpl && tpl.options) tpl.options.hidden = true;

            const CELL_W = 100;
            const CELL_H = 120;
            const IMG_H = 90; // 120-5(上padding)-5(下padding)-16(文字)-4(间距)
            const LABEL_H = 16; // 文字行高（字号10px）
            // 预览区高度：贴合2行大卡片，留少量余量
            const GRID_H = 253;
            // 黑色区域与下方开关的间距：多分配这段节点高度，让开关下移、不与黑色框重叠
            const EXTRA = 24;

            // DOM 容器（预览框）
            const widgetContainer = document.createElement("div");
            widgetContainer.style.cssText =
                "width:100%;height:" + GRID_H + "px;overflow:hidden;box-sizing:border-box;position:relative;";
            widgetContainer.dataset.captureWheel = "true";
            widgetContainer.addEventListener("wheel", (e) => e.stopPropagation(), { passive: true });
            const domW = node.addDOMWidget("template_grid", "div", widgetContainer, {});
            // 只覆盖 computeSize（去掉 computeLayoutSize，避免节点压缩预览区分配高度）
            domW.computeSize = function () {
                const w = node.size && node.size[0] ? node.size[0] : 560;
                // 多分配 EXTRA 高度给预览区：黑色区渲染仍 GRID_H，下方留出间距使开关下移
                return [w, GRID_H + EXTRA];
            };

            // 网格（绝对定位填满容器，内部滚动）
            const grid = document.createElement("div");
            grid.style.cssText =
                "position:absolute;top:0;left:0;right:0;bottom:0;overflow-y:auto;overflow-x:hidden;" +
                "box-sizing:border-box;display:grid;grid-template-columns:repeat(auto-fill," + CELL_W + "px);" +
                "grid-auto-rows:" + CELL_H + "px;gap:4px;padding:4px;background:#0d0d0d;" +
                "align-content:start;";
            widgetContainer.appendChild(grid);

            const EMPTY =
                "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgdmlld0JveD0iMCAwIDEwMCAxMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiBmaWxsPSIjMjIyIi8+CjxwYXRoIGQ9Ik0zNSA2NUw0NSA1MEw1NSA2MEw2NSA0NUw3NSA2NUgzNVoiIGZpbGw9IiM0NDQiLz4KPGNpcmNsZSBjeD0iNjUiIGN5PSIzNSIgcj0iOCIgZmlsbD0iIzQ0NCIvPgo8L3N2Zz4=";

            let map = {};
            let selected = "";
            // 缓存破坏：每次加载页面用新时间戳，替换缩略图后刷新即可看到新图
            const TS = Date.now();

            const highlight = (name) => {
                grid.querySelectorAll(".psp-cell").forEach((c) => {
                    const isSel = c.dataset.name === name;
                    c.style.borderColor = isSel ? "#4aa8ff" : "#333";
                    c.style.background = isSel ? "#1e3a5a" : "#181818";
                });
            };

            const paint = () => {
                grid.innerHTML = "";
                const names = Object.keys(map);
                const ordered = names
                    .filter((n) => map[n].starred)
                    .concat(names.filter((n) => !map[n].starred));

                ordered.forEach((name) => {
                    const cell = document.createElement("div");
                    cell.className = "psp-cell";
                    cell.dataset.name = name;
                    cell.style.cssText =
                        "position:relative;width:" + CELL_W + "px;height:" + CELL_H + "px;" +
                        "display:flex;flex-direction:column;align-items:center;cursor:pointer;" +
                        "border:1px solid #333;border-radius:3px;" +
                        "padding:5px 2px 5px;" +
                        "box-sizing:border-box;background:#181818;overflow:hidden;";

                    const imgWrap = document.createElement("div");
                    imgWrap.style.cssText =
                        "width:" + (CELL_W - 4) + "px;height:" + IMG_H + "px;margin-bottom:4px;" +
                        "flex:none;overflow:hidden;border-radius:2px;background:#222;";
                    const img = document.createElement("img");
                    img.style.cssText = "width:100%;height:100%;object-fit:cover;display:block;";
                    if (map[name].preview) {
                        img.src = "/psp/preview/" + encodeURIComponent(name) + "?t=" + TS;
                        img.onerror = () => { img.src = EMPTY; };
                    } else {
                        img.src = EMPTY;
                    }
                    imgWrap.appendChild(img);

                    const label = document.createElement("div");
                    label.style.cssText =
                        "font-size:8px;color:#aaa;width:100%;overflow:hidden;text-overflow:ellipsis;" +
                        "white-space:nowrap;text-align:center;height:" + LABEL_H + "px;" +
                        "line-height:" + LABEL_H + "px;flex:none;";
                    label.textContent = name;

                    const star = document.createElement("div");
                    star.style.cssText =
                        "position:absolute;top:0;right:0;width:18px;height:18px;display:flex;align-items:center;" +
                        "justify-content:center;cursor:pointer;font-size:13px;z-index:2;";
                    const starred = !!map[name].starred;
                    star.textContent = starred ? "★" : "☆";
                    star.style.color = starred ? "#ffd700" : "#666";
                    star.onclick = (e) => {
                        e.stopPropagation();
                        map[name].starred = !map[name].starred;
                        fetch("/psp/toggle_star", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ name: name }),
                        });
                        paint();
                    };

                    cell.appendChild(imgWrap);
                    cell.appendChild(label);
                    cell.appendChild(star);
                    cell.onclick = () => {
                        selected = name;
                        if (tpl) { tpl.value = name; if (tpl.callback) tpl.callback(name); }
                        highlight(name);
                    };
                    grid.appendChild(cell);
                });
                highlight(selected);
            };

            // 重排：预览置顶 → 开关 → 提示词 → 其余
            const enW = node.widgets.find((w) => w.name === "enable_template");
            const adW = node.widgets.find((w) => w.name === "additional_text");
            if (domW && enW && adW) {
                const others = node.widgets.filter((w) => w !== domW && w !== enW && w !== adW);
                node.widgets = [domW, enW, adW, ...others];
            }
            try { if (node.setDirtyCanvas) node.setDirtyCanvas(true, true); } catch (e) {}

            fetch("/psp/preview_map")
                .then((resp) => resp.json())
                .then((data) => {
                    map = data;
                    selected = tpl && tpl.value ? tpl.value : Object.keys(map)[0] || "";
                    paint();
                })
                .catch(() => {});

            return r;
        };
    },
});
