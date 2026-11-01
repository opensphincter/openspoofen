import { isNordProvider, providerMark } from "../lib/utils";

export default function ProviderGlyph({ providerName }) {
  if (isNordProvider(providerName)) {
    return (
      <svg viewBox="0 0 64 64" className="h-10 w-10 text-brass-300" aria-hidden="true">
        <circle cx="32" cy="32" r="30" fill="currentColor" opacity="0.12" />
        <path d="M10 43.5 23.5 24l8.2 12.5L41.6 21 54 43.5H10Z" fill="currentColor" />
        <path d="M21 43.5 31.8 27.8 42.7 43.5H21Z" fill="#f7fbff" opacity="0.92" />
      </svg>
    );
  }
  return <span className="font-display text-2xl font-semibold text-brass-300">{providerMark(providerName)}</span>;
}
