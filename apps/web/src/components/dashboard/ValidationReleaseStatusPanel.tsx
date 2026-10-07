"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  FireSenseApiError,
  getValidationReleaseStatus,
} from "@/lib/api/client";

import type {
  ValidationReleaseStatusResponse,
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


export default function ValidationReleaseStatusPanel() {
  const [
    data,
    setData,
  ] = useState<
    ValidationReleaseStatusResponse | null
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
          await getValidationReleaseStatus();

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
            "Unable to load validation release status.",
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
        id="validation-release-status"
        className="scroll-mt-20 border-t border-white/[0.07] py-16"
      >
        <p className="text-sm text-white/35">
          Loading validation release status...
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
        id="validation-release-status"
        className="scroll-mt-20 border-t border-white/[0.07] py-16"
      >
        <div className="rounded-3xl border border-red-400/15 bg-red-400/[0.04] p-7">
          <p className="text-sm text-red-200/70">
            {
              error
              ?? "Validation release status unavailable."
            }
          </p>
        </div>
      </section>
    );
  }


  const validated =
    data.independent_external_validation_available;

  return (
    <section
      id="validation-release-status"
      className="scroll-mt-20 border-t border-white/[0.07] py-16"
    >
      <div className="overflow-hidden rounded-3xl border border-white/[0.08] bg-[#080b10]">

        <div className="px-6 py-8 md:px-8 lg:px-10">
          <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-white/30">
            Trusted scientific release state
          </p>

          <div className="mt-3 flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
            <div>
              <h2 className="text-3xl font-medium tracking-[-0.035em]">
                Validation release status
              </h2>

              <p className="mt-4 max-w-3xl text-sm leading-7 text-white/42">
                Validation status can only be
                promoted from a scientifically
                reviewed frozen artifact whose
                SHA-256 is pinned in the backend.
              </p>
            </div>

            <span
              className={
                validated
                  ? "rounded-full border border-emerald-300/20 bg-emerald-300/[0.06] px-4 py-2 text-[10px] uppercase tracking-[0.14em] text-emerald-200/80"
                  : "rounded-full border border-amber-300/20 bg-amber-300/[0.06] px-4 py-2 text-[10px] uppercase tracking-[0.14em] text-amber-100/75"
              }
            >
              {
                validated
                  ? "Independent validation approved"
                  : "Independent validation not yet available"
              }
            </span>
          </div>
        </div>


        <div className="grid border-y border-white/[0.06] sm:grid-cols-2 xl:grid-cols-4">
          <Metric
            label="Frozen candidate"
            value={
              data.frozen_candidate_available
                ? "Yes"
                : "No"
            }
          />

          <Metric
            label="Scientific review"
            value={
              data.scientific_review_approved
                ? "Approved"
                : "Pending"
            }
          />

          <Metric
            label="Pinned SHA"
            value={
              data.approved_artifact_hash_frozen_in_code
                ? "Yes"
                : "No"
            }
          />

          <Metric
            label="Validation"
            value={
              validated
                ? "Available"
                : "Unavailable"
            }
          />
        </div>


        <div className="grid gap-8 px-6 py-8 md:px-8 lg:grid-cols-2 lg:px-10">

          <div className="rounded-2xl border border-white/[0.065] bg-white/[0.018] p-5">
            <p className="text-[9px] uppercase tracking-[0.16em] text-white/25">
              Current scientific state
            </p>

            <p className="mt-4 text-sm font-medium text-white/70">
              {pretty(
                data.scientific_status,
              )}
            </p>

            <p className="mt-2 font-mono text-[9px] leading-5 text-white/25">
              {data.release_status_id}
            </p>
          </div>


          <div className="rounded-2xl border border-white/[0.065] bg-white/[0.018] p-5">
            <p className="text-[9px] uppercase tracking-[0.16em] text-white/25">
              Claim policy
            </p>

            <div className="mt-4 space-y-3">
              <Policy
                label="Independent validation"
                allowed={validated}
              />

              <Policy
                label="Production-ready"
                allowed={
                  data.production_ready_claim_allowed
                }
              />

              <Policy
                label="Certification"
                allowed={
                  data.certification_claim_allowed
                }
              />
            </div>
          </div>
        </div>


        <div className="grid gap-8 border-t border-white/[0.06] px-6 py-8 md:px-8 lg:grid-cols-2 lg:px-10">

          <div>
            <p className="text-[10px] uppercase tracking-[0.17em] text-white/25">
              Blocking reasons
            </p>

            <div className="mt-4 space-y-3">
              {data.blocking_reasons.map(
                (
                  reason,
                  index,
                ) => (
                  <div
                    key={`${index}-${reason}`}
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


          <div>
            <p className="text-[10px] uppercase tracking-[0.17em] text-white/25">
              Release guardrails
            </p>

            <div className="mt-4 space-y-3">
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

      </div>
    </section>
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

      <p className="mt-3 font-mono text-sm text-white/75">
        {value}
      </p>
    </div>
  );
}


function Policy({
  label,
  allowed,
}: {
  label: string;
  allowed: boolean;
}) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-white/[0.055] px-4 py-3">
      <span className="text-xs text-white/40">
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
            ? "Allowed"
            : "Blocked"
        }
      </span>
    </div>
  );
}
