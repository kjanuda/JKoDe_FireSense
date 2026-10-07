"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import { getFigure222Evidence } from "@/lib/api/client";

import type {
  Figure222EvidenceResponse,
} from "@/lib/api/contracts";


type Figure222Record =
  Figure222EvidenceResponse["records"][number];


function humanize(
  value: string,
): string {
  return value
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase(),
    );
}


function formatNumber(
  value: number,
  digits = 3,
): string {
  return value.toLocaleString(
    "en-US",
    {
      maximumFractionDigits:
        digits,
    },
  );
}


function gravityLabel(
  value:
    | string
    | null
    | undefined,
): string {
  if (
    value === "microgravity"
  ) {
    return "Microgravity";
  }

  if (
    value === "normal_gravity"
  ) {
    return "Normal gravity";
  }

  return "Unresolved";
}


function duplicateLabel(
  record: Figure222Record,
): string {
  const classification =
    record.duplicate_linkage
      ?.classification;

  if (!classification) {
    return "No flagged linkage";
  }

  return humanize(
    classification,
  );
}


export default function Figure222ComparisonEvidence() {
  const [
    data,
    setData,
  ] =
    useState<
      Figure222EvidenceResponse
      | null
    >(null);

  const [
    error,
    setError,
  ] =
    useState<
      string
      | null
    >(null);


  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const response =
          await getFigure222Evidence();

        if (!cancelled) {
          setData(response);
          setError(null);
        }
      } catch (
        caughtError
      ) {
        if (cancelled) {
          return;
        }

        setError(
          caughtError
            instanceof Error
            ? caughtError.message
            : (
              "Unable to load "
              + "Figure 2.22 evidence."
            ),
        );
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);


  const series = useMemo(
    () => {
      if (!data) {
        return [];
      }

      return Object.entries(
        data.series_counts,
      )
        .map(
          ([
            seriesKey,
            count,
          ]) => {
            const firstRecord =
              data.records.find(
                (record) =>
                  record.series_key
                  === seriesKey,
              );

            return {
              key: seriesKey,
              label:
                firstRecord
                  ?.series_label
                ?? humanize(
                  seriesKey,
                ),
              count,
              gravity:
                gravityLabel(
                  firstRecord
                    ?.gravity_context,
                ),
            };
          },
        )
        .sort(
          (left, right) =>
            right.count
            - left.count,
        );
    },
    [data],
  );


  const sortedRecords =
    useMemo(
      () => {
        if (!data) {
          return [];
        }

        return [
          ...data.records,
        ].sort(
          (
            left,
            right,
          ) => {
            const seriesCompare =
              left.series_label.localeCompare(
                right.series_label,
              );

            if (
              seriesCompare
              !== 0
            ) {
              return seriesCompare;
            }

            return (
              left.thickness_um
              - right.thickness_um
            );
          },
        );
      },
      [data],
    );


  if (!data && !error) {
    return (
      <section
        id="comparison-evidence"
        className="scroll-mt-24"
      >
        <div className="rounded-[28px] border border-white/[0.07] bg-white/[0.025] p-6 md:p-8">
          <div className="flex items-center gap-3">
            <span className="h-2 w-2 animate-pulse rounded-full bg-white/35" />

            <p className="text-sm text-white/45">
              Loading Figure 2.22
              comparison evidence…
            </p>
          </div>
        </div>
      </section>
    );
  }


  if (error || !data) {
    return (
      <section
        id="comparison-evidence"
        className="scroll-mt-24"
      >
        <div className="rounded-[28px] border border-red-300/15 bg-red-300/[0.035] p-6 md:p-8">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-red-200/55">
            Figure 2.22
          </p>

          <h2 className="mt-3 text-xl font-medium tracking-[-0.025em] text-red-50">
            Comparison evidence
            unavailable
          </h2>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-white/45">
            {error}
          </p>
        </div>
      </section>
    );
  }


  const gravity =
    data.gravity_context_counts;

  const duplicateCounts =
    data.duplicate_linkage_class_counts;


  return (
    <section
      id="comparison-evidence"
      className="scroll-mt-24"
    >
      <div className="overflow-hidden rounded-[30px] border border-white/[0.07] bg-[#090c11]">
        <div className="border-b border-white/[0.06] px-6 py-7 md:px-8 md:py-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-3xl">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-full border border-sky-300/15 bg-sky-300/[0.05] px-3 py-1 text-[10px] font-medium uppercase tracking-[0.16em] text-sky-200/70">
                  Figure 2.22
                </span>

                <span className="rounded-full border border-amber-300/15 bg-amber-300/[0.05] px-3 py-1 text-[10px] font-medium uppercase tracking-[0.16em] text-amber-100/65">
                  Comparison only
                </span>

                {data.dataset_sha256_verified ? (
                  <span className="rounded-full border border-emerald-300/15 bg-emerald-300/[0.05] px-3 py-1 text-[10px] font-medium uppercase tracking-[0.16em] text-emerald-200/65">
                    Integrity verified
                  </span>
                ) : null}
              </div>

              <h2 className="mt-5 text-2xl font-medium tracking-[-0.035em] text-white md:text-3xl">
                Within-source comparison
                evidence
              </h2>

              <p className="mt-4 max-w-2xl text-sm leading-6 text-white/45">
                Experimental points
                digitized from Figure 2.22
                are exposed as a separate
                comparison layer. They are
                not merged into the
                canonical Figure 2.21
                training evidence.
              </p>
            </div>

            <div className="rounded-2xl border border-amber-300/15 bg-amber-300/[0.035] p-4 lg:max-w-sm">
              <p className="text-[10px] font-medium uppercase tracking-[0.16em] text-amber-100/55">
                Scientific boundary
              </p>

              <p className="mt-2 text-sm leading-6 text-amber-50/70">
                Figure 2.22 is not
                independent external
                validation. Source identity,
                run linkage, and experimental
                conditions remain unresolved
                for part of this evidence.
              </p>
            </div>
          </div>
        </div>


        <div className="grid gap-px bg-white/[0.06] sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            label="Experimental points"
            value={String(
              data.experimental_point_count,
            )}
            detail="Human-overlay verified"
          />

          <MetricCard
            label="Training eligible"
            value={String(
              data.training_eligible_count,
            )}
            detail="Explicitly blocked"
          />

          <MetricCard
            label="Independent validation"
            value={String(
              data.independent_validation_eligible_count,
            )}
            detail="Not established"
          />

          <MetricCard
            label="Theory included"
            value={
              data.theoretical_curves_included
                ? "Yes"
                : "No"
            }
            detail="Experimental layer only"
          />
        </div>


        <div className="grid gap-6 p-6 md:p-8 xl:grid-cols-[minmax(0,1fr)_360px]">
          <div className="min-w-0">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-[10px] font-medium uppercase tracking-[0.17em] text-white/30">
                  Evidence records
                </p>

                <h3 className="mt-2 text-lg font-medium tracking-[-0.02em] text-white/90">
                  All 33 experimental
                  observations
                </h3>
              </div>

              <p className="text-xs text-white/30">
                Thickness → spread rate
              </p>
            </div>


            <div className="mt-5 overflow-hidden rounded-2xl border border-white/[0.07]">
              <div className="max-h-[520px] overflow-auto">
                <table className="w-full min-w-[760px] border-collapse text-left">
                  <thead className="sticky top-0 z-10 bg-[#0d1117]">
                    <tr className="border-b border-white/[0.07]">
                      <TableHeader>
                        Series
                      </TableHeader>

                      <TableHeader>
                        Gravity
                      </TableHeader>

                      <TableHeader>
                        Thickness
                      </TableHeader>

                      <TableHeader>
                        Spread rate
                      </TableHeader>

                      <TableHeader>
                        Linkage
                      </TableHeader>
                    </tr>
                  </thead>

                  <tbody>
                    {sortedRecords.map(
                      (
                        record,
                      ) => (
                        <tr
                          key={
                            record.record_id
                          }
                          className="border-b border-white/[0.045] last:border-b-0"
                        >
                          <TableCell>
                            <div>
                              <p className="font-medium text-white/75">
                                {
                                  record.series_label
                                }
                              </p>

                              <p className="mt-1 font-mono text-[9px] text-white/22">
                                {
                                  record.record_id
                                }
                              </p>
                            </div>
                          </TableCell>

                          <TableCell>
                            <span className="text-white/55">
                              {gravityLabel(
                                record.gravity_context,
                              )}
                            </span>
                          </TableCell>

                          <TableCell>
                            <span className="font-mono text-white/70">
                              {formatNumber(
                                record.thickness_um,
                              )}
                            </span>

                            <span className="ml-1 text-white/25">
                              µm
                            </span>
                          </TableCell>

                          <TableCell>
                            <span className="font-mono text-white/70">
                              {formatNumber(
                                record.observed_spread_rate_mm_s,
                                5,
                              )}
                            </span>

                            <span className="ml-1 text-white/25">
                              mm/s
                            </span>
                          </TableCell>

                          <TableCell>
                            <span
                              className={
                                record.duplicate_linkage
                                  ? (
                                    "text-amber-100/55"
                                  )
                                  : (
                                    "text-white/30"
                                  )
                              }
                            >
                              {duplicateLabel(
                                record,
                              )}
                            </span>
                          </TableCell>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>


          <div className="space-y-5">
            <InfoPanel
              eyebrow="Gravity context"
              title="What is resolved"
            >
              <CountRow
                label="Microgravity"
                value={
                  gravity.microgravity
                  ?? 0
                }
              />

              <CountRow
                label="Normal gravity"
                value={
                  gravity.normal_gravity
                  ?? 0
                }
              />

              <CountRow
                label="Unresolved"
                value={
                  gravity.unresolved
                  ?? 0
                }
                emphasize
              />
            </InfoPanel>


            <InfoPanel
              eyebrow="Series"
              title="Evidence breakdown"
            >
              <div className="space-y-3">
                {series.map(
                  (item) => (
                    <div
                      key={item.key}
                      className="flex items-center justify-between gap-4"
                    >
                      <div className="min-w-0">
                        <p className="truncate text-xs font-medium text-white/65">
                          {item.label}
                        </p>

                        <p className="mt-0.5 text-[10px] text-white/25">
                          {item.gravity}
                        </p>
                      </div>

                      <span className="font-mono text-xs text-white/55">
                        {item.count}
                      </span>
                    </div>
                  ),
                )}
              </div>
            </InfoPanel>


            <InfoPanel
              eyebrow="Duplicate review"
              title="Linkage candidates"
            >
              <CountRow
                label="Strong"
                value={
                  duplicateCounts[
                    "strong_duplicate_candidate"
                  ]
                  ?? 0
                }
              />

              <CountRow
                label="Moderate"
                value={
                  duplicateCounts[
                    "moderate_duplicate_candidate"
                  ]
                  ?? 0
                }
              />

              <CountRow
                label="Possible"
                value={
                  duplicateCounts[
                    "possible_duplicate_candidate"
                  ]
                  ?? 0
                }
              />

              <p className="pt-2 text-[11px] leading-5 text-white/30">
                Similarity flags review
                priority only. They do not
                prove same-run identity.
              </p>
            </InfoPanel>


            <InfoPanel
              eyebrow="Provenance"
              title="Frozen artifact"
            >
              <p className="text-xs leading-5 text-white/45">
                {
                  data.source_id
                }
                {" · Figure "}
                {
                  data.figure_ref
                }
                {" · "}
                {
                  data.dataset_version
                }
              </p>

              <div className="mt-3 rounded-xl border border-white/[0.06] bg-black/20 p-3">
                <p className="text-[9px] uppercase tracking-[0.14em] text-white/20">
                  SHA-256
                </p>

                <p className="mt-2 break-all font-mono text-[9px] leading-4 text-white/35">
                  {
                    data.dataset_sha256
                  }
                </p>
              </div>

              <p className="mt-3 text-[11px] leading-5 text-white/30">
                {
                  data.digitization_uncertainty_status
                    .replaceAll(
                      "_",
                      " ",
                    )
                }
              </p>
            </InfoPanel>
          </div>
        </div>


        <div className="border-t border-white/[0.06] px-6 py-6 md:px-8">
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
    <div className="bg-[#090c11] p-5 md:p-6">
      <p className="text-[9px] font-medium uppercase tracking-[0.16em] text-white/25">
        {label}
      </p>

      <p className="mt-3 font-mono text-2xl tracking-[-0.04em] text-white/90">
        {value}
      </p>

      <p className="mt-2 text-[10px] text-white/30">
        {detail}
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


function CountRow({
  label,
  value,
  emphasize = false,
}: {
  label: string;
  value: number;
  emphasize?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span
        className={
          emphasize
            ? "text-xs text-amber-100/55"
            : "text-xs text-white/45"
        }
      >
        {label}
      </span>

      <span
        className={
          emphasize
            ? "font-mono text-xs text-amber-100/70"
            : "font-mono text-xs text-white/60"
        }
      >
        {value}
      </span>
    </div>
  );
}


function TableHeader({
  children,
}: {
  children:
    React.ReactNode;
}) {
  return (
    <th className="px-4 py-3 text-[9px] font-medium uppercase tracking-[0.15em] text-white/25">
      {children}
    </th>
  );
}


function TableCell({
  children,
}: {
  children:
    React.ReactNode;
}) {
  return (
    <td className="px-4 py-3 text-xs">
      {children}
    </td>
  );
}
