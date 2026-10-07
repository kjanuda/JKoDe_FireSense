import json
import webbrowser
from pathlib import Path

from PIL import Image

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"

IMAGE_NAME = "page_050_image_01.jpeg"


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

    metadata_path = (
        root
        / "digitization"
        / "figure_2_21"
        / "calibration_metadata.json"
    )

    output_dir = (
        root
        / "digitization"
        / "figure_2_21"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Missing image: {image_path}"
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

    bounds = metadata[
        "pixel_bounds"
    ]

    x_axis = metadata[
        "x_axis"
    ]

    y_axis = metadata[
        "y_axis"
    ]

    image = Image.open(
        image_path
    )

    width, height = image.size

    image_uri = (
        Path(image_path)
        .resolve()
        .as_uri()
    )

    html_path = (
        output_dir
        / "manual_digitizer.html"
    )

    calibration_json = json.dumps(
        {
            "bounds": bounds,
            "x_axis": x_axis,
            "y_axis": y_axis,
        }
    )

    html = f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<title>
Figure 2.21 Manual Digitizer
</title>

<style>

body {{
    font-family:
        Arial,
        sans-serif;

    margin: 20px;

    background:
        #f5f5f5;
}}

h2 {{
    margin-bottom: 6px;
}}

.instructions {{
    background: white;

    border:
        1px solid #ccc;

    padding: 14px;

    margin-bottom: 15px;

    max-width: 1100px;

    line-height: 1.5;
}}

.controls {{
    margin-bottom: 14px;
}}

button {{
    padding:
        8px 14px;

    margin-right: 6px;

    margin-bottom: 5px;

    cursor: pointer;
}}

button.active {{
    font-weight: bold;

    outline:
        3px solid #444;
}}

.viewer {{
    position: relative;

    display: inline-block;

    border:
        1px solid #555;

    background: white;
}}

#figure {{
    display: block;

    width:
        {width}px;

    height:
        {height}px;
}}

.marker {{
    position: absolute;

    width: 20px;
    height: 20px;

    transform:
        translate(
            -50%,
            -50%
        );

    pointer-events: none;

    box-sizing:
        border-box;
}}

.microgravity {{
    border:
        3px solid limegreen;

    border-radius: 50%;
}}

.downward {{
    border:
        3px solid purple;
}}

.label {{
    position: absolute;

    font-size: 12px;

    font-weight: bold;

    transform:
        translate(
            12px,
            -16px
        );

    pointer-events: none;

    background:
        rgba(
            255,
            255,
            255,
            0.75
        );
}}

pre {{
    background: white;

    border:
        1px solid #ccc;

    padding: 14px;

    white-space:
        pre-wrap;

    max-height: 650px;

    overflow: auto;

    max-width: 1100px;
}}

.status {{
    margin:
        10px 0;

    font-weight: bold;
}}

</style>

</head>


<body>

<h2>
Figure 2.21 Manual Experimental Point Digitizer
</h2>


<div class="instructions">

<strong>Important:</strong>

Click only the centres of experimental markers.

<br><br>

Blue filled circles =
microgravity experimental.

<br>

Red open circles =
downward experimental.

<br><br>

Do NOT click:

red theoretical curve,
legend markers,
axis ticks,
equation text.

<br><br>

Recommended order:

select Microgravity and click every visible blue experimental marker once.

Then select Downward and click every visible red open experimental marker once.

</div>


<div class="controls">

<button
    id="microBtn"
    onclick="setSeries('microgravity')"
    class="active"
>
Microgravity
</button>

<button
    id="downBtn"
    onclick="setSeries('downward')"
>
Downward
</button>

<button
    onclick="undoPoint()"
>
Undo last
</button>

<button
    onclick="clearCurrentSeries()"
>
Clear current series
</button>

<button
    onclick="resetAll()"
>
Reset all
</button>

<button
    onclick="copyJson()"
>
Copy JSON
</button>

</div>


<div
    id="status"
    class="status"
>
</div>


<div
    id="viewer"
    class="viewer"
>

<img
    id="figure"
    src="{image_uri}"
    alt="Figure 2.21"
>

</div>


<h3>
Digitized data
</h3>

<pre id="output"></pre>


<script>

const calibration =
    {calibration_json};

let currentSeries =
    "microgravity";

let points = {{
    microgravity: [],
    downward: []
}};


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

const status =
    document.getElementById(
        "status"
    );


function pixelToValue(
    pixel,
    axis
) {{

    const pixelRange =
        axis.pixel_max
        - axis.pixel_min;

    const fraction =
        (
            pixel
            - axis.pixel_min
        )
        / pixelRange;

    return (
        axis.value_min
        + fraction
        * (
            axis.value_max
            - axis.value_min
        )
    );
}}


function setSeries(
    series
) {{

    currentSeries =
        series;

    document
        .getElementById(
            "microBtn"
        )
        .classList
        .toggle(
            "active",
            series
            === "microgravity"
        );

    document
        .getElementById(
            "downBtn"
        )
        .classList
        .toggle(
            "active",
            series
            === "downward"
        );

    render();
}}


function addPoint(
    pixelX,
    pixelY
) {{

    const thickness =
        pixelToValue(
            pixelX,
            calibration.x_axis
        );

    const spreadRate =
        pixelToValue(
            pixelY,
            calibration.y_axis
        );

    points[
        currentSeries
    ].push(
        {{
            pixel_x:
                Math.round(
                    pixelX
                    * 100
                ) / 100,

            pixel_y:
                Math.round(
                    pixelY
                    * 100
                ) / 100,

            thickness_um:
                Math.round(
                    thickness
                    * 1000
                ) / 1000,

            spread_rate_mm_s:
                Math.round(
                    spreadRate
                    * 10000
                ) / 10000
        }}
    );

    render();
}}


image.addEventListener(
    "click",
    function(event) {{

        const rect =
            image
            .getBoundingClientRect();

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

        const bounds =
            calibration.bounds;

        if (
            pixelX
                < bounds.left_px
            ||
            pixelX
                > bounds.right_px
            ||
            pixelY
                < bounds.top_px
            ||
            pixelY
                > bounds.bottom_px
        ) {{

            alert(
                "Click is outside "
                + "the calibrated plot area."
            );

            return;
        }}

        addPoint(
            pixelX,
            pixelY
        );
    }}
);


function undoPoint() {{

    const seriesPoints =
        points[
            currentSeries
        ];

    if (
        seriesPoints.length > 0
    ) {{
        seriesPoints.pop();
    }}

    render();
}}


function clearCurrentSeries() {{

    points[
        currentSeries
    ] = [];

    render();
}}


function resetAll() {{

    points = {{
        microgravity: [],
        downward: []
    }};

    render();
}}


function buildResult() {{

    const micro =
        [...points.microgravity]
        .sort(
            (
                a,
                b
            ) =>
                a.thickness_um
                - b.thickness_um
        );

    const downward =
        [...points.downward]
        .sort(
            (
                a,
                b
            ) =>
                a.thickness_um
                - b.thickness_um
        );

    return {{
        source_id:
            "{SOURCE_ID}",

        figure_ref:
            "2.21",

        extraction_method:
            "manual_human_digitization",

        calibration_status:
            "axis_calibrated_visual_pass",

        verification_status:
            "needs_second_review",

        theoretical_curve_included:
            false,

        series: {{

            microgravity: {{
                evidence_type:
                    "experimental",

                marker:
                    "blue filled circle",

                point_count:
                    micro.length,

                points:
                    micro
            }},

            downward: {{
                evidence_type:
                    "experimental",

                marker:
                    "red open circle",

                point_count:
                    downward.length,

                points:
                    downward
            }}
        }}
    }};
}}


function render() {{

    document
        .querySelectorAll(
            ".marker, .label"
        )
        .forEach(
            element =>
                element.remove()
        );

    for (
        const series
        of [
            "microgravity",
            "downward"
        ]
    ) {{

        points[
            series
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
                    "marker "
                    + series;

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
                    "label";

                label.style.left =
                    point.pixel_x
                    + "px";

                label.style.top =
                    point.pixel_y
                    + "px";

                label.textContent =
                    (
                        series
                        === "microgravity"
                        ? "M"
                        : "D"
                    )
                    + (
                        index + 1
                    );

                viewer.appendChild(
                    label
                );
            }}
        );
    }}

    const result =
        buildResult();

    output.textContent =
        JSON.stringify(
            result,
            null,
            2
        );

    status.textContent =
        "Current series: "
        + currentSeries
        + " | microgravity="
        + points.microgravity.length
        + " | downward="
        + points.downward.length;
}}


async function copyJson() {{

    const result =
        JSON.stringify(
            buildResult(),
            null,
            2
        );

    try {{

        await navigator
            .clipboard
            .writeText(
                result
            );

        alert(
            "JSON copied to clipboard."
        );

    }} catch (error) {{

        alert(
            "Clipboard failed. "
            + "Copy JSON manually "
            + "from the output box."
        );
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
        "FIGURE 2.21 MANUAL DIGITIZER"
    )
    print(
        "----------------------------"
    )

    print(
        f"Image      : "
        f"{image_path}"
    )

    print(
        f"Dimensions : "
        f"{width} x {height}"
    )

    print(
        f"HTML       : "
        f"{html_path}"
    )

    print()
    print(
        "Workflow:"
    )

    print(
        "  1. Click all blue "
        "microgravity markers."
    )

    print(
        "  2. Switch to Downward."
    )

    print(
        "  3. Click all red "
        "open-circle markers."
    )

    print(
        "  4. Review marker overlays."
    )

    print(
        "  5. Press Copy JSON."
    )

    print()
    print(
        "Do NOT click the theoretical "
        "red curve or legend."
    )

    webbrowser.open(
        html_path
        .resolve()
        .as_uri()
    )


if __name__ == "__main__":
    main()