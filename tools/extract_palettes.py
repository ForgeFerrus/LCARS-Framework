#!/usr/bin/env python3
"""Simple palette extractor for LCARS palette images.

Usage: python tools/extract_palettes.py <image-path>

This script finds horizontal bands of non-background color and extracts
representative colors from each contiguous color block in the band.
It prints per-band palettes as hex color lists.
"""
from PIL import Image
import numpy as np
import sys
import os


def to_hex(rgb):
    return '#%02X%02X%02X' % rgb


def load_image(path):
    im = Image.open(path).convert('RGB')
    return im


def extract_bands(im, bg_thresh=30):
    """Detect horizontal bands of non-background using numpy histograms."""
    arr = np.array(im)
    h, w, _ = arr.shape
    brightness = arr.max(axis=2)
    mask = brightness > bg_thresh

    y_hist = mask.sum(axis=1)
    thresh = max(3, int(w * 0.01))
    bands = []
    in_band = False
    start = 0
    for y, v in enumerate(y_hist):
        if not in_band and v >= thresh:
            in_band = True
            start = y
        elif in_band and v < thresh:
            in_band = False
            end = y
            if end - start > 2:
                bands.append((start, end))
    if in_band:
        bands.append((start, h))
    return bands


def extract_colors_from_band(im, band, min_block_width=4, bg_thresh=30):
    arr = np.array(im)
    top, bottom = band
    band_arr = arr[top:bottom, :, :]
    h, w, _ = band_arr.shape
    brightness = band_arr.max(axis=2)
    mask = brightness > bg_thresh

    x_hist = mask.sum(axis=0)
    threshx = max(2, int(h * 0.05))
    blocks = []
    in_block = False
    bx = 0
    for x, v in enumerate(x_hist):
        if not in_block and v >= threshx:
            in_block = True
            bx = x
        elif in_block and v < threshx:
            in_block = False
            ex = x
            if ex - bx >= min_block_width:
                blocks.append((bx, ex))
    if in_block:
        blocks.append((bx, w))

    colors = []
    for (bx, ex) in blocks:
        block = band_arr[:, bx:ex, :]
        # average color of non-background pixels in block
        block_bright = block[block.max(axis=2) > bg_thresh]
        if block_bright.size == 0:
            # fallback to center pixel
            cy = h // 2
            cx = (bx + ex) // 2
            r, g, b = band_arr[cy, cx]
        else:
            mean = block_bright.mean(axis=0)
            r, g, b = [int(x) for x in mean]
        colors.append(to_hex((r, g, b)))
    return colors


def main():
    if len(sys.argv) < 2:
        print('Usage: python tools/extract_palettes.py <image-path>')
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print('Image not found:', path)
        sys.exit(1)

    im = load_image(path)
    bands = extract_bands(im)
    print(f'Found {len(bands)} bands')
    all_palettes = []
    for i, band in enumerate(bands):
        colors = extract_colors_from_band(im, band)
        print(f'Band {i+1} ({band[0]}-{band[1]}): {colors}')
        all_palettes.append(colors)

    # Also produce a quantized representative palette per band (6 colors)
    print('\nQuantized representative palettes:')
    for i, band in enumerate(bands):
        top, bottom = band
        crop = im.crop((0, top, im.size[0], bottom))
        # quantize to 6 colors
        q = crop.convert('P', palette=Image.ADAPTIVE, colors=6)
        palette = q.getpalette()  # flat list
        color_counts = sorted(q.getcolors(), reverse=True)
        rep = []
        for count, idx in color_counts:
            r = palette[idx*3]
            g = palette[idx*3+1]
            b = palette[idx*3+2]
            if max(r, g, b) < 30:
                continue
            rep.append(to_hex((r, g, b)))
            if len(rep) >= 6:
                break
        print(f'Band {i+1} quantized: {rep}')

    # Print a compact per-era assignment (best-effort)
    print('\nSuggested PALETTES (first 5 bands):')
    for i, pal in enumerate(all_palettes[:8]):
        print(f"'{i+1}': {pal}")


if __name__ == '__main__':
    main()
