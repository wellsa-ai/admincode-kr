"""행정안전부 법정동코드 전체자료 → Markdown(사람용) + JSON(기계용) 빌드.

소스: 행정표준코드관리시스템(code.go.kr) '법정동코드 전체자료' (무료 공개, 로그인 불필요)
  POST https://www.code.go.kr/etc/codeFullDown.do (codeseId=법정동코드) → ZIP(txt, euc-kr)
  형식: 법정동코드(10자리) \t 법정동명 \t 폐지여부

산출:
  kr/{시도}.md          — 시도별 시군구/읍면동 목록 (YAML frontmatter, git diff 로 개편 추적)
  data/legal_dong.json  — {"dong_sido": {동이름: [시도약칭...]}, "meta": {...}} (주소 검증 등 서비스 소비용)

갱신: 행정구역 개편(통폐합) 시만 변경 → 분기 1회 실행 권장.
사용: python3 pipeline/build.py [--from-file 법정동코드.txt]
"""
from __future__ import annotations

import io
import json
import sys
import urllib.parse
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

DOWN_URL = "https://www.code.go.kr/etc/codeFullDown.do"
ROOT = Path(__file__).resolve().parent.parent

SIDO_SHORT = {
    "서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구", "인천광역시": "인천",
    "광주광역시": "광주", "대전광역시": "대전", "울산광역시": "울산",
    "세종특별자치시": "세종", "경기도": "경기",
    "강원특별자치도": "강원", "강원도": "강원",
    "충청북도": "충북", "충청남도": "충남",
    "전북특별자치도": "전북", "전라북도": "전북", "전라남도": "전남",
    "경상북도": "경북", "경상남도": "경남",
    "제주특별자치도": "제주", "제주도": "제주",
}


def download() -> str:
    body = urllib.parse.urlencode({"codeseId": "법정동코드"}).encode()
    req = urllib.request.Request(DOWN_URL, data=body)
    with urllib.request.urlopen(req, timeout=60) as r:
        zdata = r.read()
    z = zipfile.ZipFile(io.BytesIO(zdata))
    return z.read(z.infolist()[0]).decode("euc-kr", errors="replace")


def parse(text: str):
    """존재 행만 → {시도전체명: {시군구명: [하위지명...]}} + dong_sido 맵."""
    tree: dict[str, dict[str, list[str]]] = {}
    dong_sido: dict[str, set[str]] = {}
    total = 0
    for line in text.splitlines()[1:]:
        parts = line.strip().split("\t")
        if len(parts) < 3:
            continue
        total += 1
        _code, name, status = parts[0], parts[1], parts[2]
        if status != "존재":
            continue
        tokens = name.split()
        sido_full = tokens[0]
        short = SIDO_SHORT.get(sido_full)
        if not short:
            continue
        if len(tokens) == 1:
            tree.setdefault(sido_full, {})
            continue
        # 시군구 단위: 두 번째 토큰부터 시/군/구로 끝나는 연속 토큰
        sgg_tokens, rest = [], []
        for tok in tokens[1:]:
            if not rest and tok.endswith(("시", "군", "구")):
                sgg_tokens.append(tok)
            else:
                rest.append(tok)
        sgg = " ".join(sgg_tokens) if sgg_tokens else "(직할)"
        node = tree.setdefault(sido_full, {}).setdefault(sgg, [])
        if rest:
            leaf = " ".join(rest)
            node.append(leaf)
            for tok in rest:
                if tok.endswith(("동", "읍", "면", "리", "가")) and not tok.endswith(("시", "군", "구")):
                    dong_sido.setdefault(tok, set()).add(short)
    return tree, dong_sido, total


def write_markdown(tree) -> int:
    kr = ROOT / "kr"
    kr.mkdir(exist_ok=True)
    today = date.today().isoformat()
    count = 0
    for sido_full, sggs in sorted(tree.items()):
        dong_total = sum(len(v) for v in sggs.values())
        lines = [
            "---",
            f"sido: {sido_full}",
            f"generated: {today}",
            f"sigungu_count: {len(sggs)}",
            f"legal_dong_count: {dong_total}",
            "source: 행정안전부 행정표준코드관리시스템(code.go.kr) 법정동코드 전체자료",
            "---",
            "",
            f"# {sido_full} 법정동",
            "",
        ]
        for sgg, dongs in sorted(sggs.items()):
            lines.append(f"## {sgg}")
            lines.append("")
            if dongs:
                lines.append(" · ".join(dongs))
            else:
                lines.append("(하위 법정동 없음)")
            lines.append("")
        (kr / f"{sido_full}.md").write_text("\n".join(lines), encoding="utf-8")
        count += 1
    return count


def write_json(dong_sido, total) -> Path:
    out = ROOT / "data" / "legal_dong.json"
    out.parent.mkdir(exist_ok=True)
    data = {
        "dong_sido": {k: sorted(v) for k, v in sorted(dong_sido.items())},
        "meta": {
            "source": "행정안전부 행정표준코드관리시스템(code.go.kr) 법정동코드 전체자료",
            "generated": date.today().isoformat(),
            "rows_total": total,
            "dong_count": len(dong_sido),
        },
    }
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return out


def main() -> int:
    if "--from-file" in sys.argv:
        path = sys.argv[sys.argv.index("--from-file") + 1]
        text = open(path, "rb").read().decode("euc-kr", errors="replace")
        print(f"로컬 파일 사용: {path}")
    else:
        print(f"다운로드: {DOWN_URL}")
        text = download()
    tree, dong_sido, total = parse(text)
    md_count = write_markdown(tree)
    json_path = write_json(dong_sido, total)
    print(f"Markdown {md_count}개 시도 파일 → kr/")
    print(f"JSON → {json_path} (고유 동/읍/면/리 {len(dong_sido)}개, 원본 {total}행)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
