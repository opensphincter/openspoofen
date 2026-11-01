export function releaseTapFocus(event) {
  if (!(event?.currentTarget instanceof HTMLElement)) {
    return;
  }
  window.requestAnimationFrame(() => {
    event.currentTarget.blur();
  });
}

export function triggerHaptic(pattern = 18) {
  if (typeof navigator === "undefined" || typeof navigator.vibrate !== "function") {
    return;
  }
  navigator.vibrate(pattern);
}

export function formatDateish(value) {
  if (!value) {
    return "Unavailable";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.valueOf())) {
    return String(value);
  }
  return parsed.toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function formatTvModel(connectivity) {
  if (connectivity?.exact_model) {
    return connectivity.exact_model;
  }
  if (connectivity?.vendor_hint) {
    return `${connectivity.vendor_hint} model unavailable`;
  }
  return "Model unavailable";
}

function normalizeProviderName(name) {
  return String(name || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

export function isNordProvider(name) {
  const normalized = normalizeProviderName(name);
  return normalized === "nordvpn" || normalized === "nord vpn" || normalized.startsWith("nord ");
}

export function providerMark(name) {
  const explicitMarks = {
    nordvpn: "NV",
    "nord vpn": "NV",
    "wireguard profiles": "WG",
    expressvpn: "EX",
    "express vpn": "EX",
    "proton vpn": "PV",
    "mock provider": "MK",
    mullvad: "MU",
    surfshark: "SS",
  };
  const normalized = normalizeProviderName(name);
  if (explicitMarks[normalized]) {
    return explicitMarks[normalized];
  }
  const words = String(name || "OpenSpoofen")
    .replace(/\//g, " ")
    .split(/\s+/)
    .filter(Boolean);
  if (!words.length) {
    return "OS";
  }
  if (words.length === 1) {
    return words[0][0].toUpperCase();
  }
  return words
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
}

export function getConnectionMode(topology, upstreamName) {
  const fingerprint = `${topology || ""} ${upstreamName || ""}`.toLowerCase();
  const isWifi = fingerprint.includes("wifi") || fingerprint.includes("wlan");
  return {
    icon: isWifi ? "wifi" : "cable",
    label: isWifi ? "Wi-Fi" : "LAN",
  };
}

export function getRouteStatus(state) {
  if (state?.connected) {
    return {
      availability: "Available",
      tunnel: "Connected",
      summary: state.status_summary || "VPN tunnel is active.",
    };
  }
  if (state?.authenticated) {
    return {
      availability: "Available",
      tunnel: "Not connected",
      summary: state.status_summary || "Provider is ready, but the tunnel is idle.",
    };
  }
  return {
    availability: "Unavailable",
    tunnel: "Not connected",
    summary: state?.status_summary || "Authenticate this provider to route traffic.",
  };
}
