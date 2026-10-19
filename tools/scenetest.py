"""한글 ISO 로 빠른 경기 진입 → 장면 캡처 (메모리 여유 시험)."""
import sys, time, os
sys.path.insert(0, os.path.dirname(__file__)); import emu
out = sys.argv[1]
emu.start(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'NBA 2K11 (USA) (Korean).iso')))
time.sleep(40); emu.keys('start w3 x w8 x w3 x w5 x w5 x w8 x w10')
emu.shot(out.replace('.png', '_a.png')); emu.keys('x w2 x w2 x'); time.sleep(45); emu.shot(out)
emu.stop()
