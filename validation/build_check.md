# 빌드 검증 기록 (v1.2, 2026-10-20)

```
syllables 975
font {'name': 'Arial_11', 'set': 0, 'cell': (14, 13), 'n': 975, 'slots': 31, 'add_cpu': 94032, 'add_gpu': 0}
font {'name': 'Arial_13_bold', 'set': 1, 'cell': (16, 17), 'n': 975, 'slots': 60, 'add_cpu': 8368, 'add_gpu': 0}
font {'name': 'Arial_15_bold', 'set': 1, 'cell': (16, 17), 'n': 975, 'slots': 62, 'add_cpu': 141200, 'add_gpu': 0}
font {'name': 'Arial_Black_15_Italic', 'set': 1, 'cell': (16, 17), 'n': 975, 'slots': 53, 'add_cpu': 7632, 'add_gpu': 0}
font {'name': 'Arial_Black_17', 'set': 1, 'cell': (16, 17), 'n': 975, 'slots': 44, 'add_cpu': 6672, 'add_gpu': 0}
font {'name': 'Arial_Black_20', 'set': 2, 'cell': (22, 21), 'n': 975, 'slots': 74, 'add_cpu': 235088, 'add_gpu': 0}
font {'name': 'Arial_Black_25', 'set': 2, 'cell': (22, 21), 'n': 975, 'slots': 58, 'add_cpu': 8160, 'add_gpu': 0}
rost names 3056
mrk strings 588
tdb keys 3923
tdb strings 5303 218448 -> 218448
elf strings 2719
code {'hook1': '0x32cea0', 'hadv': '0x32cf20', 'hook3': '0xb548a8'}
copy iso
done 1663033 sectors
빌드 결과 SHA-1: 2cc9edc1f743a1f9769aa67efbcc46fbec932438 (저장소 상태로 재빌드해 동일 확인)
xdelta round-trip SHA-1: 2cc9edc1f743a1f9769aa67efbcc46fbec932438 (= 결과 ISO)
```

## 경기 진입 시험 (`tools/freezetest.py`, PCSX2 v2.2.0 소프트웨어 렌더러)

| 빌드 | 멈춤 / 횟수 |
| --- | --- |
| 원본 ISO | 0 / 17 |
| v1.1 방식(글꼴 텍스처 +220KB) | 4 / 12, 3 / 12 |
| 글꼴 텍스처 256×256 상한(+88KB) | 9 / 12 |
| 작은 글꼴 3종만 확대 / Arial Black 4종만 확대 | 1 / 12 / 1 / 12 |
| 글꼴 텍스처 원래 크기(확인용, 한글 칸 4~43) | 0 / 12 |
| **v1.2 (원래 크기 + 라틴 확장 자리 활용, 한글 칸 31~74)** | **1 / 36** |

멈춤 상태: EE `0x4d02ac` 에서 프레임 완료 플래그(`0xb2095c`) 대기, VIF1 CHCR STR·VIF1_STAT VIS+INT, GIF CHCR STR·PATH3 마스크.

## 화면 확인

- 마이클 조던 모드(1985-86 불스 대 레이커스): v1.1 은 불스 유니폼 얼룩, `HOME`/`AWAY`/색 이름 번역 시 유니폼 무늬 사라짐 → v1.2 정상(원본과 비교).
- 메인 메뉴, VIP 안내·이름 입력, 팀 선택, 연출 설정, 선발 소개, 경기 HUD(선수 이름·득점 표시).
