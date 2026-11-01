import clsx from "clsx";

export function SectionCard({ title, subtitle, children, action }) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-white/5 p-4 shadow-screen backdrop-blur-xl">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <h3 className="font-display text-[0.92rem] uppercase tracking-[0.22em] text-white/70">{title}</h3>
          {subtitle ? <p className="mt-1 text-sm text-white/55">{subtitle}</p> : null}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

export function InfoGrid({ items }) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {items.map((item) => (
        <div key={item.label} className={clsx("min-w-0 rounded-[22px] border border-white/10 bg-black/20 p-3", item.fullWidth && "col-span-2")}>
          <div className="text-[0.7rem] uppercase tracking-[0.22em] text-white/45">{item.label}</div>
          <div className={clsx("mt-2 min-w-0 text-sm font-semibold text-white", item.valueClassName)} title={typeof item.value === "string" ? item.value : undefined}>
            {item.value}
          </div>
          {item.meta ? <div className="mt-1 text-xs text-white/45">{item.meta}</div> : null}
        </div>
      ))}
    </div>
  );
}
