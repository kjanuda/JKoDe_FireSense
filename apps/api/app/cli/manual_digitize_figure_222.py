import json
import webbrowser
from pathlib import Path

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"
IMAGE_NAME = "page_051_image_01.jpeg"


SERIES = [
    {
        "id": "mrc",
        "label": "MRC",
        "marker": "red open circle",
    },
    {
        "id": "vcf",
        "label": "VCF",
        "marker": "green open circle",
    },
    {
        "id": "astra",
        "label": "Astra",
        "marker": "blue open circle",
    },
    {
        "id": "nasa",
        "label": "NASA",
        "marker": "black open circle",
    },
    {
        "id": "bass",
        "label": "BASS",
        "marker": "red filled circle",
    },
    {
        "id": "ridout",
        "label": "Ridout",
        "marker": "red filled triangle",
    },
    {
        "id": "fernandez_pello_williams",
        "label": "Fernandez-Pello and Williams",
        "marker": "blue filled triangle",
    },
]


def main():

    root = (
        FIGURES_DATA_DIR
        / SOURCE_ID
    )

    image_path = (
        root
        / "embedded"
        / "figures_2_21_2_22"
        / IMAGE_NAME
    )

    figure_dir = (
        root
        / "digitization"
        / "figure_2_22"
    )

    metadata_path = (
        figure_dir
        / "calibration_metadata.json"
    )

    html_path = (
        figure_dir
        / "manual_digitizer.html"
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Missing Figure 2.22 image: "
            f"{image_path}"
        )

    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Missing calibration metadata: "
            f"{metadata_path}"
        )

    metadata = json.loads(
        metadata_path.read_text(
            encoding="utf-8"
        )
    )

    plot_bounds = metadata[
        "plot_bounds"
    ]

    x_axis = metadata[
        "x_axis"
    ]

    y_axis = metadata[
        "y_axis"
    ]

    left = float(
        plot_bounds["left"]
    )

    right = float(
        plot_bounds["right"]
    )

    top = float(
        plot_bounds["top"]
    )

    bottom = float(
        plot_bounds["bottom"]
    )

    x_min = float(
        x_axis["value_min"]
    )

    x_max = float(
        x_axis["value_max"]
    )

    x_pixel_left = float(
        x_axis["pixel_left"]
    )

    x_pixel_right = float(
        x_axis["pixel_right"]
    )

    y_high_value = float(
        y_axis[
            "reference_value_high"
        ]
    )

    y_high_pixel = float(
        y_axis[
            "reference_pixel_high"
        ]
    )

    y_low_value = float(
        y_axis[
            "reference_value_low"
        ]
    )

    y_low_pixel = float(
        y_axis[
            "reference_pixel_low"
        ]
    )

    image_uri = (
        image_path
        .resolve()
        .as_uri()
    )

    series_json = json.dumps(
        SERIES,
        ensure_ascii=False,
    )

    html = f"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<title>
Figure 2.22 Manual Digitizer
</title>

<style>

body {{
    margin: 18px;
    font-family: Arial, sans-serif;
    background: #f4f4f4;
}}

h2 {{
    margin-bottom: 8px;
}}

.instructions {{
    background: white;
    border: 1px solid #ccc;
    padding: 14px;
    max-width: 1200px;
    line-height: 1.55;
}}

.warning {{
    margin-top: 10px;
    padding: 10px;
    background: #fff2f2;
    border: 1px solid #dd8888;
}}

.controls {{
    margin-top: 14px;
    margin-bottom: 14px;
    background: white;
    padding: 12px;
    border: 1px solid #ccc;
    max-width: 1200px;
}}

select,
button {{
    padding: 8px 12px;
    margin-right: 6px;
    margin-bottom: 6px;
}}

.status {{
    margin-top: 8px;
    font-weight: bold;
}}

.viewer {{
    position: relative;
    display: inline-block;
    border: 2px solid #333;
    background: white;
}}

#figure {{
    display: block;
    max-width: none;
}}

.marker {{
    position: absolute;
    width: 14px;
    height: 14px;
    border: 3px solid #00c853;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
}}

.marker-label {{
    position: absolute;
    transform: translate(9px, -18px);
    font-size: 11px;
    font-weight: bold;
    background: rgba(255,255,255,0.75);
    padding: 1px 3px;
    pointer-events: none;
}}

pre {{
    background: white;
    border: 1px solid #ccc;
    padding: 14px;
    max-width: 1200px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}}

.summary {{
    background: white;
    border: 1px solid #ccc;
    padding: 12px;
    max-width: 1200px;
    margin-top: 14px;
}}

</style>

</head>

<body>

<h2>
Figure 2.22 — Manual Experimental-Series Digitization
</h2>

<div class="instructions">

<strong>Workflow:</strong>

<br><br>

1. Select one experimental series.
<br>
2. Click the exact centre of every marker belonging to that series.
<br>
3. Change series and continue.
<br>
4. Use Undo if a click is wrong.
<br>
5. When finished, press <strong>Copy JSON</strong>.

<div class="warning">

<strong>DO NOT CLICK:</strong>

<br>

• legend example markers
<br>
• Thermally thin limit line
<br>
• Thermally thick limit line
<br>
• equation/text/axis ticks

<br><br>

Only click actual experimental points inside the plot.

</div>

</div>


<div class="controls">

<label for="seriesSelect">
<strong>Current series:</strong>
</label>

<select id="seriesSelect"></select>

<button onclick="undoLast()">
Undo last click
</button>

<button onclick="clearCurrentSeries()">
Clear current series
</button>

<button onclick="resetAll()">
Reset all
</button>

<button onclick="copyJson()">
Copy JSON
</button>

<div
    id="status"
    class="status"
>
Ready.
</div>

</div>


<div
    id="viewer"
    class="viewer"
>

<img
    id="figure"
    src="{image_uri}"
    alt="Figure 2.22"
>

</div>


<div class="summary">

<strong>Series counts</strong>

<div id="counts"></div>

</div>


<h3>
Generated JSON
</h3>

<pre id="output"></pre>


<script>

const sourceId =
    "{SOURCE_ID}";

const figureRef =
    "2.22";

const seriesDefinitions =
    {series_json};


const calibration = {{

    plot: {{
        left: {left},
        right: {right},
        top: {top},
        bottom: {bottom}
    }},

    x: {{
        valueMin: {x_min},
        valueMax: {x_max},
        pixelLeft: {x_pixel_left},
        pixelRight: {x_pixel_right}
    }},

    y: {{
        highValue: {y_high_value},
        highPixel: {y_high_pixel},
        lowValue: {y_low_value},
        lowPixel: {y_low_pixel}
    }}
}};


const points = {{}};

seriesDefinitions.forEach(
    series => {{
        points[series.id] = [];
    }}
);


const image =
    document.getElementById(
        "figure"
    );

const viewer =
    document.getElementById(
        "viewer"
    );

const output =
    document.getElementById(
        "output"
    );

const select =
    document.getElementById(
        "seriesSelect"
    );

const status =
    document.getElementById(
        "status"
    );

const counts =
    document.getElementById(
        "counts"
    );


seriesDefinitions.forEach(
    series => {{

        const option =
            document.createElement(
                "option"
            );

        option.value =
            series.id;

        option.textContent =
            `${{series.label}} — ${{series.marker}}`;

        select.appendChild(
            option
        );
    }}
);


function log10(value) {{

    return Math.log(value)
        / Math.LN10;
}}


function pixelToX(pixelX) {{

    const fraction =
        (
            pixelX
            - calibration.x.pixelLeft
        )
        /
        (
            calibration.x.pixelRight
            - calibration.x.pixelLeft
        );

    const logMin =
        log10(
            calibration.x.valueMin
        );

    const logMax =
        log10(
            calibration.x.valueMax
        );

    const logValue =
        logMin
        + fraction
        * (
            logMax
            - logMin
        );

    return Math.pow(
        10,
        logValue
    );
}}


function pixelToY(pixelY) {{

    const fraction =
        (
            pixelY
            - calibration.y.highPixel
        )
        /
        (
            calibration.y.lowPixel
            - calibration.y.highPixel
        );

    const logHigh =
        log10(
            calibration.y.highValue
        );

    const logLow =
        log10(
            calibration.y.lowValue
        );

    const logValue =
        logHigh
        - fraction
        * (
            logHigh
            - logLow
        );

    return Math.pow(
        10,
        logValue
    );
}}


function roundValue(
    value,
    digits
) {{

    const factor =
        Math.pow(
            10,
            digits
        );

    return (
        Math.round(
            value
            * factor
        )
        / factor
    );
}}


function insidePlot(
    x,
    y
) {{

    return (
        x >= calibration.plot.left
        &&
        x <= calibration.plot.right
        &&
        y >= calibration.plot.top
        &&
        y <= calibration.plot.bottom
    );
}}


image.addEventListener(
    "click",
    function(event) {{

        const rect =
            image.getBoundingClientRect();

        const scaleX =
            image.naturalWidth
            / rect.width;

        const scaleY =
            image.naturalHeight
            / rect.height;

        const pixelX =
            (
                event.clientX
                - rect.left
            )
            * scaleX;

        const pixelY =
            (
                event.clientY
                - rect.top
            )
            * scaleY;


        if (
            !insidePlot(
                pixelX,
                pixelY
            )
        ) {{

            status.textContent =
                "Ignored: click was outside the calibrated plot area.";

            return;
        }}


        const seriesId =
            select.value;


        const point = {{

            pixel_x:
                roundValue(
                    pixelX,
                    2
                ),

            pixel_y:
                roundValue(
                    pixelY,
                    2
                ),

            thickness_um:
                roundValue(
                    pixelToX(
                        pixelX
                    ),
                    3
                ),

            spread_rate_mm_s:
                roundValue(
                    pixelToY(
                        pixelY
                    ),
                    5
                )
        }};


        points[
            seriesId
        ].push(
            point
        );


        status.textContent =
            `Added point to ${{getSeries(seriesId).label}}`;

        render();
    }}
);


function getSeries(
    seriesId
) {{

    return (
        seriesDefinitions.find(
            series =>
                series.id
                === seriesId
        )
    );
}}


function undoLast() {{

    const seriesId =
        select.value;

    if (
        points[seriesId].length
        === 0
    ) {{

        status.textContent =
            "Nothing to undo for current series.";

        return;
    }}

    points[
        seriesId
    ].pop();

    status.textContent =
        `Removed last ${{getSeries(seriesId).label}} point.`;

    render();
}}


function clearCurrentSeries() {{

    const seriesId =
        select.value;

    points[
        seriesId
    ] = [];

    status.textContent =
        `Cleared ${{getSeries(seriesId).label}}.`;

    render();
}}


function resetAll() {{

    const confirmed =
        confirm(
            "Clear ALL digitized points?"
        );

    if (!confirmed) {{
        return;
    }}

    seriesDefinitions.forEach(
        series => {{
            points[
                series.id
            ] = [];
        }}
    );

    status.textContent =
        "All points cleared.";

    render();
}}


function buildPayload() {{

    const resultSeries = {{}};


    seriesDefinitions.forEach(
        definition => {{

            const sortedPoints =
                [...points[
                    definition.id
                ]]
                .sort(
                    (
                        a,
                        b
                    ) =>
                        a.thickness_um
                        - b.thickness_um
                );


            resultSeries[
                definition.id
            ] = {{

                evidence_type:
                    "experimental",

                label:
                    definition.label,

                marker:
                    definition.marker,

                point_count:
                    sortedPoints.length,

                points:
                    sortedPoints
            }};
        }}
    );


    return {{

        source_id:
            sourceId,

        figure_ref:
            figureRef,

        extraction_method:
            "manual_human_digitization",

        calibration_status:
            "axis_calibrated_visual_pass",

        verification_status:
            "needs_second_review",

        theoretical_curves_included:
            false,

        excluded_theoretical_series: [
            "Thermally thin limit",
            "Thermally thick limit"
        ],

        series:
            resultSeries
    }};
}}


function render() {{

    document
        .querySelectorAll(
            ".marker, .marker-label"
        )
        .forEach(
            element =>
                element.remove()
        );


    seriesDefinitions.forEach(
        definition => {{

            points[
                definition.id
            ].forEach(
                (
                    point,
                    index
                ) => {{

                    const marker =
                        document
                        .createElement(
                            "div"
                        );

                    marker.className =
                        "marker";

                    marker.style.left =
                        point.pixel_x
                        + "px";

                    marker.style.top =
                        point.pixel_y
                        + "px";

                    viewer.appendChild(
                        marker
                    );


                    const label =
                        document
                        .createElement(
                            "div"
                        );

                    label.className =
                        "marker-label";

                    label.style.left =
                        point.pixel_x
                        + "px";

                    label.style.top =
                        point.pixel_y
                        + "px";

                    label.textContent =
                        `${{definition.label}}-${{index + 1}}`;

                    viewer.appendChild(
                        label
                    );
                }}
            );
        }}
    );


    const payload =
        buildPayload();


    output.textContent =
        JSON.stringify(
            payload,
            null,
            2
        );


    counts.innerHTML =
        seriesDefinitions
        .map(
            definition =>
                `${{definition.label}}: <strong>${{
                    points[
                        definition.id
                    ].length
                }}</strong>`
        )
        .join(
            "<br>"
        );
}}


async function copyJson() {{

    const text =
        JSON.stringify(
            buildPayload(),
            null,
            2
        );

    try {{

        await navigator.clipboard
            .writeText(
                text
            );

        status.textContent =
            "JSON copied to clipboard.";

    }} catch (error) {{

        status.textContent =
            "Clipboard blocked. Copy JSON manually from below.";
    }}
}}


render();

</script>

</body>

</html>
"""

    html_path.write_text(
        html,
        encoding="utf-8",
    )

    print()
    print(
        "FIGURE 2.22 MANUAL DIGITIZER"
    )

    print(
        "----------------------------"
    )

    print()
    print(
        f"HTML:"
    )

    print(
        f"  {html_path}"
    )

    print()
    print(
        "Experimental series:"
    )

    for series in SERIES:

        print(
            f"  - "
            f"{series['label']}"
            f" | "
            f"{series['marker']}"
        )

    print()
    print(
        "EXCLUDED:"
    )

    print(
        "  - Thermally thin limit"
    )

    print(
        "  - Thermally thick limit"
    )

    print()
    print(
        "Workflow:"
    )

    print(
        "  1. Select one series."
    )

    print(
        "  2. Click marker CENTERS only."
    )

    print(
        "  3. Do not click legend markers."
    )

    print(
        "  4. Do not click theory curves."
    )

    print(
        "  5. Copy JSON when finished."
    )

    print()

    webbrowser.open(
        html_path
        .resolve()
        .as_uri()
    )


if __name__ == "__main__":
    main()