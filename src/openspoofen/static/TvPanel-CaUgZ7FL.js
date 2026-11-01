import { n as e, t, u as n } from "./utils-CvlVkSmf.js";
import { n as r, t as i } from "./Overlay-B74g5Pir.js";
//#region frontend/panels/TvPanel.jsx
var a = n();
function o({ title: e, subtitle: t, onClose: n, children: r, mobile: i = !1 }) {
	return /* @__PURE__ */ (0, a.jsxs)("section", {
		className: `absolute inset-0 z-30 flex flex-col border border-white/10 bg-[#09111bcc] backdrop-blur-2xl ${i ? "rounded-none" : "rounded-[44px]"}`,
		style: {
			paddingTop: "calc(1.25rem + env(safe-area-inset-top))",
			paddingBottom: "calc(1.25rem + env(safe-area-inset-bottom))",
			paddingLeft: "1.25rem",
			paddingRight: "1.25rem"
		},
		children: [/* @__PURE__ */ (0, a.jsxs)("div", {
			className: "mb-4 flex items-start justify-between gap-4",
			children: [/* @__PURE__ */ (0, a.jsxs)("div", { children: [
				/* @__PURE__ */ (0, a.jsx)("div", {
					className: "text-[0.72rem] uppercase tracking-[0.26em] text-brass-300",
					children: "OpenSpoofen"
				}),
				/* @__PURE__ */ (0, a.jsx)("h2", {
					className: "mt-2 font-display text-2xl font-semibold text-white",
					children: e
				}),
				/* @__PURE__ */ (0, a.jsx)("p", {
					className: "mt-1 max-w-[18rem] text-sm text-white/60",
					children: t
				})
			] }), /* @__PURE__ */ (0, a.jsx)("button", {
				type: "button",
				onClick: n,
				className: "grid h-11 w-11 place-items-center rounded-full border border-white/10 bg-white/5 text-white transition hover:bg-white/10",
				"aria-label": "Close overlay",
				children: /* @__PURE__ */ (0, a.jsxs)("svg", {
					xmlns: "http://www.w3.org/2000/svg",
					width: "20",
					height: "20",
					viewBox: "0 0 24 24",
					fill: "none",
					stroke: "currentColor",
					strokeWidth: "2",
					strokeLinecap: "round",
					strokeLinejoin: "round",
					children: [/* @__PURE__ */ (0, a.jsx)("line", {
						x1: "18",
						y1: "6",
						x2: "6",
						y2: "18"
					}), /* @__PURE__ */ (0, a.jsx)("line", {
						x1: "6",
						y1: "6",
						x2: "18",
						y2: "18"
					})]
				})
			})]
		}), /* @__PURE__ */ (0, a.jsx)("div", {
			className: "remote-panel-scroll min-h-0 flex-1 overflow-y-auto pr-1",
			children: r
		})]
	});
}
function s({ layout: n, network: s, remote: c, onClose: l }) {
	var u, d, f, p, m, h, g;
	return /* @__PURE__ */ (0, a.jsx)(o, {
		title: "TV diagnostics",
		subtitle: "Everything that should have been cluttering the home screen now lives here.",
		onClose: l,
		mobile: n.mobile,
		children: /* @__PURE__ */ (0, a.jsxs)("div", {
			className: "space-y-4",
			children: [/* @__PURE__ */ (0, a.jsx)(r, {
				title: "Connectivity",
				subtitle: s.tv_status_detail || "Downstream diagnostics are not yet available.",
				children: /* @__PURE__ */ (0, a.jsx)(i, { items: [
					{
						label: "Status",
						value: s.tv_status || "Unknown"
					},
					{
						label: "Neighbor",
						value: ((u = s.tv_connectivity) == null ? void 0 : u.neighbor_state) || "No neighbor"
					},
					{
						label: "Lease host",
						value: ((d = s.tv_connectivity) == null ? void 0 : d.hostname) || "Unknown client"
					},
					{
						label: "Lease IP",
						value: ((f = s.tv_connectivity) == null ? void 0 : f.address) || "Not leased"
					},
					{
						label: "MAC",
						value: ((p = s.tv_connectivity) == null ? void 0 : p.mac) || "Unseen"
					},
					{
						label: "Lease expiry",
						value: t((m = s.tv_connectivity) == null ? void 0 : m.lease_expires_at)
					},
					{
						label: "Model",
						value: e(s.tv_connectivity)
					},
					{
						label: "VPN path",
						value: ((h = s.tv_connectivity) == null ? void 0 : h.vpn_path_hint) || "No route hint available"
					}
				] })
			}), /* @__PURE__ */ (0, a.jsx)(r, {
				title: "Remote target",
				subtitle: (c == null ? void 0 : c.status_summary) || "Remote pairing state unavailable.",
				children: /* @__PURE__ */ (0, a.jsx)(i, { items: [
					{
						label: "Host",
						value: (c == null ? void 0 : c.effective_host) || (c == null ? void 0 : c.host) || (c == null ? void 0 : c.candidate_host) || "Not configured"
					},
					{
						label: "Display name",
						value: (c == null ? void 0 : c.display_name) || "OpenSpoofen Remote"
					},
					{
						label: "Token",
						value: c != null && c.token_cached ? "Cached" : "Pending"
					},
					{
						label: "Mode",
						value: c != null && c.auto_detected ? "Auto-detected" : c != null && c.configured ? "Saved" : "Unset"
					},
					{
						label: "Neighbor seen",
						value: (g = s.tv_connectivity) != null && g.live_neighbor ? "Live link" : "Not live"
					}
				] })
			})]
		})
	});
}
//#endregion
export { s as default };
