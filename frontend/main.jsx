import { useEffect, useMemo, useRef, useState, lazy, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { m, AnimatePresence, LazyMotion, domAnimation } from "framer-motion";
import clsx from "clsx";
import {
  ArrowLeft,
  Cable,
  ChevronRight,
  CirclePower,
  ExternalLink,
  FastForward,
  Home,
  Keyboard,
  Logs,
  MapPinned,
  Minus,
  MonitorSmartphone,
  Play,
  Plus,
  Settings2,
  ShieldCheck,
  SkipBack,
  Tv,
  Volume2,
  Wifi,
  X,
} from "lucide-react";
import RemoteCanvas from "./components/RemoteCanvas";
import ProviderGlyph from "./components/ProviderGlyph";
import Toasts from "./components/Toasts";
import useRemoteLayout, { BASE_WIDTH, BASE_HEIGHT } from "./hooks/useRemoteLayout";
import {
  releaseTapFocus,
  triggerHaptic,
  getConnectionMode,
  getRouteStatus,
  providerMark,
  isNordProvider,
} from "./lib/utils";
import "./styles.css";

const RoutePanel = lazy(() => import("./panels/RoutePanel.jsx"));
const TvPanel = lazy(() => import("./panels/TvPanel.jsx"));
const LogsPanel = lazy(() => import("./panels/LogsPanel.jsx"));
const ConfigPanel = lazy(() => import("./panels/ConfigPanel.jsx"));

function readBootstrap() {
  const node = document.getElementById("dashboard-bootstrap");
  if (!node?.textContent) return {};
  try {
    return JSON.parse(node.textContent);
  } catch (error) {
    console.error("Failed to parse dashboard bootstrap payload", error);
    return {};
  }
}

const bootstrap = readBootstrap();

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: { Accept: "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "Request failed");
  return payload;
}

function PanelsFallback() {
  return (
    <div className="absolute inset-0 z-30 flex items-center justify-center rounded-[44px] bg-[#09111bcc] backdrop-blur-2xl">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-brass-300 border-t-transparent" />
    </div>
  );
}

function App() {
  const layout = useRemoteLayout();
  const [dashboard, setDashboard] = useState(bootstrap);
  const [specs, setSpecs] = useState(null);
  const [logs, setLogs] = useState(null);
  const [wifi, setWifi] = useState(null);
  const [remote, setRemote] = useState(bootstrap.tv_remote || null);
  const [activePanel, setActivePanel] = useState("");
  const [busyKey, setBusyKey] = useState("");
  const [textEntryOpen, setTextEntryOpen] = useState(false);
  const [textEntryDraft, setTextEntryDraft] = useState("");
  const [textEntryBusy, setTextEntryBusy] = useState(false);
  const [toasts, setToasts] = useState([]);
  const textEntryInputRef = useRef(null);
  const [remoteForm, setRemoteForm] = useState({
    host: bootstrap.tv_remote?.host || bootstrap.tv_remote?.candidate_host || "",
    display_name: bootstrap.tv_remote?.display_name || "OpenSpoofen Remote",
    port: bootstrap.tv_remote?.port || "",
  });
  const [wifiForm, setWifiForm] = useState({ ssid: "", password: "", country: "" });

  const urls = dashboard.urls || {};
  const network = dashboard.network || {};
  const state = dashboard.state || {};
  const providerName = dashboard.provider_name || state.provider_name || "OpenSpoofen";
  const conciseLocation = state.current_location?.label || "Choose a region";
  const connectionMode = getConnectionMode(
    specs?.preferred_topology || network.preferred_topology,
    specs?.upstream_interface || network.upstream_interface?.name,
  );
  const ConnectionModeIcon = connectionMode.icon === "wifi" ? Wifi : Cable;
  const routeStatus = getRouteStatus(state);

  useEffect(() => {
    document.body.style.overflow = layout.mobile ? "auto" : "hidden";
    document.body.style.overscrollBehaviorY = layout.mobile ? "auto" : "none";
    return () => {
      document.body.style.overflow = "";
      document.body.style.overscrollBehaviorY = "";
    };
  }, [layout.mobile]);

  useEffect(() => {
    if (!textEntryOpen) return;
    const frame = window.requestAnimationFrame(() => {
      textEntryInputRef.current?.focus();
      textEntryInputRef.current?.select();
    });
    return () => window.cancelAnimationFrame(frame);
  }, [textEntryOpen]);

  const addToast = (message, category = "success") => {
    if (!message) return;
    const id = `${Date.now()}-${Math.random()}`;
    setToasts((current) => [...current, { id, message, category }]);
    window.setTimeout(() => {
      setToasts((current) => current.filter((toast) => toast.id !== id));
    }, 3200);
  };

  useEffect(() => {
    for (const flash of bootstrap.messages || []) {
      addToast(flash.message, flash.category === "error" ? "error" : "success");
    }
  }, []);

  useEffect(() => {
    if (!urls.status) return undefined;
    const refresh = async () => {
      try {
        const payload = await fetchJson(urls.status);
        setDashboard((current) => ({ ...current, ...payload, urls: current.urls, access: current.access, available_providers: current.available_providers, messages: [] }));
        if (payload.tv_remote) setRemote(payload.tv_remote);
      } catch {
        // silent
      }
    };
    refresh();
    let timer = window.setInterval(refresh, 10000);

    const onVisible = () => {
      if (document.hidden) {
        if (timer) { window.clearInterval(timer); timer = null; }
      } else {
        refresh();
        timer = window.setInterval(refresh, 10000);
      }
    };
    document.addEventListener("visibilitychange", onVisible);

    return () => {
      if (timer) window.clearInterval(timer);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [urls.status]);

  useEffect(() => {
    if (!remote) return;
    setRemoteForm((current) => ({
      host: current.host || remote.host || remote.candidate_host || "",
      display_name: current.display_name || remote.display_name || "OpenSpoofen Remote",
      port: current.port || remote.port || "",
    }));
  }, [remote]);

  const refreshSpecs = async () => {
    if (!urls.appliance_specs) return;
    const payload = await fetchJson(urls.appliance_specs);
    setSpecs(payload.specs || {});
    if (payload.specs?.tv_remote) setRemote(payload.specs.tv_remote);
  };

  const refreshLogs = async () => {
    if (!urls.appliance_logs) return;
    const payload = await fetchJson(urls.appliance_logs);
    setLogs(payload.logs || {});
  };

  const refreshRemote = async () => {
    if (!urls.remote_status) return;
    const payload = await fetchJson(urls.remote_status);
    setRemote(payload.remote || null);
  };

  useEffect(() => {
    if (activePanel === "logs") {
      refreshLogs().catch((error) => addToast(error.message, "error"));
    }
    if (activePanel === "config" || activePanel === "tv") {
      Promise.all([refreshSpecs(), refreshRemote()]).catch((error) => addToast(error.message, "error"));
    }
  }, [activePanel]);

  const handlePanel = (name) => {
    setActivePanel((current) => (current === name ? "" : name));
  };

  const handleProviderSelect = async (providerId) => {
    try {
      const payload = await fetchJson(urls.provider_select, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: providerId }),
      });
      setDashboard((current) => ({ ...current, ...payload, urls: current.urls, access: current.access, available_providers: current.available_providers, messages: [] }));
      addToast(payload.message || "Switched provider backend.");
    } catch (error) {
      addToast(error.message, "error");
    }
  };

  const handleRegion = async (location) => {
    setDashboard((current) => ({
      ...current,
      state: {
        ...current.state,
        connected: false,
        current_location: location,
        status_summary: `Switching to ${location.label}...`,
      },
    }));
    addToast(`Switching to ${location.label}...`);
    setActivePanel("");
    try {
      const payload = await fetchJson(urls.region_switch, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider: dashboard.provider, country: location.country, city: location.city || "" }),
      });
      setDashboard((current) => ({ ...current, ...payload, urls: current.urls, access: current.access, available_providers: current.available_providers, messages: [] }));
      addToast(payload.message || `Switched route to ${location.label}.`);
    } catch (error) {
      addToast(error.message, "error");
    }
  };

  const handleDisconnect = async () => {
    try {
      const payload = await fetchJson(urls.disconnect, { method: "POST" });
      setDashboard((current) => ({ ...current, ...payload, urls: current.urls, access: current.access, available_providers: current.available_providers, messages: [] }));
      addToast(payload.message || "Disconnected provider.");
    } catch (error) {
      addToast(error.message, "error");
    }
  };

  const handleRemoteKey = async (key) => {
    if (!urls.remote_key) return;
    setBusyKey(key);
    try {
      const payload = await fetchJson(urls.remote_key, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key }),
      });
      setRemote(payload.remote || null);
    } catch (error) {
      addToast(error.message, "error");
    } finally {
      window.setTimeout(() => setBusyKey(""), 140);
    }
  };

  const handleRemoteText = async (submit = true) => {
    if (!urls.remote_text) return;
    if (!textEntryDraft.length) {
      addToast("Enter text first.", "error");
      textEntryInputRef.current?.focus();
      return;
    }
    setTextEntryBusy(true);
    try {
      const payload = await fetchJson(urls.remote_text, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textEntryDraft, submit }),
      });
      setRemote(payload.remote || null);
      addToast(payload.message || "TV text sent.");
      setTextEntryDraft("");
      if (submit) {
        setTextEntryOpen(false);
        textEntryInputRef.current?.blur();
      }
    } catch (error) {
      addToast(error.message, "error");
    } finally {
      setTextEntryBusy(false);
    }
  };

  const handleRemoteSave = async (event) => {
    event.preventDefault();
    try {
      const payload = await fetchJson(urls.remote_config, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          host: remoteForm.host,
          display_name: remoteForm.display_name,
          vendor: "samsung",
          port: remoteForm.port ? Number(remoteForm.port) : undefined,
        }),
      });
      setRemote(payload.remote || null);
      addToast(payload.message || "Saved TV remote target.");
    } catch (error) {
      addToast(error.message, "error");
    }
  };

  const handleWifiScan = async () => {
    try {
      const payload = await fetchJson(urls.wifi_scan, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ country: wifiForm.country.trim().toUpperCase() }),
      });
      setWifi(payload.wifi || null);
      addToast("Refreshed nearby Wi-Fi networks.");
    } catch (error) {
      addToast(error.message, "error");
    }
  };

  const handleWifiSave = async (event) => {
    event.preventDefault();
    try {
      const payload = await fetchJson(urls.wifi_connect, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ssid: wifiForm.ssid,
          password: wifiForm.password,
          country: wifiForm.country.trim().toUpperCase(),
        }),
      });
      setWifi(payload.wifi || null);
      setWifiForm((current) => ({ ...current, password: "" }));
      addToast(payload.message || "Saved Wi-Fi uplink.");
    } catch (error) {
      addToast(error.message, "error");
    }
  };

  const dpadButton = (key, label, className) => (
    <button
      type="button"
      aria-label={key.charAt(0).toUpperCase() + key.slice(1)}
      onClick={(event) => {
        releaseTapFocus(event);
        triggerHaptic(10);
        handleRemoteKey(key);
      }}
      className={clsx(
        "absolute grid place-items-center rounded-full border border-white/10 bg-white/10 text-lg font-semibold text-white transition hover:bg-white/20 active:scale-95",
        busyKey === key && "bg-mint-400 text-slate-950",
        className,
      )}
    >
      {label}
    </button>
  );

  const panelProps = {
    layout,
    dashboard,
    state,
    providerName,
    conciseLocation,
    routeStatus,
    urls,
    specs,
    logs,
    wifi,
    remote,
    remoteForm,
    setRemoteForm,
    wifiForm,
    setWifiForm,
    handleRegion,
    handleDisconnect,
    handleProviderSelect,
    handleRemoteSave,
    handleWifiScan,
    handleWifiSave,
    refreshSpecs,
    refreshLogs,
    refreshRemote,
    addToast,
  };

  const renderPanel = () => {
    if (!activePanel) return null;
    return (
      <Suspense fallback={<PanelsFallback />}>
        {activePanel === "route" && <RoutePanel {...panelProps} onClose={() => setActivePanel("")} />}
        {activePanel === "tv" && <TvPanel layout={layout} network={network} remote={remote} onClose={() => setActivePanel("")} />}
        {activePanel === "logs" && <LogsPanel layout={layout} logs={logs} refreshLogs={refreshLogs} addToast={addToast} onClose={() => setActivePanel("")} />}
        {activePanel === "config" && <ConfigPanel {...panelProps} onClose={() => setActivePanel("")} />}
      </Suspense>
    );
  };

  return (
    <div
      className={clsx(
        "relative w-screen bg-[radial-gradient(circle_at_top,_rgba(26,84,161,0.35),_transparent_38%),linear-gradient(180deg,#09111a_0%,#05080d_100%)] text-white",
        layout.mobile ? "min-h-screen overflow-x-hidden overflow-y-auto" : "min-h-screen overflow-hidden",
      )}
      style={{ minHeight: "100dvh" }}
    >
      <Toasts toasts={toasts} />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom,_rgba(38,139,110,0.15),_transparent_32%)]" aria-hidden="true" />

      <div
        className={clsx(layout.mobile ? "relative" : "absolute left-1/2 top-1/2")}
        style={layout.mobile ? { width: `${layout.width}px`, height: `${layout.height}px` } : { width: `${layout.width}px`, height: `${layout.height}px`, transform: "translate(-50%, -50%)" }}
      >
        <div
          className={clsx(
            "remote-scale-shell relative origin-top-left",
            layout.mobile ? "rounded-none shadow-none" : "overflow-hidden rounded-[44px] shadow-shell",
          )}
          style={{ width: `${BASE_WIDTH}px`, height: `${BASE_HEIGHT}px`, transform: `scale(${layout.scale})` }}
        >
          <RemoteCanvas connected={Boolean(state.connected)} edgeToEdge={layout.mobile} />

           <div className="absolute inset-0 flex flex-col px-5 pb-[calc(1.5rem+env(safe-area-inset-bottom))] pt-[calc(1.5rem+env(safe-area-inset-top))]">
            <div className="flex items-center justify-between">
              <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-[0.68rem] uppercase tracking-[0.24em] text-white/55">OpenSpoofen</div>
              <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs font-semibold text-white/80">
                <ConnectionModeIcon className="h-4 w-4 text-brass-300" />
                {connectionMode.label}
              </div>
            </div>

            <div className="mt-5 grid grid-cols-4 gap-3">
              {[
                { key: "power", label: "Power", icon: CirclePower, tone: "bg-coral-500" },
                { panel: "tv", label: "TV", icon: Tv, tone: "bg-white/10" },
                { panel: "logs", label: "Logs", icon: Logs, tone: "bg-white/10" },
                { panel: "config", label: "Config", icon: Settings2, tone: "bg-white/10" },
              ].map((item) => {
                const Icon = item.icon;
                const isPanel = Boolean(item.panel);
                return (
                  <m.button
                    key={item.label}
                    whileTap={{ scale: 0.96 }}
                    type="button"
                    onClick={(event) => {
                      releaseTapFocus(event);
                      triggerHaptic(10);
                      if (isPanel) { handlePanel(item.panel); return; }
                      handleRemoteKey(item.key);
                    }}
                    className={clsx("rounded-[22px] border border-white/10 px-3 py-3 text-left text-white shadow-screen transition", item.tone, activePanel === item.panel && "ring-2 ring-mint-300/70")}
                  >
                    <Icon className="h-5 w-5" />
                    <div className="mt-3 text-[0.72rem] font-semibold uppercase tracking-[0.18em] text-white/70">{item.label}</div>
                  </m.button>
                );
              })}
            </div>

            <m.button
              whileTap={{ scale: 0.985 }}
              type="button"
              onClick={(event) => {
                releaseTapFocus(event);
                triggerHaptic(12);
                handlePanel("route");
              }}
              className="mt-5 flex items-center gap-4 rounded-[30px] border border-white/10 bg-[linear-gradient(135deg,rgba(13,88,138,0.92),rgba(26,54,94,0.86))] px-5 py-5 text-left shadow-screen transition hover:bg-white/10"
            >
              <div className="grid h-16 w-16 place-items-center rounded-2xl bg-white/10">
                <ProviderGlyph providerName={providerName} />
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-[0.72rem] uppercase tracking-[0.2em] text-white/50">{providerName}</div>
                <div className="mt-1 truncate font-display text-[1.6rem] font-semibold leading-tight text-white">{conciseLocation}</div>
                <div className="mt-1 truncate text-sm text-white/60">{routeStatus.availability} • {routeStatus.tunnel}</div>
              </div>
              <ChevronRight className="h-6 w-6 text-white/55" />
            </m.button>

            <div className="mt-5 flex items-center justify-between rounded-[26px] border border-white/10 bg-black/20 px-4 py-3 text-sm text-white/65">
              <div className="flex items-center gap-2"><Cable className="h-4 w-4 text-brass-300" /> {network.tv_status || "TV status unavailable"}</div>
              <div className="flex items-center gap-2">{state.connected ? <ShieldCheck className="h-4 w-4 text-mint-300" /> : routeStatus.availability === "Available" ? <ShieldCheck className="h-4 w-4 text-mint-300" /> : <ShieldCheck className="h-4 w-4 text-coral-400" />} {state.connected ? "VPN connected" : routeStatus.availability === "Available" ? "Provider ready" : routeStatus.summary.length > 50 ? "Provider unavailable" : routeStatus.summary}</div>
            </div>

            <div className="mt-4 flex items-center gap-3">
              <button
                type="button"
                onClick={(event) => {
                  releaseTapFocus(event);
                  triggerHaptic(10);
                  if (!textEntryOpen) { setTextEntryOpen(true); return; }
                  textEntryInputRef.current?.focus();
                }}
                disabled={!remote?.ready || !urls.remote_text}
                className={clsx(
                  "flex min-w-0 flex-1 items-center gap-3 rounded-[22px] border px-4 py-3 text-left transition",
                  remote?.ready && urls.remote_text ? "border-white/10 bg-white/8 text-white hover:bg-white/12" : "cursor-not-allowed border-white/10 bg-black/20 text-white/35",
                )}
              >
                <div className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-brass-400/15 text-brass-300"><Keyboard className="h-5 w-5" /></div>
                <div className="min-w-0">
                  <div className="text-[0.72rem] uppercase tracking-[0.18em] text-white/45">Type on TV</div>
                  <div className="mt-1 truncate text-sm font-semibold text-white">{remote?.ready ? "Use the phone keyboard for search or sign-in fields" : "TV text entry becomes available when the remote is ready"}</div>
                </div>
              </button>
              {textEntryOpen ? (
                <button type="button" onClick={(event) => { releaseTapFocus(event); triggerHaptic(8); setTextEntryOpen(false); setTextEntryDraft(""); textEntryInputRef.current?.blur(); }} className="grid h-[58px] w-[58px] shrink-0 place-items-center rounded-[22px] border border-white/10 bg-black/20 text-white transition hover:bg-white/10" aria-label="Close TV typing panel">
                  <X className="h-5 w-5" />
                </button>
              ) : null}
            </div>

            <div className="mt-6 flex items-center justify-between">
              <div className="flex w-[88px] flex-col gap-3">
                <button type="button" aria-label="Volume up" onClick={(event) => { releaseTapFocus(event); triggerHaptic(10); handleRemoteKey("volume_up"); }} className={clsx("grid h-[72px] place-items-center rounded-[26px] border border-white/10 bg-white/10 text-white transition hover:bg-white/20", busyKey === "volume_up" && "bg-mint-400 text-slate-950")}><Plus className="h-6 w-6" /><span className="text-[0.7rem] uppercase tracking-[0.2em]">Vol</span></button>
                <button type="button" aria-label="Volume down" onClick={(event) => { releaseTapFocus(event); triggerHaptic(10); handleRemoteKey("volume_down"); }} className={clsx("grid h-[72px] place-items-center rounded-[26px] border border-white/10 bg-white/10 text-white transition hover:bg-white/20", busyKey === "volume_down" && "bg-mint-400 text-slate-950")}><Minus className="h-6 w-6" /><span className="text-[0.7rem] uppercase tracking-[0.2em]">Vol</span></button>
              </div>

              <div className="relative h-[254px] w-[254px] rounded-full border border-white/10 bg-white/5 shadow-screen">
                {dpadButton("up", "▲", "left-1/2 top-4 h-16 w-16 -translate-x-1/2")}
                {dpadButton("left", "◀", "left-4 top-1/2 h-16 w-16 -translate-y-1/2")}
                {dpadButton("right", "▶", "right-4 top-1/2 h-16 w-16 -translate-y-1/2")}
                {dpadButton("down", "▼", "bottom-4 left-1/2 h-16 w-16 -translate-x-1/2")}
                <button type="button" onClick={(event) => { releaseTapFocus(event); triggerHaptic(12); handleRemoteKey("ok"); }} className={clsx("absolute left-1/2 top-1/2 grid h-24 w-24 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full border border-brass-300/40 bg-brass-400/80 font-display text-xl font-semibold text-slate-950 shadow-screen transition hover:bg-brass-300", busyKey === "ok" && "scale-95")}>OK</button>
              </div>

              <div className="flex w-[88px] flex-col gap-3">
                <button type="button" aria-label="Channel up" onClick={(event) => { releaseTapFocus(event); triggerHaptic(10); handleRemoteKey("channel_up"); }} className={clsx("grid h-[72px] place-items-center rounded-[26px] border border-white/10 bg-white/10 text-white transition hover:bg-white/20", busyKey === "channel_up" && "bg-mint-400 text-slate-950")}><Plus className="h-6 w-6" /><span className="text-[0.7rem] uppercase tracking-[0.2em]">Ch</span></button>
                <button type="button" aria-label="Channel down" onClick={(event) => { releaseTapFocus(event); triggerHaptic(10); handleRemoteKey("channel_down"); }} className={clsx("grid h-[72px] place-items-center rounded-[26px] border border-white/10 bg-white/10 text-white transition hover:bg-white/20", busyKey === "channel_down" && "bg-mint-400 text-slate-950")}><Minus className="h-6 w-6" /><span className="text-[0.7rem] uppercase tracking-[0.2em]">Ch</span></button>
              </div>
            </div>

            <div className="mt-8 grid grid-cols-4 gap-3">
              {[
                { key: "back", label: "Back", icon: ArrowLeft },
                { key: "home", label: "Home", icon: Home },
                { key: "exit", label: "Exit", icon: ExternalLink },
                { key: "source", label: "Source", icon: MonitorSmartphone },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <button key={item.key} type="button" onClick={(event) => { releaseTapFocus(event); triggerHaptic(10); handleRemoteKey(item.key); }} className={clsx("grid h-[74px] place-items-center rounded-[24px] border border-white/10 bg-black/20 text-white transition hover:bg-white/10", busyKey === item.key && "bg-mint-400 text-slate-950")}>
                    <Icon className="h-5 w-5" />
                    <span className="mt-2 text-[0.68rem] uppercase tracking-[0.2em]">{item.label}</span>
                  </button>
                );
              })}
            </div>

            <div className="mt-auto grid grid-cols-4 gap-3 pt-5">
              {[
                { key: "rewind", label: "Rew", icon: SkipBack },
                { key: "play_pause", label: "Play", icon: Play },
                { key: "fast_forward", label: "Fwd", icon: FastForward },
                { key: "mute", label: "Mute", icon: Volume2 },
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <button key={item.key} type="button" onClick={(event) => { releaseTapFocus(event); triggerHaptic(10); handleRemoteKey(item.key); }} className={clsx("grid h-[82px] place-items-center rounded-[26px] border border-white/10 bg-white/10 text-white transition hover:bg-white/20", item.key === "play_pause" && "bg-mint-400 text-slate-950", busyKey === item.key && "scale-95")}>
                    <Icon className="h-5 w-5" />
                    <span className="mt-2 text-[0.68rem] uppercase tracking-[0.2em]">{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <AnimatePresence>
            {textEntryOpen ? (
              <m.form
                initial={{ opacity: 0, y: 32 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 24 }}
                transition={{ type: "spring", stiffness: 240, damping: 28 }}
                onSubmit={(event) => { event.preventDefault(); handleRemoteText(true); }}
                className={clsx(
                  "absolute inset-x-4 bottom-24 z-20 rounded-[28px] border border-white/10 bg-[#0c1621f2] p-4 shadow-shell backdrop-blur-2xl",
                  layout.mobile ? "pb-[calc(1rem+env(safe-area-inset-bottom))]" : null,
                )}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-[0.72rem] uppercase tracking-[0.22em] text-brass-300">TV keyboard</div>
                    <h3 className="mt-1 font-display text-lg font-semibold text-white">Send text from this phone</h3>
                    <p className="mt-1 text-sm text-white/55">Open a search or sign-in field on the TV first, then type here.</p>
                  </div>
                </div>
                <input ref={textEntryInputRef} value={textEntryDraft} onChange={(event) => setTextEntryDraft(event.target.value)} aria-label="Text to type on the TV" enterKeyHint="send" autoCapitalize="none" autoCorrect="off" spellCheck={false} className="mt-4 w-full rounded-[20px] border border-white/10 bg-black/25 px-4 py-3 text-base text-white outline-none placeholder:text-white/35" placeholder="Type to the current TV input field" />
                <div className="mt-3 flex gap-3">
                  <button type="submit" disabled={textEntryBusy} className="flex-1 rounded-[18px] bg-mint-400 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-mint-300 disabled:cursor-wait disabled:opacity-70">{textEntryBusy ? "Sending..." : "Send text"}</button>
                  <button type="button" onClick={(event) => { releaseTapFocus(event); triggerHaptic(8); setTextEntryDraft(""); textEntryInputRef.current?.focus(); }} className="rounded-[18px] border border-white/10 bg-black/20 px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/10">Clear</button>
                </div>
              </m.form>
            ) : null}
          </AnimatePresence>

          <AnimatePresence>{renderPanel()}</AnimatePresence>
        </div>
      </div>
    </div>
  );
}

const mountNode = document.getElementById("remote-app");
if (mountNode) {
  createRoot(mountNode).render(
    <LazyMotion features={domAnimation} strict>
      <App />
    </LazyMotion>,
  );
}
