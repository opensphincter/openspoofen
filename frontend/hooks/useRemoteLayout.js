import { useEffect, useMemo, useState } from "react";

const BASE_WIDTH = 430;
const BASE_HEIGHT = 932;
const MOBILE_BREAKPOINT = 768;

export { BASE_WIDTH, BASE_HEIGHT };

export default function useRemoteLayout() {
  const [viewport, setViewport] = useState({ width: window.innerWidth, height: window.innerHeight });

  useEffect(() => {
    const update = () => {
      setViewport({ width: window.innerWidth, height: window.innerHeight });
    };
    window.addEventListener("resize", update, { passive: true });
    window.addEventListener("orientationchange", update, { passive: true });
    return () => {
      window.removeEventListener("resize", update);
      window.removeEventListener("orientationchange", update);
    };
  }, []);

  return useMemo(() => {
    const mobile = viewport.width < MOBILE_BREAKPOINT;
    const scale = mobile
      ? viewport.width / BASE_WIDTH
      : Math.min(viewport.width / BASE_WIDTH, viewport.height / BASE_HEIGHT);
    return {
      mobile,
      scale,
      width: BASE_WIDTH * scale,
      height: BASE_HEIGHT * scale,
    };
  }, [viewport.height, viewport.width]);
}
