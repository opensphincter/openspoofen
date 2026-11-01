import { useMemo, useState } from "react";
import clsx from "clsx";
import { AnimatePresence, m } from "framer-motion";
import { ChevronRight, MapPinned, Search, X } from "lucide-react";
import { SectionCard, InfoGrid } from "../components/Overlay";
import { triggerHaptic, releaseTapFocus } from "../lib/utils";

function ProviderBackendButton({ provider, isActive, onClick }) {
  return (
    <button
      type="button"
      onClick={() => onClick(provider.provider_id)}
      className={clsx(
        "rounded-[22px] border px-4 py-4 text-left transition",
        isActive
          ? "border-mint-300/70 bg-mint-400/20 text-white"
          : "border-white/10 bg-white/5 text-white/80 hover:bg-white/10",
      )}
    >
      <div className="text-[0.72rem] uppercase tracking-[0.18em] text-white/45">{provider.provider_id}</div>
      <div className="mt-2 font-display text-lg font-semibold">{provider.provider_name}</div>
    </button>
  );
}

function RegionPickerSheet({ locations, currentLabel, onSelect, onClose }) {
  const [query, setQuery] = useState("");
  const normalizedQuery = query.trim().toLowerCase();
  const filteredLocations = useMemo(() => {
    if (!normalizedQuery) return locations;
    return locations.filter((location) => {
      const haystack = [location.label, location.country, location.city || ""].join(" ").toLowerCase();
      return haystack.includes(normalizedQuery);
    });
  }, [locations, normalizedQuery]);

  return (
    <m.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="absolute inset-0 z-40 flex items-end bg-black/45"
      onClick={onClose}
    >
      <m.section
        initial={{ y: 48, opacity: 0.96 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 48, opacity: 0.96 }}
        transition={{ type: "spring", stiffness: 240, damping: 30 }}
        className="w-full rounded-t-[34px] border border-white/10 bg-[#0d1722] p-5 shadow-shell"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mx-auto mb-4 h-1.5 w-12 rounded-full bg-white/15" aria-hidden="true" />
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <div className="text-[0.72rem] uppercase tracking-[0.22em] text-white/45">Regions</div>
            <h3 className="mt-1 font-display text-xl font-semibold text-white">Choose route</h3>
          </div>
          <button
            type="button"
            onClick={(event) => {
              releaseTapFocus(event);
              triggerHaptic(8);
              onClose();
            }}
            className="grid h-11 w-11 place-items-center rounded-full border border-white/10 bg-white/5 text-white transition hover:bg-white/10"
            aria-label="Close region chooser"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <label className="mb-4 flex items-center gap-3 rounded-[22px] border border-white/10 bg-black/20 px-4 py-3 text-white/80">
          <Search className="h-4 w-4 shrink-0 text-white/45" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            autoCapitalize="none"
            autoCorrect="off"
            spellCheck={false}
            className="w-full bg-transparent text-sm text-white outline-none placeholder:text-white/35"
            placeholder="Search country or city"
          />
        </label>
        <div className="mb-3 flex items-center justify-between gap-3 text-xs uppercase tracking-[0.18em] text-white/40">
          <span>{filteredLocations.length} routes</span>
          {normalizedQuery ? <span>Filtered</span> : <span>All regions</span>}
        </div>
        <div className="remote-panel-scroll max-h-[52vh] space-y-2 overflow-y-auto pr-1">
          {filteredLocations.map((location) => {
            const selected = currentLabel === location.label;
            return (
              <button
                key={`${location.country}-${location.city || "best"}`}
                type="button"
                onClick={(event) => {
                  releaseTapFocus(event);
                  triggerHaptic(12);
                  onSelect(location);
                }}
                className={clsx(
                  "w-full rounded-[22px] border px-4 py-4 text-left transition",
                  selected
                    ? "border-brass-300/80 bg-brass-400/15 text-white"
                    : "border-white/10 bg-black/20 text-white/80 hover:bg-white/10",
                )}
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-base font-semibold">{location.label}</div>
                    <div className="mt-1 text-xs uppercase tracking-[0.18em] text-white/45">Tap to route the TV here</div>
                  </div>
                  <ChevronRight className="h-5 w-5 shrink-0 text-white/45" />
                </div>
              </button>
            );
          })}
          {!filteredLocations.length ? (
            <div className="rounded-[22px] border border-dashed border-white/10 bg-black/20 px-4 py-5 text-sm text-white/55">
              No matching routes. Search by country, city, or the label shown in the picker.
            </div>
          ) : null}
        </div>
      </m.section>
    </m.div>
  );
}

function OverlayFrame({ title, subtitle, onClose, children, mobile = false }) {
  return (
    <m.section
      key={title}
      initial={{ opacity: 0, x: 24 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 18 }}
      transition={{ type: "spring", stiffness: 240, damping: 28 }}
        className={clsx(
          "absolute inset-0 z-30 flex flex-col border border-white/10 bg-[#09111bcc] backdrop-blur-2xl",
          mobile ? "rounded-none" : "rounded-[44px]",
        )}
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
          <X className="h-5 w-5" />
        </button>
      </div>
      <div className="remote-panel-scroll min-h-0 flex-1 overflow-y-auto pr-1">{children}</div>
    </m.section>
  );
}

export default function RoutePanel({
  layout,
  dashboard,
  state,
  providerName,
  conciseLocation,
  routeStatus,
  urls,
  handleRegion,
  handleDisconnect,
  handleProviderSelect,
}) {
  const [showRegionSheet, setShowRegionSheet] = useState(false);

  return (
    <OverlayFrame title="Route control" subtitle="Switch provider backends or jump TV traffic into a new region without leaving the remote." onClose={() => {}} mobile={layout.mobile}>
      <div className="space-y-4">
        <SectionCard
          title="Current route"
          subtitle={routeStatus.summary}
          action={
            <button
              type="button"
              onClick={(event) => {
                releaseTapFocus(event);
                triggerHaptic(10);
                handleDisconnect();
              }}
              className="rounded-full border border-white/10 px-4 py-2 text-xs font-semibold text-white/70 transition hover:bg-white/10"
            >
              Disconnect
            </button>
          }
        >
          <InfoGrid
            items={[
              { label: "Provider", value: providerName },
              { label: "Region", value: conciseLocation },
              { label: "Public IP", value: state.public_ip || "Pending provider probe" },
              { label: "Available", value: routeStatus.availability },
              { label: "VPN tunnel", value: routeStatus.tunnel },
            ]}
          />
        </SectionCard>

        <SectionCard title="Provider backends" subtitle="No dropdowns here. Tap the backend you want this remote to drive.">
          <div className="grid grid-cols-2 gap-3">
            {(dashboard.available_providers || []).map((provider) => (
              <ProviderBackendButton
                key={provider.provider_id}
                provider={provider}
                isActive={provider.provider_id === dashboard.provider}
                onClick={handleProviderSelect}
              />
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Region" subtitle="Tap the region widget to open a compact route chooser.">
          <button
            type="button"
            onClick={(event) => {
              releaseTapFocus(event);
              triggerHaptic(10);
              setShowRegionSheet(true);
            }}
            className="flex w-full items-center gap-4 rounded-[24px] border border-white/10 bg-black/20 px-4 py-4 text-left text-white transition hover:bg-white/10"
          >
            <div className="grid h-12 w-12 place-items-center rounded-2xl bg-brass-400/15 text-brass-300">
              <MapPinned className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-[0.72rem] uppercase tracking-[0.18em] text-white/45">Current selection</div>
              <div className="mt-1 truncate text-lg font-semibold text-white">{conciseLocation}</div>
              <div className="mt-1 text-sm text-white/55">Open the route picker</div>
            </div>
            <ChevronRight className="h-5 w-5 shrink-0 text-white/45" />
          </button>
          {!dashboard.regions?.length ? <p className="mt-3 text-sm text-white/55">No region list is available for this backend yet.</p> : null}
        </SectionCard>
      </div>
      <AnimatePresence>
        {showRegionSheet && dashboard.regions?.length ? (
          <RegionPickerSheet
            locations={dashboard.regions}
            currentLabel={state.current_location?.label}
            onClose={() => setShowRegionSheet(false)}
            onSelect={(location) => {
              setShowRegionSheet(false);
              handleRegion(location);
            }}
          />
        ) : null}
      </AnimatePresence>
    </OverlayFrame>
  );
}
