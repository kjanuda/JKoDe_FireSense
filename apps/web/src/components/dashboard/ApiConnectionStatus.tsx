"use client";

import {
  useEffect,
  useState,
} from "react";


type ApiState =
  | "checking"
  | "online"
  | "offline";


const API_BASE_URL = (
  process.env.NEXT_PUBLIC_FIRESENSE_API_URL
  ?? "http://127.0.0.1:8000"
).replace(
  /\/+$/,
  "",
);


async function probeApi(): Promise<boolean> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/health`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
        cache: "no-store",
      },
    );

    return response.ok;
  } catch {
    return false;
  }
}


export default function ApiConnectionStatus() {
  const [
    state,
    setState,
  ] = useState<ApiState>(
    "checking",
  );


  useEffect(() => {
    let cancelled = false;

    async function check() {
      const online =
        await probeApi();

      if (!cancelled) {
        setState(
          online
            ? "online"
            : "offline",
        );
      }
    }

    void check();

    const interval =
      window.setInterval(
        () => {
          void check();
        },
        15000,
      );

    return () => {
      cancelled = true;

      window.clearInterval(
        interval,
      );
    };
  }, []);


  async function retry() {
    setState(
      "checking",
    );

    const online =
      await probeApi();

    setState(
      online
        ? "online"
        : "offline",
    );
  }


  if (state === "online") {
    return (
      <div
        role="status"
        className="fixed bottom-5 right-5 z-[100] hidden items-center gap-2 rounded-full border border-emerald-300/15 bg-[#07100d]/90 px-3 py-2 text-[10px] text-emerald-200/70 shadow-2xl backdrop-blur-xl md:flex"
      >
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />

        API connected
      </div>
    );
  }


  if (state === "checking") {
    return (
      <div
        role="status"
        className="fixed bottom-5 right-5 z-[100] flex items-center gap-3 rounded-2xl border border-white/[0.08] bg-[#090c11]/95 px-4 py-3 shadow-2xl backdrop-blur-xl"
      >
        <span className="h-2 w-2 animate-pulse rounded-full bg-white/40" />

        <p className="text-xs text-white/45">
          Checking FireSense API…
        </p>
      </div>
    );
  }


  return (
    <div
      role="alert"
      className="fixed bottom-5 right-5 z-[100] w-[calc(100vw-2.5rem)] max-w-sm rounded-2xl border border-red-300/15 bg-[#12090a]/95 p-4 shadow-2xl backdrop-blur-xl"
    >
      <div className="flex items-start gap-3">
        <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-red-300" />

        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-red-100">
            FireSense API unavailable
          </p>

          <p className="mt-1 text-xs leading-5 text-white/40">
            The frontend cannot currently reach
            the FireSense research backend.
          </p>

          <p className="mt-2 font-mono text-[10px] text-white/25">
            {API_BASE_URL}
          </p>

          <button
            type="button"
            onClick={() => {
              void retry();
            }}
            className="mt-4 rounded-xl border border-red-200/15 bg-red-200/[0.05] px-3 py-2 text-xs font-medium text-red-100 transition hover:bg-red-200/[0.09]"
          >
            Retry connection
          </button>
        </div>
      </div>
    </div>
  );
}
