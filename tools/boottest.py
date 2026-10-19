"""부팅해서 타이틀 화면까지 가는지(멈춤 없이) 확인: 출력 OK/HANG."""
import sys, time, os, subprocess
sys.path.insert(0, os.path.dirname(__file__)); import emu
from PIL import Image
emu.start(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'NBA 2K11 (USA) (Korean).iso')))
time.sleep(45); im = emu.shot(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'work', 'boot.png'))
emu.stop()
# 법적 고지(흰 배경) 화면이면 멈춤
px = im.resize((8, 8)).convert('L').getdata()
print('HANG' if sum(px) / 64 > 180 else 'OK')
