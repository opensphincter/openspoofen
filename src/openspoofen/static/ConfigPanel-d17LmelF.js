import { c as e, l as t, s as n, u as r } from "./utils-CvlVkSmf.js";
import { t as i } from "./createLucideIcon-BgE0l-ix.js";
import { t as a } from "./external-link-B0RWATZ-.js";
import { n as o, t as s } from "./Overlay-B74g5Pir.js";
//#region node_modules/lucide-react/dist/esm/icons/log-out.mjs
var c = {
	name: "log-out",
	size: 24,
	node: [
		["path", {
			d: "m16 17 5-5-5-5",
			key: "1bji2h"
		}],
		["path", {
			d: "M21 12H9",
			key: "dn1m92"
		}],
		["path", {
			d: "M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4",
			key: "1uf3rs"
		}]
	]
};
c.node;
var l = i(c), u = r();
function d({ layout: r, dashboard: i, urls: c, specs: d, wifi: f, remote: p, remoteForm: m, setRemoteForm: h, wifiForm: g, setWifiForm: _, handleRemoteSave: v, handleWifiScan: y, handleWifiSave: b, refreshSpecs: x, addToast: S, onClose: C }) {
	var w, T, E, D, O, k, A, j;
	let M = i.network || {};
	return /* @__PURE__ */ (0, u.jsxs)("section", {
		className: `absolute inset-0 z-30 flex flex-col border border-white/10 bg-[#09111bcc] backdrop-blur-2xl ${r.mobile ? "rounded-none" : "rounded-[44px]"}`,
		style: {
			paddingTop: "calc(1.25rem + env(safe-area-inset-top))",
			paddingBottom: "calc(1.25rem + env(safe-area-inset-bottom))",
			paddingLeft: "1.25rem",
			paddingRight: "1.25rem"
		},
		children: [/* @__PURE__ */ (0, u.jsxs)("div", {
			className: "mb-4 flex items-start justify-between gap-4",
			children: [/* @__PURE__ */ (0, u.jsxs)("div", { children: [
				/* @__PURE__ */ (0, u.jsx)("div", {
					className: "text-[0.72rem] uppercase tracking-[0.26em] text-brass-300",
					children: "OpenSpoofen"
				}),
				/* @__PURE__ */ (0, u.jsx)("h2", {
					className: "mt-2 font-display text-2xl font-semibold text-white",
					children: "Config and control"
				}),
				/* @__PURE__ */ (0, u.jsx)("p", {
					className: "mt-1 max-w-[18rem] text-sm text-white/60",
					children: "Provider auth, Wi-Fi uplink, remote target, access details, and appliance specs live here."
				})
			] }), /* @__PURE__ */ (0, u.jsx)("button", {
				type: "button",
				onClick: C,
				className: "grid h-11 w-11 place-items-center rounded-full border border-white/10 bg-white/5 text-white transition hover:bg-white/10",
				"aria-label": "Close overlay",
				children: /* @__PURE__ */ (0, u.jsxs)("svg", {
					xmlns: "http://www.w3.org/2000/svg",
					width: "20",
					height: "20",
					viewBox: "0 0 24 24",
					fill: "none",
					stroke: "currentColor",
					strokeWidth: "2",
					strokeLinecap: "round",
					strokeLinejoin: "round",
					children: [/* @__PURE__ */ (0, u.jsx)("line", {
						x1: "18",
						y1: "6",
						x2: "6",
						y2: "18"
					}), /* @__PURE__ */ (0, u.jsx)("line", {
						x1: "6",
						y1: "6",
						x2: "18",
						y2: "18"
					})]
				})
			})]
		}), /* @__PURE__ */ (0, u.jsx)("div", {
			className: "remote-panel-scroll min-h-0 flex-1 overflow-y-auto pr-1",
			children: /* @__PURE__ */ (0, u.jsxs)("div", {
				className: "space-y-4",
				children: [
					/* @__PURE__ */ (0, u.jsx)(o, {
						title: "Access",
						subtitle: "LAN session and local endpoints.",
						children: /* @__PURE__ */ (0, u.jsx)(s, { items: [
							{
								label: "Sign-in",
								value: (w = i.access) != null && w.require_pairing_token ? "Password + pairing" : "Password only"
							},
							{
								label: "Session",
								value: `${((T = i.access) == null ? void 0 : T.session_persist_days) || 30} days`
							},
							{
								label: "Direct URL",
								value: ((E = i.access) == null ? void 0 : E.device_origin) || window.location.origin,
								fullWidth: !0,
								valueClassName: "info-value-clip"
							},
							{
								label: "mDNS",
								value: ((D = i.access) == null ? void 0 : D.mdns_origin) || "Unavailable",
								fullWidth: !0,
								valueClassName: "info-value-clip"
							}
						] })
					}),
					/* @__PURE__ */ (0, u.jsx)(o, {
						title: "TV remote target",
						subtitle: (p == null ? void 0 : p.status_summary) || "Set the target TV IP and display name.",
						children: /* @__PURE__ */ (0, u.jsxs)("form", {
							className: "grid gap-3",
							onSubmit: v,
							children: [
								/* @__PURE__ */ (0, u.jsx)("input", {
									value: m.host,
									onChange: (e) => h((t) => ({
										...t,
										host: e.target.value
									})),
									className: "rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35",
									placeholder: "TV IP or hostname",
									"aria-label": "TV IP or hostname",
									name: "host"
								}),
								/* @__PURE__ */ (0, u.jsxs)("div", {
									className: "grid grid-cols-[1fr,108px] gap-3",
									children: [/* @__PURE__ */ (0, u.jsx)("input", {
										value: m.display_name,
										onChange: (e) => h((t) => ({
											...t,
											display_name: e.target.value
										})),
										className: "rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35",
										placeholder: "Remote display name",
										"aria-label": "Remote display name",
										name: "display_name"
									}), /* @__PURE__ */ (0, u.jsx)("input", {
										value: m.port,
										onChange: (e) => h((t) => ({
											...t,
											port: e.target.value
										})),
										className: "rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35",
										placeholder: "Port",
										"aria-label": "Remote port",
										name: "port"
									})]
								}),
								/* @__PURE__ */ (0, u.jsx)("button", {
									type: "submit",
									className: "rounded-[18px] bg-mint-400 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-mint-300",
									children: "Save TV target"
								})
							]
						})
					}),
					/* @__PURE__ */ (0, u.jsxs)(o, {
						title: "Wi-Fi uplink",
						subtitle: (f == null ? void 0 : f.error) || "Keep this here for wireless fallback or alternate bench setups.",
						action: /* @__PURE__ */ (0, u.jsx)("button", {
							type: "button",
							onClick: (t) => {
								n(t), e(10), y();
							},
							className: "rounded-full border border-white/10 px-4 py-2 text-xs font-semibold text-white/70 transition hover:bg-white/10",
							children: "Scan"
						}),
						children: [/* @__PURE__ */ (0, u.jsxs)("form", {
							className: "grid gap-3",
							onSubmit: b,
							children: [
								/* @__PURE__ */ (0, u.jsxs)("div", {
									className: "grid grid-cols-[1fr,100px] gap-3",
									children: [/* @__PURE__ */ (0, u.jsx)("input", {
										value: g.ssid,
										onChange: (e) => _((t) => ({
											...t,
											ssid: e.target.value
										})),
										className: "rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35",
										placeholder: "SSID",
										"aria-label": "Wi-Fi network name (SSID)"
									}), /* @__PURE__ */ (0, u.jsx)("input", {
										value: g.country,
										onChange: (e) => _((t) => ({
											...t,
											country: e.target.value
										})),
										className: "rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm uppercase text-white outline-none placeholder:text-white/35",
										placeholder: "US",
										"aria-label": "Wi-Fi country code"
									})]
								}),
								/* @__PURE__ */ (0, u.jsx)("input", {
									type: "password",
									value: g.password,
									onChange: (e) => _((t) => ({
										...t,
										password: e.target.value
									})),
									className: "rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35",
									placeholder: "Wi-Fi password",
									"aria-label": "Wi-Fi password"
								}),
								/* @__PURE__ */ (0, u.jsx)("button", {
									type: "submit",
									className: "rounded-[18px] bg-white/90 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-white",
									children: "Save uplink"
								})
							]
						}), /* @__PURE__ */ (0, u.jsx)("div", {
							className: "mt-4 grid gap-2",
							children: ((f == null ? void 0 : f.networks) || []).map((e) => /* @__PURE__ */ (0, u.jsxs)("button", {
								type: "button",
								onClick: () => _((t) => ({
									...t,
									ssid: e.ssid
								})),
								className: t("rounded-[18px] border px-4 py-3 text-left transition", g.ssid === e.ssid ? "border-brass-300/70 bg-brass-400/15 text-white" : "border-white/10 bg-black/20 text-white/70 hover:bg-white/10"),
								children: [/* @__PURE__ */ (0, u.jsx)("div", {
									className: "font-semibold",
									children: e.ssid
								}), /* @__PURE__ */ (0, u.jsxs)("div", {
									className: "mt-1 text-xs text-white/45",
									children: [
										e.signal,
										"% • ",
										e.security || "Open",
										e.saved ? " • saved" : "",
										e.active ? " • active" : ""
									]
								})]
							}, e.ssid))
						})]
					}),
					/* @__PURE__ */ (0, u.jsx)(o, {
						title: "Appliance specs",
						subtitle: "Live hardware, route, and service state from the Pi.",
						action: /* @__PURE__ */ (0, u.jsx)("button", {
							type: "button",
							onClick: (t) => {
								n(t), e(10), x().catch((e) => S(e.message, "error"));
							},
							className: "rounded-full border border-white/10 px-4 py-2 text-xs font-semibold text-white/70 transition hover:bg-white/10",
							children: "Refresh"
						}),
						children: /* @__PURE__ */ (0, u.jsx)(s, { items: [
							{
								label: "Topology",
								value: (d == null ? void 0 : d.preferred_topology) || M.preferred_topology || "Unknown"
							},
							{
								label: "Provider",
								value: (d == null ? void 0 : d.default_provider) || i.provider || "Unknown"
							},
							{
								label: "Upstream",
								value: (d == null ? void 0 : d.upstream_interface) || ((O = M.upstream_interface) == null ? void 0 : O.name) || "Unknown"
							},
							{
								label: "Downstream",
								value: (d == null ? void 0 : d.downstream_interface) || ((k = M.downstream_interface) == null ? void 0 : k.name) || "Unknown"
							},
							{
								label: "Default route",
								value: (d == null ? void 0 : d.default_route) || M.default_route || "Unavailable",
								fullWidth: !0,
								valueClassName: "info-value-clip"
							},
							{
								label: "DNS",
								value: ((d == null ? void 0 : d.dns_servers) || M.dns_servers || []).join(", ") || "Unavailable",
								fullWidth: !0,
								valueClassName: "info-value-clip"
							}
						] })
					}),
					i.show_provider_login && (A = i.provider_metadata) != null && (A = A.auth_fields) != null && A.length ? /* @__PURE__ */ (0, u.jsx)(o, {
						title: "Provider auth",
						subtitle: `Authenticate ${i.provider_metadata.provider_name} from inside the remote overlay.`,
						children: /* @__PURE__ */ (0, u.jsxs)("form", {
							method: "post",
							action: c.provider_login,
							className: "grid gap-3",
							children: [
								/* @__PURE__ */ (0, u.jsx)("input", {
									type: "hidden",
									name: "provider",
									value: i.provider
								}),
								i.provider_metadata.auth_fields.map((e) => /* @__PURE__ */ (0, u.jsxs)("label", {
									className: "grid gap-2 text-sm text-white/70",
									children: [
										e.label,
										/* @__PURE__ */ (0, u.jsx)("input", {
											name: e.key,
											type: e.secret ? "password" : "text",
											placeholder: e.placeholder,
											className: "rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35"
										}),
										e.help_text ? /* @__PURE__ */ (0, u.jsx)("span", {
											className: "text-xs text-white/45",
											children: e.help_text
										}) : null
									]
								}, e.key)),
								/* @__PURE__ */ (0, u.jsx)("button", {
									type: "submit",
									className: "rounded-[18px] bg-brass-400 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-brass-300",
									children: "Authenticate provider"
								})
							]
						})
					}) : null,
					i.provider_auth_summary && !i.show_provider_login ? /* @__PURE__ */ (0, u.jsx)(o, {
						title: "Provider auth",
						subtitle: "Authentication is already stored on the appliance for this backend.",
						children: /* @__PURE__ */ (0, u.jsx)("div", {
							className: "rounded-[22px] border border-mint-300/30 bg-mint-400/12 p-4 text-sm font-medium text-white",
							children: i.provider_auth_summary
						})
					}) : null,
					/* @__PURE__ */ (0, u.jsx)(o, {
						title: "Session",
						subtitle: "Leave the appliance cleanly or jump back out to the LAN address.",
						children: /* @__PURE__ */ (0, u.jsxs)("div", {
							className: "flex gap-3",
							children: [/* @__PURE__ */ (0, u.jsxs)("a", {
								href: ((j = i.access) == null ? void 0 : j.device_origin) || window.location.origin,
								className: "inline-flex flex-1 items-center justify-center gap-2 rounded-[18px] border border-white/10 bg-black/20 px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/10",
								children: [/* @__PURE__ */ (0, u.jsx)(a, { className: "h-4 w-4" }), " Open direct URL"]
							}), /* @__PURE__ */ (0, u.jsx)("form", {
								method: "post",
								action: c.logout,
								className: "flex-1",
								children: /* @__PURE__ */ (0, u.jsxs)("button", {
									type: "submit",
									className: "inline-flex w-full items-center justify-center gap-2 rounded-[18px] border border-white/10 bg-coral-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-coral-400",
									children: [/* @__PURE__ */ (0, u.jsx)(l, { className: "h-4 w-4" }), " Sign out"]
								})
							})]
						})
					})
				]
			})
		})]
	});
}
//#endregion
export { d as default };
