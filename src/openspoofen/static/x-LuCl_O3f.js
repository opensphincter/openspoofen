import { f as e, u as t } from "./utils-CvlVkSmf.js";
import { n, t as r } from "./createLucideIcon-BgE0l-ix.js";
//#region node_modules/framer-motion/dist/es/context/LayoutGroupContext.mjs
var i = t(), a = /* @__PURE__ */ e(n(), 1), o = (0, a.createContext)({});
//#endregion
//#region node_modules/framer-motion/dist/es/utils/use-constant.mjs
function s(e) {
	let t = (0, a.useRef)(null);
	return t.current === null && (t.current = e()), t.current;
}
//#endregion
//#region node_modules/framer-motion/dist/es/utils/use-isomorphic-effect.mjs
var c = typeof window < "u" ? a.useLayoutEffect : a.useEffect, l = /* @__PURE__ */ (0, a.createContext)(null);
//#endregion
//#region node_modules/motion-utils/dist/es/array.mjs
function u(e, t) {
	e.indexOf(t) === -1 && e.push(t);
}
function d(e, t) {
	let n = e.indexOf(t);
	n > -1 && e.splice(n, 1);
}
//#endregion
//#region node_modules/motion-utils/dist/es/clamp.mjs
var f = (e, t, n) => n > t ? t : n < e ? e : n, p = () => {}, m = () => {}, h = {}, g = (e) => /^-?(?:\d+(?:\.\d+)?|\.\d+)$/u.test(e), _ = (e) => typeof e == "object" && !!e, v = (e) => /^0[^.\s]+$/u.test(e);
//#endregion
//#region node_modules/motion-utils/dist/es/memo.mjs
/*#__NO_SIDE_EFFECTS__*/
function y(e) {
	let t;
	return () => (t === void 0 && (t = e()), t);
}
//#endregion
//#region node_modules/motion-utils/dist/es/noop.mjs
var b = /* @__NO_SIDE_EFFECTS__ */ (e) => e, x = class {
	constructor() {
		this.subscriptions = [];
	}
	add(e) {
		return u(this.subscriptions, e), () => this.remove(e);
	}
	remove(e) {
		d(this.subscriptions, e);
	}
	notify(e, t, n) {
		let r = this.subscriptions.length;
		if (r) {
			if (r === 1) this.subscriptions[0](e, t, n);
			else for (let i = 0; i < r; i++) {
				let r = this.subscriptions[i];
				r && r(e, t, n);
			}
		}
	}
	getSize() {
		return this.subscriptions.length;
	}
	clear() {
		this.subscriptions.length = 0;
	}
}, S = /* @__NO_SIDE_EFFECTS__ */ (e) => e * 1e3, C = /* @__NO_SIDE_EFFECTS__ */ (e) => e / 1e3, w = /* @__NO_SIDE_EFFECTS__ */ (e, t) => t ? 1e3 / t * e : 0, T = /* @__NO_SIDE_EFFECTS__ */ (e) => Array.isArray(e) && typeof e[0] == "number", E = {
	delta: 0,
	timestamp: 0,
	isProcessing: !1
}, D;
function ee() {
	D = void 0;
}
var O = {
	now: () => (D === void 0 && O.set(E.isProcessing || h.useManualTiming ? E.timestamp : performance.now()), D),
	set: (e) => {
		D = e, queueMicrotask(ee);
	}
}, k = (e) => Math.round(e * 1e5) / 1e5, te = (e) => (t) => typeof t == "string" && t.startsWith(e), ne = /*@__PURE__*/ te("--"), re = /*@__PURE__*/ te("var(--"), ie = (e) => re(e) ? ae.test(e.split("/*")[0].trim()) : !1, ae = /var\(--(?:[\w-]+\s*|[\w-]+\s*,(?:\s*[^)(\s]|\s*\((?:[^)(]|\([^)(]*\))*\))+\s*)\)$/iu;
function oe(e) {
	return typeof e == "string" && e.split("/*")[0].includes("var(--");
}
//#endregion
//#region node_modules/motion-dom/dist/es/value/types/numbers/index.mjs
var A = {
	test: (e) => typeof e == "number",
	parse: parseFloat,
	transform: (e) => e
}, j = {
	...A,
	transform: (e) => f(0, 1, e)
}, M = {
	...A,
	default: 1
}, se = /-?(?:\d+(?:\.\d+)?|\.\d+)/gu;
//#endregion
//#region node_modules/motion-dom/dist/es/value/types/utils/is-nullish.mjs
function ce(e) {
	return e == null;
}
//#endregion
//#region node_modules/motion-dom/dist/es/value/types/utils/single-color-regex.mjs
var le = /^(?:#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\))$/iu, ue = (e, t) => (n) => !!(typeof n == "string" && le.test(n) && n.startsWith(e) || t && !ce(n) && Object.prototype.hasOwnProperty.call(n, t)), de = (e, t, n) => (r) => {
	if (typeof r != "string") return r;
	let [i, a, o, s] = r.match(se);
	return {
		[e]: parseFloat(i),
		[t]: parseFloat(a),
		[n]: parseFloat(o),
		alpha: s === void 0 ? 1 : parseFloat(s)
	};
}, fe = (e) => f(0, 255, e), pe = {
	...A,
	transform: (e) => Math.round(fe(e))
}, N = {
	test: /*@__PURE__*/ ue("rgb", "red"),
	parse: /*@__PURE__*/ de("red", "green", "blue"),
	transform: ({ red: e, green: t, blue: n, alpha: r = 1 }) => "rgba(" + pe.transform(e) + ", " + pe.transform(t) + ", " + pe.transform(n) + ", " + k(j.transform(r)) + ")"
};
//#endregion
//#region node_modules/motion-dom/dist/es/value/types/color/hex.mjs
function me(e) {
	let t = "", n = "", r = "", i = "";
	return e.length > 5 ? (t = e.substring(1, 3), n = e.substring(3, 5), r = e.substring(5, 7), i = e.substring(7, 9)) : (t = e.substring(1, 2), n = e.substring(2, 3), r = e.substring(3, 4), i = e.substring(4, 5), t += t, n += n, r += r, i += i), {
		red: parseInt(t, 16),
		green: parseInt(n, 16),
		blue: parseInt(r, 16),
		alpha: i ? parseInt(i, 16) / 255 : 1
	};
}
var he = {
	test: /*@__PURE__*/ ue("#"),
	parse: me,
	transform: N.transform
}, P = /* @__NO_SIDE_EFFECTS__ */ (e) => ({
	test: (t) => typeof t == "string" && t.endsWith(e) && t.split(" ").length === 1,
	parse: parseFloat,
	transform: (t) => `${t}${e}`
}), F = /*@__PURE__*/ P("deg"), I = /*@__PURE__*/ P("%"), L = /*@__PURE__*/ P("px"), ge = /*@__PURE__*/ P("vh"), _e = /*@__PURE__*/ P("vw"), ve = {
	...I,
	parse: (e) => I.parse(e) / 100,
	transform: (e) => I.transform(e * 100)
}, R = {
	test: /*@__PURE__*/ ue("hsl", "hue"),
	parse: /*@__PURE__*/ de("hue", "saturation", "lightness"),
	transform: ({ hue: e, saturation: t, lightness: n, alpha: r = 1 }) => "hsla(" + Math.round(e) + ", " + I.transform(k(t)) + ", " + I.transform(k(n)) + ", " + k(j.transform(r)) + ")"
}, z = {
	test: (e) => N.test(e) || he.test(e) || R.test(e),
	parse: (e) => N.test(e) ? N.parse(e) : R.test(e) ? R.parse(e) : he.parse(e),
	transform: (e) => typeof e == "string" ? e : e.hasOwnProperty("red") ? N.transform(e) : R.transform(e),
	getAnimatableNone: (e) => {
		let t = z.parse(e);
		return t.alpha = 0, z.transform(t);
	}
}, ye = /(?:#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\))/giu, be = /*@__PURE__*/ new RegExp(se.source), xe = /*@__PURE__*/ new RegExp(ye.source, "i");
function Se(e) {
	return isNaN(e) && typeof e == "string" && (be.test(e) || xe.test(e));
}
var Ce = "number", we = "color", Te = "var", Ee = "var(", De = "${}", Oe = /var\s*\(\s*--(?:[\w-]+\s*|[\w-]+\s*,(?:\s*[^)(\s]|\s*\((?:[^)(]|\([^)(]*\))*\))+\s*)\)|#[\da-f]{3,8}|(?:rgb|hsl)a?\((?:-?[\d.]+%?[,\s]+){2}-?[\d.]+%?\s*(?:[,/]\s*)?(?:\b\d+(?:\.\d+)?|\.\d+)?%?\)|-?(?:\d+(?:\.\d+)?|\.\d+)/giu;
function ke(e) {
	let t = e.toString();
	return be.test(t) || xe.test(t);
}
function B(e) {
	let t = e.toString(), n = [], r = {
		color: [],
		number: [],
		var: []
	}, i = [], a = 0;
	return {
		values: n,
		split: t.replace(Oe, (e) => (z.test(e) ? (r.color.push(a), i.push(we), n.push(z.parse(e))) : e.startsWith(Ee) ? (r.var.push(a), i.push(Te), n.push(e)) : (r.number.push(a), i.push(Ce), n.push(parseFloat(e))), ++a, De)).split(De),
		indexes: r,
		types: i
	};
}
function Ae(e) {
	return B(e).values;
}
function je({ split: e, types: t }) {
	let n = e.length;
	return (r) => {
		let i = "";
		for (let a = 0; a < n; a++) if (i += e[a], r[a] !== void 0) {
			let e = t[a];
			i += e === Ce ? k(r[a]) : e === we ? z.transform(r[a]) : r[a];
		}
		return i;
	};
}
function Me(e) {
	return je(B(e));
}
var Ne = (e) => typeof e == "number" ? 0 : z.test(e) ? z.getAnimatableNone(e) : e, Pe = (e, t) => typeof e == "number" ? t != null && t.trim().endsWith("/") ? e : 0 : Ne(e);
function Fe(e) {
	let t = B(e);
	return je(t)(t.values.map((e, n) => Pe(e, t.split[n])));
}
var V = {
	test: Se,
	parse: Ae,
	createTransformer: Me,
	getAnimatableNone: Fe
}, H = [
	"setup",
	"read",
	"resolveKeyframes",
	"preUpdate",
	"update",
	"preRender",
	"render",
	"postRender"
];
//#endregion
//#region node_modules/motion-dom/dist/es/frameloop/render-step.mjs
function Ie(e) {
	let t = /* @__PURE__ */ new Set(), n = /* @__PURE__ */ new Set(), r = !1, i = !1, a = /* @__PURE__ */ new Set(), o = {
		delta: 0,
		timestamp: 0,
		isProcessing: !1
	};
	function s(t) {
		a.has(t) && (n.add(t), e()), t(o);
	}
	let c = {
		schedule: (e, i = !1, o = !1) => {
			let s = o && r ? t : n;
			return i && a.add(e), s.add(e), e;
		},
		cancel: (e) => {
			n.delete(e), a.delete(e);
		},
		process: (e) => {
			if (o = e, r) {
				i = !0;
				return;
			}
			r = !0;
			let a = t;
			t = n, n = a, t.forEach(s), t.clear(), r = !1, i && (i = !1, c.process(e));
		}
	};
	return c;
}
//#endregion
//#region node_modules/motion-dom/dist/es/frameloop/batcher.mjs
var Le = 40;
function Re(e, t, n = {
	delta: 0,
	timestamp: 0,
	isProcessing: !1
}) {
	let r = !1, i = !0, a = () => r = !0, o = H.reduce((e, t) => (e[t] = Ie(a), e), {}), { setup: s, read: c, resolveKeyframes: l, preUpdate: u, update: d, preRender: f, render: p, postRender: m } = o, g = () => {
		let a = h.useManualTiming, o = a ? n.timestamp : performance.now();
		r = !1, a || (n.delta = i ? 1e3 / 60 : Math.max(Math.min(o - n.timestamp, Le), 1)), n.timestamp = o, n.isProcessing = !0, s.process(n), c.process(n), l.process(n), u.process(n), d.process(n), f.process(n), p.process(n), m.process(n), n.isProcessing = !1, r && t && (i = !1, e(g));
	}, _ = () => {
		r = !0, i = !0, n.isProcessing || e(g);
	};
	return {
		schedule: H.reduce((e, t) => {
			let n = o[t];
			return e[t] = (e, t = !1, i = !1) => (r || _(), n.schedule(e, t, i)), e;
		}, {}),
		cancel: (e) => {
			for (let t = 0; t < H.length; t++) o[H[t]].cancel(e);
		},
		state: n,
		steps: o
	};
}
//#endregion
//#region node_modules/motion-dom/dist/es/frameloop/frame.mjs
var { schedule: U, cancel: ze, steps: Be } = /* @__PURE__ */ Re(typeof requestAnimationFrame < "u" ? requestAnimationFrame : b, !0, E), Ve = (e, t, n = 10) => {
	let r = "", i = Math.max(Math.round(t / n), 2);
	for (let t = 0; t < i; t++) r += Math.round(e(t / (i - 1)) * 1e4) / 1e4 + ", ";
	return `linear(${r.substring(0, r.length - 2)})`;
}, He = (e) => e !== null;
function Ue(e, { repeat: t, repeatType: n = "loop" }, r, i = 1) {
	let a = e.filter(He), o = i < 0 || t && n !== "loop" && t % 2 == 1 ? 0 : a.length - 1;
	return !o || r === void 0 ? a[o] : r;
}
//#endregion
//#region node_modules/motion-dom/dist/es/animation/utils/notify-inspector.mjs
function We(e, t) {
	return {
		kind: e,
		animation: t,
		timestamp: O.now(),
		frameTimestamp: E.timestamp,
		frameIsProcessing: E.isProcessing
	};
}
function Ge(e, t, n) {
	let r = globalThis.__MOTION_INSPECT__;
	if (r) try {
		r({
			...We("animation-start", e),
			options: n ? {
				...t,
				...n
			} : t
		});
	} catch {}
}
//#endregion
//#region node_modules/motion-dom/dist/es/animation/utils/WithPromise.mjs
var Ke = class {
	constructor() {
		this.isResolved = !1;
	}
	get finished() {
		return this._finished ||= this.isResolved ? Promise.resolve() : new Promise((e) => {
			this._resolve = e;
		}), this._finished;
	}
	updateFinished() {
		this._finished = this._resolve = void 0, this.isResolved = !1;
	}
	notifyFinished() {
		var e;
		this.isResolved = !0, (e = this._resolve) == null || e.call(this);
	}
	then(e, t) {
		return this.finished.then(e, t);
	}
}, qe = /* @__PURE__ */ new Set([
	"brightness",
	"contrast",
	"saturate",
	"opacity"
]);
function Je(e) {
	let [t, n] = e.slice(0, -1).split("(");
	if (t === "drop-shadow") return e;
	let [r] = n.match(se) || [];
	if (!r) return e;
	let i = n.replace(r, ""), a = +!!qe.has(t);
	return r !== n && (a *= 100), t + "(" + a + i + ")";
}
var Ye = /\b([a-z-]*)\(.*?\)/gu, Xe = {
	...V,
	getAnimatableNone: (e) => {
		let t = e.match(Ye);
		return t ? t.map(Je).join(" ") : e;
	}
}, Ze = {
	...V,
	getAnimatableNone: (e) => {
		let t = V.parse(e);
		return V.createTransformer(e)(t.map((e) => typeof e == "number" ? 0 : typeof e == "object" ? {
			...e,
			alpha: 1
		} : e));
	}
}, Qe = {
	...A,
	transform: Math.round
}, W = {
	borderWidth: L,
	borderTopWidth: L,
	borderRightWidth: L,
	borderBottomWidth: L,
	borderLeftWidth: L,
	borderRadius: L,
	borderTopLeftRadius: L,
	borderTopRightRadius: L,
	borderBottomRightRadius: L,
	borderBottomLeftRadius: L,
	width: L,
	maxWidth: L,
	height: L,
	maxHeight: L,
	top: L,
	right: L,
	bottom: L,
	left: L,
	inset: L,
	insetBlock: L,
	insetBlockStart: L,
	insetBlockEnd: L,
	insetInline: L,
	insetInlineStart: L,
	insetInlineEnd: L,
	padding: L,
	paddingTop: L,
	paddingRight: L,
	paddingBottom: L,
	paddingLeft: L,
	paddingBlock: L,
	paddingBlockStart: L,
	paddingBlockEnd: L,
	paddingInline: L,
	paddingInlineStart: L,
	paddingInlineEnd: L,
	margin: L,
	marginTop: L,
	marginRight: L,
	marginBottom: L,
	marginLeft: L,
	marginBlock: L,
	marginBlockStart: L,
	marginBlockEnd: L,
	marginInline: L,
	marginInlineStart: L,
	marginInlineEnd: L,
	fontSize: L,
	backgroundPositionX: L,
	backgroundPositionY: L,
	rotate: F,
	pathRotation: F,
	rotateX: F,
	rotateY: F,
	rotateZ: F,
	scale: M,
	scaleX: M,
	scaleY: M,
	scaleZ: M,
	skew: F,
	skewX: F,
	skewY: F,
	distance: L,
	translateX: L,
	translateY: L,
	translateZ: L,
	x: L,
	y: L,
	z: L,
	perspective: L,
	transformPerspective: L,
	opacity: j,
	originX: ve,
	originY: ve,
	originZ: L,
	zIndex: Qe,
	fillOpacity: j,
	strokeOpacity: j,
	numOctaves: Qe
}, $e = {
	...W,
	color: z,
	backgroundColor: z,
	outlineColor: z,
	fill: z,
	stroke: z,
	borderColor: z,
	borderTopColor: z,
	borderRightColor: z,
	borderBottomColor: z,
	borderLeftColor: z,
	filter: Xe,
	WebkitFilter: Xe,
	mask: Ze,
	WebkitMask: Ze
}, et = (e) => $e[e], tt = /*@__PURE__*/ new Set([Xe, Ze]);
function nt(e, t) {
	let n = et(e);
	return tt.has(n) || (n = V), n.getAnimatableNone ? n.getAnimatableNone(t) : void 0;
}
//#endregion
//#region node_modules/motion-dom/dist/es/animation/keyframes/utils/fill-wildcards.mjs
function rt(e) {
	for (let t = 1; t < e.length; t++) e[t] ?? (e[t] = e[t - 1]);
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/dom/parse-transform.mjs
var G = (e) => e * 180 / Math.PI, it = (e) => ot(G(Math.atan2(e[1], e[0]))), at = {
	x: 4,
	y: 5,
	translateX: 4,
	translateY: 5,
	scaleX: 0,
	scaleY: 3,
	scale: (e) => (Math.abs(e[0]) + Math.abs(e[3])) / 2,
	rotate: it,
	rotateZ: it,
	skewX: (e) => G(Math.atan(e[1])),
	skewY: (e) => G(Math.atan(e[2])),
	skew: (e) => (Math.abs(e[1]) + Math.abs(e[2])) / 2
}, ot = (e) => (e %= 360, e < 0 && (e += 360), e), st = it, ct = (e) => Math.sqrt(e[0] * e[0] + e[1] * e[1]), lt = (e) => Math.sqrt(e[4] * e[4] + e[5] * e[5]), ut = {
	x: 12,
	y: 13,
	z: 14,
	translateX: 12,
	translateY: 13,
	translateZ: 14,
	scaleX: ct,
	scaleY: lt,
	scale: (e) => (ct(e) + lt(e)) / 2,
	rotateX: (e) => ot(G(Math.atan2(e[6], e[5]))),
	rotateY: (e) => ot(G(Math.atan2(-e[2], e[0]))),
	rotateZ: st,
	rotate: st,
	skewX: (e) => G(Math.atan(e[4])),
	skewY: (e) => G(Math.atan(e[1])),
	skew: (e) => (Math.abs(e[1]) + Math.abs(e[4])) / 2
};
function dt(e) {
	return +!!e.includes("scale");
}
function ft(e, t) {
	if (!e || e === "none") return dt(t);
	let n = e.match(/^matrix3d\(([-\d.e\s,]+)\)$/u), r, i;
	if (n) r = ut, i = n;
	else {
		let t = e.match(/^matrix\(([-\d.e\s,]+)\)$/u);
		r = at, i = t;
	}
	if (!i) return dt(t);
	let a = r[t], o = i[1].split(",").map(mt);
	return typeof a == "function" ? a(o) : o[a];
}
var pt = (e, t) => {
	let { transform: n = "none" } = getComputedStyle(e);
	return ft(n, t);
};
function mt(e) {
	return parseFloat(e.trim());
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/utils/keys-transform.mjs
var K = [
	"transformPerspective",
	"x",
	"y",
	"z",
	"translateX",
	"translateY",
	"translateZ",
	"scale",
	"scaleX",
	"scaleY",
	"rotate",
	"rotateX",
	"rotateY",
	"rotateZ",
	"skew",
	"skewX",
	"skewY"
], q = /* @__PURE__ */ new Set([...K, "pathRotation"]), ht = (e) => e === A || e === L, gt = /* @__PURE__ */ new Set([
	"x",
	"y",
	"z"
]), _t = K.filter((e) => !gt.has(e));
function vt(e) {
	let t = [];
	return _t.forEach((n) => {
		let r = e.getValue(n);
		if (r !== void 0) {
			let e = r.get(), i = +!!n.startsWith("scale");
			if (e === i) return;
			t.push([n, e]), r.set(i);
		}
	}), t;
}
var yt = /* @__PURE__ */ new Set(["bottom", "right"]);
function bt(e, t, n, r, i, a) {
	let o = parseFloat(e);
	if (!isNaN(o)) return o;
	let { min: s, max: c } = t()[n], l = c - s;
	return a === "border-box" ? l : l - parseFloat(r) - parseFloat(i);
}
var J = {
	width: ({ width: e, paddingLeft: t = "0", paddingRight: n = "0", boxSizing: r }, i) => bt(e, i, "x", t, n, r),
	height: ({ height: e, paddingTop: t = "0", paddingBottom: n = "0", boxSizing: r }, i) => bt(e, i, "y", t, n, r),
	top: ({ top: e }) => parseFloat(e),
	left: ({ left: e }) => parseFloat(e),
	bottom: ({ top: e }, t) => {
		let { y: n } = t();
		return parseFloat(e) + (n.max - n.min);
	},
	right: ({ left: e }, t) => {
		let { x: n } = t();
		return parseFloat(e) + (n.max - n.min);
	},
	x: ({ transform: e }) => ft(e, "x"),
	y: ({ transform: e }) => ft(e, "y")
};
J.translateX = J.x, J.translateY = J.y;
//#endregion
//#region node_modules/motion-dom/dist/es/animation/keyframes/KeyframesResolver.mjs
var Y = /* @__PURE__ */ new Set(), xt = !1, St = !1, Ct = !1;
function wt() {
	if (St) {
		let e = [], t = /* @__PURE__ */ new Set(), n = /* @__PURE__ */ new Set();
		Y.forEach((r) => {
			r.needsMeasurement && (e.push(r), t.add(r.element), yt.has(r.name) && n.add(r.element));
		});
		let r = /* @__PURE__ */ new Map();
		n.forEach((e) => {
			let t = vt(e);
			t.length && (r.set(e, t), e.render());
		}), e.forEach((e) => e.measureInitialState()), t.forEach((e) => {
			e.render();
			let t = r.get(e);
			t && t.forEach(([t, n]) => {
				var r;
				(r = e.getValue(t)) == null || r.set(n);
			});
		}), e.forEach((e) => e.measureEndState()), e.forEach((e) => {
			e.suspendedScrollY !== void 0 && window.scrollTo(0, e.suspendedScrollY);
		});
	}
	St = !1, xt = !1, Y.forEach((e) => e.complete(Ct)), Y.clear();
}
function Tt() {
	Y.forEach((e) => {
		e.readKeyframes(), e.needsMeasurement && (St = !0);
	});
}
function Et() {
	Ct = !0, Tt(), wt(), Ct = !1;
}
function Dt(e, t, n) {
	if (typeof e == "string") {
		if (g(e) || v(e)) return parseFloat(e);
		if (!V.test(e) && V.test(n)) return nt(t, n);
	}
	return e ?? void 0;
}
var Ot = class {
	constructor(e, t, n, r, i, a = !1) {
		this.state = "pending", this.isAsync = !1, this.needsMeasurement = !1, this.unresolvedKeyframes = [...e], this.onComplete = t, this.name = n, this.motionValue = r, this.element = i, this.isAsync = a;
	}
	scheduleResolve() {
		this.state = "scheduled", this.isAsync ? (Y.add(this), xt || (xt = !0, U.read(Tt), U.resolveKeyframes(wt))) : (this.readKeyframes(), this.complete());
	}
	readKeyframes() {
		let { unresolvedKeyframes: e, name: t, element: n, motionValue: r } = this;
		if (e[0] === null) {
			let i = r == null ? void 0 : r.get(), a = e[e.length - 1];
			if (i !== void 0) e[0] = i;
			else if (n && t) {
				let r = Dt(n.readValue(t, a), t, a);
				r !== void 0 && (e[0] = r);
			}
			e[0] === void 0 && (e[0] = a), r && i === void 0 && r.set(e[0]);
		}
		rt(e);
	}
	setFinalKeyframe() {}
	measureInitialState() {}
	renderEndStyles() {}
	measureEndState() {}
	complete(e = !1) {
		this.state = "complete", this.onComplete(this.unresolvedKeyframes, this.finalKeyframe, e), Y.delete(this);
	}
	cancel() {
		this.state === "scheduled" && (Y.delete(this), this.state = "pending");
	}
	resume() {
		this.state === "pending" && this.scheduleResolve();
	}
}, kt = (e) => e.startsWith("--");
//#endregion
//#region node_modules/motion-dom/dist/es/render/dom/style-set.mjs
function At(e, t, n) {
	kt(t) ? e.style.setProperty(t, n) : e.style[t] = n;
}
//#endregion
//#region node_modules/motion-dom/dist/es/utils/supports/flags.mjs
var jt = {};
//#endregion
//#region node_modules/motion-dom/dist/es/utils/supports/memo.mjs
function Mt(e, t) {
	let n = /* @__PURE__ */ y(e);
	return () => jt[t] ?? n();
}
//#endregion
//#region node_modules/motion-dom/dist/es/utils/supports/scroll-timeline.mjs
var Nt = /* @__PURE__ */ Mt(() => window.ScrollTimeline !== void 0, "scrollTimeline"), Pt = /*@__PURE__*/ Mt(() => {
	try {
		document.createElement("div").animate({ opacity: 0 }, { easing: "linear(0, 1)" });
	} catch {
		return !1;
	}
	return !0;
}, "linearEasing"), X = ([e, t, n, r]) => `cubic-bezier(${e}, ${t}, ${n}, ${r})`, Ft = {
	linear: "linear",
	ease: "ease",
	easeIn: "ease-in",
	easeOut: "ease-out",
	easeInOut: "ease-in-out",
	circIn: /*@__PURE__*/ X([
		0,
		.65,
		.55,
		1
	]),
	circOut: /*@__PURE__*/ X([
		.55,
		0,
		1,
		.45
	]),
	backIn: /*@__PURE__*/ X([
		.31,
		.01,
		.66,
		-.59
	]),
	backOut: /*@__PURE__*/ X([
		.33,
		1.53,
		.69,
		.99
	])
};
//#endregion
//#region node_modules/motion-dom/dist/es/animation/waapi/easing/map-easing.mjs
function It(e, t) {
	if (e) return typeof e == "function" ? Pt() ? Ve(e, t) : "ease-out" : /* @__PURE__ */ T(e) ? X(e) : Array.isArray(e) ? e.map((e) => It(e, t) || Ft.easeOut) : Ft[e];
}
//#endregion
//#region node_modules/motion-dom/dist/es/animation/waapi/start-waapi-animation.mjs
function Lt(e, t, n, { delay: r = 0, duration: i = 300, repeat: a = 0, repeatType: o = "loop", ease: s = "easeOut", times: c } = {}, l = void 0) {
	let u = { [t]: n };
	c && (u.offset = c);
	let d = It(s, i);
	Array.isArray(d) && (u.easing = d);
	let f = {
		delay: r,
		duration: i,
		easing: Array.isArray(d) ? "linear" : d,
		fill: "both",
		iterations: a + 1,
		direction: o === "reverse" ? "alternate" : "normal"
	};
	return l && (f.pseudoElement = l), e.animate(u, f);
}
//#endregion
//#region node_modules/motion-dom/dist/es/animation/generators/utils/is-generator.mjs
function Rt(e) {
	return typeof e == "function" && "applyToOptions" in e;
}
//#endregion
//#region node_modules/motion-dom/dist/es/animation/waapi/utils/apply-generator.mjs
function zt({ type: e, ...t }) {
	return Rt(e) && Pt() ? e.applyToOptions(t) : (t.duration ??= 300, t.ease ??= "easeOut", t);
}
//#endregion
//#region node_modules/motion-dom/dist/es/animation/NativeAnimation.mjs
var Bt = class extends Ke {
	constructor(e) {
		if (super(), this.finishedTime = null, this.isStopped = !1, this.manualStartTime = null, !e) return;
		let { element: t, name: n, keyframes: r, pseudoElement: i, allowFlatten: a = !1, finalKeyframe: o, onComplete: s } = e;
		this.isPseudoElement = !!i, this.allowFlatten = a, this.options = e, e.type;
		let c = zt(e);
		this.animation = Lt(t, n, r, c, i), c.autoplay === !1 && this.animation.pause(), this.animation.onfinish = () => {
			if (this.finishedTime = this.time, !i) {
				let e = Ue(r, this.options, o, this.speed);
				this.updateMotionValue && this.updateMotionValue(e), At(t, n, e), this.animation.cancel();
			}
			s == null || s(), this.notifyFinished();
		}, Ge(this, e, c);
	}
	play() {
		this.isStopped || (this.manualStartTime = null, this.animation.play(), this.state === "finished" && this.updateFinished());
	}
	pause() {
		this.animation.pause();
	}
	complete() {
		var e, t;
		(e = (t = this.animation).finish) == null || e.call(t);
	}
	cancel() {
		try {
			this.animation.cancel();
		} catch {}
	}
	stop() {
		if (this.isStopped) return;
		this.isStopped = !0;
		let { state: e } = this;
		e !== "idle" && e !== "finished" && (this.updateMotionValue ? this.updateMotionValue() : this.commitStyles(), this.isPseudoElement || this.cancel());
	}
	commitStyles() {
		var e;
		let t = (e = this.options) == null ? void 0 : e.element;
		if (!this.isPseudoElement && t != null && t.isConnected) {
			var n, r;
			(n = (r = this.animation).commitStyles) == null || n.call(r);
		}
	}
	get duration() {
		var e, t;
		let n = ((e = this.animation.effect) == null || (t = e.getComputedTiming) == null ? void 0 : t.call(e).duration) || 0;
		return /* @__PURE__ */ C(Number(n));
	}
	get iterationDuration() {
		let { delay: e = 0 } = this.options || {};
		return this.duration + /* @__PURE__ */ C(e);
	}
	get time() {
		return /* @__PURE__ */ C(Number(this.animation.currentTime) || 0);
	}
	set time(e) {
		let t = this.finishedTime !== null;
		this.manualStartTime = null, this.finishedTime = null, this.animation.currentTime = /* @__PURE__ */ S(e), t && this.animation.pause();
	}
	get speed() {
		return this.animation.playbackRate;
	}
	set speed(e) {
		e < 0 && (this.finishedTime = null), this.animation.playbackRate = e;
	}
	get state() {
		return this.finishedTime === null ? this.animation.playState : "finished";
	}
	get startTime() {
		return this.manualStartTime ?? Number(this.animation.startTime);
	}
	set startTime(e) {
		this.manualStartTime = this.animation.startTime = e;
	}
	attachTimeline({ timeline: e, onAttach: t, observe: n }) {
		if (this.allowFlatten) {
			var r;
			(r = this.animation.effect) == null || r.updateTiming({ easing: "linear" });
		}
		return this.animation.onfinish = null, e && Nt() ? (this.animation.timeline = e, t == null || t(this.animation), b) : n(this);
	}
}, Vt = /* @__PURE__ */ new Set([
	"opacity",
	"clipPath",
	"filter",
	"transform",
	"backgroundColor"
]), Ht = 30, Ut = (e) => !isNaN(parseFloat(e)), Wt = { current: void 0 }, Gt = class {
	constructor(e, t = {}) {
		this.canTrackVelocity = null, this.events = {}, this.updateAndNotify = (e) => {
			let t = O.now();
			if (this.updatedAt !== t && this.setPrevFrameValue(), this.prev = this.current, this.setCurrent(e), this.current !== this.prev && (this.notifyChange(), this.dependents)) for (let e of this.dependents) e.dirty();
		}, this.hasAnimated = !1, this.setCurrent(e), this.owner = t.owner;
	}
	setCurrent(e) {
		this.current = e, this.updatedAt = O.now(), this.canTrackVelocity === null && e !== void 0 && (this.canTrackVelocity = Ut(this.current));
	}
	setPrevFrameValue(e = this.current) {
		this.prevFrameValue = e, this.prevUpdatedAt = this.updatedAt;
	}
	onChange(e) {
		return this.on("change", e);
	}
	on(e, t) {
		var n;
		return e === "change" ? this.onChangeSubscribe(t) : ((n = this.events)[e] || (n[e] = new x())).add(t);
	}
	onChangeSubscribe(e) {
		let { events: t } = this;
		return !t.change && !this.changeSubscriber ? this.changeSubscriber = e : (t.change || (t.change = new x(), t.change.add(this.changeSubscriber), this.changeSubscriber = void 0), t.change.add(e)), () => {
			if (this.changeSubscriber === e) this.changeSubscriber = void 0;
			else {
				var n;
				(n = t.change) == null || n.remove(e);
			}
			this.stopIfUnobserved();
		};
	}
	stopIfUnobserved() {
		U.read(() => {
			var e;
			!this.changeSubscriber && !((e = this.events.change) != null && e.getSize()) && this.stop();
		});
	}
	clearListeners() {
		this.changeSubscriber = void 0;
		for (let e in this.events) this.events[e].clear();
	}
	attach(e, t) {
		this.passiveEffect = e, this.stopPassiveEffect = t;
	}
	set(e) {
		this.passiveEffect ? this.passiveEffect(e, this.updateAndNotify) : this.updateAndNotify(e);
	}
	setWithVelocity(e, t, n) {
		this.set(t), this.prev = void 0, this.prevFrameValue = e, this.prevUpdatedAt = this.updatedAt - n;
	}
	jump(e, t = !0) {
		this.updateAndNotify(e), this.prev = e, this.prevUpdatedAt = this.prevFrameValue = void 0, t && this.stop(), this.stopPassiveEffect && this.stopPassiveEffect();
	}
	dirty() {
		this.notifyChange();
	}
	notifyChange() {
		let { current: e, changeSubscriber: t } = this;
		if (t) t(e);
		else {
			var n;
			(n = this.events.change) == null || n.notify(e);
		}
	}
	addDependent(e) {
		this.dependents ||= /* @__PURE__ */ new Set(), this.dependents.add(e);
	}
	removeDependent(e) {
		this.dependents && this.dependents.delete(e);
	}
	get() {
		return Wt.current && Wt.current.push(this), this.current;
	}
	getPrevious() {
		return this.prev;
	}
	getVelocity() {
		let e = O.now();
		if (!this.canTrackVelocity || this.prevFrameValue === void 0 || e - this.updatedAt > Ht) return 0;
		let t = Math.min(this.updatedAt - this.prevUpdatedAt, Ht);
		return /* @__PURE__ */ w(parseFloat(this.current) - parseFloat(this.prevFrameValue), t);
	}
	start(e) {
		return this.stop(), new Promise((t) => {
			var n;
			this.hasAnimated = !0;
			let r = !1, i;
			i = e(() => {
				var e;
				r = !0, (e = this.events.animationComplete) == null || e.notify(), this.animation === i && this.clearAnimation(), t();
			}), r || (this.animation = i), (n = this.events.animationStart) == null || n.notify();
		});
	}
	stop() {
		this.animation && (this.animation.stop(), this.events.animationCancel && this.events.animationCancel.notify()), this.clearAnimation();
	}
	isAnimating() {
		return !!this.animation;
	}
	clearAnimation() {
		this.animation = void 0;
	}
	destroy() {
		var e, t;
		(e = this.dependents) == null || e.clear(), (t = this.events.destroy) == null || t.notify(), this.clearListeners(), this.stop(), this.stopPassiveEffect && this.stopPassiveEffect();
	}
};
function Z(e, t) {
	return new Gt(e, t);
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/utils/resolve-variants.mjs
function Kt(e) {
	let t = [{}, {}];
	return e == null || e.values.forEach((e, n) => {
		t[0][n] = e.get(), t[1][n] = e.getVelocity();
	}), t;
}
function qt(e, t, n, r) {
	let i = (t) => typeof t == "function" ? t(n === void 0 ? e.custom : n, ...Kt(r)) : t;
	return t = i(t), typeof t == "string" && (t = e.variants && e.variants[t]), i(t);
}
//#endregion
//#region node_modules/motion-dom/dist/es/value/utils/is-motion-value.mjs
var Q = (e) => !!(e && e.getVelocity);
//#endregion
//#region node_modules/motion-dom/dist/es/render/dom/utils/camel-to-dash.mjs
function Jt(e) {
	return e.replace(/([A-Z])/g, (e) => `-${e.toLowerCase()}`);
}
var Yt = "data-" + Jt("framerAppearId");
//#endregion
//#region node_modules/motion-dom/dist/es/utils/is-html-element.mjs
function Xt(e) {
	return _(e) && "offsetHeight" in e && !("ownerSVGElement" in e);
}
//#endregion
//#region node_modules/motion-dom/dist/es/value/types/utils/get-as-type.mjs
var Zt = (e, t) => t && typeof e == "number" ? t.transform(e) : e, Qt = {
	x: "translateX",
	y: "translateY",
	z: "translateZ",
	transformPerspective: "perspective"
}, $t = K.length;
function en(e, t, n) {
	let r = "", i = !0;
	for (let a = 0; a < $t; a++) {
		let o = K[a], s = e[o];
		if (s === void 0) continue;
		let c = !0;
		if (typeof s == "number") c = s === +!!o.startsWith("scale");
		else {
			let e = parseFloat(s);
			c = o.startsWith("scale") ? e === 1 : e === 0;
		}
		if (!c || n) {
			let e = Zt(s, W[o]);
			if (!c) {
				i = !1;
				let t = Qt[o] || o;
				r += `${t}(${e}) `;
			}
			n && (t[o] = e);
		}
	}
	let a = e.pathRotation;
	return a && (i = !1, r += `rotate(${Zt(a, W.pathRotation)}) `), r = r.trim(), n ? r = n(t, i ? "" : r) : i && (r = "none"), r;
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/html/utils/build-styles.mjs
function tn(e, t, n) {
	let { style: r, vars: i, transformOrigin: a } = e, o = !1, s = !1;
	for (let e in t) {
		let n = t[e];
		if (q.has(e)) o = !0;
		else if (ne(e)) i[e] = n;
		else {
			let t = Zt(n, W[e]);
			e.startsWith("origin") ? (s = !0, a[e] = t) : r[e] = t;
		}
	}
	if (t.transform || (o || n ? r.transform = en(t, e.transform, n) : r.transform &&= "none"), s) {
		let { originX: e = "50%", originY: t = "50%", originZ: n = 0 } = a;
		r.transformOrigin = `${e} ${t} ${n}`;
	}
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/svg/utils/path.mjs
var nn = {
	offset: "stroke-dashoffset",
	array: "stroke-dasharray"
}, rn = {
	offset: "strokeDashoffset",
	array: "strokeDasharray"
};
function an(e, t, n = 1, r = 0, i = !0) {
	e.pathLength = 1;
	let a = i ? nn : rn;
	e[a.offset] = `${-r}`, e[a.array] = `${t} ${n}`;
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/svg/utils/build-attrs.mjs
var on = [
	"transform",
	"opacity",
	"offsetDistance",
	"offsetPath",
	"offsetRotate",
	"offsetAnchor"
];
function sn(e, { attrX: t, attrY: n, attrScale: r, pathLength: i, pathSpacing: a = 1, pathOffset: o = 0, ...s }, c, l, u) {
	if (tn(e, s, l), c) {
		e.style.viewBox && (e.attrs.viewBox = e.style.viewBox);
		return;
	}
	e.attrs = e.style, e.style = {};
	let { attrs: d, style: f } = e;
	for (let e of on) d[e] !== void 0 && (f[e] = d[e], delete d[e]);
	(f.transform || d.transformOrigin) && (f.transformOrigin = d.transformOrigin ?? "50% 50%", delete d.transformOrigin), f.transform && (f.transformBox = (u == null ? void 0 : u.transformBox) ?? "fill-box", delete d.transformBox), t !== void 0 && (d.x = t), n !== void 0 && (d.y = n), r !== void 0 && (d.scale = r), i !== void 0 && an(d, i, a, o, !1);
}
//#endregion
//#region node_modules/motion-dom/dist/es/frameloop/microtask.mjs
var { schedule: cn, cancel: ln } = /* @__PURE__ */ Re(queueMicrotask, !1), un = () => ({
	min: 0,
	max: 0
}), dn = () => ({
	x: un(),
	y: un()
}), fn = /* @__PURE__ */ new WeakMap();
//#endregion
//#region node_modules/motion-dom/dist/es/render/utils/is-animation-controls.mjs
function pn(e) {
	return typeof e == "object" && !!e && typeof e.start == "function";
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/utils/is-variant-label.mjs
function mn(e) {
	return typeof e == "string" || Array.isArray(e);
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/utils/variant-props.mjs
var hn = [
	"animate",
	"whileInView",
	"whileFocus",
	"whileHover",
	"whileTap",
	"whileDrag",
	"exit"
], gn = ["initial", ...hn];
//#endregion
//#region node_modules/motion-dom/dist/es/render/utils/is-controlling-variants.mjs
function _n(e) {
	if (pn(e.animate)) return !0;
	for (let t = 0; t < gn.length; t++) if (mn(e[gn[t]])) return !0;
	return !1;
}
function vn(e) {
	return !!(_n(e) || e.variants);
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/utils/motion-values.mjs
function yn(e, t, n) {
	for (let r in t) {
		let i = t[r], a = n[r];
		if (Q(i)) e.addValue(r, i);
		else if (Q(a)) e.addValue(r, Z(i, { owner: e }));
		else if (a !== i) {
			if (e.hasValue(r)) {
				let t = e.getValue(r);
				t.liveStyle === !0 ? t.jump(i) : t.hasAnimated || t.set(i);
			} else {
				let t = e.getStaticValue(r);
				e.addValue(r, Z(t === void 0 ? i : t, { owner: e }));
			}
		}
	}
	for (let r in n) t[r] === void 0 && e.removeValue(r);
	return t;
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/utils/reduced-motion/state.mjs
var bn = { current: null }, xn = { current: !1 }, Sn = typeof window < "u";
function Cn() {
	if (xn.current = !0, Sn) {
		if (window.matchMedia) {
			let e = window.matchMedia("(prefers-reduced-motion)"), t = () => bn.current = e.matches;
			e.addEventListener("change", t), t();
		} else bn.current = !1;
	}
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/VisualElement.mjs
var wn = [
	"AnimationStart",
	"AnimationComplete",
	"Update",
	"BeforeLayoutMeasure",
	"LayoutMeasure",
	"LayoutAnimationStart",
	"LayoutAnimationComplete"
], Tn = {};
function En(e) {
	Tn = e;
}
function Dn() {
	return Tn;
}
var On = class {
	scrapeMotionValuesFromProps(e, t, n) {
		return {};
	}
	constructor({ parent: e, props: t, presenceContext: n, reducedMotionConfig: r, skipAnimations: i, blockInitialAnimation: a, visualState: o }, s = {}) {
		this.current = null, this.children = /* @__PURE__ */ new Set(), this.isVariantNode = !1, this.isControllingVariants = !1, this.shouldReduceMotion = null, this.shouldSkipAnimations = !1, this.values = /* @__PURE__ */ new Map(), this.KeyframeResolver = Ot, this.features = {}, this.valueSubscriptions = /* @__PURE__ */ new Map(), this.prevMotionValues = {}, this.hasBeenMounted = !1, this.events = {}, this.propEventSubscriptions = {}, this.notifyUpdate = () => this.notify("Update", this.latestValues), this.render = () => {
			this.current && (this.triggerBuild(), this.renderInstance(this.current, this.renderState, this.props.style, this.projection));
		}, this.renderScheduledAt = 0, this.scheduleRender = () => {
			let e = O.now();
			this.renderScheduledAt < e && (this.renderScheduledAt = e, U.render(this.render, !1, !0));
		};
		let { latestValues: c, renderState: l } = o;
		this.latestValues = c, this.baseTarget = { ...c }, this.initialValues = t.initial ? { ...c } : {}, this.renderState = l, this.parent = e, this.props = t, this.presenceContext = n, this.depth = e ? e.depth + 1 : 0, this.reducedMotionConfig = r, this.skipAnimationsConfig = i, this.options = s, this.blockInitialAnimation = !!a, this.isControllingVariants = _n(t), this.isVariantNode = vn(t), this.isVariantNode && (this.variantChildren = /* @__PURE__ */ new Set()), this.manuallyAnimateOnMount = !!(e && e.current);
		let { willChange: u, ...d } = this.scrapeMotionValuesFromProps(t, {}, this);
		for (let e in d) {
			let t = d[e];
			c[e] !== void 0 && Q(t) && t.set(c[e]);
		}
	}
	mount(e) {
		var t;
		if (this.hasBeenMounted) for (let e in this.initialValues) {
			var n;
			(n = this.values.get(e)) == null || n.jump(this.initialValues[e]), this.latestValues[e] = this.initialValues[e];
		}
		if (this.current = e, fn.set(e, this), this.projection && !this.projection.instance && this.projection.mount(e), this.isVariantNode && !this.isControllingVariants) {
			let e = this;
			do
				e = e.props.inherit !== !1 && e.parent;
			while (e && !e.isVariantNode);
			if (e) {
				let { variantChildren: t } = e;
				t.add(this), this.removeFromVariantTree = () => t.delete(this);
			}
		}
		this.values.forEach((e, t) => this.bindToMotionValue(t, e)), this.reducedMotionConfig === "never" ? this.shouldReduceMotion = !1 : this.reducedMotionConfig === "always" ? this.shouldReduceMotion = !0 : (xn.current || Cn(), this.shouldReduceMotion = bn.current), this.shouldSkipAnimations = this.skipAnimationsConfig ?? !1, (t = this.parent) == null || t.addChild(this), this.update(this.props, this.presenceContext), this.hasBeenMounted = !0;
	}
	unmount() {
		var e;
		this.projection && this.projection.unmount(), ze(this.notifyUpdate), ze(this.render), this.valueSubscriptions.forEach((e) => e()), this.valueSubscriptions.clear(), this.removeFromVariantTree && this.removeFromVariantTree(), (e = this.parent) == null || e.removeChild(this);
		for (let e in this.events) this.events[e].clear();
		for (let e in this.features) {
			let t = this.features[e];
			t && (t.unmount(), t.isMounted = !1);
		}
		this.current = null;
	}
	addChild(e) {
		this.children.add(e), this.enteringChildren ??= /* @__PURE__ */ new Set(), this.enteringChildren.add(e);
	}
	removeChild(e) {
		this.children.delete(e), this.enteringChildren && this.enteringChildren.delete(e);
	}
	bindToMotionValue(e, t) {
		if (this.valueSubscriptions.has(e) && this.valueSubscriptions.get(e)(), t.accelerate && Vt.has(e) && this.current instanceof HTMLElement) {
			let { factory: n, keyframes: r, times: i, ease: a, duration: o } = t.accelerate, s = new Bt({
				element: this.current,
				name: e,
				keyframes: r,
				times: i,
				ease: a,
				duration: /* @__PURE__ */ S(o)
			}), c = n(s);
			this.valueSubscriptions.set(e, () => {
				c(), s.cancel();
			});
			return;
		}
		let n = q.has(e);
		n && this.onBindTransform && this.onBindTransform();
		let r = t.on("change", (t) => {
			this.latestValues[e] = t, this.props.onUpdate && U.preRender(this.notifyUpdate), n && this.projection && (this.projection.isTransformDirty = !0), this.scheduleRender();
		}), i;
		typeof window < "u" && window.MotionCheckAppearSync && (i = window.MotionCheckAppearSync(this, e, t)), this.valueSubscriptions.set(e, () => {
			r(), i && i();
		});
	}
	sortNodePosition(e) {
		return !this.current || !e.current || !this.sortInstanceNodePosition || this.type !== e.type ? 0 : this.sortInstanceNodePosition(this.current, e.current);
	}
	updateFeatures() {
		let e = "animation";
		for (e in Tn) {
			let t = Tn[e];
			if (!t) continue;
			let { isEnabled: n, Feature: r } = t;
			if (!this.features[e] && r && n(this.props) && (this.features[e] = new r(this)), this.features[e]) {
				let t = this.features[e];
				t.isMounted ? t.update() : (t.mount(), t.isMounted = !0);
			}
		}
	}
	triggerBuild() {
		this.build(this.renderState, this.latestValues, this.props);
	}
	measureViewportBox() {
		return this.current ? this.measureInstanceViewportBox(this.current, this.props) : dn();
	}
	getStaticValue(e) {
		return this.latestValues[e];
	}
	setStaticValue(e, t) {
		this.latestValues[e] = t;
	}
	update(e, t) {
		(e.transformTemplate || this.props.transformTemplate) && this.scheduleRender(), this.prevProps = this.props, this.props = e, this.prevPresenceContext = this.presenceContext, this.presenceContext = t;
		for (let t = 0; t < wn.length; t++) {
			let n = wn[t];
			this.propEventSubscriptions[n] && (this.propEventSubscriptions[n](), delete this.propEventSubscriptions[n]);
			let r = e["on" + n];
			r && (this.propEventSubscriptions[n] = this.on(n, r));
		}
		this.prevMotionValues = yn(this, this.scrapeMotionValuesFromProps(e, this.prevProps || {}, this), this.prevMotionValues), this.handleChildMotionValue && this.handleChildMotionValue();
	}
	getProps() {
		return this.props;
	}
	getVariant(e) {
		return this.props.variants ? this.props.variants[e] : void 0;
	}
	getDefaultTransition() {
		return this.props.transition;
	}
	getTransformPagePoint() {
		return this.props.transformPagePoint;
	}
	addValue(e, t) {
		let n = this.values.get(e);
		if (t !== n) {
			n && this.removeValue(e), this.bindToMotionValue(e, t), this.values.set(e, t);
			let r = t.get();
			r !== void 0 && (this.latestValues[e] = r);
		}
	}
	removeValue(e) {
		this.values.delete(e);
		let t = this.valueSubscriptions.get(e);
		t && (t(), this.valueSubscriptions.delete(e)), delete this.latestValues[e], this.removeValueFromRenderState(e, this.renderState);
	}
	hasValue(e) {
		return this.values.has(e);
	}
	getValue(e, t) {
		if (this.props.values && this.props.values[e]) return this.props.values[e];
		let n = this.values.get(e);
		if (n === void 0 && t !== void 0) {
			var r;
			n = Z(t ?? ((r = this.getDefaultValue) == null ? void 0 : r.call(this, e)), { owner: this }), this.addValue(e, n);
		}
		return n;
	}
	readValue(e, t) {
		let n = this.latestValues[e] !== void 0 || !this.current ? this.latestValues[e] : this.getBaseTargetFromProps(this.props, e) ?? this.readValueFromInstance(this.current, e, this.options);
		return n != null && (typeof n == "string" && (g(n) || v(n)) ? n = parseFloat(n) : typeof n != "number" && !V.test(n) && V.test(t) && (n = nt(e, t)), this.setBaseTarget(e, Q(n) ? n.get() : n)), Q(n) ? n.get() : n;
	}
	setBaseTarget(e, t) {
		this.baseTarget[e] = t;
	}
	on(e, t) {
		return this.events[e] || (this.events[e] = new x()), this.events[e].add(t);
	}
	notify(e, ...t) {
		this.events[e] && this.events[e].notify(...t);
	}
	scheduleRenderMicrotask() {
		cn.render(this.render);
	}
}, kn = {};
//#endregion
//#region node_modules/motion-dom/dist/es/render/utils/is-forced-motion-value.mjs
function An(e, { layout: t, layoutId: n }) {
	return q.has(e) || e.startsWith("origin") || (t || n !== void 0) && (!!kn[e] || e === "opacity");
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/html/utils/scrape-motion-values.mjs
function jn(e, t, n) {
	let r = e.style, i = t == null ? void 0 : t.style, a = {};
	if (!r) return a;
	for (let t in r) {
		var o;
		(Q(r[t]) || i && Q(i[t]) || An(t, e) || (n == null || (o = n.getValue(t)) == null ? void 0 : o.liveStyle) !== void 0) && (a[t] = r[t]);
	}
	return a;
}
//#endregion
//#region node_modules/motion-dom/dist/es/render/svg/utils/is-svg-tag.mjs
var Mn = (e) => typeof e == "string" && e.toLowerCase() === "svg";
//#endregion
//#region node_modules/motion-dom/dist/es/render/svg/utils/scrape-motion-values.mjs
function Nn(e, t, n) {
	let r = jn(e, t, n);
	for (let n in e) if (Q(e[n]) || Q(t[n])) {
		let t = K.indexOf(n) === -1 ? n : "attr" + n.charAt(0).toUpperCase() + n.substring(1);
		r[t] = e[n];
	}
	return r;
}
//#endregion
//#region node_modules/motion-dom/dist/es/value/utils/resolve-motion-value.mjs
function Pn(e) {
	return Q(e) ? e.get() : e;
}
//#endregion
//#region node_modules/framer-motion/dist/es/context/MotionConfigContext.mjs
var Fn = (0, a.createContext)({
	transformPagePoint: (e) => e,
	isStatic: !1,
	reducedMotion: "never"
});
//#endregion
//#region node_modules/framer-motion/dist/es/utils/use-composed-ref.mjs
function In(e, t) {
	if (typeof e == "function") return e(t);
	e != null && (e.current = t);
}
function Ln(...e) {
	return (t) => {
		let n = !1, r = e.map((e) => {
			let r = In(e, t);
			return !n && typeof r == "function" && (n = !0), r;
		});
		if (n) return () => {
			for (let t = 0; t < r.length; t++) {
				let n = r[t];
				typeof n == "function" ? n() : In(e[t], null);
			}
		};
	};
}
function Rn(...e) {
	return a.useCallback(Ln(...e), e);
}
//#endregion
//#region node_modules/framer-motion/dist/es/components/AnimatePresence/PopChild.mjs
var zn = class extends a.Component {
	getSnapshotBeforeUpdate(e) {
		let t = this.props.childRef.current;
		if (Xt(t) && e.isPresent && !this.props.isPresent && this.props.pop !== !1) {
			let e = t.offsetParent, n = Xt(e) && e.offsetWidth || 0, r = Xt(e) && e.offsetHeight || 0, i = getComputedStyle(t), a = this.props.sizeRef.current;
			a.height = parseFloat(i.height), a.width = parseFloat(i.width), a.top = t.offsetTop, a.left = t.offsetLeft, a.right = n - a.width - a.left, a.bottom = r - a.height - a.top, a.direction = i.direction;
		}
		return null;
	}
	componentDidUpdate() {}
	render() {
		return this.props.children;
	}
};
function Bn({ children: e, isPresent: t, anchorX: n, anchorY: r, root: o, pop: s }) {
	var c;
	let l = (0, a.useId)(), u = (0, a.useRef)(null), d = (0, a.useRef)({
		width: 0,
		height: 0,
		top: 0,
		left: 0,
		right: 0,
		bottom: 0,
		direction: "ltr"
	}), { nonce: f } = (0, a.useContext)(Fn), p = Rn(u, s === !1 ? void 0 : ((c = e.props) == null ? void 0 : c.ref) ?? (e == null ? void 0 : e.ref));
	return (0, a.useInsertionEffect)(() => {
		let { width: e, height: i, top: a, left: c, right: p, bottom: m, direction: h } = d.current;
		if (t || s === !1 || !u.current || !e || !i) return;
		let g = h === "rtl", _ = n === "left" ? g ? `right: ${p}` : `left: ${c}` : g ? `left: ${c}` : `right: ${p}`, v = r === "bottom" ? `bottom: ${m}` : `top: ${a}`;
		u.current.dataset.motionPopId = l;
		let y = document.createElement("style");
		f && (y.nonce = f);
		let b = o ?? document.head;
		return b.appendChild(y), y.sheet && y.sheet.insertRule(`
          [data-motion-pop-id="${l}"] {
            position: absolute !important;
            width: ${e}px !important;
            height: ${i}px !important;
            ${_}px !important;
            ${v}px !important;
          }
        `), () => {
			var e;
			(e = u.current) == null || e.removeAttribute("data-motion-pop-id"), b.contains(y) && b.removeChild(y);
		};
	}, [t]), (0, i.jsx)(zn, {
		isPresent: t,
		childRef: u,
		sizeRef: d,
		pop: s,
		children: s === !1 ? e : a.cloneElement(e, { ref: p })
	});
}
//#endregion
//#region node_modules/framer-motion/dist/es/components/AnimatePresence/PresenceChild.mjs
var Vn = ({ children: e, initial: t, isPresent: n, onExitComplete: r, custom: o, presenceAffectsLayout: u, mode: d, anchorX: f, anchorY: p, root: m }) => {
	let h = s(Hn), g = (0, a.useId)(), _ = (0, a.useRef)(n), v = (0, a.useRef)(r);
	c(() => {
		_.current = n, v.current = r;
	});
	let y = !0, b = (0, a.useMemo)(() => (y = !1, {
		id: g,
		initial: t,
		isPresent: n,
		custom: o,
		onExitComplete: (e) => {
			h.set(e, !0);
			for (let e of h.values()) if (!e) return;
			r && r();
		},
		register: (e) => (h.set(e, !1), () => {
			var t;
			h.delete(e), !_.current && !h.size && ((t = v.current) == null || t.call(v));
		})
	}), [
		n,
		h,
		r
	]);
	return u && y && (b = { ...b }), (0, a.useMemo)(() => {
		h.forEach((e, t) => h.set(t, !1));
	}, [n]), a.useEffect(() => {
		!n && !h.size && r && r();
	}, [n]), e = (0, i.jsx)(Bn, {
		pop: d === "popLayout",
		isPresent: n,
		anchorX: f,
		anchorY: p,
		root: m,
		children: e
	}), (0, i.jsx)(l.Provider, {
		value: b,
		children: e
	});
};
function Hn() {
	return /* @__PURE__ */ new Map();
}
//#endregion
//#region node_modules/framer-motion/dist/es/components/AnimatePresence/use-presence.mjs
function Un(e = !0) {
	let t = (0, a.useContext)(l);
	if (t === null) return [!0, null];
	let { isPresent: n, onExitComplete: r, register: i } = t, o = (0, a.useId)();
	(0, a.useEffect)(() => {
		if (e) return i(o);
	}, [e]);
	let s = (0, a.useCallback)(() => e && r && r(o), [
		o,
		r,
		e
	]);
	return !n && r ? [!1, s] : [!0];
}
//#endregion
//#region node_modules/framer-motion/dist/es/components/AnimatePresence/utils.mjs
var $ = (e) => e.key || "";
function Wn(e) {
	let t = [];
	return a.Children.forEach(e, (e) => {
		(0, a.isValidElement)(e) && t.push(e);
	}), t;
}
//#endregion
//#region node_modules/framer-motion/dist/es/components/AnimatePresence/index.mjs
var Gn = ({ children: e, custom: t, initial: n = !0, onExitComplete: r, presenceAffectsLayout: l = !0, mode: u = "sync", propagate: d = !1, anchorX: f = "left", anchorY: p = "top", root: m }) => {
	let [h, g] = Un(d), _ = (0, a.useMemo)(() => Wn(e), [e]), v = d && !h ? [] : _.map($), y = (0, a.useRef)(!0), b = s(() => /* @__PURE__ */ new Map()), x = (0, a.useRef)(/* @__PURE__ */ new Set()), [S, C] = (0, a.useState)(_), [w, T] = (0, a.useState)(_);
	c(() => {
		d && !h && !w.length && (g == null || g());
	}, [
		h,
		d,
		w.length,
		g
	]), c(() => {
		y.current = !1;
		for (let e = 0; e < w.length; e++) {
			let t = $(w[e]);
			v.includes(t) ? (b.delete(t), x.current.delete(t)) : b.get(t) !== !0 && b.set(t, !1);
		}
	}, [
		w,
		v.length,
		v.join("-")
	]);
	let E = [];
	if (_ !== S) {
		let e = [..._], t = 0;
		for (let n of w) {
			let r = v.indexOf($(n));
			r === -1 ? (e.splice(t++, 0, n), E.push(n)) : t = r + E.length + 1;
		}
		return E.every((e) => b.get($(e))) ? e = _ : u === "wait" && (e = E), T(Wn(e)), C(_), null;
	}
	let { forceRender: D } = (0, a.useContext)(o);
	return (0, i.jsx)(i.Fragment, { children: w.map((e) => {
		let a = $(e), o = d && !h ? !1 : _ === w || v.includes(a);
		return (0, i.jsx)(Vn, {
			isPresent: o,
			initial: !y.current || n ? void 0 : !1,
			custom: t,
			presenceAffectsLayout: l,
			mode: u,
			root: m,
			onExitComplete: o ? void 0 : () => {
				if (x.current.has(a)) return;
				if (b.has(a)) x.current.add(a), b.set(a, !0);
				else return;
				let e = !0;
				b.forEach((t) => {
					t || (e = !1);
				}), e && (D == null || D(), C([]), d && (g == null || g()), r && r());
			},
			anchorX: f,
			anchorY: p,
			children: e
		}, a);
	}) });
}, Kn = (0, a.createContext)({ strict: !1 }), qn = {
	animation: [
		"animate",
		"variants",
		"whileHover",
		"whileTap",
		"exit",
		"whileInView",
		"whileFocus",
		"whileDrag"
	],
	exit: ["exit"],
	drag: ["drag", "dragControls"],
	focus: ["whileFocus"],
	hover: [
		"whileHover",
		"onHoverStart",
		"onHoverEnd"
	],
	tap: [
		"whileTap",
		"onTap",
		"onTapStart",
		"onTapCancel"
	],
	pan: [
		"onPan",
		"onPanStart",
		"onPanSessionStart",
		"onPanEnd"
	],
	inView: [
		"whileInView",
		"onViewportEnter",
		"onViewportLeave"
	],
	layout: ["layout", "layoutId"]
}, Jn = !1;
function Yn() {
	if (Jn) return;
	let e = {};
	for (let t in qn) e[t] = { isEnabled: (e) => qn[t].some((t) => !!e[t]) };
	En(e), Jn = !0;
}
function Xn() {
	return Yn(), Dn();
}
//#endregion
//#region node_modules/framer-motion/dist/es/motion/features/load-features.mjs
function Zn(e) {
	let t = Xn();
	for (let n in e) t[n] = {
		...t[n],
		...e[n]
	};
	En(t);
}
//#endregion
//#region node_modules/framer-motion/dist/es/context/MotionContext/index.mjs
var Qn = /* @__PURE__ */ (0, a.createContext)({});
//#endregion
//#region node_modules/framer-motion/dist/es/context/MotionContext/utils.mjs
function $n(e, t) {
	if (_n(e)) {
		let { initial: t, animate: n } = e;
		return {
			initial: t === !1 || mn(t) ? t : void 0,
			animate: mn(n) ? n : void 0
		};
	}
	return e.inherit === !1 ? {} : t;
}
//#endregion
//#region node_modules/framer-motion/dist/es/context/MotionContext/create.mjs
function er(e) {
	let { initial: t, animate: n } = $n(e, (0, a.useContext)(Qn));
	return (0, a.useMemo)(() => ({
		initial: t,
		animate: n
	}), [tr(t), tr(n)]);
}
function tr(e) {
	return Array.isArray(e) ? e.join(" ") : e;
}
//#endregion
//#region node_modules/framer-motion/dist/es/render/html/utils/create-render-state.mjs
var nr = () => ({
	style: {},
	transform: {},
	transformOrigin: {},
	vars: {}
});
//#endregion
//#region node_modules/framer-motion/dist/es/render/html/use-props.mjs
function rr(e, t, n) {
	for (let r in t) !Q(t[r]) && !An(r, n) && (e[r] = t[r]);
}
function ir({ transformTemplate: e }, t) {
	return (0, a.useMemo)(() => {
		let n = nr();
		return tn(n, t, e), Object.assign({}, n.vars, n.style);
	}, [t]);
}
function ar(e, t) {
	let n = e.style || {}, r = {};
	return rr(r, n, e), Object.assign(r, ir(e, t)), r;
}
function or(e, t) {
	let n = {}, r = ar(e, t);
	return e.drag && e.dragListener !== !1 && (n.draggable = !1, r.userSelect = r.WebkitUserSelect = r.WebkitTouchCallout = "none", r.touchAction = e.drag === !0 ? "none" : `pan-${e.drag === "x" ? "y" : "x"}`), e.tabIndex === void 0 && (e.onTap || e.onTapStart || e.whileTap) && (n.tabIndex = 0), n.style = r, n;
}
//#endregion
//#region node_modules/framer-motion/dist/es/render/svg/utils/create-render-state.mjs
var sr = () => ({
	...nr(),
	attrs: {}
});
//#endregion
//#region node_modules/framer-motion/dist/es/render/svg/use-props.mjs
function cr(e, t, n, r) {
	let i = (0, a.useMemo)(() => {
		let n = sr();
		return sn(n, t, Mn(r), e.transformTemplate, e.style), {
			...n.attrs,
			style: { ...n.style }
		};
	}, [t]);
	if (e.style) {
		let t = {};
		rr(t, e.style, e), i.style = {
			...t,
			...i.style
		};
	}
	return i;
}
//#endregion
//#region node_modules/framer-motion/dist/es/motion/utils/valid-prop.mjs
var lr = /* @__PURE__ */ new Set(/* @__PURE__ */ "animate.exit.variants.initial.style.values.transition.transformTemplate.custom.inherit.onBeforeLayoutMeasure.onAnimationStart.onAnimationComplete.onUpdate.onDragStart.onDrag.onDragEnd.onMeasureDragConstraints.onDirectionLock.onDragTransitionEnd._dragX._dragY.onHoverStart.onHoverEnd.onViewportEnter.onViewportLeave.globalTapTarget.propagate.ignoreStrict.viewport".split("."));
function ur(e) {
	return e.startsWith("while") || e.startsWith("drag") && e !== "draggable" || e.startsWith("layout") || e.startsWith("onTap") || e.startsWith("onPan") || e.startsWith("onLayout") || lr.has(e);
}
//#endregion
//#region node_modules/framer-motion/dist/es/render/dom/utils/filter-props.mjs
function dr(e, t) {
	return e.startsWith("on") ? !ur(e) : (t == null ? void 0 : t(e)) ?? !ur(e);
}
function fr(e, t, n, r) {
	let i = {};
	for (let a in e) (a !== "values" || typeof e.values != "object") && (Q(e[a]) || (dr(a, r) || n === !0 && ur(a) || !t && !ur(a) || e.draggable && a.startsWith("onDrag")) && (i[a] = e[a]));
	return i;
}
//#endregion
//#region node_modules/framer-motion/dist/es/render/svg/lowercase-elements.mjs
var pr = [
	"animate",
	"circle",
	"defs",
	"desc",
	"ellipse",
	"g",
	"image",
	"line",
	"filter",
	"marker",
	"mask",
	"metadata",
	"path",
	"pattern",
	"polygon",
	"polyline",
	"rect",
	"stop",
	"switch",
	"symbol",
	"svg",
	"text",
	"tspan",
	"use",
	"view"
];
//#endregion
//#region node_modules/framer-motion/dist/es/render/dom/utils/is-svg-component.mjs
function mr(e) {
	return typeof e != "string" || e.includes("-") ? !1 : !!(pr.indexOf(e) > -1 || /[A-Z]/u.test(e));
}
//#endregion
//#region node_modules/framer-motion/dist/es/render/dom/use-render.mjs
function hr(e, t, n, { latestValues: r }, i, o = !1, s, c) {
	let l = (s ?? mr(e) ? cr : or)(t, r, i, e), u = fr(t, typeof e == "string", o, c), d = e === a.Fragment ? {} : {
		...u,
		...l,
		ref: n
	}, { children: f } = t, p = (0, a.useMemo)(() => Q(f) ? f.get() : f, [f]);
	return (0, a.createElement)(e, {
		...d,
		children: p
	});
}
//#endregion
//#region node_modules/framer-motion/dist/es/motion/utils/use-visual-state.mjs
function gr({ scrapeMotionValuesFromProps: e, createRenderState: t }, n, r, i) {
	return {
		latestValues: _r(n, r, i, e),
		renderState: t()
	};
}
function _r(e, t, n, r) {
	let i = {}, a = r(e, {});
	for (let e in a) i[e] = Pn(a[e]);
	let { initial: o, animate: s } = e, c = _n(e), l = vn(e);
	t && l && !c && e.inherit !== !1 && (o === void 0 && (o = t.initial), s === void 0 && (s = t.animate));
	let u = n ? n.initial === !1 : !1;
	u ||= o === !1;
	let d = u ? s : o;
	if (d && typeof d != "boolean" && !pn(d)) {
		let t = Array.isArray(d) ? d : [d];
		for (let n = 0; n < t.length; n++) {
			let r = qt(e, t[n]);
			if (r) {
				let { transitionEnd: e, transition: t, ...n } = r;
				for (let e in n) {
					let t = n[e];
					if (Array.isArray(t)) {
						let e = u ? t.length - 1 : 0;
						t = t[e];
					}
					t !== null && (i[e] = t);
				}
				for (let t in e) i[t] = e[t];
			}
		}
	}
	return i;
}
var vr = (e) => (t, n) => {
	let r = (0, a.useContext)(Qn), i = (0, a.useContext)(l), o = () => gr(e, t, r, i);
	return n ? o() : s(o);
}, yr = /*@__PURE__*/ vr({
	scrapeMotionValuesFromProps: jn,
	createRenderState: nr
}), br = /*@__PURE__*/ vr({
	scrapeMotionValuesFromProps: Nn,
	createRenderState: sr
}), xr = Symbol.for("motionComponentSymbol");
//#endregion
//#region node_modules/framer-motion/dist/es/motion/utils/use-motion-ref.mjs
function Sr(e, t, n) {
	let r = (0, a.useRef)(n);
	(0, a.useInsertionEffect)(() => {
		r.current = n;
	});
	let i = (0, a.useRef)(null);
	return (0, a.useCallback)((n) => {
		if (n) {
			var a;
			(a = e.onMount) == null || a.call(e, n);
		}
		t && (n ? t.mount(n) : t.unmount());
		let o = r.current;
		if (typeof o == "function") {
			if (n) {
				let e = o(n);
				typeof e == "function" && (i.current = e);
			} else i.current ? (i.current(), i.current = null) : o(n);
		} else o && (o.current = n);
	}, [t]);
}
//#endregion
//#region node_modules/framer-motion/dist/es/context/SwitchLayoutGroupContext.mjs
var Cr = (0, a.createContext)({});
//#endregion
//#region node_modules/framer-motion/dist/es/utils/is-ref-object.mjs
function wr(e) {
	return e && typeof e == "object" && Object.prototype.hasOwnProperty.call(e, "current");
}
//#endregion
//#region node_modules/framer-motion/dist/es/motion/utils/use-visual-element.mjs
function Tr(e, t, n, r, i, o) {
	var s, u, d, f;
	let { visualElement: p } = (0, a.useContext)(Qn), m = (0, a.useContext)(Kn), h = (0, a.useContext)(l), g = (0, a.useContext)(Fn), _ = g.reducedMotion, v = g.skipAnimations, y = (0, a.useRef)(null), b = (0, a.useRef)(!1);
	r ||= m.renderer, !y.current && r && (y.current = r(e, {
		visualState: t,
		parent: p,
		props: n,
		presenceContext: h,
		blockInitialAnimation: h ? h.initial === !1 : !1,
		reducedMotionConfig: _,
		skipAnimations: v,
		isSVG: o
	}), b.current && y.current && (y.current.manuallyAnimateOnMount = !0));
	let x = y.current, S = (0, a.useContext)(Cr);
	x && !x.projection && i && (x.type === "html" || x.type === "svg") && Er(y.current, n, i, S);
	let C = (0, a.useRef)(!1);
	(0, a.useInsertionEffect)(() => {
		x && C.current && x.update(n, h);
	});
	let w = n[Yt], T = (0, a.useRef)(!!w && typeof window < "u" && !((s = (u = window).MotionHandoffIsComplete) != null && s.call(u, w)) && ((d = (f = window).MotionHasOptimisedAnimation) == null ? void 0 : d.call(f, w)));
	return c(() => {
		var e;
		b.current && x && ((e = x.animationState) == null || e.animateChanges(), x.enteringChildren = void 0);
	}, []), c(() => {
		b.current = !0, x && (C.current = !0, window.MotionIsMounted = !0, x.updateFeatures(), x.scheduleRenderMicrotask(), T.current && x.animationState && x.animationState.animateChanges());
	}), (0, a.useEffect)(() => {
		x && (!T.current && x.animationState && x.animationState.animateChanges(), T.current &&= (queueMicrotask(() => {
			var e, t;
			(e = (t = window).MotionHandoffMarkAsComplete) == null || e.call(t, w);
		}), !1), x.enteringChildren = void 0);
	}), x;
}
function Er(e, t, n, r) {
	let { layoutId: i, layout: a, drag: o, dragConstraints: s, layoutScroll: c, layoutRoot: l, layoutAnchor: u, layoutCrossfade: d } = t;
	e.projection = new n(e.latestValues, t["data-framer-portal-id"] ? void 0 : Dr(e.parent)), e.projection.setOptions({
		layoutId: i,
		layout: a,
		alwaysMeasureLayout: !!o || s && wr(s),
		visualElement: e,
		animationType: typeof a == "string" ? a : "both",
		initialPromotionConfig: r,
		crossfade: d,
		layoutScroll: c,
		layoutRoot: l,
		layoutAnchor: u
	});
}
function Dr(e) {
	if (e) return e.options.allowProjection === !1 ? Dr(e.parent) : e.projection;
}
//#endregion
//#region node_modules/framer-motion/dist/es/motion/index.mjs
function Or(e, { forwardMotionProps: t = !1, type: n } = {}, r, o) {
	r && Zn(r);
	let s = n ? n === "svg" : mr(e), c = s ? br : yr;
	function l(n, l) {
		let u, d = {
			...(0, a.useContext)(Fn),
			...n,
			layoutId: kr(n)
		}, { isStatic: f, isValidProp: p } = d, m = er(n), h = c(n, f);
		if (!f && typeof window < "u") {
			Ar(d, r);
			let t = jr(d);
			u = t.MeasureLayout, m.visualElement = Tr(e, h, d, o, t.ProjectionNode, s);
		}
		return (0, i.jsxs)(Qn.Provider, {
			value: m,
			children: [u && m.visualElement ? (0, i.jsx)(u, {
				visualElement: m.visualElement,
				...d
			}) : null, hr(e, n, Sr(h, m.visualElement, l), h, f, t, s, p)]
		});
	}
	l.displayName = `motion.${typeof e == "string" ? e : `create(${e.displayName ?? e.name ?? ""})`}`;
	let u = (0, a.forwardRef)(l);
	return u[xr] = e, u;
}
function kr({ layoutId: e }) {
	let t = (0, a.useContext)(o).id;
	return t && e !== void 0 ? t + "-" + e : e;
}
function Ar(e, t) {
	(0, a.useContext)(Kn).strict;
}
function jr(e) {
	let { drag: t, layout: n } = Xn();
	if (!t && !n) return {};
	let r = {
		...t,
		...n
	};
	return {
		MeasureLayout: t != null && t.isEnabled(e) || n != null && n.isEnabled(e) ? r.MeasureLayout : void 0,
		ProjectionNode: r.ProjectionNode
	};
}
//#endregion
//#region node_modules/framer-motion/dist/es/render/components/create-proxy.mjs
function Mr(e, t) {
	if (typeof Proxy > "u") return Or;
	let n = /* @__PURE__ */ new Map(), r = (n, r) => Or(n, r, e, t);
	return new Proxy((e, t) => r(e, t), { get: (i, a) => a === "create" ? r : (n.has(a) || n.set(a, Or(a, void 0, e, t)), n.get(a)) });
}
//#endregion
//#region node_modules/framer-motion/dist/es/render/components/m/proxy.mjs
var Nr = /*@__PURE__*/ Mr(), Pr = {
	name: "chevron-right",
	size: 24,
	node: [["path", {
		d: "m9 18 6-6-6-6",
		key: "mthhwq"
	}]]
};
Pr.node;
var Fr = r(Pr), Ir = {
	name: "x",
	size: 24,
	node: [["path", {
		d: "M18 6 6 18",
		key: "1bl5f8"
	}], ["path", {
		d: "m6 6 12 12",
		key: "d8bk6v"
	}]]
};
Ir.node;
var Lr = r(Ir);
//#endregion
export { ge as $, Et as A, Ge as B, qt as C, Rt as D, Bt as E, dt as F, B as G, Ve as H, pt as I, z as J, V as K, nt as L, J as M, K as N, At as O, q as P, L as Q, et as R, Q as S, Vt as T, ze as U, Ue as V, U as W, F as X, R as Y, I as Z, on as _, g as _t, Zn as a, ne as at, Yt as b, p as bt, Nn as c, O as ct, On as d, w as dt, _e as et, hn as f, C as ft, sn as g, v as gt, dn as h, y as ht, mr as i, oe as it, ht as j, Ot as k, Mn as l, E as lt, pn as m, b as mt, Fr as n, N as nt, Kn as o, ie as ot, mn as p, S as pt, ke as q, Nr as r, A as rt, Gn as s, k as st, Lr as t, he as tt, jn as u, T as ut, tn as v, h as vt, Z as w, Jt as x, f as xt, Xt as y, m as yt, Ke as z };
