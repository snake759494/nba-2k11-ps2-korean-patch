"""한글 ISO 경기 진입 후 멈춤 여부: FREEZE/OK."""
import sys, time, os
sys.path.insert(0, os.path.dirname(__file__)); import emu
from PIL import ImageChops
emu.start(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'NBA 2K11 (USA) (Korean).iso')))
time.sleep(50); emu.keys('start w2 start w3 x w8 x w3 x w5 x w5 x w8 x w10 x w2 x w2 x')
time.sleep(25)
shots = []
for i in range(4):
    time.sleep(15); shots.append(emu.shot('work/fz_%d.png' % i).convert('L')); emu.keys('x')
emu.stop()
from PIL import Image, ImageStat
# work/title_ref.png: 타이틀 화면 캡처(있으면 타이틀 복귀를 TITLE 로 따로 판정)
RP = os.path.join(os.path.dirname(__file__), '..', 'work', 'title_ref.png')
ref = Image.open(RP).convert('L').resize((64, 48)) if os.path.exists(RP) else None
def near_title(im): return ref is not None and ImageStat.Stat(ImageChops.difference(im.resize((64, 48)), ref)).mean[0] < 12
if all(near_title(s) for s in shots): print('TITLE')
else:
    fr = any(ImageChops.difference(shots[i], shots[i + 1]).getbbox() is None and not near_title(shots[i]) for i in range(3))
    print('FREEZE' if fr else 'OK')
