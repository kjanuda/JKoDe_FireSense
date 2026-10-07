"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  FireSenseApiError,
  getNextExperimentExplanation,
  getNextExperimentRecommendation,
} from "@/lib/api/client";

import type {
  ExplainedPredictionResponse,
  FireBehaviorPredictionRequest,
  NextExperimentExplanationResponse,
  NextExperimentRecommendationResponse,
} from "@/lib/api/contracts";

import FireBehaviorPredictor from "./FireBehaviorPredictor";
import EvidenceMap from "./EvidenceMap";
import Figure222ComparisonEvidence from "./Figure222ComparisonEvidence";
import ExternalComparisonEvidence from "./ExternalComparisonEvidence";
import ValidationReadinessPanel from "./ValidationReadinessPanel";
import ValidationReleaseStatusPanel from "./ValidationReleaseStatusPanel";
import DecisionTrace from "./DecisionTrace";
import ModelUncertaintyComparison from "./ModelUncertaintyComparison";


function formatNumber(
  value: number | undefined,
  digits = 3,
) {
  if (value === undefined) {
    return "—";
  }

  return value.toFixed(digits);
}


function StatusDot({
  ok,
}: {
  ok: boolean;
}) {
  return (
    <span
      className={[
        "inline-block h-2 w-2 rounded-full",
        ok
          ? "bg-emerald-400"
          : "bg-amber-400",
      ].join(" ")}
    />
  );
}


export default function FireSenseDashboard() {
  const [
    recommendation,
    setRecommendation,
  ] = useState<
    NextExperimentRecommendationResponse | null
  >(null);

  const [
    explanation,
    setExplanation,
  ] = useState<
    NextExperimentExplanationResponse | null
  >(null);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(null);


  const [
    activePredictionInput,
    setActivePredictionInput,
  ] = useState<
    FireBehaviorPredictionRequest | null
  >(null);


  const [
    activePredictionResponse,
    setActivePredictionResponse,
  ] = useState<
    ExplainedPredictionResponse | null
  >(null);


  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const [
          recommendationResult,
          explanationResult,
        ] = await Promise.all([
          getNextExperimentRecommendation(),
          getNextExperimentExplanation(),
        ]);

        setRecommendation(
          recommendationResult,
        );

        setExplanation(
          explanationResult,
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
          setError(caught.message);
        } else {
          setError(
            "Unable to connect to FireSense API.",
          );
        }
      } finally {
        setLoading(false);
      }
    }

    void loadDashboard();
  }, []);


  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#05070a] text-white">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-white/15 border-t-orange-400" />

          <p className="mt-5 text-sm text-white/50">
            Loading FireSense evidence...
          </p>
        </div>
      </main>
    );
  }


  if (
    error
    || !recommendation
    || !explanation
  ) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#05070a] px-6 text-white">
        <div className="max-w-lg rounded-3xl border border-red-500/20 bg-red-500/5 p-8">
          <p className="text-xs uppercase tracking-[0.25em] text-red-300">
            FireSense API
          </p>

          <h1 className="mt-3 text-2xl font-semibold">
            Dashboard unavailable
          </h1>

          <p className="mt-4 text-sm leading-7 text-white/55">
            {error ?? "Unknown API error."}
          </p>
        </div>
      </main>
    );
  }


  const integrityHealthy =
    recommendation.integrity
      .dataset_sha256_verified
    && recommendation.integrity
      .coverage_artifact_sha256_verified
    && recommendation.integrity
      .bayesian_artifact_sha256_verified;


  return (
    <main className="min-h-screen bg-[#05070a] text-[#f5f7fa]">
      <header className="sticky top-0 z-50 border-b border-white/[0.07] bg-[#05070a]/90 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-[1500px] items-center justify-between px-5 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-orange-400/30 bg-orange-400/10">
              <span className="text-sm font-semibold text-orange-300">
                F
              </span>
            </div>

            <div>
              <p className="text-sm font-semibold tracking-tight">
                FireSense
              </p>

              <p className="text-[10px] uppercase tracking-[0.2em] text-white/35">
                Reduced-gravity fire intelligence
              </p>
            </div>
          </div>

          <nav className="hidden items-center gap-7 text-xs text-white/45 lg:flex">
            <a
              href="#overview"
              className="transition hover:text-white"
            >
              Overview
            </a>

            <a
              href="#predictor"
              className="transition hover:text-white"
            >
              Predictor
            </a>

            <a
              href="#evidence-map"
              className="transition hover:text-white"
            >
              Evidence
            </a>


            <a
              href="#comparison-evidence"
              className="transition hover:text-white"
            >
              Comparison
            </a>

            <a
              href="#external-comparison"
              className="transition hover:text-white"
            >
              External
            </a>

            <a
              href="#validation-readiness"
              className="transition hover:text-white"
            >
              Validation
            </a>

            <a
              href="#validation-release-status"
              className="transition hover:text-white"
            >
              Release
            </a>

            <a
              href="#model-uncertainty"
              className="transition hover:text-white"
            >
              Uncertainty
            </a>

            <a
              href="#next-experiment"
              className="transition hover:text-white"
            >
              Next experiment
            </a>
          </nav>

          <div className="flex items-center gap-2 rounded-full border border-emerald-400/15 bg-emerald-400/[0.06] px-3 py-1.5 text-[11px] text-emerald-200">
            <StatusDot ok={integrityHealthy} />
            Evidence integrity verified
          </div>
        </div>
      </header>


      <div className="mx-auto max-w-[1500px] px-5 pb-20 lg:px-8">
        <section
          id="overview"
          className="scroll-mt-20 relative overflow-hidden border-b border-white/[0.07] py-16 lg:py-24"
        >
          <div className="firesense-grid pointer-events-none absolute inset-0 opacity-30" />

          <div className="relative grid gap-12 xl:grid-cols-[1.25fr_0.75fr] xl:items-end">
            <div>
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-orange-300/15 bg-orange-300/[0.05] px-3 py-1.5 text-[11px] uppercase tracking-[0.19em] text-orange-200/80">
                Evidence-grounded research system
              </div>

              <h1 className="max-w-5xl text-4xl font-medium leading-[1.04] tracking-[-0.045em] sm:text-5xl lg:text-7xl">
                Map what we know about{" "}
                <span className="text-orange-300">
                  fire in reduced gravity.
                </span>
              </h1>

              <p className="mt-7 max-w-3xl text-sm leading-7 text-white/48 sm:text-base">
                FireSense connects experimental evidence,
                physics-informed models, uncertainty and
                provenance to show what is supported, what
                conflicts, where evidence is missing, and
                which experiment could reduce uncertainty next.
              </p>
            </div>

            <div className="rounded-3xl border border-white/[0.08] bg-white/[0.025] p-6">
              <div className="flex items-center justify-between">
                <p className="text-[11px] uppercase tracking-[0.2em] text-white/35">
                  Current research priority
                </p>

                <span className="rounded-full border border-amber-300/20 bg-amber-300/[0.06] px-2.5 py-1 text-[10px] uppercase tracking-wider text-amber-200">
                  Not approved
                </span>
              </div>

              <div className="mt-8 flex items-end gap-3">
                <span className="text-5xl font-medium tracking-[-0.05em]">
                  {formatNumber(
                    recommendation.thickness_um,
                    3,
                  )}
                </span>

                <span className="pb-1.5 text-sm text-white/35">
                  um
                </span>
              </div>

              <p className="mt-3 font-mono text-[11px] text-white/35">
                {recommendation.candidate_id}
              </p>

              <p className="mt-7 text-sm leading-7 text-white/55">
                {recommendation.why_selected}
              </p>
            </div>
          </div>
        </section>


        <section className="grid border-b border-white/[0.07] md:grid-cols-2 xl:grid-cols-4">
          <div className="border-white/[0.07] py-7 md:border-r xl:pr-7">
            <p className="text-[10px] uppercase tracking-[0.2em] text-white/30">
              Evidence source
            </p>

            <p className="mt-3 text-sm font-medium">
              NASA BASS-II
            </p>

            <p className="mt-1 font-mono text-[10px] text-white/30">
              {recommendation.evidence.source_id}
            </p>
          </div>

          <div className="border-white/[0.07] py-7 md:pl-7 xl:border-r xl:px-7">
            <p className="text-[10px] uppercase tracking-[0.2em] text-white/30">
              Canonical figure
            </p>

            <p className="mt-3 text-sm font-medium">
              Figure {recommendation.evidence.figure}
            </p>

            <p className="mt-1 text-xs text-white/30">
              Dataset {recommendation.evidence.dataset_version}
            </p>
          </div>

          <div className="border-white/[0.07] py-7 md:border-r xl:px-7">
            <p className="text-[10px] uppercase tracking-[0.2em] text-white/30">
              Gravity pair
            </p>

            <p className="mt-3 text-sm font-medium">
              Microgravity + Normal
            </p>

            <p className="mt-1 text-xs text-white/30">
              Matched thin-sheet comparison
            </p>
          </div>

          <div className="py-7 md:pl-7">
            <p className="text-[10px] uppercase tracking-[0.2em] text-white/30">
              External validation
            </p>

            <p className="mt-3 text-sm font-medium">
              Not performed
            </p>

            <p className="mt-1 text-xs text-white/30">
              Internal convergence only
            </p>
          </div>
        </section>


        <FireBehaviorPredictor
          onResult={(
            predictionInput,
            predictionResponse,
          ) => {
            setActivePredictionInput(
              predictionInput,
            );

            setActivePredictionResponse(
              predictionResponse,
            );
          }}
        />


        <EvidenceMap
          recommendation={recommendation}
          activeQuery={
            activePredictionInput
          }
          activePrediction={
            activePredictionResponse
          }
        />

        <Figure222ComparisonEvidence />

        <ExternalComparisonEvidence />

        <ValidationReadinessPanel />

        <ValidationReleaseStatusPanel />


        <DecisionTrace
          recommendation={recommendation}
          explanation={explanation}
        />


        <ModelUncertaintyComparison
          recommendation={recommendation}
        />


        <section
          id="evidence"
          className="scroll-mt-20 border-t border-white/[0.07] py-16"
        >
          


          <article className="rounded-3xl border border-white/[0.08] bg-[#0a0d12] p-7 lg:p-9">
            <p className="text-[11px] uppercase tracking-[0.22em] text-emerald-300/70">
              Provenance
            </p>

            <h2 className="mt-3 text-2xl font-medium">
              Evidence integrity
            </h2>

            <div className="mt-8 space-y-3">
              {[
                [
                  "Baseline dataset hash",
                  recommendation.integrity
                    .dataset_sha256_verified,
                ],
                [
                  "Coverage artifact hash",
                  recommendation.integrity
                    .coverage_artifact_sha256_verified,
                ],
                [
                  "Bayesian artifact hash",
                  recommendation.integrity
                    .bayesian_artifact_sha256_verified,
                ],
              ].map(([label, ok]) => (
                <div
                  key={String(label)}
                  className="flex items-center justify-between rounded-xl border border-white/[0.06] px-4 py-3"
                >
                  <span className="text-sm text-white/45">
                    {String(label)}
                  </span>

                  <span className="flex items-center gap-2 text-xs text-emerald-200">
                    <StatusDot
                      ok={Boolean(ok)}
                    />
                    Verified
                  </span>
                </div>
              ))}
            </div>

            <div className="mt-6 rounded-xl border border-white/[0.06] bg-white/[0.02] p-4">
              <p className="text-[10px] uppercase tracking-wider text-white/25">
                Dataset SHA-256
              </p>

              <p className="mt-2 break-all font-mono text-[10px] leading-5 text-white/35">
                {
                  recommendation.evidence
                    .dataset_sha256
                }
              </p>
            </div>
          </article>
        </section>


        <section className="border-t border-white/[0.07] py-16">
          <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr]">
            <div>
              <p className="text-[11px] uppercase tracking-[0.22em] text-white/30">
                Scientific boundaries
              </p>

              <h2 className="mt-3 text-3xl font-medium tracking-[-0.035em]">
                What this result does not claim
              </h2>

              <p className="mt-5 text-sm leading-7 text-white/40">
                FireSense keeps evidence,
                uncertainty and research decisions
                separate from certification or
                operational safety claims.
              </p>
            </div>

            <div className="grid gap-3">
              {recommendation.scientific_guardrails.map(
                (guardrail, index) => (
                  <div
                    key={guardrail}
                    className="flex gap-4 rounded-2xl border border-white/[0.06] bg-white/[0.018] p-4"
                  >
                    <span className="font-mono text-[10px] text-orange-300/55">
                      {String(index + 1).padStart(
                        2,
                        "0",
                      )}
                    </span>

                    <p className="text-sm leading-6 text-white/48">
                      {guardrail}
                    </p>
                  </div>
                ),
              )}
            </div>
          </div>
        </section>


        <footer className="flex flex-col justify-between gap-4 border-t border-white/[0.07] py-8 text-[11px] text-white/25 md:flex-row">
          <p>
            FireSense · Evidence-grounded reduced-gravity fire behavior intelligence
          </p>

          <p>
            Research decision support · Not certification
          </p>
        </footer>
      </div>
    </main>
  );
}
