import { useRef, useEffect } from "react";
import { BASE_WIDTH, BASE_HEIGHT } from "../hooks/useRemoteLayout";

function traceRoundedRect(context, x, y, width, height, radius) {
  const safeRadius = Math.max(0, Math.min(radius, width / 2, height / 2));
  context.beginPath();
  if (typeof context.roundRect === "function") {
    context.roundRect(x, y, width, height, safeRadius);
    return;
  }
  context.moveTo(x + safeRadius, y);
  context.lineTo(x + width - safeRadius, y);
  context.quadraticCurveTo(x + width, y, x + width, y + safeRadius);
  context.lineTo(x + width, y + height - safeRadius);
  context.quadraticCurveTo(x + width, y + height, x + width - safeRadius, y + height);
  context.lineTo(x + safeRadius, y + height);
  context.quadraticCurveTo(x, y + height, x, y + height - safeRadius);
  context.lineTo(x, y + safeRadius);
  context.quadraticCurveTo(x, y, x + safeRadius, y);
  context.closePath();
}

export default function RemoteCanvas({ connected, edgeToEdge = false }) {
  const ref = useRef(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!(canvas instanceof HTMLCanvasElement)) {
      return;
    }
    const context = canvas.getContext("2d");
    if (!context) {
      return;
    }
    const dpr = window.devicePixelRatio || 1;
    canvas.width = BASE_WIDTH * dpr;
    canvas.height = BASE_HEIGHT * dpr;
    canvas.style.width = `${BASE_WIDTH}px`;
    canvas.style.height = `${BASE_HEIGHT}px`;
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    context.clearRect(0, 0, BASE_WIDTH, BASE_HEIGHT);

    const shellGradient = context.createLinearGradient(0, 0, BASE_WIDTH, BASE_HEIGHT);
    shellGradient.addColorStop(0, connected ? "#10253a" : "#111a28");
    shellGradient.addColorStop(0.5, "#09131d");
    shellGradient.addColorStop(1, "#050a11");
    context.fillStyle = shellGradient;
    if (edgeToEdge) {
      context.fillRect(0, 0, BASE_WIDTH, BASE_HEIGHT);
    } else {
      traceRoundedRect(context, 0, 0, BASE_WIDTH, BASE_HEIGHT, 48);
      context.fill();
    }

    if (!edgeToEdge) {
      context.strokeStyle = "rgba(255,255,255,0.08)";
      context.lineWidth = 2;
      traceRoundedRect(context, 8, 8, BASE_WIDTH - 16, BASE_HEIGHT - 16, 42);
      context.stroke();
    }

    const glow = context.createRadialGradient(215, 156, 20, 215, 156, 260);
    glow.addColorStop(0, connected ? "rgba(62, 200, 153, 0.25)" : "rgba(58, 103, 214, 0.16)");
    glow.addColorStop(1, "rgba(6,12,18,0)");
    context.fillStyle = glow;
    context.fillRect(0, 0, BASE_WIDTH, 420);

    context.fillStyle = "rgba(255,255,255,0.04)";
    traceRoundedRect(context, 144, 28, 140, 8, 4);
    context.fill();

    context.fillStyle = "rgba(255,255,255,0.03)";
    traceRoundedRect(context, 46, 98, BASE_WIDTH - 92, 170, 30);
    context.fill();
    traceRoundedRect(context, 84, 328, BASE_WIDTH - 168, 216, 108);
    context.fill();
    traceRoundedRect(context, 52, 598, BASE_WIDTH - 104, 92, 28);
    context.fill();
  }, [connected, edgeToEdge]);

  return <canvas ref={ref} className="absolute inset-0 h-full w-full" aria-hidden="true" />;
}
