"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  FireSenseApiError,
  getValidationReadiness,
} from "@/lib/api/client";

import type {
  ValidationReadinessResponse,
} from "@/lib/api/contracts";


function pretty(
  value: string,
) {
  return value
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase(),
    );
}


export default function ValidationReadinessPanel() {
  const [
    data,
    setData,
  ] = useState<
    ValidationReadinessResponse | null
  >(null);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(true);


  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError(null);

        const result =
          await getValidationReadiness();

        setData(result);
      } catch (caught) {
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
          setError(
            caught.message,
          );
        } else {
          setError(
            "Unable to load validation readiness.",
          );
        }
      } finally {
        setLoading(false);
      }
    }

    void load();
  }, []);


  if (loading) {
    return (
      <section
        id="validation-readiness"
        className="scroll-mt-20 border-t border-white/[0.07] py-16"
      >
        <p className="text-sm text-white/35">
          Loading validation readiness...
        </p>
      </section>
    );
  }


  if (
    error
    || !data
  ) {
    return (
      <section
        id="validation-readiness"
        className="scroll-mt-20 border-t border-white/[0.07] py-16"
      >
        <div className="rounded-3xl border border-red-400/15 bg-red-400/[0.04] p-7">
          <p className="text-sm text-red-200/70">
            {
              error
              ?? "Validation readiness unavailable."
            }
          </p>
        </div>
      </section>
    );
  }


  return (
    <section
      id="validation-readiness"
      className="scroll-mt-20 border-t border-white/[0.07] py-16"
    >
      <div className="overflow-hidden rounded-3xl border border-white/[0.08] bg-[#080b10]">

        <div className="px-6 py-8 md:px-8 lg:px-10">
          <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-amber-200/65">
            Scientific validation gate
          </p>

          <div className="mt-3 flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
            <div>
              <h2 className="text-3xl font-medium tracking-[-0.035em]">
                Independent validation readiness
              </h2>

              <p className="mt-4 max-w-3xl text-sm leading-7 text-white/42">
                FireSense evaluates external
                evidence against a frozen
                validation protocol before any
                validation claim can be made.
              </p>
            </div>

            <div className="flex flex-col gap-2">
              <StatusBadge
                good
                text="External comparison available"
              />

              <StatusBadge
                text="External validation not yet available"
              />
            </div>
          </div>
        </div>


        <div className="grid border-y border-white/[0.06] sm:grid-cols-2 xl:grid-cols-4">
          <Metric
            label="Candidates screened"
            value={String(
              data.screened_candidate_count,
            )}
          />

          <Metric
            label="Comparison sources"
            value={String(
              data.independent_comparison_source_count,
            )}
          />

          <Metric
            label="Exact validation sources"
            value={String(
              data.exact_validation_source_count,
            )}
          />

          <Metric
            label="Minimum validation points"
            value={String(
              data.minimum_validation_scope
                .minimum_independent_numeric_points,
            )}
          />
        </div>


        <div className="grid gap-8 px-6 py-8 md:px-8 lg:grid-cols-2 lg:px-10">

          <div className="rounded-2xl border border-white/[0.065] bg-white/[0.018] p-5">
            <p className="text-[9px] uppercase tracking-[0.16em] text-white/25">
              Frozen validation target
            </p>

            <div className="mt-5 space-y-3">
              <Row
                label="Material"
                value={data.target.material}
              />

              <Row
                label="Geometry"
                value={pretty(
                  data.target.geometry_family,
                )}
              />

              <Row
                label="Thickness"
                value={
                  `${data.target.thickness_um} µm`
                }
              />

              <Row
                label="Oxygen"
                value={
                  `${data.target.oxygen_percent}%`
                }
              />

              <Row
                label="Pressure"
                value={
                  `${data.target.pressure_kpa} kPa`
                }
              />

              <Row
                label="Microgravity mode"
                value={pretty(
                  data.target
                    .microgravity_configuration,
                )}
              />

              <Row
                label="Reference flow"
                value={
                  `${data.target.microgravity_flow_mm_s} mm/s`
                }
              />
            </div>
          </div>


          <div className="rounded-2xl border border-white/[0.065] bg-white/[0.018] p-5">
            <p className="text-[9px] uppercase tracking-[0.16em] text-white/25">
              Current Ries 2024 status
            </p>

            <h3 className="mt-3 text-sm font-medium text-white/70">
              {pretty(
                data.ries_2024_classification,
              )}
            </h3>

            <div className="mt-5 space-y-3">
              {data.ries_2024_blocking_reasons.map(
                (
                  reason,
                  index,
                ) => (
                  <div
                    key={reason}
                    className="flex gap-3 rounded-xl border border-amber-300/[0.08] bg-amber-300/[0.025] p-3"
                  >
                    <span className="font-mono text-[9px] text-amber-200/45">
                      {String(
                        index + 1,
                      ).padStart(
                        2,
                        "0",
                      )}
                    </span>

                    <p className="text-[11px] leading-5 text-white/40">
                      {reason}
                    </p>
                  </div>
                ),
              )}
            </div>
          </div>
        </div>


        <div className="grid gap-8 border-t border-white/[0.06] px-6 py-8 md:px-8 lg:grid-cols-2 lg:px-10">

          <div>
            <p className="text-[10px] uppercase tracking-[0.17em] text-white/25">
              Claim policy
            </p>

            <div className="mt-4 space-y-3">
              <PolicyRow
                label="Independent validation claim"
                allowed={
                  data.independent_external_validation_available
                }
              />

              <PolicyRow
                label="Production-ready claim"
                allowed={
                  data.production_ready_claim_allowed
                }
              />

              <PolicyRow
                label="Certification claim"
                allowed={
                  data.certification_claim_allowed
                }
              />

              <PolicyRow
                label="Artifact integrity"
                allowed={
                  data.artifact_sha256_verified
                }
                positiveLabel="Verified"
              />
            </div>
          </div>


          <div>
            <p className="text-[10px] uppercase tracking-[0.17em] text-white/25">
              Frozen protocol provenance
            </p>

            <HashBox
              label="Acceptance criteria SHA-256"
              value={
                data.acceptance_criteria_sha256
              }
            />

            <div className="mt-3">
              <HashBox
                label="Source screening SHA-256"
                value={
                  data.source_screening_sha256
                }
              />
            </div>
          </div>
        </div>


        <div className="border-t border-white/[0.06] px-6 py-7 md:px-8 lg:px-10">
          <p className="text-[10px] uppercase tracking-[0.17em] text-white/25">
            Validation guardrails
          </p>

          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {data.guardrails.map(
              (
                guardrail,
              ) => (
                <div
                  key={guardrail}
                  className="flex gap-3 rounded-xl border border-white/[0.055] bg-white/[0.018] p-3"
                >
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-white/25" />

                  <p className="text-[11px] leading-5 text-white/35">
                    {guardrail}
                  </p>
                </div>
              ),
            )}
          </div>
        </div>

      </div>
    </section>
  );
}


function StatusBadge({
  text,
  good = false,
}: {
  text: string;
  good?: boolean;
}) {
  return (
    <span
      className={
        good
          ? "rounded-full border border-emerald-300/20 bg-emerald-300/[0.06] px-3 py-1.5 text-[10px] uppercase tracking-[0.14em] text-emerald-200/80"
          : "rounded-full border border-amber-300/20 bg-amber-300/[0.06] px-3 py-1.5 text-[10px] uppercase tracking-[0.14em] text-amber-100/75"
      }
    >
      {text}
    </span>
  );
}


function Metric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="border-white/[0.06] bg-[#090c11] p-5 sm:border-r last:border-r-0 md:p-6">
      <p className="text-[9px] uppercase tracking-[0.16em] text-white/25">
        {label}
      </p>

      <p className="mt-3 font-mono text-2xl text-white/85">
        {value}
      </p>
    </div>
  );
}


function Row({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between gap-5">
      <span className="text-xs text-white/38">
        {label}
      </span>

      <span className="text-right font-mono text-[11px] text-white/65">
        {value}
      </span>
    </div>
  );
}


function PolicyRow({
  label,
  allowed,
  positiveLabel = "Allowed",
}: {
  label: string;
  allowed: boolean;
  positiveLabel?: string;
}) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-white/[0.055] px-4 py-3">
      <span className="text-xs text-white/42">
        {label}
      </span>

      <span
        className={
          allowed
            ? "font-mono text-[10px] uppercase text-emerald-200/70"
            : "font-mono text-[10px] uppercase text-amber-100/70"
        }
      >
        {
          allowed
            ? positiveLabel
            : "Blocked"
        }
      </span>
    </div>
  );
}


function HashBox({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-white/[0.055] bg-black/20 p-4">
      <p className="text-[9px] uppercase tracking-[0.14em] text-white/20">
        {label}
      </p>

      <p className="mt-2 break-all font-mono text-[9px] leading-4 text-white/35">
        {value}
      </p>
    </div>
  );
}
