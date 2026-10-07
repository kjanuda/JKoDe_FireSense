import type {
  NextExperimentExplanationResponse,
  NextExperimentRecommendationResponse,
} from "@/lib/api/contracts";


type DecisionTraceProps = {
  recommendation:
    NextExperimentRecommendationResponse;

  explanation:
    NextExperimentExplanationResponse;
};


function n(
  value: number,
  digits = 3,
) {
  return value.toFixed(digits);
}


export default function DecisionTrace({
  recommendation,
  explanation,
}: DecisionTraceProps) {
  const trace = [
    ...explanation.decision_trace,
  ].sort(
    (a, b) => a.order - b.order,
  );


  return (
    <section
      id="next-experiment"
      className="scroll-mt-20 border-b border-white/[0.07] py-16 lg:py-20"
    >
      <div className="mb-9">
        <p className="text-[11px] uppercase tracking-[0.22em] text-orange-300/70">
          Research decision trace
        </p>

        <h2 className="mt-3 text-3xl font-medium tracking-[-0.04em] lg:text-4xl">
          Why exactly{" "}
          <span className="text-orange-300">
            {n(
              recommendation.thickness_um,
            )}{" "}
            um?
          </span>
        </h2>

        <p className="mt-5 max-w-4xl text-sm leading-7 text-white/42">
          {explanation.summary}
        </p>
      </div>


      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <article className="rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-6">
          <p className="text-[10px] uppercase tracking-[0.2em] text-white/25">
            Coverage candidate
          </p>

          <p className="mt-5 text-4xl font-medium">
            {n(
              recommendation.agreement
                .coverage_candidate_um,
            )}
          </p>

          <p className="mt-1 text-xs text-white/30">
            um
          </p>

          <p className="mt-5 text-xs leading-6 text-white/38">
            Derived from spacing in the frozen
            Figure 2.21 evidence distribution.
          </p>
        </article>


        <article className="rounded-3xl border border-orange-300/15 bg-orange-300/[0.025] p-6">
          <p className="text-[10px] uppercase tracking-[0.2em] text-orange-200/55">
            Bayesian candidate
          </p>

          <p className="mt-5 text-4xl font-medium text-orange-100">
            {n(
              recommendation.agreement
                .bayesian_candidate_um,
            )}
          </p>

          <p className="mt-1 text-xs text-white/30">
            um
          </p>

          <p className="mt-5 text-xs leading-6 text-white/38">
            Prioritized by posterior uncertainty
            inside the shared empirical domain.
          </p>
        </article>


        <article className="rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-6">
          <p className="text-[10px] uppercase tracking-[0.2em] text-white/25">
            Agreement
          </p>

          <p className="mt-5 text-4xl font-medium">
            {n(
              recommendation.agreement
                .relative_difference_percent,
              2,
            )}
            %
          </p>

          <p className="mt-5 text-xs leading-6 text-white/38">
            Absolute difference{" "}
            {n(
              recommendation.agreement
                .absolute_difference_um,
            )}{" "}
            um.
          </p>

          <p className="mt-3 text-xs text-emerald-200">
            {recommendation.agreement
              .within_one_percent
              ? "✓ Within one percent"
              : "Outside one percent"}
          </p>
        </article>


        <article className="rounded-3xl border border-amber-300/15 bg-amber-300/[0.025] p-6">
          <p className="text-[10px] uppercase tracking-[0.2em] text-amber-200/55">
            Selected priority
          </p>

          <p className="mt-5 text-4xl font-medium text-amber-100">
            {n(
              recommendation.thickness_um,
            )}
          </p>

          <p className="mt-1 text-xs text-white/30">
            um PMMA
          </p>

          <p className="mt-5 font-mono text-[10px] leading-5 text-white/30">
            {recommendation.candidate_id}
          </p>

          <p className="mt-3 text-xs font-medium text-amber-200">
            NOT APPROVED
          </p>
        </article>
      </div>


      <div className="mt-6 rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-6 lg:p-8">
        <div>
          <p className="text-[10px] uppercase tracking-[0.22em] text-white/25">
            Backend decision trace
          </p>

          <h3 className="mt-2 text-xl font-medium">
            Evidence → coverage → Bayesian uncertainty → decision
          </h3>
        </div>


        <div className="mt-8 grid gap-3 xl:grid-cols-5">
          {trace.map(
            (step, index) => (
              <article
                key={`${step.order}-${step.stage}`}
                className="relative rounded-2xl border border-white/[0.07] bg-white/[0.018] p-5"
              >
                {index < trace.length - 1 && (
                  <div className="absolute -right-3 top-8 hidden h-px w-3 bg-orange-300/25 xl:block" />
                )}

                <div className="flex items-center justify-between gap-3">
                  <span className="font-mono text-[10px] text-orange-300/60">
                    {String(
                      step.order,
                    ).padStart(
                      2,
                      "0",
                    )}
                  </span>

                  <span className="rounded-full border border-white/[0.06] px-2 py-1 text-[9px] uppercase tracking-wider text-white/30">
                    {step.stage}
                  </span>
                </div>

                <h4 className="mt-5 text-sm font-medium">
                  {step.title}
                </h4>

                <p className="mt-3 text-xs leading-6 text-white/38">
                  {step.explanation}
                </p>
              </article>
            ),
          )}
        </div>
      </div>


      <div className="mt-6 grid gap-5 lg:grid-cols-[1fr_0.8fr]">
        <article className="rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-6">
          <p className="text-[10px] uppercase tracking-[0.2em] text-white/25">
            Scientific state
          </p>

          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/[0.06] p-4">
              <p className="text-[9px] uppercase tracking-wider text-white/25">
                Joint SD
              </p>

              <p className="mt-2 text-2xl font-medium">
                {n(
                  recommendation
                    .joint_uncertainty
                    .matched_pair_joint_sd_log,
                )}
              </p>

              <p className="mt-1 text-[10px] text-white/25">
                log space
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.06] p-4">
              <p className="text-[9px] uppercase tracking-wider text-white/25">
                MG prediction
              </p>

              <p className="mt-2 text-2xl font-medium">
                {n(
                  recommendation
                    .microgravity
                    .predicted_spread_rate_mm_s,
                )}
              </p>

              <p className="mt-1 text-[10px] text-white/25">
                mm/s
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.06] p-4">
              <p className="text-[9px] uppercase tracking-wider text-white/25">
                Normal prediction
              </p>

              <p className="mt-2 text-2xl font-medium">
                {n(
                  recommendation
                    .normal_gravity
                    .predicted_spread_rate_mm_s,
                )}
              </p>

              <p className="mt-1 text-[10px] text-white/25">
                mm/s
              </p>
            </div>
          </div>

          <div className="mt-5 rounded-2xl border border-amber-300/10 bg-amber-300/[0.025] p-4">
            <p className="text-xs leading-6 text-white/45">
              Coverage and Bayesian methods share
              the same frozen Figure 2.21 evidence.
              Agreement is internal convergence,
              not independent validation.
            </p>
          </div>
        </article>


        <article className="rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-6">
          <p className="text-[10px] uppercase tracking-[0.2em] text-white/25">
            Before approval
          </p>

          <div className="mt-5 space-y-3">
            {explanation
              .required_before_experiment_approval
              .map(
                (
                  requirement,
                  index,
                ) => (
                  <div
                    key={requirement}
                    className="flex gap-3 rounded-xl border border-white/[0.05] p-3"
                  >
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-white/[0.08] font-mono text-[9px] text-white/30">
                      {index + 1}
                    </span>

                    <p className="text-xs leading-6 text-white/42">
                      {requirement}
                    </p>
                  </div>
                ),
              )}
          </div>
        </article>
      </div>
    </section>
  );
}
