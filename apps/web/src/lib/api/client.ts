import type { ValidationReleaseStatusResponse } from "./contracts";
import type {
  ExternalComparisonEvidenceResponse,
  ValidationReadinessResponse,
  Figure222EvidenceResponse,
  ExplainedPredictionResponse,
  FireBehaviorPredictionRequest,
  FireBehaviorPredictionResponse,
  NextExperimentExplanationResponse,
  NextExperimentRecommendationResponse,
} from "./contracts";


const DEFAULT_API_BASE_URL =
  "http://127.0.0.1:8000";


export class FireSenseApiError extends Error {
  status: number;
  detail: string;

  constructor(
    status: number,
    detail: string,
  ) {
    super(detail);

    this.name = "FireSenseApiError";
    this.status = status;
    this.detail = detail;
  }
}


function getApiBaseUrl(): string {
  const configured =
    process.env.NEXT_PUBLIC_FIRESENSE_API_URL;

  return (
    configured
    ?? DEFAULT_API_BASE_URL
  ).replace(/\/+$/, "");
}


function getErrorDetail(
  body: unknown,
  fallback: string,
): string {
  if (
    typeof body === "object"
    && body !== null
    && "detail" in body
  ) {
    const detail = (
      body as {
        detail?: unknown;
      }
    ).detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (detail !== undefined) {
      return JSON.stringify(detail);
    }
  }

  return fallback;
}


async function apiRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${getApiBaseUrl()}${path}`,
    {
      ...init,

      headers: {
        Accept: "application/json",
        ...init?.headers,
      },

      cache: "no-store",
    },
  );

  const raw = await response.text();

  let body: unknown = null;

  if (raw) {
    try {
      body = JSON.parse(raw);
    } catch {
      body = raw;
    }
  }

  if (!response.ok) {
    throw new FireSenseApiError(
      response.status,
      getErrorDetail(
        body,
        response.statusText
        || "FireSense API request failed.",
      ),
    );
  }

  return body as T;
}


export async function predictFireBehavior(
  input: FireBehaviorPredictionRequest,
): Promise<FireBehaviorPredictionResponse> {
  return apiRequest<
    FireBehaviorPredictionResponse
  >(
    "/api/predict/fire-behavior",
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(input),
    },
  );
}


export async function explainFireBehavior(
  input: FireBehaviorPredictionRequest,
): Promise<ExplainedPredictionResponse> {
  return apiRequest<
    ExplainedPredictionResponse
  >(
    "/api/predict/fire-behavior/explain",
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(input),
    },
  );
}


export async function getNextExperimentRecommendation(
): Promise<NextExperimentRecommendationResponse> {
  return apiRequest<
    NextExperimentRecommendationResponse
  >(
    "/api/recommendations/next-experiment",
  );
}


export async function getNextExperimentExplanation(
): Promise<NextExperimentExplanationResponse> {
  return apiRequest<
    NextExperimentExplanationResponse
  >(
    "/api/recommendations/next-experiment/explain",
  );
}


export async function getFigure222Evidence(
): Promise<Figure222EvidenceResponse> {
  return apiRequest<
    Figure222EvidenceResponse
  >(
    "/api/evidence/figure-2-22",
  );
}


export async function getExternalComparisonEvidence(
): Promise<ExternalComparisonEvidenceResponse> {
  return apiRequest<
    ExternalComparisonEvidenceResponse
  >(
    "/api/evidence/external-comparison",
  );
}

export async function getValidationReadiness(
): Promise<ValidationReadinessResponse> {
  return apiRequest<
    ValidationReadinessResponse
  >(
    "/api/evidence/validation-readiness",
  );
}

export async function getValidationReleaseStatus(
): Promise<ValidationReleaseStatusResponse> {
  return apiRequest<
    ValidationReleaseStatusResponse
  >(
    "/api/evidence/validation-release-status",
  );
}

