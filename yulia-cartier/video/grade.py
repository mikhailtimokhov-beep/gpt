# Portrait processing: upscale, subject cut-out, soft background blur, warm "Paris" grade, gentle skin smoothing.
import cv2, numpy as np, sys, os
from PIL import Image
from rembg import remove, new_session

SRC = os.path.join(os.path.dirname(__file__), '..', 'photos')
OUT = os.path.join(SRC, 'graded')
U = '/root/.claude/uploads/08fe52de-14d4-5ade-858f-7ff7e16713c1/'
session = new_session('u2net_human_seg')
sr = cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel('/root/models/FSRCNN_x3.pb'); sr.setModel('fsrcnn', 3)

def load(name):
    if name == 'sveta':   # crop Sveta from the 1 September photo
        im = Image.open(U + 'd6187723-image.jpg').convert('RGB'); W, H = im.size
        x0, x1, y0 = .64, .905, .16; w = (x1 - x0) * W
        return np.array(im.crop((int(x0*W), int(y0*H), int(x1*W), int(y0*H + w*1.25))))[:, :, ::-1]
    return cv2.imread(os.path.join(SRC, name))

def upscale(img, target=1100):
    while max(img.shape[:2]) < target * .7:
        img = sr.upsample(img)
    h, w = img.shape[:2]; s = target / max(h, w)
    return cv2.resize(img, (int(w*s), int(h*s)), interpolation=cv2.INTER_LANCZOS4 if s < 1 else cv2.INTER_CUBIC)

def grade(img):
    f = img.astype(np.float32) / 255
    f = f ** 0.95                                         # lift mids
    f = 0.5 + (f - 0.5) * 1.06                            # gentle contrast
    b, g, r = cv2.split(f)
    r = r * 1.04 + .012; g = g * 1.01 + .006; b = b * .94   # warm
    f = cv2.merge([b, g, r])
    gray = cv2.cvtColor(np.clip(f, 0, 1), cv2.COLOR_BGR2GRAY)[..., None]
    f = gray + (f - gray) * .88                           # soft desaturation
    return np.clip(f, 0, 1)

def process(name, out, blur=90):
    img = upscale(load(name))
    mask = np.array(remove(Image.fromarray(img[:, :, ::-1]), session=session, only_mask=True)).astype(np.float32) / 255
    mask = cv2.GaussianBlur(mask, (0, 0), 3)[..., None]
    smooth = cv2.bilateralFilter(img, 9, 28, 9)            # light skin retouch on subject only
    subj = cv2.addWeighted(img, .55, smooth, .45, 0)
    bg = cv2.GaussianBlur(img, (0, 0), max(img.shape[:2]) / blur)
    bg = (bg.astype(np.float32) * .88).astype(np.uint8)    # recede background
    comp = (subj * mask + bg * (1 - mask)).astype(np.uint8)
    f = grade(comp)
    h, w = f.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    vig = 1 - .35 * (((xx - w/2) / (w/1.3))**2 + ((yy - h/2.2) / (h/1.3))**2)
    f = f * np.clip(vig, .55, 1)[..., None]
    rng = np.random.default_rng(7)
    f = f + rng.normal(0, .012, f.shape[:2])[..., None]   # fine film grain
    cv2.imwrite(os.path.join(OUT, out), (np.clip(f, 0, 1) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(out, f.shape[1], 'x', f.shape[0])

JOBS = [('solo-2017.jpg', 'y2017.jpg'), ('solo-bike.jpg', 'ybike.jpg'), ('solo-today.jpg', 'ytoday.jpg'),
        ('solo-selfie.jpg', 'yselfie.jpg'), ('solo-us.jpg', 'yfinal.jpg'), ('yulia-blossom.jpg', 'yblossom.jpg', 260),
        ('yulia-courage.jpg', 'ycourage.jpg'), ('tatyana-2.jpg', 'tatyana.jpg'), ('tatyana-1.jpg', 'tatyana-hall.jpg'),
        ('sveta', 'sveta.jpg')]
for job in JOBS:
    if len(sys.argv) > 1 and job[1] not in sys.argv[1:]: continue
    process(*job)
