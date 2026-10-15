# Кадры анимации первого экрана: черновая → покраска → санузел → готовая комната.
# python _build/frames.py <папка с исходными фото>  →  frames/ (1440) и frames-sm/ (720)
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1])
PHOTOS = ['dd1d0cb7', '77283472', '2a6f7783', 'f4d31233']
N, S, CARD, R = 121, 1440, 1180, 64

def cover(im, w, h, zoom):
    W, H = im.size
    k = max(w / W, h / H) * zoom
    im = im.resize((round(W * k), round(H * k)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

srcs = [Image.open(SRC / (p + '.jpg')).convert('RGB') for p in PHOTOS]
mask = Image.new('L', (CARD, CARD), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, CARD - 1, CARD - 1), R, fill=255)
shadow = Image.new('L', (S, S), 0)
off = (S - CARD) // 2
ImageDraw.Draw(shadow).rounded_rectangle((off + 30, off + 60, off + CARD - 30, off + CARD + 30), R, fill=70)
shadow = shadow.filter(ImageFilter.GaussianBlur(40))
base = Image.new('RGB', (S, S), 'white')
base.paste(Image.new('RGB', (S, S), (16, 27, 48)), (0, 0), shadow)

for d in ('frames', 'frames-sm'):
    (HERE / d).mkdir(exist_ok=True)
seg = (N - 1) / len(PHOTOS)
for i in range(N):
    t = i / seg                       # номер фото с дробной частью
    k = min(int(t), len(PHOTOS) - 1)
    f = t - k
    zoom = 1.0 + 0.08 * f             # медленный наезд внутри каждого фото
    img = cover(srcs[k], CARD, CARD, zoom)
    if f > 0.75 and k + 1 < len(PHOTOS):   # последняя четверть отрезка — переход к следующему фото
        a = (f - 0.75) / 0.25
        a = a * a * (3 - 2 * a)
        img = Image.blend(img, cover(srcs[k + 1], CARD, CARD, 1.0), a)
    fr = base.copy()
    fr.paste(img, (off, off), mask)
    fr.save(HERE / 'frames' / f'frame_{i + 1:04d}.jpg', quality=80, optimize=True)
    fr.resize((720, 720), Image.LANCZOS).save(HERE / 'frames-sm' / f'frame_{i + 1:04d}.jpg', quality=78, optimize=True)
print('кадров:', N)
