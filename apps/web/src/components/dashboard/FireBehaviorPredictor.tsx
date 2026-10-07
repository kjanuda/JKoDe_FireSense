"use client";

import {
  type FormEvent,
  useState,
} from "react";

import {
  explainFireBehavior,
  FireSenseApiError,
} from "@/lib/api/client";

import type {
  ExplainedPredictionResponse,
  FireBehaviorPredictionRequest,
} from "@/lib/api/contracts";


const DEFAULT_INPUT: FireBehaviorPredictionRequest = {
  material: "PMMA",
  geometry: "thin_sheet",
  thickness_um: 200,
  gravity_regime: "microgravity",
  oxygen_fraction: 0.21,
  pressure_kpa: 101.325,
};


function formatNumber(
  value: number | null | undefined,
  digits = 3,
) {
  if (value === null || value === undefined) {
    return "—";
  }

  return value.toFixed(digits);
}


type FireBehaviorPredictorProps = {
  onResult?: (
    input: FireBehaviorPredictionRequest,
    response: ExplainedPredictionResponse,
  ) => void;
};


export default function FireBehaviorPredictor({
  onResult,
}: FireBehaviorPredictorProps) {
  const [
    input,
    setInput,
  ] = useState<
    FireBehaviorPredictionRequest
  >(DEFAULT_INPUT);

  const [
    response,
    setResponse,
  ] = useState<
    ExplainedPredictionResponse | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(null);


  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    try {
      setLoading(true);
      setError(null);

      const result =
        await explainFireBehavior(input);

      setResponse(result);

      onResult?.(
        {
          ...input,
        },
        result,
      );
    } catch (caught) {
      setResponse(null);

      if (
        caught
        instanceof FireSenseApiError
      ) {
        setError(
          `${caught.status}: ${caught.detail}`,
        );
      } else if (
        caught instanceof Error
      ) {
        setError(caught.message);
      } else {
        setError(
          "Unable to run FireSense prediction.",
        );
      }
    } finally {
      setLoading(false);
    }
  }


  const result = response?.result;
  const evidence = response?.evidence_trace;


  return (
    <section
      id="predictor"
      className="scroll-mt-20 border-b border-white/[0.07] py-16 lg:py-20"
    >
      <div className="mb-9 flex flex-col justify-between gap-5 lg:flex-row lg:items-end">
        <div>
          <p className="text-[11px] uppercase tracking-[0.22em] text-orange-300/70">
            Fire behavior model
          </p>

          <h2 className="mt-3 text-3xl font-medium tracking-[-0.035em]">
            Explore a supported fire condition
          </h2>
        </div>

        <p className="max-w-2xl text-sm leading-7 text-white/40">
          The numerical model estimates measurable
          flame spread behavior only inside its
          supported empirical domain. Unsupported
          conditions return an explicit abstention.
        </p>
      </div>


      <div className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
        <form
          onSubmit={handleSubmit}
          className="rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-6 lg:p-8"
        >
          <div className="mb-7">
            <p className="text-[10px] uppercase tracking-[0.2em] text-white/30">
              Model inputs
            </p>

            <p className="mt-2 text-sm leading-6 text-white/40">
              Default values match the current
              canonical PMMA thin-sheet evidence family.
            </p>
          </div>


          <div className="grid gap-5 sm:grid-cols-2">
            <label className="block">
              <span className="text-xs text-white/45">
                Material
              </span>

              <input
                value={input.material}
                onChange={(event) =>
                  setInput((current) => ({
                    ...current,
                    material:
                      event.target.value,
                  }))
                }
                className="mt-2 h-11 w-full rounded-xl border border-white/[0.08] bg-white/[0.025] px-3 text-sm outline-none transition focus:border-orange-300/40"
              />
            </label>


            <label className="block">
              <span className="text-xs text-white/45">
                Geometry
              </span>

              <input
                value={input.geometry}
                onChange={(event) =>
                  setInput((current) => ({
                    ...current,
                    geometry:
                      event.target.value,
                  }))
                }
                className="mt-2 h-11 w-full rounded-xl border border-white/[0.08] bg-white/[0.025] px-3 text-sm outline-none transition focus:border-orange-300/40"
              />
            </label>


            <label className="block">
              <span className="text-xs text-white/45">
                Thickness
              </span>

              <div className="relative mt-2">
                <input
                  type="number"
                  step="0.001"
                  min="0"
                  value={input.thickness_um}
                  onChange={(event) =>
                    setInput((current) => ({
                      ...current,
                      thickness_um:
                        Number(
                          event.target.value,
                        ),
                    }))
                  }
                  className="h-11 w-full rounded-xl border border-white/[0.08] bg-white/[0.025] px-3 pr-12 text-sm outline-none transition focus:border-orange-300/40"
                />

                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-white/25">
                  um
                </span>
              </div>
            </label>


            <label className="block">
              <span className="text-xs text-white/45">
                Gravity regime
              </span>

              <select
                value={input.gravity_regime}
                onChange={(event) =>
                  setInput((current) => ({
                    ...current,
                    gravity_regime:
                      event.target.value as
                        | "microgravity"
                        | "normal_gravity",
                  }))
                }
                className="mt-2 h-11 w-full rounded-xl border border-white/[0.08] bg-[#0d1117] px-3 text-sm outline-none transition focus:border-orange-300/40"
              >
                <option value="microgravity">
                  Microgravity
                </option>

                <option value="normal_gravity">
                  Normal gravity
                </option>
              </select>
            </label>


            <label className="block">
              <span className="text-xs text-white/45">
                Oxygen fraction
              </span>

              <input
                type="number"
                step="0.001"
                min="0"
                max="1"
                value={input.oxygen_fraction}
                onChange={(event) =>
                  setInput((current) => ({
                    ...current,
                    oxygen_fraction:
                      Number(
                        event.target.value,
                      ),
                  }))
                }
                className="mt-2 h-11 w-full rounded-xl border border-white/[0.08] bg-white/[0.025] px-3 text-sm outline-none transition focus:border-orange-300/40"
              />
            </label>


            <label className="block">
              <span className="text-xs text-white/45">
                Pressure
              </span>

              <div className="relative mt-2">
                <input
                  type="number"
                  step="0.001"
                  min="0"
                  value={input.pressure_kpa}
                  onChange={(event) =>
                    setInput((current) => ({
                      ...current,
                      pressure_kpa:
                        Number(
                          event.target.value,
                        ),
                    }))
                  }
                  className="h-11 w-full rounded-xl border border-white/[0.08] bg-white/[0.025] px-3 pr-12 text-sm outline-none transition focus:border-orange-300/40"
                />

                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-white/25">
                  kPa
                </span>
              </div>
            </label>
          </div>


          <button
            type="submit"
            disabled={loading}
            className="mt-7 flex h-12 w-full items-center justify-center rounded-xl bg-orange-300 px-5 text-sm font-medium text-[#15100a] transition hover:bg-orange-200 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading
              ? "Evaluating evidence..."
              : "Predict fire behavior"}
          </button>


          <p className="mt-4 text-[11px] leading-5 text-white/25">
            Research decision support only.
            No certification or cabin-fire
            probability claim is produced.
          </p>
        </form>


        <div className="rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-6 lg:p-8">
          {!response && !error && (
            <div className="flex min-h-[470px] items-center justify-center">
              <div className="max-w-sm text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-orange-300/15 bg-orange-300/[0.05] text-orange-200">
                  F
                </div>

                <h3 className="mt-5 text-lg font-medium">
                  Awaiting a condition
                </h3>

                <p className="mt-3 text-sm leading-6 text-white/35">
                  Run the model to see the
                  prediction or abstention together
                  with its evidence trace.
                </p>
              </div>
            </div>
          )}


          {error && (
            <div className="rounded-2xl border border-red-400/15 bg-red-400/[0.04] p-5">
              <p className="text-xs uppercase tracking-[0.18em] text-red-300">
                API error
              </p>

              <p className="mt-3 text-sm leading-6 text-white/55">
                {error}
              </p>
            </div>
          )}


          {result && evidence && (
            <div>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-[10px] uppercase tracking-[0.2em] text-white/30">
                    Model decision
                  </p>

                  <p
                    className={[
                      "mt-2 text-lg font-medium",
                      result.decision === "predict"
                        ? "text-emerald-300"
                        : "text-amber-300",
                    ].join(" ")}
                  >
                    {result.decision === "predict"
                      ? "Prediction supported"
                      : "Model abstained"}
                  </p>
                </div>

                <span className="rounded-full border border-white/[0.08] px-3 py-1.5 font-mono text-[10px] text-white/40">
                  {
                    evidence.gravity_regime
                  }
                </span>
              </div>


              {result.decision === "predict"
                && result.prediction && (
                <div className="mt-8 rounded-3xl border border-orange-300/10 bg-orange-300/[0.035] p-6">
                  <p className="text-[10px] uppercase tracking-[0.2em] text-white/30">
                    Predicted flame spread rate
                  </p>

                  <div className="mt-4 flex items-end gap-3">
                    <span className="text-5xl font-medium tracking-[-0.05em] text-orange-200">
                      {formatNumber(
                        result.prediction.value,
                        4,
                      )}
                    </span>

                    <span className="pb-1 text-sm text-white/35">
                      {
                        result.prediction.unit
                      }
                    </span>
                  </div>
                </div>
              )}


              {result.decision === "abstain" && (
                <div className="mt-8 rounded-2xl border border-amber-300/15 bg-amber-300/[0.04] p-5">
                  <p className="text-xs font-medium text-amber-200">
                    Outside supported prediction conditions
                  </p>

                  <div className="mt-4 space-y-2">
                    {result.abstention_reasons.map(
                      (reason) => (
                        <p
                          key={reason}
                          className="text-sm leading-6 text-white/50"
                        >
                          • {reason}
                        </p>
                      ),
                    )}
                  </div>

                  {result.supported_domain && (
                    <details className="mt-5">
                      <summary className="cursor-pointer text-xs text-white/40">
                        View supported domain
                      </summary>

                      <pre className="mt-3 overflow-auto rounded-xl bg-black/20 p-3 text-[10px] leading-5 text-white/35">
                        {JSON.stringify(
                          result.supported_domain,
                          null,
                          2,
                        )}
                      </pre>
                    </details>
                  )}
                </div>
              )}


              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl border border-white/[0.06] p-4">
                  <p className="text-[10px] uppercase tracking-wider text-white/25">
                    Model
                  </p>

                  <p className="mt-2 text-sm text-white/65">
                    {
                      result.model
                        .model_name
                    }
                  </p>

                  <p className="mt-1 font-mono text-[10px] text-white/25">
                    {
                      result.model
                        .model_version
                    }
                  </p>
                </div>


                <div className="rounded-2xl border border-white/[0.06] p-4">
                  <p className="text-[10px] uppercase tracking-wider text-white/25">
                    Coefficient K
                  </p>

                  <p className="mt-2 text-xl font-medium">
                    {formatNumber(
                      result.model
                        .coefficient_k,
                      3,
                    )}
                  </p>
                </div>


                <div className="rounded-2xl border border-white/[0.06] p-4">
                  <p className="text-[10px] uppercase tracking-wider text-white/25">
                    Residual factor
                  </p>

                  <p className="mt-2 text-xl font-medium">
                    {formatNumber(
                      result
                        .descriptive_residual_factor,
                      3,
                    )}
                  </p>
                </div>
              </div>


              <div className="mt-5 rounded-2xl border border-white/[0.06] bg-white/[0.018] p-5">
                <p className="text-[10px] uppercase tracking-[0.18em] text-white/25">
                  Uncertainty
                </p>

                <p className="mt-3 text-sm leading-6 text-white/48">
                  {result.uncertainty_note}
                </p>
              </div>


              <div className="mt-6">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-[10px] uppercase tracking-[0.18em] text-white/25">
                      Evidence trace
                    </p>

                    <p className="mt-2 text-sm text-white/55">
                      {
                        evidence
                          .canonical_source_id
                      }
                    </p>
                  </div>

                  <p className="font-mono text-xs text-white/35">
                    {
                      evidence
                        .canonical_figure_ref
                    }
                  </p>
                </div>


                <div className="mt-5 space-y-3">
                  {
                    evidence
                      .nearest_evidence_records
                      .map((record) => (
                        <div
                          key={record.record_id}
                          className="grid gap-3 rounded-2xl border border-white/[0.06] p-4 sm:grid-cols-[1fr_auto_auto]"
                        >
                          <div>
                            <p className="font-mono text-[10px] text-white/30">
                              {record.record_id}
                            </p>

                            <p className="mt-1 text-xs text-white/45">
                              {record.gravity_regime}
                            </p>
                          </div>

                          <div>
                            <p className="text-[10px] text-white/25">
                              Thickness
                            </p>

                            <p className="mt-1 text-sm">
                              {formatNumber(
                                record.thickness_um,
                                3,
                              )}{" "}
                              um
                            </p>
                          </div>

                          <div>
                            <p className="text-[10px] text-white/25">
                              Observed
                            </p>

                            <p className="mt-1 text-sm">
                              {formatNumber(
                                record
                                  .observed_spread_rate_mm_s,
                                4,
                              )}{" "}
                              mm/s
                            </p>
                          </div>
                        </div>
                      ))
                  }
                </div>
              </div>


              {result.warnings.length > 0 && (
                <div className="mt-6">
                  <p className="text-[10px] uppercase tracking-[0.18em] text-amber-300/60">
                    Warnings
                  </p>

                  <div className="mt-3 space-y-2">
                    {result.warnings.map(
                      (warning) => (
                        <p
                          key={warning}
                          className="text-xs leading-5 text-white/38"
                        >
                          • {warning}
                        </p>
                      ),
                    )}
                  </div>
                </div>
              )}


              <div className="mt-6 flex flex-wrap gap-2">
                <span className="rounded-full border border-white/[0.07] px-3 py-1 text-[10px] text-white/30">
                  External validation:{" "}
                  {
                    evidence
                      .external_validation_status
                  }
                </span>

                <span className="rounded-full border border-white/[0.07] px-3 py-1 text-[10px] text-white/30">
                  Production ready:{" "}
                  {
                    evidence.production_ready
                      ? "yes"
                      : "no"
                  }
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
