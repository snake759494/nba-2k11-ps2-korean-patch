"""경기 진입 멈춤이 날 때까지 반복하고, 멈추면 세이브스테이트를 work/freeze.p2s 로 보관."""
import sys, time, os, shutil
sys.path.insert(0, os.path.dirname(__file__)); import emu
from PIL import ImageChops
iso = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'NBA 2K11 (USA) (Korean).iso'))
for n in range(int(sys.argv[1]) if len(sys.argv) > 1 else 10):
    emu.start(iso)
    time.sleep(50); emu.keys('start w2 start w3 x w8 x w3 x w5 x w5 x w8 x w10 x w2 x w2 x')
    time.sleep(25)
    shots = []
    for i in range(4):
        time.sleep(15); shots.append(emu.shot('work/fz_%d.png' % i).convert('L')); emu.keys('x')
    fr = any(ImageChops.difference(shots[i], shots[i + 1]).getbbox() is None for i in range(3))
    print(n, 'FREEZE' if fr else 'OK', flush=True)
    if fr:
        p = emu.savestate(8)
        if p: shutil.copy(p, 'work/freeze.p2s'); print('saved', p, flush=True)
        break
emu.stop()
