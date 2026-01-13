import sys
sys.path.insert(0, '')
from PIL import Image
import numpy as np
from tools.extract_palettes import extract_bands, extract_colors_from_band

im = Image.open('resources/okudagrams/Okudagrams_Color.png').convert('RGB')
w,h=im.size
print('size',w,h)
arr = np.array(im)
brightness = arr.max(axis=2)
mask = brightness>30
col_counts = mask.sum(axis=0)
th = max(5, int(h*0.01))
runs=[]
start=None
for x,c in enumerate(col_counts):
    if start is None and c>th:
        start=x
    elif start is not None and c<=th:
        runs.append((start,x))
        start=None
if start is not None:
    runs.append((start,w))
print('found column runs:',runs)
for i,run in enumerate(runs):
    lx,rx=run
    crop=im.crop((lx,0,rx,h))
    bands_c = extract_bands(crop, bg_thresh=20)
    print('run',i,'lx,rx',run,'bands in crop:',bands_c)
    for j,band in enumerate(bands_c):
        colors = extract_colors_from_band(crop, band, bg_thresh=20)
        print(f' run {i} band {j} colors: {colors}')
