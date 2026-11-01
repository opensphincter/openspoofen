import { t as e, u as t } from "./utils-CvlVkSmf.js";
import { n } from "./Overlay-B74g5Pir.js";
//#region frontend/panels/LogsPanel.jsx
var r = t();
function i({ layout: t, logs: i, refreshLogs: a, addToast: o, onClose: s }) {
	var c;
	return /* @__PURE__ */ (0, r.jsxs)("section", {
		className: `absolute inset-0 z-30 flex flex-col border border-white/10 bg-[#09111bcc] backdrop-blur-2xl ${t.mobile ? "rounded-none" : "rounded-[44px]"}`,
		style: {
			paddingTop: "calc(1.25rem + env(safe-area-inset-top))",
			paddingBottom: "calc(1.25rem + env(safe-area-inset-bottom))",
			paddingLeft: "1.25rem",
			paddingRight: "1.25rem"
		},
		children: [/* @__PURE__ */ (0, r.jsxs)("div", {
			className: "mb-4 flex items-start justify-between gap-4",
			children: [/* @__PURE__ */ (0, r.jsxs)("div", { children: [
				/* @__PURE__ */ (0, r.jsx)("div", {
					className: "text-[0.72rem] uppercase tracking-[0.26em] text-brass-300",
					children: "OpenSpoofen"
				}),
				/* @__PURE__ */ (0, r.jsx)("h2", {
					className: "mt-2 font-display text-2xl font-semibold text-white",
					children: "Appliance logs"
				}),
				/* @__PURE__ */ (0, r.jsx)("p", {
					className: "mt-1 max-w-[18rem] text-sm text-white/60",
					children: "Recent service logs in one scrollable pane."
				})
			] }), /* @__PURE__ */ (0, r.jsx)("button", {
				type: "button",
				onClick: s,
				className: "grid h-11 w-11 place-items-center rounded-full border border-white/10 bg-white/5 text-white transition hover:bg-white/10",
				"aria-label": "Close overlay",
				children: /* @__PURE__ */ (0, r.jsxs)("svg", {
					xmlns: "http://www.w3.org/2000/svg",
					width: "20",
					height: "20",
					viewBox: "0 0 24 24",
					fill: "none",
					stroke: "currentColor",
					strokeWidth: "2",
					strokeLinecap: "round",
					strokeLinejoin: "round",
					children: [/* @__PURE__ */ (0, r.jsx)("line", {
						x1: "18",
						y1: "6",
						x2: "6",
						y2: "18"
					}), /* @__PURE__ */ (0, r.jsx)("line", {
						x1: "6",
						y1: "6",
						x2: "18",
						y2: "18"
					})]
				})
			})]
		}), /* @__PURE__ */ (0, r.jsx)("div", {
			className: "remote-panel-scroll min-h-0 flex-1 overflow-y-auto pr-1",
			children: /* @__PURE__ */ (0, r.jsx)("div", {
				className: "space-y-4",
				children: /* @__PURE__ */ (0, r.jsx)(n, {
					title: "Log stream",
					subtitle: "Refresh whenever the TV or VPN path is misbehaving.",
					action: /* @__PURE__ */ (0, r.jsx)("button", {
						type: "button",
						onClick: (e) => {
							e != null && e.currentTarget && e.currentTarget instanceof HTMLElement && window.requestAnimationFrame(() => e.currentTarget.blur()), typeof navigator < "u" && typeof navigator.vibrate == "function" && navigator.vibrate(10), a().catch((e) => o(e.message, "error"));
						},
						className: "rounded-full border border-white/10 px-4 py-2 text-xs font-semibold text-white/70 transition hover:bg-white/10",
						children: "Refresh"
					}),
					children: /* @__PURE__ */ (0, r.jsxs)("div", {
						className: "space-y-3",
						children: [((i == null ? void 0 : i.services) || []).map((t) => /* @__PURE__ */ (0, r.jsxs)("div", {
							className: "rounded-[22px] border border-white/10 bg-black/30 p-4",
							children: [/* @__PURE__ */ (0, r.jsxs)("div", {
								className: "mb-3 flex items-center justify-between gap-3",
								children: [/* @__PURE__ */ (0, r.jsx)("div", {
									className: "font-display text-lg font-semibold text-white",
									children: t.label || t.name
								}), /* @__PURE__ */ (0, r.jsx)("div", {
									className: "text-xs uppercase tracking-[0.18em] text-white/40",
									children: i != null && i.generated_at ? e(i.generated_at) : "now"
								})]
							}), /* @__PURE__ */ (0, r.jsx)("pre", {
								className: "whitespace-pre-wrap break-words text-xs leading-5 text-white/70",
								children: (t.lines || []).join("\n") || "No log lines available."
							})]
						}, t.name)), i != null && (c = i.services) != null && c.length ? null : /* @__PURE__ */ (0, r.jsx)("div", {
							className: "rounded-[22px] border border-dashed border-white/10 bg-black/20 p-4 text-sm text-white/55",
							children: "No appliance logs loaded yet."
						})]
					})
				})
			})
		})]
	});
}
//#endregion
export { i as default };
