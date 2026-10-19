# 빌드 검증 기록 (v1.1, 2026-10-19)

```
syllables 975
font {'name': 'Arial_11', 'set': 0, 'cell': (14, 13), 'n': 975, 'slots': 220, 'add_cpu': 114064, 'add_gpu': 24576}
font {'name': 'Arial_13_bold', 'set': 1, 'cell': (16, 17), 'n': 975, 'slots': 133, 'add_cpu': 16112, 'add_gpu': 16384}
font {'name': 'Arial_15_bold', 'set': 1, 'cell': (16, 17), 'n': 975, 'slots': 129, 'add_cpu': 148304, 'add_gpu': 16384}
font {'name': 'Arial_Black_15_Italic', 'set': 2, 'cell': (22, 21), 'n': 975, 'slots': 182, 'add_cpu': 21312, 'add_gpu': 49152}
font {'name': 'Arial_Black_17', 'set': 2, 'cell': (22, 21), 'n': 975, 'slots': 176, 'add_cpu': 20656, 'add_gpu': 49152}
font {'name': 'Arial_Black_20', 'set': 2, 'cell': (22, 21), 'n': 975, 'slots': 161, 'add_cpu': 244320, 'add_gpu': 32768}
font {'name': 'Arial_Black_25', 'set': 2, 'cell': (22, 21), 'n': 975, 'slots': 137, 'add_cpu': 16544, 'add_gpu': 32768}
rost names 3056
mrk strings 588
tdb keys 3923
tdb strings 5303 218448 -> 218448
elf strings 2761
code {'hook1': '0x32cea0', 'hadv': '0x32cf20', 'hook3': '0xb548a8'}
copy iso
done 1663054 sectors
빌드 결과 SHA-1: 788a2f371912e19cf1b35ff26672a0ea5c6e2295 (저장소 상태로 재빌드해 동일 확인)
xdelta round-trip SHA-1: 788a2f371912e19cf1b35ff26672a0ea5c6e2295 (= 결과 ISO)
```

## 경기 진입 시험 (`tools/freezetest.py`, PCSX2 v2.2.0)

| 빌드 | 결과 |
| --- | --- |
| 원본 ISO | 정상 5 / 결과 없음 1 (6회) |
| v1.0 방식(`_TDB` 축소) | 멈춤 2 / 정상 4 (6회), 멈춤 1 / 정상 3 (4회) |
| 원문 그대로 재작성(크기 동일) | 정상 4 / 4 |
| 한글 대신 X 치환(`_TDB` 축소) | 멈춤 2 / 4 |
| 번역 + `_TDB` 원본 크기로 채움 | 정상 4 / 4 |
| **v1.1 최종** | **정상 8 / 8** |

화면 확인: 타이틀 → VIP 생성 → 메인 메뉴 → 빠른 경기(팀 선택, 선발 소개) → 경기 진행(선수 이름 한글), 게임 모드 / 특별 기능 / 불러오기·저장 / 어소시에이션 설정 화면.
