#!/usr/bin/env python3
"""
카드뉴스 스펙을 슬라이드별 PNG로 export. 사용자가 HTML이 아니라 바로 올릴
이미지 N장을 받게 하는 용도.

설치 의존성 없음: 시스템에 깔린 Chrome(또는 Chromium) 헤드리스로 캡처한다.
각 슬라이드를 정확히 1080×1350 뷰포트에 단독으로 렌더하고, 배율(기본 2x)을
걸어 고해상도(2160×2700)로 굽는다. 인스타 압축을 거쳐도 또렷하게 남는다.

사용법:
    python export_png.py spec.json -o png_out/
    python export_png.py spec.json -o png_out/ --scale 2 --prefix raving

생성기와 같은 디렉터리에 있어야 한다(generate_cardnews 를 import).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_cardnews import render_parts, PRETENDARD  # noqa: E402

# Chrome/Chromium 실행파일 후보. macOS 우선, 그다음 PATH.
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

# 슬라이드 1장을 1080×1350 뷰포트에 꽉 채워 단독 렌더하는 페이지.
# 캐러셀용 body의 flex/gap/padding/그림자를 제거해 좌상단에 정확히 붙인다.
PAGE = """<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<link rel="stylesheet" href="{font}"><style>
{css}
html,body{{margin:0;padding:0;background:transparent;display:block;}}
.slide{{box-shadow:none!important;}}
</style></head><body>{slide}</body></html>"""


def find_chrome(explicit=None):
    candidates = ([explicit] if explicit else []) + CHROME_CANDIDATES
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chrome"):
        candidates.append(shutil.which(name))
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def main():
    ap = argparse.ArgumentParser(description="카드뉴스 슬라이드별 PNG export (Chrome 헤드리스)")
    ap.add_argument("spec", help="스펙 JSON 경로")
    ap.add_argument("-o", "--outdir", default="png", help="PNG 출력 폴더 (기본 png/)")
    ap.add_argument("--scale", type=int, default=2,
                    help="배율. 기본 2 → 2160×2700. 1 이면 정확히 1080×1350")
    ap.add_argument("--prefix", default="slide", help="파일명 접두 (기본 slide)")
    ap.add_argument("--chrome", help="Chrome 실행파일 경로 직접 지정")
    args = ap.parse_args()

    chrome = find_chrome(args.chrome)
    if not chrome:
        sys.exit("Chrome/Chromium 실행파일을 찾지 못했습니다. --chrome 로 경로를 지정하세요.")

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    _, css, slides = render_parts(spec)
    if not slides:
        sys.exit("슬라이드가 없습니다.")

    os.makedirs(args.outdir, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="cardnews_png_")
    made = []
    try:
        for i, slide_html in enumerate(slides, start=1):
            page = PAGE.format(font=PRETENDARD, css=css, slide=slide_html)
            html_path = os.path.join(tmp, f"slide-{i:02d}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(page)
            out = os.path.abspath(os.path.join(args.outdir, f"{args.prefix}-{i:02d}.png"))
            cmd = [
                chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                "--no-sandbox",
                f"--force-device-scale-factor={args.scale}",
                "--window-size=1080,1350",
                # CDN 폰트(Pretendard) 로드를 기다리도록 가상 시간 예산을 준다.
                "--virtual-time-budget=4000",
                f"--screenshot={out}",
                "file://" + html_path,
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if not os.path.exists(out):
                sys.stderr.write(res.stderr[-800:] + "\n")
                sys.exit(f"슬라이드 {i} 캡처 실패")
            made.append(out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    w, h = 1080 * args.scale, 1350 * args.scale
    print(f"PNG {len(made)}장 생성 ({w}×{h}) → {args.outdir}", file=sys.stderr)


if __name__ == "__main__":
    main()
