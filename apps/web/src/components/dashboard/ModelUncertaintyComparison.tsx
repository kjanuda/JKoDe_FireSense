import type {
  NextExperimentRecommendationResponse,
} from "@/lib/api/contracts";


type ModelUncertaintyComparisonProps = {
  recommendation:
    NextExperimentRecommendationResponse;
};


function n(
  value: number,
  digits = 3,
) {
  return value.toFixed(digits);
}


function percent(
  value: number,
  max: number,
) {
  if (
    !Number.isFinite(value)
    || !Number.isFinite(max)
    || max <= 0
  ) {
    return 0;
  }

  return Math.max(
    4,
    Math.min(
      100,
      (value / max) * 100,
    ),
  );
}


export default function ModelUncertaintyComparison({
  recommendation,
}: ModelUncertaintyComparisonProps) {
  const mg =
    recommendation.microgravity;

  const ng =
    recommendation.normal_gravity;

  const joint =
    recommendation.joint_uncertainty;


  const maxPrediction =
    Math.max(
      mg.predicted_spread_rate_mm_s,
      ng.predicted_spread_rate_mm_s,
    );


  const maxPosteriorSd =
    Math.max(
      mg.posterior_sd_log_residual,
      ng.posterior_sd_log_residual,
    );


  return (
    <section
      id="model-uncertainty"
      className="scroll-mt-20 border-b border-white/[0.07] py-16 lg:py-20"
    >
      <div className="mb-10">
        <p className="text-[11px] uppercase tracking-[0.22em] text-violet-300/70">
          Model uncertainty
        </p>

        <h2 className="mt-3 text-3xl font-medium tracking-[-0.04em] lg:text-4xl">
          Compare predicted behavior and uncertainty.
        </h2>

        <p className="mt-5 max-w-4xl text-sm leading-7 text-white/40">
          FireSense keeps predicted flame-spread
          behavior, posterior model uncertainty,
          and distance to existing evidence as
          separate quantities.
        </p>
      </div>


      <div className="grid gap-5 lg:grid-cols-2">
        <article className="rounded-3xl border border-orange-300/12 bg-[#0a0d12] p-6 lg:p-8">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[10px] uppercase tracking-[0.2em] text-orange-200/55">
                Microgravity
              </p>

              <h3 className="mt-2 text-xl font-medium">
                Predicted flame spread
              </h3>
            </div>

            <span className="rounded-full border border-orange-300/15 bg-orange-300/[0.04] px-3 py-1.5 text-[10px] text-orange-200">
              MG
            </span>
          </div>


          <div className="mt-8">
            <div className="flex items-end justify-between gap-4">
              <div>
                <p className="text-5xl font-medium tracking-[-0.05em]">
                  {n(
                    mg.predicted_spread_rate_mm_s,
                  )}
                </p>

                <p className="mt-1 text-xs text-white/30">
                  mm/s
                </p>
              </div>

              <p className="text-right text-[10px] uppercase tracking-wider text-white/25">
                at{" "}
                {n(
                  recommendation.thickness_um,
                )}{" "}
                um
              </p>
            </div>


            <div className="mt-6 h-2 overflow-hidden rounded-full bg-white/[0.05]">
              <div
                className="h-full rounded-full bg-orange-300/70"
                style={{
                  width:
                    `${percent(
                      mg.predicted_spread_rate_mm_s,
                      maxPrediction,
                    )}%`,
                }}
              />
            </div>

            <p className="mt-2 text-[10px] text-white/22">
              Relative visual scale only
            </p>
          </div>


          <div className="mt-8 border-t border-white/[0.06] pt-6">
            <div className="flex items-end justify-between gap-4">
              <div>
                <p className="text-[10px] uppercase tracking-wider text-white/25">
                  Posterior SD
                </p>

                <p className="mt-2 text-3xl font-medium">
                  {n(
                    mg.posterior_sd_log_residual,
                  )}
                </p>

                <p className="mt-1 text-[10px] text-white/25">
                  log-residual space
                </p>
              </div>
            </div>

            <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
              <div
                className="h-full rounded-full bg-violet-300/70"
                style={{
                  width:
                    `${percent(
                      mg.posterior_sd_log_residual,
                      maxPosteriorSd,
                    )}%`,
                }}
              />
            </div>
          </div>


          <div className="mt-7 grid grid-cols-2 gap-3">
            <div className="rounded-2xl border border-white/[0.06] p-4">
              <p className="text-[9px] uppercase tracking-wider text-white/25">
                Nearest observation
              </p>

              <p className="mt-2 text-xl font-medium">
                {n(
                  mg
                    .nearest_existing_observation
                    .thickness_um,
                )}
              </p>

              <p className="text-[10px] text-white/25">
                um
              </p>
            </div>


            <div className="rounded-2xl border border-white/[0.06] p-4">
              <p className="text-[9px] uppercase tracking-wider text-white/25">
                Absolute distance
              </p>

              <p className="mt-2 text-xl font-medium">
                {n(
                  mg
                    .nearest_existing_observation
                    .absolute_distance_um,
                )}
              </p>

              <p className="text-[10px] text-white/25">
                um
              </p>
            </div>
          </div>


          <p className="mt-4 text-[11px] text-white/25">
            Log-ratio distance:{" "}
            {n(
              mg
                .nearest_existing_observation
                .log_ratio_distance,
              4,
            )}
          </p>
        </article>


        <article className="rounded-3xl border border-sky-300/12 bg-[#0a0d12] p-6 lg:p-8">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[10px] uppercase tracking-[0.2em] text-sky-200/55">
                Normal gravity
              </p>

              <h3 className="mt-2 text-xl font-medium">
                Predicted flame spread
              </h3>
            </div>

            <span className="rounded-full border border-sky-300/15 bg-sky-300/[0.04] px-3 py-1.5 text-[10px] text-sky-200">
              NG
            </span>
          </div>


          <div className="mt-8">
            <div className="flex items-end justify-between gap-4">
              <div>
                <p className="text-5xl font-medium tracking-[-0.05em]">
                  {n(
                    ng.predicted_spread_rate_mm_s,
                  )}
                </p>

                <p className="mt-1 text-xs text-white/30">
                  mm/s
                </p>
              </div>

              <p className="text-right text-[10px] uppercase tracking-wider text-white/25">
                at{" "}
                {n(
                  recommendation.thickness_um,
                )}{" "}
                um
              </p>
            </div>


            <div className="mt-6 h-2 overflow-hidden rounded-full bg-white/[0.05]">
              <div
                className="h-full rounded-full bg-sky-300/70"
                style={{
                  width:
                    `${percent(
                      ng.predicted_spread_rate_mm_s,
                      maxPrediction,
                    )}%`,
                }}
              />
            </div>

            <p className="mt-2 text-[10px] text-white/22">
              Relative visual scale only
            </p>
          </div>


          <div className="mt-8 border-t border-white/[0.06] pt-6">
            <p className="text-[10px] uppercase tracking-wider text-white/25">
              Posterior SD
            </p>

            <p className="mt-2 text-3xl font-medium">
              {n(
                ng.posterior_sd_log_residual,
              )}
            </p>

            <p className="mt-1 text-[10px] text-white/25">
              log-residual space
            </p>

            <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/[0.05]">
              <div
                className="h-full rounded-full bg-violet-300/70"
                style={{
                  width:
                    `${percent(
                      ng.posterior_sd_log_residual,
                      maxPosteriorSd,
                    )}%`,
                }}
              />
            </div>
          </div>


          <div className="mt-7 grid grid-cols-2 gap-3">
            <div className="rounded-2xl border border-white/[0.06] p-4">
              <p className="text-[9px] uppercase tracking-wider text-white/25">
                Nearest observation
              </p>

              <p className="mt-2 text-xl font-medium">
                {n(
                  ng
                    .nearest_existing_observation
                    .thickness_um,
                )}
              </p>

              <p className="text-[10px] text-white/25">
                um
              </p>
            </div>


            <div className="rounded-2xl border border-white/[0.06] p-4">
              <p className="text-[9px] uppercase tracking-wider text-white/25">
                Absolute distance
              </p>

              <p className="mt-2 text-xl font-medium">
                {n(
                  ng
                    .nearest_existing_observation
                    .absolute_distance_um,
                )}
              </p>

              <p className="text-[10px] text-white/25">
                um
              </p>
            </div>
          </div>


          <p className="mt-4 text-[11px] text-white/25">
            Log-ratio distance:{" "}
            {n(
              ng
                .nearest_existing_observation
                .log_ratio_distance,
              4,
            )}
          </p>
        </article>
      </div>


      <div className="mt-5 grid gap-5 lg:grid-cols-3">
        <article className="rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-6">
          <p className="text-[10px] uppercase tracking-[0.2em] text-white/25">
            Predicted MG / NG ratio
          </p>

          <p className="mt-4 text-4xl font-medium">
            {n(
              joint
                .predicted_mg_to_ng_spread_ratio,
            )}
            x
          </p>

          <p className="mt-4 text-xs leading-6 text-white/35">
            Describes the model-predicted spread-rate
            relationship at the selected matched
            thickness.
          </p>
        </article>


        <article className="rounded-3xl border border-violet-300/12 bg-violet-300/[0.02] p-6">
          <p className="text-[10px] uppercase tracking-[0.2em] text-violet-200/55">
            Joint uncertainty
          </p>

          <p className="mt-4 text-4xl font-medium">
            {n(
              joint
                .matched_pair_joint_sd_log,
            )}
          </p>

          <p className="mt-1 text-xs text-white/25">
            posterior SD · log space
          </p>
        </article>


        <article className="rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-6">
          <p className="text-[10px] uppercase tracking-[0.2em] text-white/25">
            One-SD ratio factor
          </p>

          <p className="mt-4 text-4xl font-medium">
            {n(
              joint
                .one_sd_ratio_uncertainty_factor,
            )}
            x
          </p>

          <p className="mt-4 text-xs leading-6 text-white/35">
            Model uncertainty summary only.
            It is not an externally calibrated
            confidence interval.
          </p>
        </article>
      </div>


      <div className="mt-5 rounded-2xl border border-amber-300/10 bg-amber-300/[0.02] px-5 py-4">
        <p className="text-[11px] leading-6 text-white/35">
          Posterior standard deviations describe the
          v0 Gaussian-process model state in
          log-residual space. They are not calibrated
          confidence intervals, experimental
          uncertainty, or external validation.
        </p>
      </div>
    </section>
  );
}
