export type Figure221GravityRegime =
  | "microgravity"
  | "normal_gravity";


export type Figure221Point = {
  plot_point_id: string;
  gravity_regime: Figure221GravityRegime;
  thickness_um: number;
  spread_rate_mm_s: number;
};


export const FIGURE_221_SOURCE_ID =
  "SRC-NASA-20210011385";

export const FIGURE_221_REF =
  "Figure 2.21";

export const FIGURE_221_DATASET_VERSION =
  "v0";

export const FIGURE_221_DATASET_SHA256 =
  "4024475ca9f0bf5d703ce1cb375e6d9e11897ead4dfc3f5e0fe6369879798ab4";


// Figure-digitization uncertainty.
// This must not be presented as complete
// experimental uncertainty.
export const FIGURE_221_DIGITIZATION_UNCERTAINTY_MM_S =
  0.048368;


export const FIGURE_221_MICROGRAVITY_POINTS:
  Figure221Point[] = [
    {
      plot_point_id: "MG-01",
      gravity_regime: "microgravity",
      thickness_um: 101.933,
      spread_rate_mm_s: 2.3067,
    },
    {
      plot_point_id: "MG-02",
      gravity_regime: "microgravity",
      thickness_um: 201.237,
      spread_rate_mm_s: 1.1456,
    },
    {
      plot_point_id: "MG-03",
      gravity_regime: "microgravity",
      thickness_um: 301.732,
      spread_rate_mm_s: 0.8042,
    },
    {
      plot_point_id: "MG-04",
      gravity_regime: "microgravity",
      thickness_um: 400.433,
      spread_rate_mm_s: 0.3304,
    },
  ];


export const FIGURE_221_NORMAL_GRAVITY_POINTS:
  Figure221Point[] = [
    {
      plot_point_id: "NG-01",
      gravity_regime: "normal_gravity",
      thickness_um: 25.147,
      spread_rate_mm_s: 8.9601,
    },
    {
      plot_point_id: "NG-02",
      gravity_regime: "normal_gravity",
      thickness_um: 45.237,
      spread_rate_mm_s: 6.5175,
    },
    {
      plot_point_id: "NG-03",
      gravity_regime: "normal_gravity",
      thickness_um: 51.933,
      spread_rate_mm_s: 5.9250,
    },
    {
      plot_point_id: "NG-04",
      gravity_regime: "normal_gravity",
      thickness_um: 76.933,
      spread_rate_mm_s: 3.8815,
    },
    {
      plot_point_id: "NG-05",
      gravity_regime: "normal_gravity",
      thickness_um: 100.446,
      spread_rate_mm_s: 2.0556,
    },
    {
      plot_point_id: "NG-06",
      gravity_regime: "normal_gravity",
      thickness_um: 200.446,
      spread_rate_mm_s: 0.8827,
    },
    {
      plot_point_id: "NG-07",
      gravity_regime: "normal_gravity",
      thickness_um: 301.786,
      spread_rate_mm_s: 0.5804,
    },
    {
      plot_point_id: "NG-08",
      gravity_regime: "normal_gravity",
      thickness_um: 402.232,
      spread_rate_mm_s: 0.4353,
    },
    {
      plot_point_id: "NG-09",
      gravity_regime: "normal_gravity",
      thickness_um: 748.808,
      spread_rate_mm_s: 0.1814,
    },
  ];


export const FIGURE_221_SUPPORTED_DOMAINS = {
  microgravity: {
    min_thickness_um: 101.933,
    max_thickness_um: 400.433,
  },

  normal_gravity: {
    min_thickness_um: 25.147,
    max_thickness_um: 748.808,
  },
} as const;
