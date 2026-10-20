"""순차 실험: 각 설정으로 빌드 후 freezetest N회. 사용: experiment.py 이름=ENV1,ENV2 ..."""
import subprocess, os, sys
N = int(os.environ.get('KO_N', '4'))
for spec in sys.argv[1:]:
    name, _, envs = spec.partition('=')
    env = dict(os.environ)
    for e in filter(None, envs.split(',')):
        k, _, v = e.partition(':'); env[k] = v or '1'
    subprocess.run([sys.executable, '-I', 'tools/build.py'], env=env, capture_output=True)
    res = []
    for i in range(N):
        r = subprocess.run([sys.executable, '-I', 'tools/freezetest.py'], capture_output=True, text=True).stdout.strip().split('\n')[-1]
        res.append(r)
    print(name, res, flush=True)
