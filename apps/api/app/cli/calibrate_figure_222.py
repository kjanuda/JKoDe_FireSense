import json
import webbrowser
from pathlib import Path

from PIL import Image

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"

IMAGE_NAME = "page_051_image_01.jpeg"


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

    output_dir = (
        root
        / "digitization"
        / "figure_2_22"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not image_path.exists():

        raise FileNotFoundError(
            f"Missing Figure 2.22 image: "
            f"{image_path}"
        )

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
        / "calibration_viewer.html"
    )

    metadata_path = (
        output_dir
        / "calibration_metadata.json"
    )

    metadata = {
        "source_id": SOURCE_ID,

        "figure_ref": "2.22",

        "image": str(
            image_path
        ),

        "image_width": width,
        "image_height": height,

        "image_sha256": (
            "9f131ab1bc34c0bf083fa48d145e80d"
            "204192329bec15aa47f7c6f79e065c7f7"
        ),

        "x_axis": {
            "label": (
                "Fuel thickness"
            ),

            "unit": "µm",

            "scale": "log10",

            # Visible major axis range
            # from Figure 2.22.
            "value_min": 10.0,
            "value_max": 100000.0,
        },

        "y_axis": {
            "label": (
                "Spread rate"
            ),

            "unit": "mm/s",

            "scale": "log10",

            "value_min": 0.01,
            "value_max": 10.0,
        },

        "series_status": (
            "not_yet_classified_by_point"
        ),

        "status": (
            "needs_axis_calibration"
        ),
    }

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    html = f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<title>
Figure 2.22 Log Calibration
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

.instructions {{
    padding: 14px;

    background: white;

    border:
        1px solid #ccc;

    max-width: 1100px;

    line-height: 1.5;

    margin-bottom: 15px;
}}

.viewer {{
    position: relative;

    display: inline-block;

    border:
        1px solid #444;
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

    width: 14px;
    height: 14px;

    border:
        3px solid limegreen;

    border-radius: 50%;

    transform:
        translate(
            -50%,
            -50%
        );

    pointer-events: none;
}}

.label {{
    position: absolute;

    font-size: 12px;

    font-weight: bold;

    background:
        rgba(
            255,
            255,
            255,
            0.8
        );

    transform:
        translate(
            10px,
            -18px
        );

    pointer-events: none;
}}

button {{
    padding:
        8px 14px;

    margin:
        10px 5px 10px 0;
}}

pre {{
    background: white;

    border:
        1px solid #ccc;

    padding: 14px;

    max-width: 1100px;
}}

</style>

</head>

<body>

<h2>
Figure 2.22 Log-Log Axis Calibration
</h2>

<div class="instructions">

Click exactly four axis points in this order:

<br><br>

1. <strong>x_left</strong>
— lower-left plot intersection
(10¹ µm)

<br>

2. <strong>x_right</strong>
— lower-right plot intersection
(10⁵ µm)

<br>

3. <strong>y_top</strong>
— upper-left plot intersection
(10¹ mm/s)

<br>

4. <strong>y_bottom</strong>
— lower-left plot intersection
(10⁻² mm/s)

<br><br>

This figure uses:

<br>

x-axis:
10¹ → 10⁵ µm, log10

<br>

y-axis:
10⁻² → 10¹ mm/s, log10

</div>


<button
    onclick="undoPoint()"
>
Undo
</button>

<button
    onclick="resetAll()"
>
Reset
</button>


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


<pre id="output"></pre>


<script>

const labels = [
    "x_left",
    "x_right",
    "y_top",
    "y_bottom"
];

let clicks = [];

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


image.addEventListener(
    "click",
    function(event) {{

        if (
            clicks.length
            >= labels.length
        ) {{
            return;
        }}

        const rect =
            image
            .getBoundingClientRect();

        const scaleX =
            image.naturalWidth
            / rect.width;

        const scaleY =
            image.naturalHeight
            / rect.height;

        const x =
            (
                event.clientX
                - rect.left
            )
            * scaleX;

        const y =
            (
                event.clientY
                - rect.top
            )
            * scaleY;

        clicks.push(
            {{
                x:
                    Math.round(
                        x * 100
                    ) / 100,

                y:
                    Math.round(
                        y * 100
                    ) / 100
            }}
        );

        render();
    }}
);


function undoPoint() {{

    clicks.pop();

    render();
}}


function resetAll() {{

    clicks = [];

    render();
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

    const result = {{}};

    clicks.forEach(
        (
            point,
            index
        ) => {{

            result[
                labels[index]
            ] = point;


            const marker =
                document
                .createElement(
                    "div"
                );

            marker.className =
                "marker";

            marker.style.left =
                point.x + "px";

            marker.style.top =
                point.y + "px";

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
                point.x + "px";

            label.style.top =
                point.y + "px";

            label.textContent =
                labels[index];

            viewer.appendChild(
                label
            );
        }}
    );

    output.textContent =
        JSON.stringify(
            result,
            null,
            2
        );
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
        "FIGURE 2.22 CALIBRATION VIEWER"
    )

    print(
        "------------------------------"
    )

    print()
    print(
        f"Dimensions : "
        f"{width} x {height}"
    )

    print(
        f"HTML       : "
        f"{html_path}"
    )

    print(
        f"Metadata   : "
        f"{metadata_path}"
    )

    print()
    print(
        "Click order:"
    )

    print(
        "  1. x_left"
    )

    print(
        "  2. x_right"
    )

    print(
        "  3. y_top"
    )

    print(
        "  4. y_bottom"
    )

    print()
    print(
        "Important:"
    )

    print(
        "  This is a log-log plot."
    )

    webbrowser.open(
        html_path
        .resolve()
        .as_uri()
    )


if __name__ == "__main__":
    main()