"use client";

import {
  useMemo,
  useState,
} from "react";

import {
  CartesianGrid,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type {
  ExplainedPredictionResponse,
  FireBehaviorPredictionRequest,
  NextExperimentRecommendationResponse,
} from "@/lib/api/contracts";

import {
  FIGURE_221_DATASET_VERSION,
  FIGURE_221_DIGITIZATION_UNCERTAINTY_MM_S,
  FIGURE_221_MICROGRAVITY_POINTS,
  FIGURE_221_NORMAL_GRAVITY_POINTS,
  FIGURE_221_REF,
  FIGURE_221_SOURCE_ID,
  FIGURE_221_SUPPORTED_DOMAINS,
  type Figure221GravityRegime,
  type Figure221Point,
} from "@/lib/evidence/figure221";


type EvidenceMapProps = {
  recommendation:
    NextExperimentRecommendationResponse;

  activeQuery:
    FireBehaviorPredictionRequest | null;

  activePrediction:
    ExplainedPredictionResponse | null;
};


type GapSummary = {
  gravity_regime: Figure221GravityRegime;
  start_um: number;
  end_um: number;
  geometric_mid_um: number;
  log_width: number;
};


function formatNumber(
  value: number,
  digits = 3,
) {
  return value.toFixed(digits);
}


function findLargestLogGap(
  points: Figure221Point[],
  gravityRegime: Figure221GravityRegime,
): GapSummary {
  const sorted = [...points].sort(
    (a, b) =>
      a.thickness_um - b.thickness_um,
  );

  if (sorted.length < 2) {
    throw new Error(
      "At least two evidence points are required.",
    );
  }

  let bestStart =
    sorted[0].thickness_um;

  let bestEnd =
    sorted[1].thickness_um;

  let bestWidth =
    Math.log(bestEnd / bestStart);


  for (
    let index = 1;
    index < sorted.length - 1;
    index += 1
  ) {
    const start =
      sorted[index].thickness_um;

    const end =
      sorted[index + 1].thickness_um;

    const width =
      Math.log(end / start);

    if (width > bestWidth) {
      bestStart = start;
      bestEnd = end;
      bestWidth = width;
    }
  }


  return {
    gravity_regime: gravityRegime,
    start_um: bestStart,
    end_um: bestEnd,
    geometric_mid_um:
      Math.sqrt(bestStart * bestEnd),
    log_width: bestWidth,
  };
}


function isFigure221Point(
  value: unknown,
): value is Figure221Point {
  if (
    typeof value !== "object"
    || value === null
  ) {
    return false;
  }

  const point =
    value as Partial<Figure221Point>;

  return (
    typeof point.plot_point_id === "string"
    && (
      point.gravity_regime
        === "microgravity"
      || point.gravity_regime
        === "normal_gravity"
    )
    && typeof point.thickness_um
      === "number"
    && typeof point.spread_rate_mm_s
      === "number"
  );
}


export default function EvidenceMap({
  recommendation,
  activeQuery,
  activePrediction,
}: EvidenceMapProps) {
  const [
    manualSelection,
    setManualSelection,
  ] = useState<{
    point: Figure221Point;
    queryKey: string;
  } | null>(null);


  const microgravityGap =
    useMemo(
      () =>
        findLargestLogGap(
          FIGURE_221_MICROGRAVITY_POINTS,
          "microgravity",
        ),
      [],
    );


  const normalGravityGap =
    useMemo(
      () =>
        findLargestLogGap(
          FIGURE_221_NORMAL_GRAVITY_POINTS,
          "normal_gravity",
        ),
      [],
    );


  const allObservedPoints =
    useMemo(
      () => [
        ...FIGURE_221_MICROGRAVITY_POINTS,
        ...FIGURE_221_NORMAL_GRAVITY_POINTS,
      ],
      [],
    );


  const candidateThickness =
    recommendation.thickness_um;


  const activeResult =
    activePrediction?.result ?? null;


  const activeQueryInChart =
    activeQuery
    && activeQuery.thickness_um >= 20
    && activeQuery.thickness_um <= 800
      ? activeQuery
      : null;


  const livePredictionPoint =
    activeQueryInChart
    && activeResult?.decision === "predict"
    && activeResult.prediction
      ? [
          {
            thickness_um:
              activeQueryInChart
                .thickness_um,

            spread_rate_mm_s:
              activeResult
                .prediction
                .value,
          },
        ]
      : [];


  const nearestEvidencePoints =
    activePrediction
      ?.evidence_trace
      .nearest_evidence_records
      .map((record) => ({
        record_id:
          record.record_id,

        gravity_regime:
          record.gravity_regime,

        thickness_um:
          record.thickness_um,

        spread_rate_mm_s:
          record
            .observed_spread_rate_mm_s,
      }))
    ?? [];


  const activeQueryKey =
    activeQuery
    && activePrediction
      ? [
          activeQuery.gravity_regime,
          activeQuery.thickness_um,
          activePrediction.result.decision,
          activePrediction.result
            .prediction?.value
            ?? "abstain",
        ].join(":")
      : "no-query";


  const autoSelectedPoint =
    useMemo(() => {
      const nearest =
        activePrediction
          ?.evidence_trace
          .nearest_evidence_records[0];

      if (!nearest) {
        return null;
      }

      return (
        allObservedPoints.find(
          (point) =>
            point.gravity_regime
              === nearest.gravity_regime
            && Math.abs(
              point.thickness_um
                - nearest.thickness_um,
            ) < 0.001,
        )
        ?? null
      );
    }, [
      activePrediction,
      allObservedPoints,
    ]);


  const selectedPoint =
    manualSelection?.queryKey
      === activeQueryKey
      ? manualSelection.point
      : autoSelectedPoint;


  function selectPoint(
    point: Figure221Point,
  ) {
    setManualSelection({
      point,
      queryKey: activeQueryKey,
    });
  }


  const selectedPointMarker =
    selectedPoint
      ? [selectedPoint]
      : [];


  const microgravityCandidate = [
    {
      thickness_um:
        candidateThickness,

      spread_rate_mm_s:
        recommendation.microgravity
          .predicted_spread_rate_mm_s,
    },
  ];


  const normalGravityCandidate = [
    {
      thickness_um:
        candidateThickness,

      spread_rate_mm_s:
        recommendation.normal_gravity
          .predicted_spread_rate_mm_s,
    },
  ];


  function handlePointClick(
    entry: unknown,
  ) {
    if (isFigure221Point(entry)) {
      selectPoint(entry);
      return;
    }

    if (
      typeof entry === "object"
      && entry !== null
      && "payload" in entry
    ) {
      const payload = (
        entry as {
          payload?: unknown;
        }
      ).payload;

      if (isFigure221Point(payload)) {
        selectPoint(payload);
      }
    }
  }


  return (
    <section
      id="evidence-map"
      className="scroll-mt-20 border-b border-white/[0.07] py-16 lg:py-20"
    >
      <div className="mb-9 flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
        <div>
          <p className="text-[11px] uppercase tracking-[0.22em] text-sky-300/70">
            Canonical evidence
          </p>

          <h2 className="mt-3 text-3xl font-medium tracking-[-0.035em]">
            Figure 2.21 evidence map
          </h2>

          <p className="mt-4 max-w-3xl text-sm leading-7 text-white/40">
            Experimental PMMA thin-sheet
            flame-spread observations across
            thickness, separated by gravity regime.
            Theory is intentionally excluded from
            this evidence layer.
          </p>
        </div>


        <div className="flex flex-wrap gap-2">
          <span className="rounded-full border border-white/[0.08] px-3 py-1.5 font-mono text-[10px] text-white/35">
            {FIGURE_221_SOURCE_ID}
          </span>

          <span className="rounded-full border border-white/[0.08] px-3 py-1.5 text-[10px] text-white/35">
            {FIGURE_221_REF}
          </span>

          <span className="rounded-full border border-white/[0.08] px-3 py-1.5 text-[10px] text-white/35">
            Dataset {FIGURE_221_DATASET_VERSION}
          </span>
        </div>
      </div>


      <div className="grid gap-5 xl:grid-cols-[1.4fr_0.6fr]">
        <article className="overflow-hidden rounded-3xl border border-white/[0.08] bg-[#0a0d12]">
          <div className="flex flex-col justify-between gap-4 border-b border-white/[0.06] p-6 md:flex-row md:items-center">
            <div>
              <p className="text-sm font-medium">
                Flame spread rate vs thickness
              </p>

              <p className="mt-1 text-xs text-white/30">
                Logarithmic axes · click an observed
                point to inspect it
              </p>
            </div>


            <div className="flex flex-wrap gap-4 text-[11px] text-white/40">
              <span className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-orange-300" />

                Microgravity
              </span>

              <span className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-sky-300" />

                Normal gravity
              </span>

              <span className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rotate-45 bg-white" />

                Model candidate
              </span>

              <span className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-violet-300" />

                Live predictor query
              </span>
            </div>
          </div>


          <div className="h-[540px] w-full p-4 sm:p-6">
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <ScatterChart
                margin={{
                  top: 20,
                  right: 25,
                  bottom: 35,
                  left: 15,
                }}
              >
                <CartesianGrid
                  stroke="rgba(255,255,255,0.06)"
                  strokeDasharray="3 3"
                />


                <ReferenceArea
                  x1={
                    microgravityGap.start_um
                  }
                  x2={
                    microgravityGap.end_um
                  }
                  fill="#fdba74"
                  fillOpacity={0.055}
                  stroke="#fdba74"
                  strokeOpacity={0.13}
                  strokeDasharray="4 4"
                />


                <ReferenceArea
                  x1={
                    normalGravityGap.start_um
                  }
                  x2={
                    normalGravityGap.end_um
                  }
                  fill="#7dd3fc"
                  fillOpacity={0.035}
                  stroke="#7dd3fc"
                  strokeOpacity={0.11}
                  strokeDasharray="4 4"
                />


                <XAxis
                  type="number"
                  dataKey="thickness_um"
                  name="Thickness"
                  unit=" um"
                  scale="log"
                  domain={[20, 800]}
                  ticks={[
                    25,
                    50,
                    100,
                    200,
                    400,
                    800,
                  ]}
                  tick={{
                    fill:
                      "rgba(255,255,255,0.38)",
                    fontSize: 11,
                  }}
                  axisLine={{
                    stroke:
                      "rgba(255,255,255,0.12)",
                  }}
                  tickLine={{
                    stroke:
                      "rgba(255,255,255,0.12)",
                  }}
                  label={{
                    value: "Thickness (um)",
                    position: "insideBottom",
                    offset: -22,
                    fill:
                      "rgba(255,255,255,0.35)",
                    fontSize: 11,
                  }}
                />


                <YAxis
                  type="number"
                  dataKey="spread_rate_mm_s"
                  name="Spread rate"
                  unit=" mm/s"
                  scale="log"
                  domain={[0.15, 10]}
                  ticks={[
                    0.2,
                    0.5,
                    1,
                    2,
                    5,
                    10,
                  ]}
                  tick={{
                    fill:
                      "rgba(255,255,255,0.38)",
                    fontSize: 11,
                  }}
                  axisLine={{
                    stroke:
                      "rgba(255,255,255,0.12)",
                  }}
                  tickLine={{
                    stroke:
                      "rgba(255,255,255,0.12)",
                  }}
                  width={60}
                  label={{
                    value:
                      "Spread rate (mm/s)",
                    angle: -90,
                    position: "insideLeft",
                    fill:
                      "rgba(255,255,255,0.35)",
                    fontSize: 11,
                  }}
                />


                <Tooltip
                  cursor={{
                    stroke:
                      "rgba(255,255,255,0.15)",
                    strokeDasharray: "3 3",
                  }}
                  contentStyle={{
                    background: "#0d1117",
                    border:
                      "1px solid rgba(255,255,255,0.12)",
                    borderRadius: "12px",
                    fontSize: "12px",
                  }}
                />


                <ReferenceLine
                  x={candidateThickness}
                  stroke="#ffffff"
                  strokeOpacity={0.4}
                  strokeDasharray="5 5"
                  label={{
                    value:
                      `${formatNumber(
                        candidateThickness,
                        1,
                      )} um candidate`,

                    position: "top",

                    fill:
                      "rgba(255,255,255,0.55)",

                    fontSize: 10,
                  }}
                />


                {activeQueryInChart && (
                  <ReferenceLine
                    x={
                      activeQueryInChart
                        .thickness_um
                    }
                    stroke="#c4b5fd"
                    strokeOpacity={0.7}
                    strokeDasharray="2 4"
                    label={{
                      value:
                        `${formatNumber(
                          activeQueryInChart
                            .thickness_um,
                          1,
                        )} um query`,

                      position: "insideTopRight",

                      fill: "#c4b5fd",

                      fontSize: 10,
                    }}
                  />
                )}


                <Scatter
                  name="Microgravity observed"
                  data={
                    FIGURE_221_MICROGRAVITY_POINTS
                  }
                  fill="#fdba74"
                  onClick={handlePointClick}
                />


                <Scatter
                  name="Normal gravity observed"
                  data={
                    FIGURE_221_NORMAL_GRAVITY_POINTS
                  }
                  fill="#7dd3fc"
                  onClick={handlePointClick}
                />


                {nearestEvidencePoints.length > 0 && (
                  <Scatter
                    name="Nearest evidence"
                    data={
                      nearestEvidencePoints
                    }
                    fill="transparent"
                    stroke="#86efac"
                    strokeWidth={3}
                  />
                )}


                {selectedPointMarker.length > 0 && (
                  <Scatter
                    name="Selected evidence point"
                    data={
                      selectedPointMarker
                    }
                    fill="transparent"
                    stroke="#ffffff"
                    strokeWidth={4}
                  />
                )}


                {livePredictionPoint.length > 0 && (
                  <Scatter
                    name="Live predictor result"
                    data={
                      livePredictionPoint
                    }
                    fill="#c4b5fd"
                    stroke="#ffffff"
                    strokeWidth={1.5}
                    shape="star"
                  />
                )}


                <Scatter
                  name="Microgravity candidate prediction"
                  data={microgravityCandidate}
                  fill="#ffffff"
                  shape="diamond"
                />


                <Scatter
                  name="Normal gravity candidate prediction"
                  data={normalGravityCandidate}
                  fill="#ffffff"
                  shape="diamond"
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>


          <div className="grid border-t border-white/[0.06] sm:grid-cols-3">
            <div className="p-5 sm:border-r sm:border-white/[0.06]">
              <p className="text-[10px] uppercase tracking-wider text-white/25">
                Experimental points
              </p>

              <p className="mt-2 text-xl font-medium">
                13
              </p>

              <p className="mt-1 text-xs text-white/30">
                4 MG + 9 normal gravity
              </p>
            </div>


            <div className="p-5 sm:border-r sm:border-white/[0.06]">
              <p className="text-[10px] uppercase tracking-wider text-white/25">
                Bayesian candidate
              </p>

              <p className="mt-2 text-xl font-medium text-orange-200">
                {formatNumber(
                  candidateThickness,
                  3,
                )}{" "}
                um
              </p>

              <p className="mt-1 text-xs text-white/30">
                Model output · not observation
              </p>
            </div>


            <div className="p-5">
              <p className="text-[10px] uppercase tracking-wider text-white/25">
                Digitization uncertainty
              </p>

              <p className="mt-2 text-xl font-medium">
                ±
                {formatNumber(
                  FIGURE_221_DIGITIZATION_UNCERTAINTY_MM_S,
                  6,
                )}
              </p>

              <p className="mt-1 text-xs text-white/30">
                mm/s · not experimental uncertainty
              </p>
            </div>
          </div>
        </article>


        <aside className="space-y-5">
          <article className="rounded-3xl border border-violet-300/15 bg-violet-300/[0.025] p-6">
            <p className="text-[10px] uppercase tracking-[0.2em] text-violet-200/65">
              Live predictor link
            </p>

            {!activeQuery
              || !activePrediction ? (
              <div className="mt-4">
                <p className="text-sm text-white/45">
                  No predictor query yet.
                </p>

                <p className="mt-2 text-xs leading-6 text-white/28">
                  Run the Fire Behavior Predictor
                  above to project the query onto
                  this evidence map.
                </p>
              </div>
            ) : (
              <div className="mt-5">
                <div className="flex items-end justify-between gap-4">
                  <div>
                    <p className="text-3xl font-medium text-violet-100">
                      {formatNumber(
                        activeQuery
                          .thickness_um,
                        3,
                      )}{" "}
                      um
                    </p>

                    <p className="mt-1 text-xs text-white/35">
                      {
                        activeQuery
                          .gravity_regime
                      }
                    </p>
                  </div>

                  <span
                    className={[
                      "rounded-full border px-2.5 py-1 text-[10px] uppercase tracking-wider",
                      activePrediction
                        .result
                        .decision
                        === "predict"
                        ? "border-emerald-300/20 bg-emerald-300/[0.05] text-emerald-200"
                        : "border-amber-300/20 bg-amber-300/[0.05] text-amber-200",
                    ].join(" ")}
                  >
                    {
                      activePrediction
                        .result
                        .decision
                    }
                  </span>
                </div>


                {activePrediction
                  .result
                  .decision === "predict"
                  && activePrediction
                    .result
                    .prediction && (
                    <div className="mt-5 rounded-2xl border border-white/[0.06] p-4">
                      <p className="text-[9px] uppercase tracking-wider text-white/25">
                        Predicted spread rate
                      </p>

                      <p className="mt-2 text-2xl font-medium">
                        {formatNumber(
                          activePrediction
                            .result
                            .prediction
                            .value,
                          4,
                        )}{" "}
                        <span className="text-xs font-normal text-white/30">
                          {
                            activePrediction
                              .result
                              .prediction
                              .unit
                          }
                        </span>
                      </p>
                    </div>
                  )}


                {activePrediction
                  .result
                  .decision === "abstain" && (
                    <div className="mt-5 rounded-2xl border border-amber-300/10 bg-amber-300/[0.025] p-4">
                      <p className="text-xs font-medium text-amber-200">
                        No numeric prediction
                      </p>

                      <div className="mt-3 space-y-2">
                        {
                          activePrediction
                            .result
                            .abstention_reasons
                            .map((reason) => (
                              <p
                                key={reason}
                                className="text-xs leading-5 text-white/40"
                              >
                                ? {reason}
                              </p>
                            ))
                        }
                      </div>
                    </div>
                  )}


                <div className="mt-5 border-t border-white/[0.06] pt-4">
                  <p className="text-[9px] uppercase tracking-wider text-white/25">
                    Nearest evidence
                  </p>

                  <div className="mt-3 space-y-2">
                    {
                      activePrediction
                        .evidence_trace
                        .nearest_evidence_records
                        .map((record) => (
                          <div
                            key={
                              record.record_id
                            }
                            className="flex items-center justify-between gap-3 rounded-xl border border-white/[0.05] px-3 py-2"
                          >
                            <div>
                              <p className="font-mono text-[9px] text-white/30">
                                {
                                  record
                                    .record_id
                                }
                              </p>

                              <p className="mt-1 text-xs text-white/45">
                                {formatNumber(
                                  record
                                    .thickness_um,
                                  3,
                                )}{" "}
                                um
                              </p>
                            </div>

                            <p className="text-xs text-emerald-200/70">
                              {formatNumber(
                                record
                                  .observed_spread_rate_mm_s,
                                4,
                              )}{" "}
                              mm/s
                            </p>
                          </div>
                        ))
                    }
                  </div>
                </div>


                {!activeQueryInChart && (
                  <p className="mt-4 text-[11px] leading-5 text-amber-200/55">
                    This query lies outside the
                    current 20?800 um chart window,
                    so its vertical marker is not
                    shown.
                  </p>
                )}
              </div>
            )}
          </article>
          <article className="rounded-3xl border border-sky-300/10 bg-[#0a0d12] p-6">
            <p className="text-[10px] uppercase tracking-[0.2em] text-sky-200/60">
              Evidence-gap map
            </p>

            <h3 className="mt-3 text-xl font-medium">
              Largest spacing gaps
            </h3>

            <p className="mt-3 text-xs leading-6 text-white/35">
              These are coverage gaps in log
              thickness only. They are not calibrated
              uncertainty intervals.
            </p>


            <div className="mt-6 rounded-2xl border border-orange-300/10 bg-orange-300/[0.025] p-4">
              <p className="text-[10px] uppercase tracking-wider text-orange-200/55">
                Microgravity
              </p>

              <p className="mt-2 text-lg font-medium">
                {formatNumber(
                  microgravityGap.start_um,
                  3,
                )}
                {" → "}
                {formatNumber(
                  microgravityGap.end_um,
                  3,
                )}
              </p>

              <p className="mt-2 text-xs text-white/30">
                Geometric midpoint{" "}
                {formatNumber(
                  microgravityGap
                    .geometric_mid_um,
                  3,
                )}{" "}
                um
              </p>
            </div>


            <div className="mt-3 rounded-2xl border border-sky-300/10 bg-sky-300/[0.02] p-4">
              <p className="text-[10px] uppercase tracking-wider text-sky-200/55">
                Normal gravity
              </p>

              <p className="mt-2 text-lg font-medium">
                {formatNumber(
                  normalGravityGap.start_um,
                  3,
                )}
                {" → "}
                {formatNumber(
                  normalGravityGap.end_um,
                  3,
                )}
              </p>

              <p className="mt-2 text-xs text-white/30">
                Geometric midpoint{" "}
                {formatNumber(
                  normalGravityGap
                    .geometric_mid_um,
                  3,
                )}{" "}
                um
              </p>
            </div>


            <div className="mt-4 border-t border-white/[0.06] pt-4">
              <p className="text-[10px] uppercase tracking-wider text-white/25">
                Frozen coverage candidate
              </p>

              <p className="mt-2 text-xl font-medium">
                {formatNumber(
                  recommendation.agreement
                    .coverage_candidate_um,
                  3,
                )}{" "}
                um
              </p>
            </div>
          </article>


          <article className="rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-6">
            <p className="text-[10px] uppercase tracking-[0.2em] text-white/25">
              Point inspector
            </p>

            {!selectedPoint && (
              <div className="mt-5 rounded-2xl border border-dashed border-white/[0.09] p-5">
                <p className="text-sm text-white/45">
                  Select an experimental point
                  on the chart.
                </p>

                <p className="mt-2 text-xs leading-5 text-white/25">
                  Candidate diamonds are model
                  outputs and cannot be inspected
                  as observations.
                </p>
              </div>
            )}


            {selectedPoint && (
              <div className="mt-5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="font-mono text-xs text-white/35">
                      {
                        selectedPoint
                          .plot_point_id
                      }
                    </p>

                    <p className="mt-1 text-sm font-medium">
                      {
                        selectedPoint
                          .gravity_regime
                      }
                    </p>
                  </div>

                  <span
                    className={[
                      "h-3 w-3 rounded-full",
                      selectedPoint.gravity_regime
                        === "microgravity"
                        ? "bg-orange-300"
                        : "bg-sky-300",
                    ].join(" ")}
                  />
                </div>


                <div className="mt-6 grid grid-cols-2 gap-3">
                  <div className="rounded-xl border border-white/[0.06] p-3">
                    <p className="text-[9px] uppercase tracking-wider text-white/25">
                      Thickness
                    </p>

                    <p className="mt-2 text-lg font-medium">
                      {formatNumber(
                        selectedPoint
                          .thickness_um,
                        3,
                      )}
                    </p>

                    <p className="text-[10px] text-white/25">
                      um
                    </p>
                  </div>


                  <div className="rounded-xl border border-white/[0.06] p-3">
                    <p className="text-[9px] uppercase tracking-wider text-white/25">
                      Observed spread
                    </p>

                    <p className="mt-2 text-lg font-medium">
                      {formatNumber(
                        selectedPoint
                          .spread_rate_mm_s,
                        4,
                      )}
                    </p>

                    <p className="text-[10px] text-white/25">
                      mm/s
                    </p>
                  </div>
                </div>


                <div className="mt-4 space-y-3 border-t border-white/[0.06] pt-4 text-xs">
                  <div className="flex justify-between gap-4">
                    <span className="text-white/25">
                      Source
                    </span>

                    <span className="text-right font-mono text-white/45">
                      {FIGURE_221_SOURCE_ID}
                    </span>
                  </div>

                  <div className="flex justify-between gap-4">
                    <span className="text-white/25">
                      Figure
                    </span>

                    <span className="text-white/45">
                      {FIGURE_221_REF}
                    </span>
                  </div>

                  <div className="flex justify-between gap-4">
                    <span className="text-white/25">
                      Digitization uncertainty
                    </span>

                    <span className="text-white/45">
                      ±
                      {formatNumber(
                        FIGURE_221_DIGITIZATION_UNCERTAINTY_MM_S,
                        6,
                      )}{" "}
                      mm/s
                    </span>
                  </div>
                </div>


                <p className="mt-5 text-[11px] leading-5 text-white/25">
                  Plot-point ID is a visualization
                  identifier, not proof of a distinct
                  independent experiment.
                </p>
              </div>
            )}


            <div className="mt-6 border-t border-white/[0.06] pt-5">
              <p className="text-[9px] uppercase tracking-[0.18em] text-white/25">
                Accessible evidence points
              </p>

              <p className="mt-2 text-[11px] leading-5 text-white/28">
                Use Tab to move through observations.
                Press Enter or Space to inspect one.
              </p>

              <div className="mt-4 grid max-h-64 gap-2 overflow-y-auto pr-1">
                {allObservedPoints.map(
                  (point) => {
                    const selected =
                      selectedPoint
                        ?.plot_point_id
                      === point.plot_point_id;

                    return (
                      <button
                        key={
                          point.plot_point_id
                        }
                        type="button"
                        onClick={() =>
                          selectPoint(
                            point,
                          )
                        }
                        aria-pressed={
                          selected
                        }
                        className={[
                          "flex w-full items-center justify-between gap-4 rounded-xl border px-3 py-3 text-left transition",
                          selected
                            ? "border-white/25 bg-white/[0.06]"
                            : "border-white/[0.05] hover:border-white/15 hover:bg-white/[0.025]",
                        ].join(" ")}
                      >
                        <div className="flex items-center gap-3">
                          <span
                            className={[
                              "h-2.5 w-2.5 shrink-0 rounded-full",
                              point.gravity_regime
                                === "microgravity"
                                ? "bg-orange-300"
                                : "bg-sky-300",
                            ].join(" ")}
                          />

                          <div>
                            <p className="font-mono text-[9px] text-white/30">
                              {
                                point
                                  .plot_point_id
                              }
                            </p>

                            <p className="mt-1 text-xs text-white/50">
                              {formatNumber(
                                point
                                  .thickness_um,
                                3,
                              )}{" "}
                              um
                            </p>
                          </div>
                        </div>

                        <p className="text-xs text-white/40">
                          {formatNumber(
                            point
                              .spread_rate_mm_s,
                            4,
                          )}{" "}
                          mm/s
                        </p>
                      </button>
                    );
                  },
                )}
              </div>
            </div>
          </article>


          <article className="rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-6">
            <p className="text-[10px] uppercase tracking-[0.2em] text-white/25">
              Supported domains
            </p>

            <div className="mt-5">
              <p className="text-xs text-white/30">
                Microgravity
              </p>

              <p className="mt-1 text-xl font-medium">
                {
                  FIGURE_221_SUPPORTED_DOMAINS
                    .microgravity
                    .min_thickness_um
                }
                <span className="mx-2 text-white/20">
                  →
                </span>
                {
                  FIGURE_221_SUPPORTED_DOMAINS
                    .microgravity
                    .max_thickness_um
                }
              </p>
            </div>


            <div className="mt-5 border-t border-white/[0.06] pt-5">
              <p className="text-xs text-white/30">
                Normal gravity
              </p>

              <p className="mt-1 text-xl font-medium">
                {
                  FIGURE_221_SUPPORTED_DOMAINS
                    .normal_gravity
                    .min_thickness_um
                }
                <span className="mx-2 text-white/20">
                  →
                </span>
                {
                  FIGURE_221_SUPPORTED_DOMAINS
                    .normal_gravity
                    .max_thickness_um
                }
              </p>
            </div>


            <p className="mt-5 text-xs leading-6 text-white/32">
              Prediction outside the matching
              supported domain should abstain rather
              than extrapolate.
            </p>
          </article>


          <article className="rounded-3xl border border-orange-300/10 bg-orange-300/[0.035] p-6">
            <p className="text-[10px] uppercase tracking-[0.2em] text-orange-200/60">
              Bayesian priority
            </p>

            <p className="mt-4 text-3xl font-medium text-orange-100">
              {formatNumber(
                recommendation.thickness_um,
                3,
              )}{" "}
              um
            </p>

            <p className="mt-4 text-xs leading-6 text-white/40">
              This is a research-priority
              matched-pair candidate, not an
              approved experiment.
            </p>
          </article>
        </aside>
      </div>


      <div className="mt-5 rounded-2xl border border-white/[0.06] bg-white/[0.015] px-5 py-4">
        <p className="text-[11px] leading-6 text-white/30">
          Shaded vertical regions show the largest
          spacing gaps in each gravity regime on a
          logarithmic thickness axis. They visualize
          evidence coverage only; they are not
          posterior confidence intervals, experimental
          approval regions, or external validation.
        </p>
      </div>
    </section>
  );
}
