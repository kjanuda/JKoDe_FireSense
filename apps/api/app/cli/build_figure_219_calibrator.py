from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.core.paths import FIGURES_DATA_DIR


SOURCE_ID = "SRC-NASA-20210011385"

IMAGE_FILENAME = "page_048_image_02.jpeg"


def build_grid_image(
    input_path: Path,
    output_path: Path,
) -> None:

    image = Image.open(
        input_path
    ).convert("RGB")

    draw = ImageDraw.Draw(
        image
    )

    width, height = image.size

    # Minor grid every 50 px
    for x in range(
        0,
        width,
        50,
    ):
        draw.line(
            (
                x,
                0,
                x,
                height,
            ),
            fill=(
                210,
                210,
                210,
            ),
            width=1,
        )

    for y in range(
        0,
        height,
        50,
    ):
        draw.line(
            (
                0,
                y,
                width,
                y,
            ),
            fill=(
                210,
                210,
                210,
            ),
            width=1,
        )

    # Major grid every 250 px
    for x in range(
        0,
        width,
        250,
    ):
        draw.line(
            (
                x,
                0,
                x,
                height,
            ),
            fill=(
                120,
                120,
                120,
            ),
            width=2,
        )

        draw.text(
            (
                x + 4,
                4,
            ),
            str(x),
            fill=(
                0,
                0,
                0,
            ),
        )

    for y in range(
        0,
        height,
        100,
    ):
        draw.line(
            (
                0,
                y,
                width,
                y,
            ),
            fill=(
                120,
                120,
                120,
            ),
            width=2,
        )

        draw.text(
            (
                4,
                y + 4,
            ),
            str(y),
            fill=(
                0,
                0,
                0,
            ),
        )

    image.save(
        output_path
    )


def build_html(
    image_filename: str,
    output_path: Path,
) -> None:

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">

<title>
FireSense Figure 2.19 Calibration
</title>

<style>

body {{
    margin: 0;
    padding: 24px;
    font-family:
        Arial,
        sans-serif;
    background: #f4f4f4;
}}

h1 {{
    margin-top: 0;
}}

.instructions {{
    max-width: 1000px;
    line-height: 1.5;
    margin-bottom: 20px;
}}

.viewer {{
    position: relative;
    display: inline-block;
    border: 2px solid #222;
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
    margin-left: -7px;
    margin-top: -7px;
    border-radius: 50%;
    border: 2px solid white;
    background: red;
    pointer-events: none;
}}

.marker-label {{
    position: absolute;
    background: rgba(
        255,
        255,
        255,
        0.92
    );
    border: 1px solid #333;
    padding: 3px 5px;
    font-size: 12px;
    pointer-events: none;
}}

.controls {{
    margin-top: 20px;
    padding: 15px;
    background: white;
    max-width: 1100px;
}}

label {{
    display: block;
    margin-top: 8px;
}}

select,
input,
button {{
    padding: 7px;
    margin-top: 4px;
}}

table {{
    margin-top: 20px;
    border-collapse: collapse;
    width: 100%;
}}

th,
td {{
    border: 1px solid #ccc;
    padding: 6px;
    text-align: left;
}}

pre {{
    background: #111;
    color: #eee;
    padding: 12px;
    overflow: auto;
}}

</style>
</head>

<body>

<h1>
FireSense — Figure 2.19 Calibration
</h1>

<div class="instructions">

<p>
Click an exact axis reference point on the figure.
Choose a label first, then click the image.
The tool records coordinates in the
original 2596 × 820 image coordinate system.
</p>

<p>
For each plot panel, capture the pixel
position corresponding to the left/right
x-axis limits and top/bottom y-axis limits.
Do not click the outer image boundary;
click the actual scientific plot axes.
</p>

</div>

<div class="controls">

<label>
Calibration point:
</label>

<select id="pointName">

<option value="A_x_left">
Panel A — X left
</option>

<option value="A_x_right">
Panel A — X right
</option>

<option value="A_y_top">
Panel A — Y top
</option>

<option value="A_y_bottom">
Panel A — Y bottom
</option>

<option value="B_x_left">
Panel B — X left
</option>

<option value="B_x_right">
Panel B — X right
</option>

<option value="B_y_top">
Panel B — Y top
</option>

<option value="B_y_bottom">
Panel B — Y bottom
</option>

</select>

<button onclick="clearPoints()">
Clear all
</button>

<button onclick="copyJson()">
Copy JSON
</button>

</div>

<br>

<div
    class="viewer"
    id="viewer"
>

<img
    id="figure"
    src="{image_filename}"
>

</div>

<div class="controls">

<h2>
Selected coordinates
</h2>

<table>

<thead>

<tr>
<th>Point</th>
<th>X</th>
<th>Y</th>
</tr>

</thead>

<tbody id="coordinates">
</tbody>

</table>

<h2>
JSON
</h2>

<pre id="jsonOutput">{{}}</pre>

</div>

<script>

const figure =
    document.getElementById(
        "figure"
    );

const viewer =
    document.getElementById(
        "viewer"
    );

const points = {{}};


figure.addEventListener(
    "click",
    function(event) {{

        const rect =
            figure.getBoundingClientRect();

        const scaleX =
            figure.naturalWidth /
            rect.width;

        const scaleY =
            figure.naturalHeight /
            rect.height;

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

        const name =
            document
            .getElementById(
                "pointName"
            )
            .value;

        points[name] = {{
            x: x,
            y: y
        }};

        render();
    }}
);


function render() {{

    document
        .querySelectorAll(
            ".marker, .marker-label"
        )
        .forEach(
            element =>
                element.remove()
        );

    const table =
        document.getElementById(
            "coordinates"
        );

    table.innerHTML = "";

    for (
        const [name, point]
        of Object.entries(points)
    ) {{

        const marker =
            document.createElement(
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
            document.createElement(
                "div"
            );

        label.className =
            "marker-label";

        label.style.left =
            (
                point.x + 10
            ) + "px";

        label.style.top =
            (
                point.y + 10
            ) + "px";

        label.textContent =
            name
            + " ("
            + point.x
            + ", "
            + point.y
            + ")";

        viewer.appendChild(
            label
        );


        const row =
            document.createElement(
                "tr"
            );

        row.innerHTML =
            "<td>"
            + name
            + "</td>"
            + "<td>"
            + point.x
            + "</td>"
            + "<td>"
            + point.y
            + "</td>";

        table.appendChild(
            row
        );
    }}

    document
        .getElementById(
            "jsonOutput"
        )
        .textContent =
        JSON.stringify(
            points,
            null,
            2
        );
}}


function clearPoints() {{

    for (
        const key
        of Object.keys(points)
    ) {{
        delete points[key];
    }}

    render();
}}


async function copyJson() {{

    const text =
        JSON.stringify(
            points,
            null,
            2
        );

    await navigator.clipboard
        .writeText(text);

    alert(
        "Calibration JSON copied."
    );
}}

</script>

</body>
</html>
"""

    output_path.write_text(
        html,
        encoding="utf-8",
    )


def main():

    source_dir = (
        FIGURES_DATA_DIR
        / SOURCE_ID
    )

    input_path = (
        source_dir
        / "embedded"
        / IMAGE_FILENAME
    )

    output_dir = (
        source_dir
        / "digitization"
        / "figure_2_19"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    grid_path = (
        output_dir
        / "figure_2_19_grid.png"
    )

    build_grid_image(
        input_path=input_path,
        output_path=grid_path,
    )

    # Copy original figure into
    # calibration folder.
    original_copy = (
        output_dir
        / "figure_2_19.jpeg"
    )

    original_copy.write_bytes(
        input_path.read_bytes()
    )

    html_path = (
        output_dir
        / "calibrator.html"
    )

    build_html(
        image_filename=(
            "figure_2_19.jpeg"
        ),
        output_path=html_path,
    )

    print()
    print(
        "FIGURE 2.19 CALIBRATION VIEW"
    )
    print(
        "----------------------------"
    )

    print(
        f"Original : "
        f"{original_copy}"
    )

    print(
        f"Grid     : "
        f"{grid_path}"
    )

    print(
        f"Calibrator: "
        f"{html_path}"
    )

    print()
    print(
        "Open calibrator.html "
        "in your browser."
    )


if __name__ == "__main__":
    main()