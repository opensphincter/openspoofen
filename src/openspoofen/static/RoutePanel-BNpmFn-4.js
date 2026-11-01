import { c as e, f as t, l as n, s as r, u as i } from "./utils-CvlVkSmf.js";
import { n as a, t as o } from "./createLucideIcon-BgE0l-ix.js";
import { n as s, r as c, s as l, t as u } from "./x-LuCl_O3f.js";
import { n as d, t as f } from "./Overlay-B74g5Pir.js";
//#region node_modules/lucide-react/dist/esm/icons/map-pinned.mjs
var p = {
	name: "map-pinned",
	size: 24,
	node: [
		["path", {
			d: "M18 8c0 3.613-3.869 7.429-5.393 8.795a1 1 0 01-1.214 0C9.87 15.429 6 11.613 6 8a6 6 0 0112 0",
			key: "61byd1"
		}],
		["path", {
			d: "M4.474 15h-.197a1 1 0 00-.969.753l-1.097 4.35a1.5 1.5 0 001.444 1.898L20.344 22a1.5 1.5 0 001.446-1.897l-1.098-4.35a1 1 0 00-.969-.753h-.197",
			key: "1m5apm"
		}],
		["circle", {
			cx: "12",
			cy: "8",
			r: "2",
			key: "1822b1"
		}]
	]
};
p.node;
var m = o(p), h = {
	name: "search",
	size: 24,
	node: [["path", {
		d: "m21 21-4.34-4.34",
		key: "14j7rj"
	}], ["circle", {
		cx: "11",
		cy: "11",
		r: "8",
		key: "4ej97u"
	}]]
};
h.node;
var g = o(h), _ = /* @__PURE__ */ t(a(), 1), v = i();
function y({ provider: e, isActive: t, onClick: r }) {
	return /* @__PURE__ */ (0, v.jsxs)("button", {
		type: "button",
		onClick: () => r(e.provider_id),
		className: n("rounded-[22px] border px-4 py-4 text-left transition", t ? "border-mint-300/70 bg-mint-400/20 text-white" : "border-white/10 bg-white/5 text-white/80 hover:bg-white/10"),
		children: [/* @__PURE__ */ (0, v.jsx)("div", {
			className: "text-[0.72rem] uppercase tracking-[0.18em] text-white/45",
			children: e.provider_id
		}), /* @__PURE__ */ (0, v.jsx)("div", {
			className: "mt-2 font-display text-lg font-semibold",
			children: e.provider_name
		})]
	});
}
function b({ locations: t, currentLabel: i, onSelect: a, onClose: o }) {
	let [l, d] = (0, _.useState)(""), f = l.trim().toLowerCase(), p = (0, _.useMemo)(() => f ? t.filter((e) => [
		e.label,
		e.country,
		e.city || ""
	].join(" ").toLowerCase().includes(f)) : t, [t, f]);
	return /* @__PURE__ */ (0, v.jsx)(c.div, {
		initial: { opacity: 0 },
		animate: { opacity: 1 },
		exit: { opacity: 0 },
		className: "absolute inset-0 z-40 flex items-end bg-black/45",
		onClick: o,
		children: /* @__PURE__ */ (0, v.jsxs)(c.section, {
			initial: {
				y: 48,
				opacity: .96
			},
			animate: {
				y: 0,
				opacity: 1
			},
			exit: {
				y: 48,
				opacity: .96
			},
			transition: {
				type: "spring",
				stiffness: 240,
				damping: 30
			},
			className: "w-full rounded-t-[34px] border border-white/10 bg-[#0d1722] p-5 shadow-shell",
			onClick: (e) => e.stopPropagation(),
			children: [
				/* @__PURE__ */ (0, v.jsx)("div", {
					className: "mx-auto mb-4 h-1.5 w-12 rounded-full bg-white/15",
					"aria-hidden": "true"
				}),
				/* @__PURE__ */ (0, v.jsxs)("div", {
					className: "mb-4 flex items-center justify-between gap-3",
					children: [/* @__PURE__ */ (0, v.jsxs)("div", { children: [/* @__PURE__ */ (0, v.jsx)("div", {
						className: "text-[0.72rem] uppercase tracking-[0.22em] text-white/45",
						children: "Regions"
					}), /* @__PURE__ */ (0, v.jsx)("h3", {
						className: "mt-1 font-display text-xl font-semibold text-white",
						children: "Choose route"
					})] }), /* @__PURE__ */ (0, v.jsx)("button", {
						type: "button",
						onClick: (t) => {
							r(t), e(8), o();
						},
						className: "grid h-11 w-11 place-items-center rounded-full border border-white/10 bg-white/5 text-white transition hover:bg-white/10",
						"aria-label": "Close region chooser",
						children: /* @__PURE__ */ (0, v.jsx)(u, { className: "h-5 w-5" })
					})]
				}),
				/* @__PURE__ */ (0, v.jsxs)("label", {
					className: "mb-4 flex items-center gap-3 rounded-[22px] border border-white/10 bg-black/20 px-4 py-3 text-white/80",
					children: [/* @__PURE__ */ (0, v.jsx)(g, { className: "h-4 w-4 shrink-0 text-white/45" }), /* @__PURE__ */ (0, v.jsx)("input", {
						value: l,
						onChange: (e) => d(e.target.value),
						autoCapitalize: "none",
						autoCorrect: "off",
						spellCheck: !1,
						className: "w-full bg-transparent text-sm text-white outline-none placeholder:text-white/35",
						placeholder: "Search country or city"
					})]
				}),
				/* @__PURE__ */ (0, v.jsxs)("div", {
					className: "mb-3 flex items-center justify-between gap-3 text-xs uppercase tracking-[0.18em] text-white/40",
					children: [/* @__PURE__ */ (0, v.jsxs)("span", { children: [p.length, " routes"] }), f ? /* @__PURE__ */ (0, v.jsx)("span", { children: "Filtered" }) : /* @__PURE__ */ (0, v.jsx)("span", { children: "All regions" })]
				}),
				/* @__PURE__ */ (0, v.jsxs)("div", {
					className: "remote-panel-scroll max-h-[52vh] space-y-2 overflow-y-auto pr-1",
					children: [p.map((t) => {
						let o = i === t.label;
						return /* @__PURE__ */ (0, v.jsx)("button", {
							type: "button",
							onClick: (n) => {
								r(n), e(12), a(t);
							},
							className: n("w-full rounded-[22px] border px-4 py-4 text-left transition", o ? "border-brass-300/80 bg-brass-400/15 text-white" : "border-white/10 bg-black/20 text-white/80 hover:bg-white/10"),
							children: /* @__PURE__ */ (0, v.jsxs)("div", {
								className: "flex items-center justify-between gap-3",
								children: [/* @__PURE__ */ (0, v.jsxs)("div", {
									className: "min-w-0",
									children: [/* @__PURE__ */ (0, v.jsx)("div", {
										className: "truncate text-base font-semibold",
										children: t.label
									}), /* @__PURE__ */ (0, v.jsx)("div", {
										className: "mt-1 text-xs uppercase tracking-[0.18em] text-white/45",
										children: "Tap to route the TV here"
									})]
								}), /* @__PURE__ */ (0, v.jsx)(s, { className: "h-5 w-5 shrink-0 text-white/45" })]
							})
						}, `${t.country}-${t.city || "best"}`);
					}), p.length ? null : /* @__PURE__ */ (0, v.jsx)("div", {
						className: "rounded-[22px] border border-dashed border-white/10 bg-black/20 px-4 py-5 text-sm text-white/55",
						children: "No matching routes. Search by country, city, or the label shown in the picker."
					})]
				})
			]
		})
	});
}
function x({ title: e, subtitle: t, onClose: r, children: i, mobile: a = !1 }) {
	return /* @__PURE__ */ (0, v.jsxs)(c.section, {
		initial: {
			opacity: 0,
			x: 24
		},
		animate: {
			opacity: 1,
			x: 0
		},
		exit: {
			opacity: 0,
			x: 18
		},
		transition: {
			type: "spring",
			stiffness: 240,
			damping: 28
		},
		className: n("absolute inset-0 z-30 flex flex-col border border-white/10 bg-[#09111bcc] backdrop-blur-2xl", a ? "rounded-none" : "rounded-[44px]"),
		style: {
			paddingTop: "calc(1.25rem + env(safe-area-inset-top))",
			paddingBottom: "calc(1.25rem + env(safe-area-inset-bottom))",
			paddingLeft: "1.25rem",
			paddingRight: "1.25rem"
		},
		children: [/* @__PURE__ */ (0, v.jsxs)("div", {
			className: "mb-4 flex items-start justify-between gap-4",
			children: [/* @__PURE__ */ (0, v.jsxs)("div", { children: [
				/* @__PURE__ */ (0, v.jsx)("div", {
					className: "text-[0.72rem] uppercase tracking-[0.26em] text-brass-300",
					children: "OpenSpoofen"
				}),
				/* @__PURE__ */ (0, v.jsx)("h2", {
					className: "mt-2 font-display text-2xl font-semibold text-white",
					children: e
				}),
				/* @__PURE__ */ (0, v.jsx)("p", {
					className: "mt-1 max-w-[18rem] text-sm text-white/60",
					children: t
				})
			] }), /* @__PURE__ */ (0, v.jsx)("button", {
				type: "button",
				onClick: r,
				className: "grid h-11 w-11 place-items-center rounded-full border border-white/10 bg-white/5 text-white transition hover:bg-white/10",
				"aria-label": "Close overlay",
				children: /* @__PURE__ */ (0, v.jsx)(u, { className: "h-5 w-5" })
			})]
		}), /* @__PURE__ */ (0, v.jsx)("div", {
			className: "remote-panel-scroll min-h-0 flex-1 overflow-y-auto pr-1",
			children: i
		})]
	}, e);
}
function S({ layout: t, dashboard: n, state: i, providerName: a, conciseLocation: o, routeStatus: c, urls: u, handleRegion: p, handleDisconnect: h, handleProviderSelect: g }) {
	var S, C, w;
	let [T, E] = (0, _.useState)(!1);
	return /* @__PURE__ */ (0, v.jsxs)(x, {
		title: "Route control",
		subtitle: "Switch provider backends or jump TV traffic into a new region without leaving the remote.",
		onClose: () => {},
		mobile: t.mobile,
		children: [/* @__PURE__ */ (0, v.jsxs)("div", {
			className: "space-y-4",
			children: [
				/* @__PURE__ */ (0, v.jsx)(d, {
					title: "Current route",
					subtitle: c.summary,
					action: /* @__PURE__ */ (0, v.jsx)("button", {
						type: "button",
						onClick: (t) => {
							r(t), e(10), h();
						},
						className: "rounded-full border border-white/10 px-4 py-2 text-xs font-semibold text-white/70 transition hover:bg-white/10",
						children: "Disconnect"
					}),
					children: /* @__PURE__ */ (0, v.jsx)(f, { items: [
						{
							label: "Provider",
							value: a
						},
						{
							label: "Region",
							value: o
						},
						{
							label: "Public IP",
							value: i.public_ip || "Pending provider probe"
						},
						{
							label: "Available",
							value: c.availability
						},
						{
							label: "VPN tunnel",
							value: c.tunnel
						}
					] })
				}),
				/* @__PURE__ */ (0, v.jsx)(d, {
					title: "Provider backends",
					subtitle: "No dropdowns here. Tap the backend you want this remote to drive.",
					children: /* @__PURE__ */ (0, v.jsx)("div", {
						className: "grid grid-cols-2 gap-3",
						children: (n.available_providers || []).map((e) => /* @__PURE__ */ (0, v.jsx)(y, {
							provider: e,
							isActive: e.provider_id === n.provider,
							onClick: g
						}, e.provider_id))
					})
				}),
				/* @__PURE__ */ (0, v.jsxs)(d, {
					title: "Region",
					subtitle: "Tap the region widget to open a compact route chooser.",
					children: [/* @__PURE__ */ (0, v.jsxs)("button", {
						type: "button",
						onClick: (t) => {
							r(t), e(10), E(!0);
						},
						className: "flex w-full items-center gap-4 rounded-[24px] border border-white/10 bg-black/20 px-4 py-4 text-left text-white transition hover:bg-white/10",
						children: [
							/* @__PURE__ */ (0, v.jsx)("div", {
								className: "grid h-12 w-12 place-items-center rounded-2xl bg-brass-400/15 text-brass-300",
								children: /* @__PURE__ */ (0, v.jsx)(m, { className: "h-5 w-5" })
							}),
							/* @__PURE__ */ (0, v.jsxs)("div", {
								className: "min-w-0 flex-1",
								children: [
									/* @__PURE__ */ (0, v.jsx)("div", {
										className: "text-[0.72rem] uppercase tracking-[0.18em] text-white/45",
										children: "Current selection"
									}),
									/* @__PURE__ */ (0, v.jsx)("div", {
										className: "mt-1 truncate text-lg font-semibold text-white",
										children: o
									}),
									/* @__PURE__ */ (0, v.jsx)("div", {
										className: "mt-1 text-sm text-white/55",
										children: "Open the route picker"
									})
								]
							}),
							/* @__PURE__ */ (0, v.jsx)(s, { className: "h-5 w-5 shrink-0 text-white/45" })
						]
					}), (S = n.regions) != null && S.length ? null : /* @__PURE__ */ (0, v.jsx)("p", {
						className: "mt-3 text-sm text-white/55",
						children: "No region list is available for this backend yet."
					})]
				})
			]
		}), /* @__PURE__ */ (0, v.jsx)(l, { children: T && (C = n.regions) != null && C.length ? /* @__PURE__ */ (0, v.jsx)(b, {
			locations: n.regions,
			currentLabel: (w = i.current_location) == null ? void 0 : w.label,
			onClose: () => E(!1),
			onSelect: (e) => {
				E(!1), p(e);
			}
		}) : null })]
	});
}
//#endregion
export { S as default };
