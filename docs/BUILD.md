# 재빌드 방법

필요한 것: Python 3.10+ (numpy, Pillow), .NET 8 SDK(`tools/vcx` 압축기 빌드), xdelta3.

## 준비

저장소 루트에 다음 파일을 둡니다(저장소에는 포함되지 않음).

- `NBA 2K11 (USA).iso`: 해시가 README 표와 일치하는 원본
- `NanumSquareNeo-dEb.ttf`, `NanumSquareNeo-eHv.ttf`: 네이버 나눔스퀘어 네오 ExtraBold·Heavy
- `Galmuri11.ttf`: 갈무리11

압축기는 다음 명령으로 빌드합니다. 결과물은 `tools/bin/vcx.exe`에 생깁니다.

```
dotnet publish tools/vcx -c Release -o tools/bin
```

## 빌드

```
python tools/build.py      # -> NBA 2K11 (USA) (Korean).iso
xdelta3 -e -S none -A -s "NBA 2K11 (USA).iso" "NBA 2K11 (USA) (Korean).iso" NBA_2K11_PS2_KO_v1.2.xdelta
```

빌드 시험용 환경 변수: `KO_NOROST`, `KO_NOTDB`, `KO_NOMRK`, `KO_NOELF`, `KO_NOCODE`(해당 부분 원본 유지).

## 번역 수정

- `translation/ko/<묶음>.json`: `{ "번호": "번역" }`. 번호는 같은 이름의 원문 묶음 `translation/en/<묶음>.json`(`[{id, en}]`) 항목을 가리킵니다. 빌드는 원문이 같은 문자열을 모두 번역문으로 바꿉니다.
- `translation/fix/`: 짧은 문자열 표, 경기 화면 예외 처리 등 수동 보정
- 번역 지침: `translation/STYLE.md`

## 검증

PCSX2 휴대용 사본 폴더를 `PCSX2_DIR` 환경 변수로 지정하고 다음 명령을 실행합니다.

```
python tools/freezetest.py         # 경기 진입 후 멈춤 검사: OK / FREEZE / TITLE
python tools/experiment.py full=   # 빌드 + freezetest 4회
```
