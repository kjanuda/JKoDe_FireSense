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
  NextExperimentExplanationResponse,
  NextExperimentRecommendationResponse,
} from "@/lib/api/contracts";


export default function ApiCheckClient() {
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
    error,
    setError,
  ] = useState<string | null>(null);

  const [
    loading,
    setLoading,
  ] = useState(true);


  useEffect(() => {
    async function load() {
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
          recommendationResult
        );

        setExplanation(
          explanationResult
        );
      } catch (caught) {
        if (
          caught
          instanceof FireSenseApiError
        ) {
          setError(
            `${caught.status}: ${caught.detail}`
          );
        } else if (
          caught instanceof Error
        ) {
          setError(caught.message);
        } else {
          setError(
            "Unknown FireSense API error."
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
      <main className="min-h-screen p-10">
        <p>Connecting to FireSense API...</p>
      </main>
    );
  }


  if (error) {
    return (
      <main className="min-h-screen p-10">
        <h1 className="text-2xl font-semibold">
          FireSense API Check
        </h1>

        <p className="mt-4 text-red-600">
          {error}
        </p>
      </main>
    );
  }


  return (
    <main className="min-h-screen p-10">
      <div className="mx-auto max-w-4xl">
        <p className="text-sm uppercase tracking-widest">
          FireSense
        </p>

        <h1 className="mt-2 text-3xl font-semibold">
          Frontend API Connection
        </h1>

        <div className="mt-8 rounded-2xl border p-6">
          <p className="text-sm">
            API status
          </p>

          <p className="mt-2 text-xl font-medium">
            Connected
          </p>
        </div>

        <div className="mt-6 grid gap-6 md:grid-cols-2">
          <section className="rounded-2xl border p-6">
            <h2 className="text-lg font-semibold">
              Next experiment
            </h2>

            <p className="mt-4 text-3xl font-semibold">
              {recommendation?.thickness_um.toFixed(3)} um
            </p>

            <p className="mt-2 text-sm">
              {recommendation?.candidate_id}
            </p>

            <p className="mt-4">
              {
                recommendation
                  ?.why_selected
              }
            </p>
          </section>

          <section className="rounded-2xl border p-6">
            <h2 className="text-lg font-semibold">
              Explanation
            </h2>

            <p className="mt-4">
              {explanation?.summary}
            </p>

            <p className="mt-4 text-sm">
              Approval:{" "}
              {
                explanation
                  ?.approval_status
              }
            </p>
          </section>
        </div>

        <section className="mt-6 rounded-2xl border p-6">
          <h2 className="text-lg font-semibold">
            Integrity
          </h2>

          <pre className="mt-4 overflow-auto text-xs">
            {
              JSON.stringify(
                recommendation?.integrity,
                null,
                2,
              )
            }
          </pre>
        </section>
      </div>
    </main>
  );
}
