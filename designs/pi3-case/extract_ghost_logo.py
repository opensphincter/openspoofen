from __future__ import annotations

from collections import deque
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE_IMAGE = ROOT / "src" / "openspoofen" / "static" / "icons" / "openspoofen-logo.png"
OUT_DIR = Path(__file__).resolve().parent / "assets"
PNG_OUTPUT = OUT_DIR / "ghost_isolated.png"
SVG_OUTPUT = OUT_DIR / "ghost_silhouette.svg"
LAYER_INCLUDE_OUTPUT = OUT_DIR / "ghost_logo_layers_generated.scad"
TARGET_MAX_MM = 40.0
SVG_MARGIN_MM = 1.5
MAX_COLOR_LAYERS = 6
MIN_COMPONENT_AREA = 20


def flood_background(candidate_mask: np.ndarray) -> np.ndarray:
    height, width = candidate_mask.shape
    visited = np.zeros((height, width), dtype=bool)
    queue: deque[tuple[int, int]] = deque()

    for x in range(width):
        if candidate_mask[0, x]:
            queue.append((x, 0))
        if candidate_mask[height - 1, x]:
            queue.append((x, height - 1))
    for y in range(height):
        if candidate_mask[y, 0]:
            queue.append((0, y))
        if candidate_mask[y, width - 1]:
            queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if x < 0 or y < 0 or x >= width or y >= height:
            continue
        if visited[y, x] or not candidate_mask[y, x]:
            continue
        visited[y, x] = True
        queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    return visited


def isolate_subject_mask(image_path: Path) -> np.ndarray:
    rgba = np.array(Image.open(image_path).convert("RGBA"))
    rgb = rgba[..., :3]

    background_candidate = np.all(rgb >= 236, axis=2)
    background_mask = flood_background(background_candidate)
    subject_mask = ~background_mask
    subject_mask = cv2.morphologyEx(subject_mask.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    component_count, labels, stats, _ = cv2.connectedComponentsWithStats(subject_mask, connectivity=8)
    if component_count <= 1:
        raise RuntimeError("Could not isolate the ghost logo from the source image.")

    largest_label = max(range(1, component_count), key=lambda label: int(stats[label, cv2.CC_STAT_AREA]))
    largest_component = (labels == largest_label).astype(np.uint8)
    return cv2.morphologyEx(largest_component, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))


def main_contour_mask(mask: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise RuntimeError("No contour found for the ghost silhouette.")

    contour = max(contours, key=cv2.contourArea)
    contour_mask = np.zeros_like(mask, dtype=np.uint8)
    cv2.drawContours(contour_mask, [contour], contourIdx=-1, color=1, thickness=cv2.FILLED)
    return contour_mask, contour


def crop_to_mask(rgba: np.ndarray, mask: np.ndarray, margin: int = 12) -> tuple[np.ndarray, np.ndarray]:
    ys, xs = np.where(mask > 0)
    x0, x1 = xs.min(), xs.max()
    y0, y1 = ys.min(), ys.max()
    cropped_rgba = rgba[max(0, y0 - margin) : y1 + margin + 1, max(0, x0 - margin) : x1 + margin + 1].copy()
    cropped_mask = mask[max(0, y0 - margin) : y1 + margin + 1, max(0, x0 - margin) : x1 + margin + 1].copy()
    return cropped_rgba, cropped_mask


def save_transparent_png(cropped_rgba: np.ndarray, output_path: Path) -> None:
    Image.fromarray(cropped_rgba).save(output_path)


def contour_to_path(contour: np.ndarray, scale: float, margin: float) -> str:
    epsilon = 0.0015 * cv2.arcLength(contour, True)
    simplified = cv2.approxPolyDP(contour, epsilon, True)[:, 0, :]
    points = [f"{x * scale + margin:.3f},{y * scale + margin:.3f}" for x, y in simplified]
    return "M " + " L ".join(points) + " Z"


def write_silhouette_svg(contour: np.ndarray, scale: float, canvas_size: tuple[float, float], output_path: Path) -> None:
    path_d = contour_to_path(contour, scale, SVG_MARGIN_MM)
    svg_width, svg_height = canvas_size
    svg_text = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width:.3f}mm" '
        f'height="{svg_height:.3f}mm" viewBox="0 0 {svg_width:.3f} {svg_height:.3f}">\n'
        f'  <path d="{path_d}" fill="#111111"/>\n'
        "</svg>\n"
    )
    output_path.write_text(svg_text, encoding="utf-8")


def remove_small_components(mask: np.ndarray, min_area: int) -> np.ndarray:
    component_count, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    cleaned = np.zeros_like(mask, dtype=np.uint8)
    for label in range(1, component_count):
        if int(stats[label, cv2.CC_STAT_AREA]) >= min_area:
            cleaned[labels == label] = 1
    return cleaned


def keep_components_touching_subject(mask: np.ndarray, subject_mask: np.ndarray) -> np.ndarray:
    component_count, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    cleaned = np.zeros_like(mask, dtype=np.uint8)
    for label in range(1, component_count):
        component = labels == label
        left = int(stats[label, cv2.CC_STAT_LEFT])
        top = int(stats[label, cv2.CC_STAT_TOP])
        width = int(stats[label, cv2.CC_STAT_WIDTH])
        height = int(stats[label, cv2.CC_STAT_HEIGHT])
        if top > int(mask.shape[0] * 0.75) and width > max(12, height * 4):
            continue
        if np.any(subject_mask[component] > 0):
            cleaned[component] = 1
    return cleaned


def quantize_non_white_layers(cropped_rgba: np.ndarray, subject_mask: np.ndarray) -> list[tuple[np.ndarray, tuple[int, int, int]]]:
    rgb = cropped_rgba[..., :3]
    alpha = cropped_rgba[..., 3] > 0
    non_white_mask = alpha & ~np.all(rgb >= 242, axis=2)
    pixels = rgb[non_white_mask].astype(np.float32)
    if not len(pixels):
        return []

    unique_count = len(np.unique(pixels.astype(np.uint8), axis=0))
    cluster_count = min(MAX_COLOR_LAYERS, max(3, unique_count), len(pixels))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.8)
    _, labels, centers = cv2.kmeans(pixels, cluster_count, None, criteria, 8, cv2.KMEANS_PP_CENTERS)

    label_map = np.full(alpha.shape, -1, dtype=np.int32)
    label_map[non_white_mask] = labels[:, 0]
    counts = np.bincount(labels[:, 0], minlength=cluster_count)
    ordered_indices = np.argsort(-counts)

    layers: list[tuple[np.ndarray, tuple[int, int, int]]] = []
    for cluster_index in ordered_indices:
        cluster_mask = (label_map == cluster_index).astype(np.uint8)
        cluster_mask = cv2.morphologyEx(cluster_mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        cluster_mask = remove_small_components(cluster_mask, MIN_COMPONENT_AREA)
        cluster_mask = keep_components_touching_subject(cluster_mask, subject_mask)
        if int(cluster_mask.sum()) == 0:
            continue

        color = tuple(int(round(channel)) for channel in centers[cluster_index].tolist())
        layers.append((cluster_mask, color))

    return layers


def write_layer_svgs(
    layers: list[tuple[np.ndarray, tuple[int, int, int]]],
    scale: float,
    canvas_size: tuple[float, float],
) -> tuple[list[str], list[tuple[float, float, float]]]:
    for stale_file in OUT_DIR.glob("ghost_layer_*.svg"):
        stale_file.unlink()

    svg_width, svg_height = canvas_size
    layer_files: list[str] = []
    layer_colors: list[tuple[float, float, float]] = []

    for index, (mask, color_rgb) in enumerate(layers, start=1):
        contours, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        if not contours:
            continue

        paths = [contour_to_path(contour, scale, SVG_MARGIN_MM) for contour in contours if cv2.contourArea(contour) >= MIN_COMPONENT_AREA]
        if not paths:
            continue

        layer_name = f"ghost_layer_{index:02d}.svg"
        layer_path = OUT_DIR / layer_name
        fill_color = f"#{color_rgb[0]:02x}{color_rgb[1]:02x}{color_rgb[2]:02x}"

        svg_text = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width:.3f}mm" height="{svg_height:.3f}mm" viewBox="0 0 {svg_width:.3f} {svg_height:.3f}">'
        ]
        svg_text.append(f'  <path d="{" ".join(paths)}" fill="{fill_color}" fill-rule="evenodd"/>')
        svg_text.append("</svg>")
        layer_path.write_text("\n".join(svg_text) + "\n", encoding="utf-8")

        layer_files.append(layer_path.as_posix())
        layer_colors.append(tuple(channel / 255.0 for channel in color_rgb))

    return layer_files, layer_colors


def write_layer_include(layer_files: list[str], layer_colors: list[tuple[float, float, float]], canvas_size: tuple[float, float]) -> None:
    lines = [
        f"ghost_art_size = [{canvas_size[0]:.3f}, {canvas_size[1]:.3f}];",
        "",
        "module generated_ghost_logo_layers(detail_height) {",
    ]
    for file_name, color in zip(layer_files, layer_colors, strict=True):
        lines.append(f"  color([{color[0]:.5f}, {color[1]:.5f}, {color[2]:.5f}])")
        lines.append(f"    linear_extrude(height = detail_height) import(\"{file_name}\");")
    lines.append("}")
    lines.append("")
    LAYER_INCLUDE_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rgba = np.array(Image.open(SOURCE_IMAGE).convert("RGBA"))
    subject_mask = isolate_subject_mask(SOURCE_IMAGE)
    contour_mask, _ = main_contour_mask(subject_mask)
    rgba[..., 3] = np.where(contour_mask > 0, 255, 0).astype(np.uint8)

    cropped_rgba, cropped_mask = crop_to_mask(rgba, contour_mask)
    cropped_contours, _ = cv2.findContours(cropped_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cropped_contour = max(cropped_contours, key=cv2.contourArea)

    scale = TARGET_MAX_MM / max(cropped_rgba.shape[1], cropped_rgba.shape[0])
    canvas_size = (
        cropped_rgba.shape[1] * scale + SVG_MARGIN_MM * 2,
        cropped_rgba.shape[0] * scale + SVG_MARGIN_MM * 2,
    )

    save_transparent_png(cropped_rgba, PNG_OUTPUT)
    write_silhouette_svg(cropped_contour, scale, canvas_size, SVG_OUTPUT)

    layers = quantize_non_white_layers(cropped_rgba, cropped_mask)
    layer_files, layer_colors = write_layer_svgs(layers, scale, canvas_size)
    write_layer_include(layer_files, layer_colors, canvas_size)

    print(f"Wrote {PNG_OUTPUT}")
    print(f"Wrote {SVG_OUTPUT}")
    print(f"Wrote {LAYER_INCLUDE_OUTPUT}")
    for file_name in layer_files:
        print(f"Wrote {OUT_DIR / Path(file_name).name}")


if __name__ == "__main__":
    main()