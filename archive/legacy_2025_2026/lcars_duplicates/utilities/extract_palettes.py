try:
    from PIL import Image
except ImportError:
    Image = None
try:
    import numpy as np
except ImportError:
    np = None

def to_hex(rgb):
    return '#%02X%02X%02X' % rgb

def load_image(path):
    if Image is None:
        raise RuntimeError("Pillow is required to load images (PIL not installed).")
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
