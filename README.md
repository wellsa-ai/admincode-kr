# Admincode KR

> 대한민국 행정표준코드(법정동)를 Git으로 관리합니다.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![data](https://img.shields.io/badge/data-Markdown-blue)](kr/) [![source](https://img.shields.io/badge/source-행정표준코드관리시스템-orange)](https://www.code.go.kr)

대한민국 **법정동(시도·시군구·읍면동·리)** 전체를 Markdown + YAML frontmatter 로 관리합니다. 행정구역 개편(신설·통폐합)이 Git diff 로 추적되며, 기계용 JSON 을 함께 산출해 서비스(주소 유효성 검증 등)가 바로 소비할 수 있습니다.

`wellsa-ai` 산하 [law-kr](https://github.com/wellsa-ai/law-kr) (법률) · [regulate-kr](https://github.com/wellsa-ai/regulate-kr) (행정규칙) · [precedent-kr](https://github.com/wellsa-ai/precedent-kr) (판례) 와 같은 패턴의 데이터 저장소입니다.

## 왜 필요한가?

주소는 **모든 생활 서비스의 입력값** 입니다. 그러나 사용자 입력 주소가 실존하는지("니미동" 같은 가짜·오타 차단) 검증하려면 신뢰 가능한 법정동 사전이 필요합니다. 행정구역은 개편 이력 자체가 정보이므로 — 언제 어떤 동이 신설·폐지·통합됐는지 — Git history 로 관리합니다.

## 구조

```
admincode-kr/
├── kr/                   # 시도별 Markdown (사람용 · diff 추적)
│   ├── 서울특별시.md      #   frontmatter: sido, generated, sigungu_count, legal_dong_count
│   └── ... (17개 시도)
├── data/
│   └── legal_dong.json   # 기계용: {"dong_sido": {동이름: [시도약칭...]}, "meta": {...}}
└── pipeline/
    └── build.py          # code.go.kr 다운로드 → md + json 빌드
```

## 빠른 시작

```bash
git clone https://github.com/wellsa-ai/admincode-kr.git
cd admincode-kr

# 서울 법정동 보기
cat kr/서울특별시.md

# 기계용 JSON (주소 검증 등)
python3 -c "import json; d=json.load(open('data/legal_dong.json')); print(d['dong_sido']['역삼동'])"
# ['서울']
```

## 갱신

법정동은 행정구역 개편 시에만 변경됩니다. 분기 1회 실행을 권장합니다.

```bash
python3 pipeline/build.py        # code.go.kr 에서 최신 전체자료 다운로드 → 재빌드
git diff                          # 개편 내역 확인
```

- 소스: 행정안전부 행정표준코드관리시스템 [code.go.kr](https://www.code.go.kr) — 법정동코드 전체자료 (무료 공개)
- 다운로드 방식: `POST /etc/codeFullDown.do` (`codeseId=법정동코드`) → ZIP(txt, euc-kr)

## 소비자

| 서비스 | 용도 |
|---|---|
| [obs-chatbot](https://github.com/wellsa-ai) 오이사 카카오 챗봇 | 견적 출발지/도착지 주소 실존 검증 (가짜 주소 접수 차단) |

## 라이선스

- 코드: MIT
- 데이터: 행정안전부 행정표준코드 (공공데이터, [공공누리](https://www.kogl.or.kr) 제1유형 — 출처표시)
