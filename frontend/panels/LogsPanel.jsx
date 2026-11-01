import { SectionCard } from "../components/Overlay";
import { formatDateish } from "../lib/utils";

export default function LogsPanel({ layout, logs, refreshLogs, addToast, onClose }) {
  const handleRefresh = (event) => {
    if (event?.currentTarget && event.currentTarget instanceof HTMLElement) {
      window.requestAnimationFrame(() => event.currentTarget.blur());
    }
    if (typeof navigator !== "undefined" && typeof navigator.vibrate === "function") {
      navigator.vibrate(10);
    }
    refreshLogs().catch((error) => addToast(error.message, "error"));
  };

  return (
    <section
      className={`absolute inset-0 z-30 flex flex-col border border-white/10 bg-[#09111bcc] backdrop-blur-2xl ${layout.mobile ? "rounded-none" : "rounded-[44px]"}`}
      style={{ paddingTop: "calc(1.25rem + env(safe-area-inset-top))", paddingBottom: "calc(1.25rem + env(safe-area-inset-bottom))", paddingLeft: "1.25rem", paddingRight: "1.25rem" }}
    >
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <div className="text-[0.72rem] uppercase tracking-[0.26em] text-brass-300">OpenSpoofen</div>
          <h2 className="mt-2 font-display text-2xl font-semibold text-white">Appliance logs</h2>
          <p className="mt-1 max-w-[18rem] text-sm text-white/60">Recent service logs in one scrollable pane.</p>
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
          <SectionCard
            title="Log stream"
            subtitle="Refresh whenever the TV or VPN path is misbehaving."
            action={
              <button type="button" onClick={handleRefresh} className="rounded-full border border-white/10 px-4 py-2 text-xs font-semibold text-white/70 transition hover:bg-white/10">Refresh</button>
            }
          >
            <div className="space-y-3">
              {(logs?.services || []).map((service) => (
                <div key={service.name} className="rounded-[22px] border border-white/10 bg-black/30 p-4">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div className="font-display text-lg font-semibold text-white">{service.label || service.name}</div>
                    <div className="text-xs uppercase tracking-[0.18em] text-white/40">{logs?.generated_at ? formatDateish(logs.generated_at) : "now"}</div>
                  </div>
                  <pre className="whitespace-pre-wrap break-words text-xs leading-5 text-white/70">{(service.lines || []).join("\n") || "No log lines available."}</pre>
                </div>
              ))}
              {!logs?.services?.length ? <div className="rounded-[22px] border border-dashed border-white/10 bg-black/20 p-4 text-sm text-white/55">No appliance logs loaded yet.</div> : null}
            </div>
          </SectionCard>
        </div>
      </div>
    </section>
  );
}
