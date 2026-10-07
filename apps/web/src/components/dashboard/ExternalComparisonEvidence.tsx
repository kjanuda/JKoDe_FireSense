"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  FireSenseApiError,
  getExternalComparisonEvidence,
} from "@/lib/api/client";

import type {
  ExternalComparisonEvidenceResponse,
} from "@/lib/api/contracts";


function formatNumber(
  value: number,
  digits = 3,
) {
  return value.toFixed(
    digits,
  );
}


function prettyLabel(
  value: string,
) {
  return value
    .replaceAll(
      "_",
      " ",
    )
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase(),
    );
}


function gravityLabel(
  value: string,
) {
  if (
    value
    === "microgravity"
  ) {
    return "Microgravity";
  }

  if (
    value
    === "normal_gravity"
  ) {
    return "Normal gravity";
  }

  return prettyLabel(
    value,
  );
}


export default function ExternalComparisonEvidence() {
  const [
    data,
    setData,
  ] = useState<
    ExternalComparisonEvidenceResponse | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(
    true,
  );

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);


  useEffect(() => {
    async function loadEvidence() {
      try {
        setLoading(
          true,
        );

        setError(
          null,
        );

        const result =
          await getExternalComparisonEvidence();

        setData(
          result,
        );
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
            "Unable to load external comparison evidence.",
          );
        }
      } finally {
        setLoading(
          false,
        );
      }
    }

    void loadEvidence();
  }, []);


  if (loading) {
    return (
      <section
        id="external-comparison"
        className="scroll-mt-20 border-t border-white/[0.07] py-16"
      >
        <div className="rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-7 lg:p-9">
          <p className="text-sm text-white/40">
            Loading independent external comparison...
          </p>
        </div>
      </section>
    );
  }


  if (
    error
    || !data
  ) {
    return (
      <section
        id="external-comparison"
        className="scroll-mt-20 border-t border-white/[0.07] py-16"
      >
        <div className="rounded-3xl border border-red-400/15 bg-red-400/[0.035] p-7 lg:p-9">
          <p className="text-[10px] font-medium uppercase tracking-[0.18em] text-red-200/60">
            External evidence unavailable
          </p>

          <p className="mt-3 text-sm leading-6 text-white/45">
            {
              error
              ?? "Unknown evidence error."
            }
          </p>
        </div>
      </section>
    );
  }


  return (
    <section
      id="external-comparison"
      className="scroll-mt-20 border-t border-white/[0.07] py-16"
    >
      <div className="overflow-hidden rounded-3xl border border-white/[0.08] bg-[#080b10]">

        <div className="px-6 py-8 md:px-8 lg:px-10 lg:py-10">
          <div className="flex flex-col gap-7 xl:flex-row xl:items-start xl:justify-between">
            <div className="max-w-4xl">
              <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-emerald-300/65">
                Independent external evidence
              </p>

              <h2 className="mt-3 text-3xl font-medium tracking-[-0.035em] text-white/95">
                Ries 2024 · Figure 4
              </h2>

              <p className="mt-4 max-w-3xl text-sm leading-7 text-white/42">
                FireSense v0 is compared numerically
                with an independent PMMA experiment.
                The evidence is suitable for external
                comparison, but the current conditions
                do not satisfy FireSense&apos;s criteria
                for direct independent validation.
              </p>

              <p className="mt-4 font-mono text-[10px] text-white/25">
                DOI {data.source_doi}
              </p>
            </div>


            <div className="flex flex-col items-start gap-2 xl:items-end">
              <span className="rounded-full border border-emerald-300/20 bg-emerald-300/[0.06] px-3 py-1.5 text-[10px] font-medium uppercase tracking-[0.15em] text-emerald-200/80">
                Independent comparison available
              </span>

              <span className="rounded-full border border-amber-300/20 bg-amber-300/[0.06] px-3 py-1.5 text-[10px] font-medium uppercase tracking-[0.15em] text-amber-100/75">
                Independent validation not yet available
              </span>
            </div>
          </div>
        </div>


        <div className="grid border-y border-white/[0.06] sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            label="Independent source"
            value="Yes"
            detail={data.source_name}
          />

          <MetricCard
            label="Numeric comparisons"
            value={String(
              data.comparison_count,
            )}
            detail="Closest 21% O₂ condition"
          />

          <MetricCard
            label="Training eligible"
            value={String(
              data.training_eligible_count,
            )}
            detail="External rows remain holdout"
          />

          <MetricCard
            label="Validation eligible"
            value={String(
              data.independent_validation_eligible_count,
            )}
            detail="Direct validation remains blocked"
          />
        </div>


        <div className="grid gap-8 px-6 py-8 md:px-8 lg:grid-cols-[1.35fr_0.65fr] lg:px-10">
          <div>
            <div className="mb-5 flex items-end justify-between gap-5">
              <div>
                <p className="text-[9px] font-medium uppercase tracking-[0.17em] text-white/25">
                  Numerical comparison
                </p>

                <h3 className="mt-2 text-lg font-medium text-white/80">
                  FireSense v0 vs Ries 2024
                </h3>
              </div>

              <p className="text-right text-[10px] leading-5 text-white/25">
                200 µm PMMA
                <br />
                ~21% O₂ · ~101.3 kPa
              </p>
            </div>


            <div className="grid gap-4 xl:grid-cols-2">
              {data.comparisons.map(
                (
                  comparison,
                ) => (
                  <article
                    key={
                      comparison.external_record_id
                    }
                    className="rounded-2xl border border-white/[0.065] bg-white/[0.018] p-5"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <p className="text-[9px] uppercase tracking-[0.16em] text-white/25">
                          Gravity
                        </p>

                        <h4 className="mt-2 text-sm font-medium text-white/75">
                          {gravityLabel(
                            comparison.gravity_context,
                          )}
                        </h4>
                      </div>

                      <span className="font-mono text-[9px] text-white/20">
                        {
                          comparison.external_record_id
                        }
                      </span>
                    </div>


                    <div className="mt-7 grid grid-cols-2 gap-3">
                      <RateBox
                        label="FireSense v0"
                        value={
                          comparison
                            .firesense_v0_rate_mm_s
                        }
                      />

                      <RateBox
                        label="Ries 2024"
                        value={
                          comparison
                            .ries_2024_rate_mm_s
                        }
                        external
                      />
                    </div>


                    <div className="mt-5 border-t border-white/[0.055] pt-5">
                      <div className="flex items-end justify-between gap-5">
                        <div>
                          <p className="text-[9px] uppercase tracking-[0.15em] text-white/25">
                            External − model
                          </p>

                          <p className="mt-2 font-mono text-sm text-white/60">
                            +
                            {formatNumber(
                              comparison
                                .external_minus_model_mm_s,
                              6,
                            )}
                            {" mm/s"}
                          </p>
                        </div>

                        <div className="text-right">
                          <p className="text-[9px] uppercase tracking-[0.15em] text-white/25">
                            Gap vs model
                          </p>

                          <p className="mt-2 font-mono text-xl text-amber-100/75">
                            +
                            {formatNumber(
                              comparison
                                .relative_gap_vs_model_percent,
                              2,
                            )}
                            %
                          </p>
                        </div>
                      </div>
                    </div>


                    <p className="mt-5 text-[10px] leading-5 text-white/27">
                      {
                        prettyLabel(
                          comparison
                            .comparison_status,
                        )
                      }
                    </p>
                  </article>
                ),
              )}
            </div>
          </div>


          <div className="space-y-5">
            <InfoPanel
              eyebrow="Flow compatibility"
              title="Condition mismatch"
            >
              <StatusRow
                label="BASS-II reference"
                value="50 mm/s"
              />

              <StatusRow
                label="Ries Figure 4"
                value="100 mm/s"
                warning
              />

              <StatusRow
                label="Flow exact match"
                value="No"
                warning
              />

              <StatusRow
                label="Flow correction"
                value="Not allowed"
                warning
              />
            </InfoPanel>


            <InfoPanel
              eyebrow="Measurement"
              title="Definition compatibility"
            >
              <p className="text-xs leading-5 text-white/45">
                {
                  prettyLabel(
                    data
                      .measurement_definition_classification,
                  )
                }
              </p>

              <StatusRow
                label="Exact definition match"
                value="No"
                warning
              />

              <p className="pt-2 text-[11px] leading-5 text-white/28">
                BASS-II tracks a visible flame
                leading edge. Ries tracks an
                IR-derived pyrolysis front using
                a 603 K criterion.
              </p>
            </InfoPanel>


            <InfoPanel
              eyebrow="Release status"
              title="Scientific classification"
            >
              <StatusRow
                label="External comparison"
                value="Available"
              />

              <StatusRow
                label="External validation"
                value="Not yet available"
                warning
              />

              <StatusRow
                label="Integrity"
                value={
                  data.artifact_sha256_verified
                    ? "Verified"
                    : "Failed"
                }
              />
            </InfoPanel>
          </div>
        </div>


        <div className="border-t border-white/[0.06] px-6 py-7 md:px-8 lg:px-10">
          <div className="grid gap-8 lg:grid-cols-2">
            <div>
              <p className="text-[10px] font-medium uppercase tracking-[0.17em] text-white/25">
                Remaining blockers
              </p>

              <div className="mt-4 space-y-3">
                {data.blocking_reasons.map(
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

                      <p className="text-[11px] leading-5 text-white/38">
                        {
                          prettyLabel(
                            reason,
                          )
                        }
                      </p>
                    </div>
                  ),
                )}
              </div>
            </div>


            <div>
              <p className="text-[10px] font-medium uppercase tracking-[0.17em] text-white/25">
                Frozen provenance
              </p>

              <div className="mt-4 rounded-2xl border border-white/[0.06] bg-black/20 p-4">
                <p className="text-[9px] uppercase tracking-[0.15em] text-white/20">
                  Comparison SHA-256
                </p>

                <p className="mt-2 break-all font-mono text-[9px] leading-4 text-white/35">
                  {
                    data.artifact_sha256
                      .comparison
                  }
                </p>

                <div className="my-4 border-t border-white/[0.05]" />

                <p className="text-[9px] uppercase tracking-[0.15em] text-white/20">
                  Flow / transport SHA-256
                </p>

                <p className="mt-2 break-all font-mono text-[9px] leading-4 text-white/35">
                  {
                    data.artifact_sha256
                      .flow_transport
                  }
                </p>
              </div>

              <p className="mt-3 text-[10px] leading-5 text-emerald-200/45">
                All frozen evidence hashes verified by
                the backend before this response was
                returned.
              </p>
            </div>
          </div>
        </div>


        <div className="border-t border-white/[0.06] px-6 py-7 md:px-8 lg:px-10">
          <p className="text-[10px] font-medium uppercase tracking-[0.17em] text-white/25">
            Guardrails
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


function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="border-white/[0.06] bg-[#090c11] p-5 sm:border-r md:p-6 last:border-r-0">
      <p className="text-[9px] font-medium uppercase tracking-[0.16em] text-white/25">
        {label}
      </p>

      <p className="mt-3 font-mono text-2xl tracking-[-0.04em] text-white/90">
        {value}
      </p>

      <p className="mt-2 text-[10px] leading-5 text-white/30">
        {detail}
      </p>
    </div>
  );
}


function RateBox({
  label,
  value,
  external = false,
}: {
  label: string;
  value: number;
  external?: boolean;
}) {
  return (
    <div className="rounded-xl border border-white/[0.055] bg-black/20 p-3">
      <p className="text-[9px] uppercase tracking-[0.14em] text-white/22">
        {label}
      </p>

      <p
        className={[
          "mt-2 font-mono text-lg",
          external
            ? "text-emerald-100/80"
            : "text-white/70",
        ].join(
          " ",
        )}
      >
        {formatNumber(
          value,
          6,
        )}
      </p>

      <p className="mt-1 text-[9px] text-white/22">
        mm/s
      </p>
    </div>
  );
}


function InfoPanel({
  eyebrow,
  title,
  children,
}: {
  eyebrow: string;
  title: string;
  children:
    React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-white/[0.065] bg-white/[0.018] p-5">
      <p className="text-[9px] font-medium uppercase tracking-[0.16em] text-white/25">
        {eyebrow}
      </p>

      <h3 className="mt-2 text-sm font-medium text-white/75">
        {title}
      </h3>

      <div className="mt-5 space-y-3">
        {children}
      </div>
    </div>
  );
}


function StatusRow({
  label,
  value,
  warning = false,
}: {
  label: string;
  value: string;
  warning?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-xs text-white/42">
        {label}
      </span>

      <span
        className={
          warning
            ? "text-right font-mono text-[11px] text-amber-100/65"
            : "text-right font-mono text-[11px] text-emerald-100/60"
        }
      >
        {value}
      </span>
    </div>
  );
}
