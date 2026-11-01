import { SectionCard, InfoGrid } from "../components/Overlay";
import { formatDateish, formatTvModel } from "../lib/utils";

function OverlayFrame({ title, subtitle, onClose, children, mobile = false }) {
  return (
    <section
      className={`absolute inset-0 z-30 flex flex-col border border-white/10 bg-[#09111bcc] backdrop-blur-2xl ${mobile ? "rounded-none" : "rounded-[44px]"}`}
      style={{ paddingTop: "calc(1.25rem + env(safe-area-inset-top))", paddingBottom: "calc(1.25rem + env(safe-area-inset-bottom))", paddingLeft: "1.25rem", paddingRight: "1.25rem" }}
    >
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <div className="text-[0.72rem] uppercase tracking-[0.26em] text-brass-300">OpenSpoofen</div>
          <h2 className="mt-2 font-display text-2xl font-semibold text-white">{title}</h2>
          <p className="mt-1 max-w-[18rem] text-sm text-white/60">{subtitle}</p>
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
      <div className="remote-panel-scroll min-h-0 flex-1 overflow-y-auto pr-1">{children}</div>
    </section>
  );
}

export default function TvPanel({ layout, network, remote, onClose }) {
  return (
    <OverlayFrame title="TV diagnostics" subtitle="Everything that should have been cluttering the home screen now lives here." onClose={onClose} mobile={layout.mobile}>
      <div className="space-y-4">
        <SectionCard title="Connectivity" subtitle={network.tv_status_detail || "Downstream diagnostics are not yet available."}>
          <InfoGrid
            items={[
              { label: "Status", value: network.tv_status || "Unknown" },
              { label: "Neighbor", value: network.tv_connectivity?.neighbor_state || "No neighbor" },
              { label: "Lease host", value: network.tv_connectivity?.hostname || "Unknown client" },
              { label: "Lease IP", value: network.tv_connectivity?.address || "Not leased" },
              { label: "MAC", value: network.tv_connectivity?.mac || "Unseen" },
              { label: "Lease expiry", value: formatDateish(network.tv_connectivity?.lease_expires_at) },
              { label: "Model", value: formatTvModel(network.tv_connectivity) },
              { label: "VPN path", value: network.tv_connectivity?.vpn_path_hint || "No route hint available" },
            ]}
          />
        </SectionCard>

        <SectionCard title="Remote target" subtitle={remote?.status_summary || "Remote pairing state unavailable."}>
          <InfoGrid
            items={[
              { label: "Host", value: remote?.effective_host || remote?.host || remote?.candidate_host || "Not configured" },
              { label: "Display name", value: remote?.display_name || "OpenSpoofen Remote" },
              { label: "Token", value: remote?.token_cached ? "Cached" : "Pending" },
              { label: "Mode", value: remote?.auto_detected ? "Auto-detected" : remote?.configured ? "Saved" : "Unset" },
              { label: "Neighbor seen", value: network.tv_connectivity?.live_neighbor ? "Live link" : "Not live" },
            ]}
          />
        </SectionCard>
      </div>
    </OverlayFrame>
  );
}
