import clsx from "clsx";
import { AnimatePresence, m } from "framer-motion";

export default function Toasts({ toasts }) {
  return (
    <div className="pointer-events-none absolute inset-x-0 top-3 z-50 flex flex-col items-center gap-2 px-4">
      <AnimatePresence>
        {toasts.map((toast) => (
          <m.div
            key={toast.id}
            role="status"
            initial={{ opacity: 0, y: -16, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -12, scale: 0.96 }}
            className={clsx(
              "max-w-[18rem] rounded-full border px-4 py-2 text-center text-sm font-semibold shadow-lg backdrop-blur-lg",
              toast.category === "error"
                ? "border-coral-400/50 bg-coral-500/85 text-white"
                : "border-mint-300/50 bg-mint-500/80 text-slate-950",
            )}
          >
            {toast.message}
          </m.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
