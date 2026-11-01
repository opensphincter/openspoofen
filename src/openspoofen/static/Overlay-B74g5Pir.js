import { l as e, u as t } from "./utils-CvlVkSmf.js";
//#region frontend/components/Overlay.jsx
var n = t();
function r({ title: e, subtitle: t, children: r, action: i }) {
	return /* @__PURE__ */ (0, n.jsxs)("section", {
		className: "rounded-[28px] border border-white/10 bg-white/5 p-4 shadow-screen backdrop-blur-xl",
		children: [/* @__PURE__ */ (0, n.jsxs)("div", {
			className: "mb-3 flex items-start justify-between gap-3",
			children: [/* @__PURE__ */ (0, n.jsxs)("div", { children: [/* @__PURE__ */ (0, n.jsx)("h3", {
				className: "font-display text-[0.92rem] uppercase tracking-[0.22em] text-white/70",
				children: e
			}), t ? /* @__PURE__ */ (0, n.jsx)("p", {
				className: "mt-1 text-sm text-white/55",
				children: t
			}) : null] }), i]
		}), r]
	});
}
function i({ items: t }) {
	return /* @__PURE__ */ (0, n.jsx)("div", {
		className: "grid grid-cols-2 gap-3",
		children: t.map((t) => /* @__PURE__ */ (0, n.jsxs)("div", {
			className: e("min-w-0 rounded-[22px] border border-white/10 bg-black/20 p-3", t.fullWidth && "col-span-2"),
			children: [
				/* @__PURE__ */ (0, n.jsx)("div", {
					className: "text-[0.7rem] uppercase tracking-[0.22em] text-white/45",
					children: t.label
				}),
				/* @__PURE__ */ (0, n.jsx)("div", {
					className: e("mt-2 min-w-0 text-sm font-semibold text-white", t.valueClassName),
					title: typeof t.value == "string" ? t.value : void 0,
					children: t.value
				}),
				t.meta ? /* @__PURE__ */ (0, n.jsx)("div", {
					className: "mt-1 text-xs text-white/45",
					children: t.meta
				}) : null
			]
		}, t.label))
	});
}
//#endregion
export { r as n, i as t };
