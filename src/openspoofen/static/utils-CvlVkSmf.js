//#region \0rolldown/runtime.js
var e = Object.create, t = Object.defineProperty, n = Object.getOwnPropertyDescriptor, r = Object.getOwnPropertyNames, i = Object.getPrototypeOf, a = Object.prototype.hasOwnProperty, o = (e, t) => () => (t || (e((t = { exports: {} }).exports, t), e = null), t.exports), s = (e, i, o, s) => {
	if (i && typeof i == "object" || typeof i == "function") for (var c = r(i), l = 0, u = c.length, d; l < u; l++) d = c[l], !a.call(e, d) && d !== o && t(e, d, {
		get: ((e) => i[e]).bind(null, d),
		enumerable: !(s = n(i, d)) || s.enumerable
	});
	return e;
}, c = (n, r, o) => (o = n == null ? {} : e(i(n)), s(r || !n || !n.__esModule || !a.call(n, "default") ? t(o, "default", {
	value: n,
	enumerable: !0
}) : o, n)), l = /* @__PURE__ */ o(((e) => {
	var t = Symbol.for("react.transitional.element"), n = Symbol.for("react.fragment");
	function r(e, n, r) {
		var i = null;
		if (r !== void 0 && (i = "" + r), n.key !== void 0 && (i = "" + n.key), "key" in n) for (var a in r = {}, n) a !== "key" && (r[a] = n[a]);
		else r = n;
		return n = r.ref, {
			$$typeof: t,
			type: e,
			key: i,
			ref: n === void 0 ? null : n,
			props: r
		};
	}
	e.Fragment = n, e.jsx = r, e.jsxs = r;
})), u = /* @__PURE__ */ o(((e, t) => {
	t.exports = l();
}));
//#endregion
//#region node_modules/clsx/dist/clsx.mjs
function d(e) {
	var t, n, r = "";
	if (typeof e == "string" || typeof e == "number") r += e;
	else if (typeof e == "object") {
		if (Array.isArray(e)) {
			var i = e.length;
			for (t = 0; t < i; t++) e[t] && (n = d(e[t])) && (r && (r += " "), r += n);
		} else for (n in e) e[n] && (r && (r += " "), r += n);
	}
	return r;
}
function f() {
	for (var e, t, n = 0, r = "", i = arguments.length; n < i; n++) (e = arguments[n]) && (t = d(e)) && (r && (r += " "), r += t);
	return r;
}
//#endregion
//#region frontend/lib/utils.js
function p(e) {
	(e == null ? void 0 : e.currentTarget) instanceof HTMLElement && window.requestAnimationFrame(() => {
		e.currentTarget.blur();
	});
}
function m(e = 18) {
	typeof navigator < "u" && typeof navigator.vibrate == "function" && navigator.vibrate(e);
}
function h(e) {
	if (!e) return "Unavailable";
	let t = new Date(e);
	return Number.isNaN(t.valueOf()) ? String(e) : t.toLocaleString([], {
		month: "short",
		day: "numeric",
		hour: "numeric",
		minute: "2-digit"
	});
}
function g(e) {
	return e != null && e.exact_model ? e.exact_model : e != null && e.vendor_hint ? `${e.vendor_hint} model unavailable` : "Model unavailable";
}
function _(e) {
	return String(e || "").trim().toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}
function v(e) {
	let t = _(e);
	return t === "nordvpn" || t === "nord vpn" || t.startsWith("nord ");
}
function y(e) {
	let t = {
		nordvpn: "NV",
		"nord vpn": "NV",
		"wireguard profiles": "WG",
		expressvpn: "EX",
		"express vpn": "EX",
		"proton vpn": "PV",
		"mock provider": "MK",
		mullvad: "MU",
		surfshark: "SS"
	}, n = _(e);
	if (t[n]) return t[n];
	let r = String(e || "OpenSpoofen").replace(/\//g, " ").split(/\s+/).filter(Boolean);
	return r.length ? r.length === 1 ? r[0][0].toUpperCase() : r.slice(0, 2).map((e) => e[0]).join("").toUpperCase() : "OS";
}
function b(e, t) {
	let n = `${e || ""} ${t || ""}`.toLowerCase(), r = n.includes("wifi") || n.includes("wlan");
	return {
		icon: r ? "wifi" : "cable",
		label: r ? "Wi-Fi" : "LAN"
	};
}
function x(e) {
	return e != null && e.connected ? {
		availability: "Available",
		tunnel: "Connected",
		summary: e.status_summary || "VPN tunnel is active."
	} : e != null && e.authenticated ? {
		availability: "Available",
		tunnel: "Not connected",
		summary: e.status_summary || "Provider is ready, but the tunnel is idle."
	} : {
		availability: "Unavailable",
		tunnel: "Not connected",
		summary: (e == null ? void 0 : e.status_summary) || "Authenticate this provider to route traffic."
	};
}
//#endregion
export { v as a, m as c, o as d, c as f, x as i, f as l, g as n, y as o, b as r, p as s, h as t, u };
