import clsx from "clsx";
import { ExternalLink, LogOut, Wifi } from "lucide-react";
import { SectionCard, InfoGrid } from "../components/Overlay";
import { releaseTapFocus, triggerHaptic } from "../lib/utils";

export default function ConfigPanel({
  layout,
  dashboard,
  urls,
  specs,
  wifi,
  remote,
  remoteForm,
  setRemoteForm,
  wifiForm,
  setWifiForm,
  handleRemoteSave,
  handleWifiScan,
  handleWifiSave,
  refreshSpecs,
  addToast,
  onClose,
}) {
  const network = dashboard.network || {};

  const handleSpecsRefresh = (event) => {
    releaseTapFocus(event);
    triggerHaptic(10);
    refreshSpecs().catch((error) => addToast(error.message, "error"));
  };

  const handleWifiRefresh = (event) => {
    releaseTapFocus(event);
    triggerHaptic(10);
    handleWifiScan();
  };

  return (
    <section
      className={`absolute inset-0 z-30 flex flex-col border border-white/10 bg-[#09111bcc] backdrop-blur-2xl ${layout.mobile ? "rounded-none" : "rounded-[44px]"}`}
      style={{ paddingTop: "calc(1.25rem + env(safe-area-inset-top))", paddingBottom: "calc(1.25rem + env(safe-area-inset-bottom))", paddingLeft: "1.25rem", paddingRight: "1.25rem" }}
    >
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <div className="text-[0.72rem] uppercase tracking-[0.26em] text-brass-300">OpenSpoofen</div>
          <h2 className="mt-2 font-display text-2xl font-semibold text-white">Config and control</h2>
          <p className="mt-1 max-w-[18rem] text-sm text-white/60">Provider auth, Wi-Fi uplink, remote target, access details, and appliance specs live here.</p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="grid h-11 w-11 place-items-center rounded-full border border-white/10 bg-white/5 text-white transition hover:bg-white/10"
          aria-label="Close overlay"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
        </button>
      </div>
      <div className="remote-panel-scroll min-h-0 flex-1 overflow-y-auto pr-1">
        <div className="space-y-4">
          <SectionCard title="Access" subtitle="LAN session and local endpoints.">
            <InfoGrid
              items={[
                { label: "Sign-in", value: dashboard.access?.require_pairing_token ? "Password + pairing" : "Password only" },
                { label: "Session", value: `${dashboard.access?.session_persist_days || 30} days` },
                { label: "Direct URL", value: dashboard.access?.device_origin || window.location.origin, fullWidth: true, valueClassName: "info-value-clip" },
                { label: "mDNS", value: dashboard.access?.mdns_origin || "Unavailable", fullWidth: true, valueClassName: "info-value-clip" },
              ]}
            />
          </SectionCard>

          <SectionCard title="TV remote target" subtitle={remote?.status_summary || "Set the target TV IP and display name."}>
            <form className="grid gap-3" onSubmit={handleRemoteSave}>
              <input
                value={remoteForm.host}
                onChange={(event) => setRemoteForm((current) => ({ ...current, host: event.target.value }))}
                className="rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35"
                placeholder="TV IP or hostname"
                aria-label="TV IP or hostname"
                name="host"
              />
              <div className="grid grid-cols-[1fr,108px] gap-3">
                <input
                  value={remoteForm.display_name}
                  onChange={(event) => setRemoteForm((current) => ({ ...current, display_name: event.target.value }))}
                  className="rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35"
                  placeholder="Remote display name"
                  aria-label="Remote display name"
                  name="display_name"
                />
                <input
                  value={remoteForm.port}
                  onChange={(event) => setRemoteForm((current) => ({ ...current, port: event.target.value }))}
                  className="rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35"
                  placeholder="Port"
                  aria-label="Remote port"
                  name="port"
                />
              </div>
              <button type="submit" className="rounded-[18px] bg-mint-400 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-mint-300">Save TV target</button>
            </form>
          </SectionCard>

          <SectionCard
            title="Wi-Fi uplink"
            subtitle={wifi?.error || "Keep this here for wireless fallback or alternate bench setups."}
            action={<button type="button" onClick={handleWifiRefresh} className="rounded-full border border-white/10 px-4 py-2 text-xs font-semibold text-white/70 transition hover:bg-white/10">Scan</button>}
          >
            <form className="grid gap-3" onSubmit={handleWifiSave}>
              <div className="grid grid-cols-[1fr,100px] gap-3">
                <input
                  value={wifiForm.ssid}
                  onChange={(event) => setWifiForm((current) => ({ ...current, ssid: event.target.value }))}
                  className="rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35"
                  placeholder="SSID"
                  aria-label="Wi-Fi network name (SSID)"
                />
                <input
                  value={wifiForm.country}
                  onChange={(event) => setWifiForm((current) => ({ ...current, country: event.target.value }))}
                  className="rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm uppercase text-white outline-none placeholder:text-white/35"
                  placeholder="US"
                  aria-label="Wi-Fi country code"
                />
              </div>
              <input
                type="password"
                value={wifiForm.password}
                onChange={(event) => setWifiForm((current) => ({ ...current, password: event.target.value }))}
                className="rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35"
                placeholder="Wi-Fi password"
                aria-label="Wi-Fi password"
              />
              <button type="submit" className="rounded-[18px] bg-white/90 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-white">Save uplink</button>
            </form>
            <div className="mt-4 grid gap-2">
              {(wifi?.networks || []).map((networkItem) => (
                <button
                  type="button"
                  key={networkItem.ssid}
                  onClick={() => setWifiForm((current) => ({ ...current, ssid: networkItem.ssid }))}
                  className={clsx(
                    "rounded-[18px] border px-4 py-3 text-left transition",
                    wifiForm.ssid === networkItem.ssid
                      ? "border-brass-300/70 bg-brass-400/15 text-white"
                      : "border-white/10 bg-black/20 text-white/70 hover:bg-white/10",
                  )}
                >
                  <div className="font-semibold">{networkItem.ssid}</div>
                  <div className="mt-1 text-xs text-white/45">{networkItem.signal}% • {networkItem.security || "Open"}{networkItem.saved ? " • saved" : ""}{networkItem.active ? " • active" : ""}</div>
                </button>
              ))}
            </div>
          </SectionCard>

          <SectionCard
            title="Appliance specs"
            subtitle="Live hardware, route, and service state from the Pi."
            action={<button type="button" onClick={handleSpecsRefresh} className="rounded-full border border-white/10 px-4 py-2 text-xs font-semibold text-white/70 transition hover:bg-white/10">Refresh</button>}
          >
            <InfoGrid
              items={[
                { label: "Topology", value: specs?.preferred_topology || network.preferred_topology || "Unknown" },
                { label: "Provider", value: specs?.default_provider || dashboard.provider || "Unknown" },
                { label: "Upstream", value: specs?.upstream_interface || network.upstream_interface?.name || "Unknown" },
                { label: "Downstream", value: specs?.downstream_interface || network.downstream_interface?.name || "Unknown" },
                { label: "Default route", value: specs?.default_route || network.default_route || "Unavailable", fullWidth: true, valueClassName: "info-value-clip" },
                { label: "DNS", value: (specs?.dns_servers || network.dns_servers || []).join(", ") || "Unavailable", fullWidth: true, valueClassName: "info-value-clip" },
              ]}
            />
          </SectionCard>

          {dashboard.show_provider_login && dashboard.provider_metadata?.auth_fields?.length ? (
            <SectionCard title="Provider auth" subtitle={`Authenticate ${dashboard.provider_metadata.provider_name} from inside the remote overlay.`}>
              <form method="post" action={urls.provider_login} className="grid gap-3">
                <input type="hidden" name="provider" value={dashboard.provider} />
                {dashboard.provider_metadata.auth_fields.map((field) => (
                  <label key={field.key} className="grid gap-2 text-sm text-white/70">
                    {field.label}
                    <input
                      name={field.key}
                      type={field.secret ? "password" : "text"}
                      placeholder={field.placeholder}
                      className="rounded-[18px] border border-white/10 bg-black/25 px-4 py-3 text-sm text-white outline-none placeholder:text-white/35"
                    />
                    {field.help_text ? <span className="text-xs text-white/45">{field.help_text}</span> : null}
                  </label>
                ))}
                <button type="submit" className="rounded-[18px] bg-brass-400 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-brass-300">Authenticate provider</button>
              </form>
            </SectionCard>
          ) : null}

          {dashboard.provider_auth_summary && !dashboard.show_provider_login ? (
            <SectionCard title="Provider auth" subtitle="Authentication is already stored on the appliance for this backend.">
              <div className="rounded-[22px] border border-mint-300/30 bg-mint-400/12 p-4 text-sm font-medium text-white">
                {dashboard.provider_auth_summary}
              </div>
            </SectionCard>
          ) : null}

          <SectionCard title="Session" subtitle="Leave the appliance cleanly or jump back out to the LAN address.">
            <div className="flex gap-3">
              <a href={dashboard.access?.device_origin || window.location.origin} className="inline-flex flex-1 items-center justify-center gap-2 rounded-[18px] border border-white/10 bg-black/20 px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/10">
                <ExternalLink className="h-4 w-4" /> Open direct URL
              </a>
              <form method="post" action={urls.logout} className="flex-1">
                <button type="submit" className="inline-flex w-full items-center justify-center gap-2 rounded-[18px] border border-white/10 bg-coral-500 px-4 py-3 text-sm font-semibold text-white transition hover:bg-coral-400">
                  <LogOut className="h-4 w-4" /> Sign out
                </button>
              </form>
            </div>
          </SectionCard>
        </div>
      </div>
    </section>
  );
}
