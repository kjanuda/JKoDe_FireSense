import json
import webbrowser
from pathlib import Path

from PIL import Image

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"

IMAGE_NAME = "page_050_image_01.jpeg"


def main():

    image_path = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "embedded"
        / "figures_2_21_2_22"
        / IMAGE_NAME
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Figure 2.21 image missing: "
            f"{image_path}"
        )

    output_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
        / "digitization"
        / "figure_2_21"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = Image.open(
        image_path
    )

    width, height = image.size

    html_path = (
        output_dir
        / "calibration_viewer.html"
    )

    result_path = (
        output_dir
        / "axis_clicks.json"
    )

    image_uri = (
        Path(image_path)
        .resolve()
        .as_uri()
    )

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Figure 2.21 Calibration</title>

<style>
body {{
    font-family: Arial, sans-serif;
    margin: 20px;
    background: #f5f5f5;
}}

h2 {{
    margin-bottom: 8px;
}}

.instructions {{
    margin-bottom: 20px;
    line-height: 1.5;
}}

.viewer {{
    position: relative;
    display: inline-block;
    border: 1px solid #444;
}}

#figure {{
    display: block;
    width: {width}px;
    height: {height}px;
}}

#marker {{
    position: absolute;
    width: 12px;
    height: 12px;
    border: 2px solid red;
    border-radius: 50%;
    pointer-events: none;
    transform: translate(-50%, -50%);
    display: none;
}}

pre {{
    margin-top: 20px;
    padding: 15px;
    background: white;
    border: 1px solid #ccc;
}}

button {{
    margin-top: 15px;
    margin-right: 8px;
    padding: 8px 14px;
}}
</style>
</head>

<body>

<h2>Figure 2.21 Axis Calibration</h2>

<div class="instructions">
Click these points in order:
<br>
1. x-axis LEFT intersection
<br>
2. x-axis RIGHT end
<br>
3. y-axis TOP end
<br>
4. y-axis BOTTOM intersection
<br><br>
Expected scientific ranges:
<br>
x = 0 → 800 µm
<br>
y = 0 → 10 mm/s
</div>

<div class="viewer">
    <img
        id="figure"
        src="{image_uri}"
        alt="Figure 2.21"
    >
    <div id="marker"></div>
</div>

<br>

<button onclick="undoClick()">
Undo
</button>

<button onclick="resetClicks()">
Reset
</button>

<pre id="output"></pre>

<script>

const labels = [
    "x_left",
    "x_right",
    "y_top",
    "y_bottom"
];

let clicks = [];

const img = document.getElementById(
    "figure"
);

const output = document.getElementById(
    "output"
);

const marker = document.getElementById(
    "marker"
);

function render() {{

    const result = {{}};

    clicks.forEach(
        (point, index) => {{
            result[
                labels[index]
            ] = point;
        }}
    );

    output.textContent =
        JSON.stringify(
            result,
            null,
            2
        );

    if (clicks.length > 0) {{

        const last =
            clicks[
                clicks.length - 1
            ];

        marker.style.left =
            last.x + "px";

        marker.style.top =
            last.y + "px";

        marker.style.display =
            "block";

    }} else {{

        marker.style.display =
            "none";
    }}
}}

img.addEventListener(
    "click",
    function(event) {{

        if (
            clicks.length
            >= labels.length
        ) {{
            return;
        }}

        const rect =
            img.getBoundingClientRect();

        const scaleX =
            img.naturalWidth
            / rect.width;

        const scaleY =
            img.naturalHeight
            / rect.height;

        const x =
            Math.round(
                (
                    event.clientX
                    - rect.left
                )
                * scaleX
            );

        const y =
            Math.round(
                (
                    event.clientY
                    - rect.top
                )
                * scaleY
            );

        clicks.push(
            {{
                x: x,
                y: y
            }}
        );

        render();
    }}
);

function undoClick() {{
    clicks.pop();
    render();
}}

function resetClicks() {{
    clicks = [];
    render();
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

    metadata_path = (
        output_dir
        / "calibration_metadata.json"
    )

    metadata = {
        "source_id": SOURCE_ID,
        "figure_ref": "2.21",
        "image": str(
            image_path
        ),
        "image_width": width,
        "image_height": height,
        "sha256": (
            "39b56d57117cd3d03a1cce2414f122a910c738a28e6a6f308c3231313cc52b30"
        ),
        "x_axis": {
            "label": (
                "Fuel thickness"
            ),
            "unit": "µm",
            "scale": "linear",
            "value_min": 0.0,
            "value_max": 800.0,
        },
        "y_axis": {
            "label": (
                "Spread rate"
            ),
            "unit": "mm/s",
            "scale": "linear",
            "value_min": 0.0,
            "value_max": 10.0,
        },
        "series": [
            {
                "id": (
                    "microgravity"
                ),
                "label": (
                    "21 percent O2, "
                    "1 atm: microgravity"
                ),
                "evidence_type": (
                    "experimental"
                ),
                "marker": (
                    "blue filled circle"
                ),
                "training_eligible": True,
            },
            {
                "id": (
                    "downward"
                ),
                "label": (
                    "21 percent O2, "
                    "1 atm: downward"
                ),
                "evidence_type": (
                    "experimental"
                ),
                "marker": (
                    "red open circle"
                ),
                "training_eligible": True,
            },
            {
                "id": (
                    "thin_behavior"
                ),
                "label": (
                    "Thin behavior: "
                    "Vf = 223 / tau"
                ),
                "evidence_type": (
                    "theoretical"
                ),
                "marker": (
                    "red solid line"
                ),
                "training_eligible": False,
            },
        ],
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

    print()
    print(
        "FIGURE 2.21 CALIBRATION VIEWER"
    )
    print(
        "------------------------------"
    )

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

    webbrowser.open(
        html_path.resolve().as_uri()
    )


if __name__ == "__main__":
    main()