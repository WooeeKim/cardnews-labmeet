#!/usr/bin/env python3
"""카드뉴스 스펙을 '편집형 HTML(editor)'로 export.

생성기(generate_cardnews)와 같은 render_parts 를 써서 슬라이드는 동일하게 굽고,
브라우저에서 글자를 직접 고치고(contenteditable) 버튼으로 PNG를 내려받게 만든다.
→ 문구 수정 때마다 다시 굽지 않아도 된다. PNG 출력은 사용자가 브라우저에서.

특징:
- Pretendard 를 data URI 로 인라인 → 오프라인에서도 폰트 그대로, 캡처 빠름.
- 캡처는 html2canvas-pro. 부모 transform(축소 보기) 때문에 잘리는 걸 피하려고
  변형 없는 오프스크린 클론을 원본 1080x1350 으로 떠서 굽는다.
- 텍스트 요소에만 contenteditable 을 부여(이미지/위치는 잠금). 슬라이드 배경색은
  각 슬라이드에서 읽어 캡처 배경으로 쓴다(다크/라이트 테마 모두 대응).

사용법:
    python export_editor.py spec.json -o out.editor.html
    python export_editor.py spec.json                     # spec 옆에 <spec>.editor.html
"""
import argparse
import base64
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_cardnews import render_parts, PRETENDARD  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(REPO, "assets", "Pretendard.woff2")

# 편집 가능하게 만들 텍스트 요소들 (이미지·도형은 제외).
EDITABLE = (".h,.body,.info,.brand,.counter,.qb,.ab,.cover-label,"
            ".q-text,.q-by,.closing-note,.closing-cta")

EDITOR_CSS = """
body{background:#1b1b1d;margin:0;padding:40px 20px 120px;font-family:'Pretendard',sans-serif;}
.bar{position:fixed;left:0;top:0;right:0;z-index:50;display:flex;align-items:center;gap:16px;
  padding:14px 22px;background:rgba(20,20,22,0.92);backdrop-filter:blur(8px);
  border-bottom:1px solid #2c2c30;color:#eaeaea;font-size:14px;flex-wrap:wrap;}
.bar b{color:var(--accent,#5DCAA5);}
.bar .sp{flex:1;}
.bar button{background:var(--accent,#5DCAA5);color:#08231c;border:0;border-radius:999px;
  padding:10px 18px;font-size:14px;font-weight:700;cursor:pointer;font-family:inherit;}
.bar input[type=range]{accent-color:var(--accent,#5DCAA5);}
.tip{color:#9a9a9e;font-size:13px;}
.frames{display:flex;flex-direction:column;align-items:center;gap:28px;margin-top:72px;}
.frame{display:flex;flex-direction:column;align-items:center;gap:12px;}
.holder{width:calc(1080px * var(--z,0.5));height:calc(1350px * var(--z,0.5));}
.holder .slide{transform:scale(var(--z,0.5));transform-origin:top left;
  box-shadow:0 10px 40px rgba(0,0,0,0.5);border-radius:6px;}
.frame .dl{background:#26262a;color:#eaeaea;border:1px solid #3a3a40;border-radius:999px;
  padding:8px 16px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;}
[contenteditable]{outline:none;cursor:text;border-radius:4px;transition:box-shadow .12s;}
[contenteditable]:hover{box-shadow:0 0 0 2px rgba(125,125,125,0.45);}
[contenteditable]:focus{box-shadow:0 0 0 2px var(--accent,#5DCAA5);}
"""

# {SEL} 자리에 편집 대상 셀렉터를 끼워 넣는다.
EDITOR_JS = """
import h2c from 'https://cdn.jsdelivr.net/npm/html2canvas-pro@1.5.11/+esm';

const SEL = '__SEL__';
document.querySelectorAll('.slide').forEach(s => {
  s.querySelectorAll(SEL).forEach(el => { el.contentEditable = 'true'; el.spellcheck = false; });
});

const sandbox = document.createElement('div');
sandbox.style.cssText = 'position:fixed;left:-100000px;top:0;width:1080px;height:0;overflow:visible;';
document.body.appendChild(sandbox);
const pad = n => String(n).padStart(2, '0');

async function shoot(slide, name) {
  await document.fonts.ready;
  const bg = getComputedStyle(slide).backgroundColor || '#0e0e10';
  const clone = slide.cloneNode(true);
  clone.style.transform = 'none';
  clone.style.boxShadow = 'none';
  clone.style.borderRadius = '0';
  sandbox.innerHTML = '';
  sandbox.appendChild(clone);
  await new Promise(r => setTimeout(r, 20));
  const canvas = await h2c(clone, { scale: 2, width: 1080, height: 1350,
    backgroundColor: bg, useCORS: true, logging: false });
  sandbox.innerHTML = '';
  const blob = await new Promise(res => canvas.toBlob(res, 'image/png'));
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

document.querySelectorAll('.frame .dl').forEach((btn, i) => {
  btn.onclick = () => shoot(btn.parentElement.querySelector('.slide'), `slide-${pad(i+1)}.png`);
});
document.getElementById('all').onclick = async () => {
  const slides = [...document.querySelectorAll('.frame .slide')];
  for (let i = 0; i < slides.length; i++) {
    await shoot(slides[i], `slide-${pad(i+1)}.png`);
    await new Promise(r => setTimeout(r, 400));
  }
};
const z = document.getElementById('zoom');
const setZ = () => document.documentElement.style.setProperty('--z', z.value);
z.oninput = setZ; setZ();
"""


def font_face():
    """Pretendard woff2 를 data URI @font-face 로 인라인. 폰트가 없으면 CDN @import 로 폴백."""
    if os.path.exists(FONT_PATH):
        with open(FONT_PATH, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return (f"@font-face{{font-family:'Pretendard';font-weight:45 920;font-style:normal;"
                f"font-display:swap;src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    sys.stderr.write(f"경고: {FONT_PATH} 없음 → CDN 폰트로 폴백(오프라인 캡처 시 폰트 깨질 수 있음)\n")
    return f"@import url('{PRETENDARD}');"


def build_editor(spec):
    title, css, slides = render_parts(spec)
    accent = spec.get("theme", {}).get("accent", "#5DCAA5")
    frames = []
    for i, s in enumerate(slides, start=1):
        frames.append(f'<div class="frame"><div class="holder">{s}</div>'
                      f'<button class="dl">{i:02d} · 이 장 PNG 저장</button></div>')
    bar = (f'<div class="bar" style="--accent:{accent}"><b>{title} · 편집기</b>'
           '<span class="tip">글자를 클릭해서 바로 고치세요. 다 고치면 저장 버튼 ›</span>'
           '<span class="sp"></span>'
           '<label class="tip">보기 크기 <input id="zoom" type="range" min="0.25" max="1" step="0.05" value="0.5"></label>'
           f'<button id="all">전체 {len(slides)}장 PNG 저장</button></div>')
    js = EDITOR_JS.replace("__SEL__", EDITABLE)
    return (
        '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{title} · 편집기</title>'
        '<style>' + font_face() + css + EDITOR_CSS +
        f':root{{--accent:{accent};}}</style></head><body>'
        + bar + '<div class="frames">' + "".join(frames) + '</div>'
        + '<script type="module">' + js + '</script></body></html>'
    )


def main():
    ap = argparse.ArgumentParser(description="카드뉴스 편집형 HTML export")
    ap.add_argument("spec", help="스펙 JSON 경로")
    ap.add_argument("-o", "--output", help="출력 HTML 경로 (생략 시 <spec>.editor.html)")
    args = ap.parse_args()

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    out = build_editor(spec)

    path = args.output or (os.path.splitext(args.spec)[0] + ".editor.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"편집기 생성: {path} (슬라이드 {len(spec.get('slides', []))}장)", file=sys.stderr)


if __name__ == "__main__":
    main()
