#!/usr/bin/env python3
"""
인터뷰형 카드뉴스(인스타 캐러셀) HTML 생성기.

스펙(JSON) -> HTML 1파일(슬라이드 N장 세로 나열). 모든 위치/타이포 규칙은
references/design-system.md 에서 추출한 검증된 값. 브랜드/테마만 바꾸면
어떤 이벤트든 동일한 완성도로 찍어낼 수 있다.

사용법:
    python generate_cardnews.py spec.json -o out.html
    python generate_cardnews.py spec.json            # stdout 으로 출력

스펙 스키마는 references/example-spec.json 참고.
"""
import argparse
import html
import json
import sys

# --- 전역 토큰 (테마와 무관하게 고정) -------------------------------------
PRETENDARD = ("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/"
              "dist/web/static/pretendard.css")

# 인터뷰 카드 제목 글자크기 자동 버킷 (한 줄 nowrap 기준, 길수록 작게).
# 명시적으로 heading_size 를 주면 무시된다.
def auto_heading_size(text):
    n = len(text)
    if n <= 9:   return 58
    if n <= 11:  return 56
    if n <= 13:  return 54
    if n <= 15:  return 50
    if n <= 17:  return 48
    return 44

# 본문 길이에 따른 3단계 처리 (글이 길수록 작게/줄간격 좁게/위로 끌어올림).
# design-system.md 의 "긴 후기 처리" 규칙.
def body_style(text, info_top):
    n = len(text)
    if n <= 190:
        return 34, 1.74, info_top + 78, False     # 기본
    if n <= 240:
        return 32, 1.68, 500, False                # 긴 글
    return 31, 1.64, 500, True                     # 매우 긴 글 (제목도 위로)

def esc(s):
    """텍스트 이스케이프. \n 은 <br> 로 (헤드라인 줄바꿈용)."""
    return html.escape(str(s)).replace("\n", "<br>")


def brand_html(brand):
    name = esc(brand.get("name", "랩미"))
    suffix = esc(brand.get("suffix", "magazine"))
    return f'<div class="brand">{name} <span>{suffix}</span></div>'

def counter_html(n, total):
    return f'<div class="counter">{n:02d} / {total:02d}</div>'

def arrow_html(accent):
    return (f'<svg style="position:absolute;right:74px;top:1218px;" width="78" '
            f'height="46" viewBox="0 0 78 46" fill="none"><path d="M6 23 H68 '
            f'M48 7 L70 23 L48 39" stroke="{accent}" stroke-width="6" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg>')


def render_cover(slide, ctx):
    accent = ctx["accent"]
    parts = [ctx["brand"], counter_html(ctx["n"], ctx["total"])]
    # 말풍선 대화 (질문 -> 답변). 둘 다 있을 때만 그린다.
    q = slide.get("question")
    a = slide.get("answer")
    if q or a:
        parts.append('<div style="position:absolute;left:80px;top:300px;width:64px;'
                     'height:64px;border-radius:50%;background:rgba(255,255,255,0.18);"></div>')
    if q:
        parts.append(f'<div style="position:absolute;left:168px;top:300px;background:'
                     f'{ctx["bubble_gray_bg"]};color:#eee;font-size:36px;padding:20px 30px;'
                     f'border-radius:34px 34px 34px 10px;">{esc(q)}</div>')
    if a:
        parts.append(f'<div style="position:absolute;right:80px;top:415px;background:{accent};'
                     f'color:{ctx["answer_text"]};font-size:36px;font-weight:500;'
                     f'padding:20px 34px;border-radius:34px 34px 10px 34px;">{esc(a)}</div>')
    # 헤드라인
    headline = slide.get("headline", "")
    if isinstance(headline, list):
        headline = "\n".join(headline)
    htop = slide.get("headline_top", 830)
    hsize = slide.get("headline_size", 76)
    lh = slide.get("headline_line_height", 1.16)
    parts.append(f'<div class="h" style="top:{htop}px;font-size:{hsize}px;'
                 f'line-height:{lh};">{esc(headline)}</div>')
    # 하단 라벨
    label = slide.get("label")
    if label:
        parts.append(f'<div style="position:absolute;left:80px;top:1170px;font-size:36px;'
                     f'color:{accent};">{esc(label)}</div>')
    parts.append(arrow_html(accent))
    return '<div class="slide">' + "".join(parts) + '</div>'


def render_interview(slide, ctx):
    accent = ctx["accent"]
    heading = slide.get("heading", "")
    byline = slide.get("byline", "")
    body = slide.get("body", "")

    hsize = slide.get("heading_size") or auto_heading_size(heading)
    bfs, blh, btop_auto, lift = body_style(body, 0)

    # 매우 긴 글이면 제목을 살짝 위로 올려 공간 확보 (default 348), 아니면 360.
    htop = slide.get("heading_top") or (348 if lift else 360)
    info_top = htop + hsize + 30                       # 위치 공식
    bfs, blh, btop_auto, lift = body_style(body, info_top)
    btop = slide.get("body_top") or btop_auto

    nowrap = ";white-space:nowrap" if "\n" not in str(heading) else ""
    parts = [
        ctx["brand"], counter_html(ctx["n"], ctx["total"]),
        f'<div class="h" style="top:{htop}px;font-size:{hsize}px{nowrap};">{esc(heading)}</div>',
        f'<div class="info" style="top:{info_top}px;">{esc(byline)}</div>',
        f'<div class="body" style="top:{btop}px;font-size:{bfs}px;line-height:{blh};">{esc(body)}</div>',
        arrow_html(accent),
    ]
    return '<div class="slide">' + "".join(parts) + '</div>'


def render_closing(slide, ctx):
    accent = ctx["accent"]
    parts = [ctx["brand"], counter_html(ctx["n"], ctx["total"])]
    headline = slide.get("headline", "")
    if isinstance(headline, list):
        headline = "\n".join(headline)
    htop = slide.get("headline_top", 300)
    hsize = slide.get("headline_size", 56)
    lh = slide.get("headline_line_height", 1.22)
    parts.append(f'<div class="h" style="top:{htop}px;font-size:{hsize}px;'
                 f'line-height:{lh};">{esc(headline)}</div>')
    # 짧은 인용 모음 (text + byline 블록을 150px 간격으로)
    quotes = slide.get("quotes", [])
    top = slide.get("quotes_top", 550)
    for qt in quotes:
        parts.append(f'<div style="position:absolute;left:80px;top:{top}px;font-size:37px;'
                     f'color:rgba(255,255,255,0.85);">{esc(qt.get("text",""))}</div>')
        if qt.get("byline"):
            parts.append(f'<div style="position:absolute;left:80px;top:{top+52}px;font-size:30px;'
                         f'color:rgba(255,255,255,0.4);">{esc(qt["byline"])}</div>')
        top += 150
    # 안내 문단
    note = slide.get("note")
    if note:
        ntop = slide.get("note_top", 1105)
        parts.append(f'<div style="position:absolute;left:80px;top:{ntop}px;width:920px;'
                     f'font-size:33px;line-height:1.55;color:rgba(255,255,255,0.55);">{esc(note)}</div>')
    # CTA
    cta = slide.get("cta")
    if cta:
        ctop = slide.get("cta_top", 1235)
        csize = slide.get("cta_size", 37)
        parts.append(f'<div style="position:absolute;left:80px;top:{ctop}px;font-size:{csize}px;'
                     f'font-weight:500;color:{accent};">{esc(cta)}</div>')
    # 마감 슬라이드는 화살표 없음.
    return '<div class="slide">' + "".join(parts) + '</div>'


RENDERERS = {"cover": render_cover, "interview": render_interview, "closing": render_closing}


def render_parts(spec):
    """스펙을 (title, css, [슬라이드 HTML...]) 로 분해. 전체 페이지(build)와
    슬라이드별 PNG export(export_png) 양쪽에서 재사용한다."""
    theme = spec.get("theme", {})
    bg = theme.get("bg", "#0e0e10")
    accent = theme.get("accent", "#5DCAA5")
    bubble_gray_bg = theme.get("bubble_gray_bg", "#2a2a2e")
    answer_text = theme.get("answer_text", "#04342C")
    brand = brand_html(spec.get("brand", {}))
    title = esc(spec.get("title", "랩미 magazine"))
    slides = spec.get("slides", [])
    total = len(slides)

    css = f"""*{{margin:0;padding:0;box-sizing:border-box;}}body{{font-family:'Pretendard',sans-serif;}}
.slide{{width:1080px;height:1350px;background:{bg};color:#fff;position:relative;overflow:hidden;}}
.brand{{position:absolute;left:80px;top:64px;font-size:42px;font-weight:500;}}.brand span{{color:{accent};}}
.counter{{position:absolute;right:80px;top:72px;font-size:33px;color:rgba(255,255,255,0.4);}}
.h{{position:absolute;left:80px;font-weight:700;color:#fff;letter-spacing:-1px;}}
.info{{position:absolute;left:80px;font-size:32px;font-weight:500;color:rgba(255,255,255,0.5);}}
.body{{position:absolute;left:80px;width:920px;font-size:34px;line-height:1.74;color:rgba(255,255,255,0.8);}}
body{{background:#f2f0e9;display:flex;flex-direction:column;align-items:center;gap:32px;padding:48px;}}.slide{{box-shadow:0 4px 24px rgba(0,0,0,0.15);}}"""

    rendered = []
    for i, slide in enumerate(slides, start=1):
        stype = slide.get("type", "interview")
        ctx = {"brand": brand, "n": i, "total": total, "accent": accent,
               "bubble_gray_bg": bubble_gray_bg, "answer_text": answer_text}
        renderer = RENDERERS.get(stype)
        if renderer is None:
            raise ValueError(f"알 수 없는 슬라이드 type: {stype!r} (cover/interview/closing)")
        rendered.append(renderer(slide, ctx))

    return title, css, rendered


def build(spec):
    title, css, rendered = render_parts(spec)
    return (f'<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">'
            f'<title>{title}</title><link rel="stylesheet" href="{PRETENDARD}">'
            f'<style>{css}</style></head><body>' + "".join(rendered) + '</body></html>')


def main():
    ap = argparse.ArgumentParser(description="인터뷰형 카드뉴스 HTML 생성기")
    ap.add_argument("spec", help="스펙 JSON 파일 경로")
    ap.add_argument("-o", "--output", help="출력 HTML 경로 (생략 시 stdout)")
    args = ap.parse_args()

    with open(args.spec, encoding="utf-8") as f:
        spec = json.load(f)
    out = build(spec)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"생성 완료: {args.output} (슬라이드 {len(spec.get('slides', []))}장)", file=sys.stderr)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
