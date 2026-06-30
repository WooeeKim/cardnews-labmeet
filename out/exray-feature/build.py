#!/usr/bin/env python3
"""EX-RAY 리포트 미리보기 카드뉴스 (8장) — 정적 / 광고용 / 기능 나열형.

스토리(exray-intro)와 달리 '리포트가 어떻게 생겼는지'를 목업 UI로 보여준다.
- 목차, 카톡 원문 인용 근거, 관계 7단계 타임라인, 정량 지표 바,
  재회 가능성 게이지, 다음 연애 가이드 카드.
- 크림 라이트 + 핑크 브랜드 토큰은 exray-intro와 공유.
- 결합 HTML + 슬라이드별 PNG + 편집기 HTML 생성.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# --- 테마 (EX-RAY / 크림 라이트 + 핑크) --------------------------------------
BG = "#fff8ef"
ACCENT = "#ff2e63"
ANSWER_TEXT = "#ffffff"
INK = "#0d0d0d"
INK_RGB = "13,13,13"
PRETENDARD = ("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/"
              "dist/web/static/pretendard.css")

CSS = f"""*{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Pretendard',sans-serif;}}
.slide{{width:1080px;height:1350px;color:{INK};position:relative;overflow:hidden;
  background-color:{BG};
  background-image:radial-gradient(rgba({INK_RGB},0.05) 1px, transparent 1.5px);
  background-size:30px 30px;}}
.slide h1,.slide h2,.slide p,.slide span,.slide div{{word-break:keep-all;}}
.brand{{position:absolute;left:80px;top:72px;font-size:34px;font-weight:800;letter-spacing:-0.5px;}}
.brand span{{color:{ACCENT};}}
.counter{{position:absolute;left:80px;bottom:62px;font-size:27px;font-weight:600;
  line-height:1;letter-spacing:1px;color:rgba({INK_RGB},0.30);}}
.kicker{{position:absolute;left:80px;font-size:25px;font-weight:800;letter-spacing:2px;
  color:{ACCENT};}}
.h{{position:absolute;left:80px;width:920px;font-weight:800;color:{INK};
  letter-spacing:-1px;line-height:1.22;}}
.note{{position:absolute;left:80px;width:920px;font-size:29px;line-height:1.7;
  color:rgba({INK_RGB},0.55);}}
.cta{{position:absolute;left:80px;font-size:36px;font-weight:700;color:{ACCENT};}}
/* 리포트 패널(흰 카드) */
.panel{{position:absolute;left:80px;width:920px;background:#fff;
  border:1px solid rgba({INK_RGB},0.08);border-radius:30px;
  box-shadow:0 16px 38px rgba(0,0,0,0.06);padding:46px 48px;}}
.plab{{font-size:23px;font-weight:800;letter-spacing:1px;color:rgba({INK_RGB},0.4);
  margin-bottom:24px;}}
/* 목차 */
.toc-row{{display:flex;align-items:center;gap:28px;padding:21px 0;
  border-bottom:1px solid rgba({INK_RGB},0.07);}}
.toc-row.last{{border-bottom:0;padding-bottom:0;}}
.toc-row.first{{padding-top:0;}}
.toc-num{{font-size:25px;font-weight:800;color:{ACCENT};width:42px;flex:none;}}
.toc-title{{font-size:31px;font-weight:600;color:{INK};}}
/* 인용 */
.quote{{font-size:33px;line-height:1.5;color:{INK};font-weight:600;}}
.quote-meta{{font-size:24px;color:rgba({INK_RGB},0.4);margin-top:18px;}}
.verdict{{font-size:30px;line-height:1.55;color:rgba({INK_RGB},0.75);}}
.verdict b{{color:{ACCENT};font-weight:800;}}
/* 정량 지표 바 */
.stat{{margin-bottom:30px;}}
.stat.last{{margin-bottom:0;}}
.stat-top{{display:flex;justify-content:space-between;align-items:baseline;
  font-size:28px;margin-bottom:13px;}}
.stat-label{{color:rgba({INK_RGB},0.6);font-weight:600;}}
.stat-val{{color:{INK};font-weight:800;}}
.bar{{height:18px;border-radius:999px;background:rgba({INK_RGB},0.08);overflow:hidden;}}
.bar > i{{display:block;height:100%;border-radius:999px;background:{ACCENT};}}
/* 타임라인 */
.tl-wrap{{position:relative;margin-top:66px;}}
.tl-line{{position:absolute;top:13px;left:7%;right:7%;height:3px;
  background:rgba({INK_RGB},0.13);}}
.tl{{display:flex;position:relative;}}
.tl-cell{{flex:1;display:flex;flex-direction:column;align-items:center;gap:20px;}}
.tl-dot{{width:28px;height:28px;border-radius:50%;background:rgba({INK_RGB},0.18);
  border:5px solid #fff;box-shadow:0 0 0 2px rgba({INK_RGB},0.10);}}
.tl-dot.on{{background:{ACCENT};box-shadow:0 0 0 3px {ACCENT}44;width:34px;height:34px;
  margin-top:-3px;}}
.tl-lab{{font-size:23px;color:rgba({INK_RGB},0.5);font-weight:600;}}
.tl-lab.on{{color:{ACCENT};font-weight:800;}}
.tl-call{{position:absolute;font-size:24px;font-weight:700;color:{ACCENT};}}
/* 게이지 */
.gnum{{font-size:150px;font-weight:800;color:{ACCENT};line-height:0.9;
  letter-spacing:-5px;}}
.gnum span{{font-size:64px;letter-spacing:-2px;}}
.gsub{{font-size:30px;font-weight:700;color:rgba({INK_RGB},0.5);margin-top:8px;}}
/* 가이드 액션 */
.act{{display:flex;gap:26px;align-items:flex-start;padding:22px 0;
  border-bottom:1px solid rgba({INK_RGB},0.07);}}
.act.last{{border-bottom:0;padding-bottom:0;}}
.act.first{{padding-top:0;}}
.act-n{{width:50px;height:50px;flex:none;border-radius:50%;background:{ACCENT};
  color:#fff;font-size:26px;font-weight:800;display:flex;align-items:center;
  justify-content:center;}}
.act-t{{font-size:30px;line-height:1.45;color:{INK};font-weight:500;padding-top:6px;}}
.act-t b{{font-weight:800;}}
/* 칩(커버) */
.pill{{display:inline-block;background:#fff;border:1px solid rgba({INK_RGB},0.1);
  border-radius:999px;padding:15px 28px;font-size:27px;font-weight:700;
  color:rgba({INK_RGB},0.7);margin:0 12px 14px 0;}}
.pill b{{color:{ACCENT};}}
/* Top3 이유(랭크 + 기여도 바) */
.rank{{display:flex;gap:24px;align-items:flex-start;padding:26px 0;
  border-bottom:1px solid rgba({INK_RGB},0.07);}}
.rank.first{{padding-top:0;}}
.rank.last{{border-bottom:0;padding-bottom:0;}}
.rank-n{{width:46px;height:46px;flex:none;border-radius:13px;background:{ACCENT};
  color:#fff;font-size:25px;font-weight:800;display:flex;align-items:center;
  justify-content:center;margin-top:2px;}}
.rank-body{{flex:1;}}
.rank-top{{display:flex;justify-content:space-between;align-items:baseline;
  margin-bottom:14px;}}
.rank-title{{font-size:31px;font-weight:800;color:{INK};}}
.rank-pct{{font-size:29px;font-weight:800;color:{ACCENT};flex:none;margin-left:18px;}}
.rank-ev{{font-size:25px;color:rgba({INK_RGB},0.55);line-height:1.45;}}
/* 명대사(무드 행) */
.mrow{{display:flex;align-items:center;gap:24px;padding:23px 0;
  border-bottom:1px solid rgba({INK_RGB},0.07);}}
.mrow.first{{padding-top:0;}}
.mrow.last{{border-bottom:0;padding-bottom:0;}}
.mtag{{font-size:26px;font-weight:800;flex:none;width:138px;color:{INK};}}
.mq{{font-size:28px;font-weight:600;color:{INK};line-height:1.4;}}
/* 팩폭(나 vs 상대) */
.faults{{display:flex;gap:40px;}}
.fcol{{flex:1;}}
.fcol.them{{border-left:1px solid rgba({INK_RGB},0.08);padding-left:38px;}}
.fname{{font-size:27px;font-weight:700;color:rgba({INK_RGB},0.55);}}
.fpct{{font-size:64px;font-weight:800;letter-spacing:-2px;color:{INK};
  margin:4px 0 22px;}}
.fpct.hi{{color:{ACCENT};}}
.fchip{{background:rgba({INK_RGB},0.05);border-radius:15px;padding:15px 18px;
  font-size:25px;font-weight:600;color:rgba({INK_RGB},0.78);margin-bottom:13px;}}
.fchip b{{color:{ACCENT};font-weight:800;}}
.tag{{display:inline-block;background:{ACCENT}1a;color:{ACCENT};border-radius:999px;
  padding:12px 24px;font-size:27px;font-weight:800;}}
/* 지표 칩(차별점) */
.mchip{{display:inline-block;background:rgba({INK_RGB},0.05);border-radius:15px;
  padding:14px 24px;font-size:27px;font-weight:700;color:rgba({INK_RGB},0.8);
  margin:0 13px 14px 0;}}
/* 톤 4모드 카드 */
.modes{{display:flex;flex-wrap:wrap;gap:22px;}}
.mode{{flex:1 1 calc(50% - 11px);background:rgba({INK_RGB},0.035);
  border:1px solid rgba({INK_RGB},0.06);border-radius:22px;padding:30px 30px;}}
.mode-emo{{font-size:42px;line-height:1;}}
.mode-name{{font-size:30px;font-weight:800;color:{INK};margin:12px 0 8px;}}
.mode-desc{{font-size:24px;line-height:1.45;color:rgba({INK_RGB},0.55);}}"""

ARROW = (f'<div class="arrow" style="position:absolute;right:84px;bottom:62px;'
         f'font-size:27px;font-weight:600;line-height:1;color:{ACCENT};">&gt;</div>')


def chrome_path(explicit=None):
    cands = ([explicit] if explicit else []) + [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for n in ("google-chrome", "google-chrome-stable", "chromium", "chrome"):
        cands.append(shutil.which(n))
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


def brand(n, total, arrow=True):
    s = ('<div class="brand">EX-<span>RAY</span></div>'
         f'<div class="counter">{n:02d}</div>')
    return s, (ARROW if arrow else "")


def head_block(kicker, heading, *, ktop=288, htop=326, hsize=46):
    """챕터 키커 + 제목."""
    return (f'<div class="kicker" style="top:{ktop}px;">{kicker}</div>'
            f'<div class="h" style="top:{htop}px;font-size:{hsize}px;">{heading}</div>')


# ── 슬라이드 ──────────────────────────────────────────────────────────────────
def slides():
    total = 8
    out = []

    # 01 · 커버 — 서비스가 뭔지
    head, arr = brand(1, total)
    pills = ('<div style="position:absolute;left:80px;top:1000px;width:920px;">'
             '<span class="pill"><b>8</b>챕터</span>'
             '<span class="pill">약 <b>7,000</b>자</span>'
             '<span class="pill">실제 카톡 <b>원문 근거</b></span></div>')
    out.append(
        '<div class="slide">' + head +
        '<div class="kicker" style="top:368px;">WHAT IS EX-RAY</div>'
        '<div class="h" style="top:412px;font-size:60px;line-height:1.22;">'
        '전남친·전여친 카톡,<br>AI가 통째로<br>해부해드려요.</div>'
        '<div class="note" style="top:786px;width:880px;">카톡 한 번 올리면, 시작부터 이별까지 '
        '<b style="color:#0d0d0d;">내 전체 연애를 한 권</b>으로 정리해줘요.</div>'
        + pills + arr + '</div>'
    )

    # 02 · 왜 — 답은 이미 카톡 안에
    head, arr = brand(2, total)
    out.append(
        '<div class="slide">' + head +
        head_block("WHY", "전남친한테<br>물어볼 필요 없어요.", htop=360, hsize=54) +
        '<div class="note" style="top:600px;width:880px;font-size:31px;line-height:1.75;">'
        '직접 묻기도 그렇고, 물어봐도 솔직히 말 안 해주잖아요. '
        '<b style="color:#0d0d0d;">답은 이미 카톡 안에 다 있어요.</b> '
        '감정 다 빼고, 둘이 나눈 대화만 보고 객관적으로 짚어드려요.</div>'
        + arr + '</div>'
    )

    # 03 · 쓰는 법 3단계
    steps = [
        ("카톡을 통째로 올려요", "대화방 → 대화 내보내기로 받은 .txt 파일을 그대로 업로드. "
         "아이폰에서 쪼개진 파일도 한 번에 올리면 알아서 합쳐요."),
        ("지금 내 마음을 고르고 적어요", "정리·재회·분석·학습 중 내 상황 하나 선택. "
         "지금 뭐가 제일 궁금한지 메모하면 더 정확해져요."),
        ("메일로 리포트가 와요", "AI가 몇천 줄을 다 읽고 8챕터로 정리. "
         "분석이 끝나면 원본 카톡은 바로 삭제돼요."),
    ]
    arows = ""
    for i, (t, d) in enumerate(steps, 1):
        cls = "act" + (" first" if i == 1 else "") + (" last" if i == len(steps) else "")
        arows += (f'<div class="{cls}"><span class="act-n">{i}</span>'
                  f'<span class="act-t"><b>{t}</b><br>'
                  f'<span style="font-weight:500;color:rgba({INK_RGB},0.55);font-size:26px;">{d}</span>'
                  f'</span></div>')
    head, arr = brand(3, total)
    out.append(
        '<div class="slide">' + head +
        head_block("HOW IT WORKS", "쓰는 법은,<br>딱 3단계예요.", htop=326, hsize=46) +
        f'<div class="panel" style="top:548px;">{arows}</div>'
        + arr + '</div>'
    )

    # 04 · 차별점 — 전체 통째로 + 정량 근거
    metrics = ["호칭 변화", "평균 응답속도", "메시지 빈도", "갈등 횟수", "미련 가능성 %"]
    mchips = "".join(f'<span class="mchip">{m}</span>' for m in metrics)
    diff_panel = (
        '<div class="plab">ChatGPT에 몇 줄 붙여넣는 거랑 달라요</div>'
        '<div class="verdict" style="margin-bottom:30px;">처음 ‘안녕하세요’부터 마지막 인사까지 '
        '<b>전체 대화를 통째로</b> 읽어요. 그래서 흐름과 맥락까지 잡아내죠.</div>'
        '<div class="plab" style="margin-bottom:20px;">느낌이 아니라, 이런 걸 숫자로</div>'
        f'<div>{mchips}</div>'
        '<div class="verdict" style="margin-top:14px;font-size:27px;">'
        '모든 결론엔 <b>실제 카톡 원문</b>이 근거로 붙어요.</div>'
    )
    head, arr = brand(4, total)
    out.append(
        '<div class="slide">' + head +
        head_block("뭐가 다른데", "대화 몇 줄이 아니라,<br>관계 전체를 읽어요.", htop=326, hsize=46) +
        f'<div class="panel" style="top:548px;">{diff_panel}</div>'
        + arr + '</div>'
    )

    # 05 · 톤 4모드 (페르소나)
    modes = [
        ("🕊️", "이제 마음 정리하고 싶음", "차분하게, 깔끔한 마무리로"),
        ("💌", "재회 가능성 보고 싶음", "가능성과 비용을 직설 팩폭으로"),
        ("🔬", "분석 자체가 재밌음", "감정 빼고 통계·패턴 위주로"),
        ("🎓", "다음 연애에 써먹고 싶음", "바로 쓸 교훈 위주로"),
    ]
    mcards = "".join(
        f'<div class="mode"><div class="mode-emo">{e}</div>'
        f'<div class="mode-name">{n}</div>'
        f'<div class="mode-desc">{d}</div></div>'
        for e, n, d in modes)
    head, arr = brand(5, total)
    out.append(
        '<div class="slide">' + head +
        head_block("내 상황에 맞게", "지금 내 마음 그대로,<br>골라서 받아요.", htop=326, hsize=46) +
        f'<div class="panel" style="top:548px;"><div class="modes">{mcards}</div></div>'
        + arr + '</div>'
    )

    # 06 · 8챕터로 받아요 (랜딩 마케팅 목록)
    toc_items = [
        "어떻게 시작됐는지", "헤어진 진짜 이유 Top 3",
        "관계 페이즈 7단계", "명대사 모음 5개",
        "둘 다 들어봐 팩폭", "그 사람 속마음 + 성격 진단",
        "재회 가이드", "EX-RAY가 한 마디",
    ]
    rows = ""
    for i, t in enumerate(toc_items, 1):
        cls = "toc-row" + (" first" if i == 1 else "") + (" last" if i == len(toc_items) else "")
        rows += (f'<div class="{cls}"><span class="toc-num">{i:02d}</span>'
                 f'<span class="toc-title">{t}</span></div>')
    head, arr = brand(6, total)
    out.append(
        '<div class="slide">' + head +
        head_block("이런 걸 받아요", "8개 챕터,<br>약 7,000자로.", htop=326, hsize=46) +
        f'<div class="panel" style="top:540px;">{rows}</div>'
        + arr + '</div>'
    )

    # 07 · 신뢰 / 보안 3종
    safe = [
        ("🗑️", "분석 끝나면 원본 카톡 자동 삭제", "서버에 남기지 않아요. 리포트만 본인 계정에 잠금 보관."),
        ("🙈", "나 말고 0명 열람", "암호화된 환경에서 본인만. 상대 동의도 필요 없어요."),
        ("💸", "못 받으면 100% 환불", "리포트 못 받은 경우엔 전액 돌려드려요."),
    ]
    srows = ""
    for i, (e, t, d) in enumerate(safe, 1):
        cls = "act" + (" first" if i == 1 else "") + (" last" if i == len(safe) else "")
        srows += (f'<div class="{cls}">'
                  f'<span class="act-n" style="background:transparent;font-size:38px;">{e}</span>'
                  f'<span class="act-t"><b>{t}</b><br>'
                  f'<span style="font-weight:500;color:rgba({INK_RGB},0.55);font-size:26px;">{d}</span>'
                  f'</span></div>')
    head, arr = brand(7, total)
    out.append(
        '<div class="slide">' + head +
        head_block("안심하고 올려요", "카톡인데,<br>안전한 거 맞아요.", htop=326, hsize=46) +
        f'<div class="panel" style="top:548px;">{srows}</div>'
        + arr + '</div>'
    )

    # 08 · 마감 CTA — 화살표 없음
    head, _ = brand(8, total, arrow=False)
    out.append(
        '<div class="slide">' + head +
        '<div class="h" style="top:372px;font-size:58px;line-height:1.24;text-align:center;width:920px;">'
        f'지금 카톡 한 번,<br><span style="color:{ACCENT};">올려볼까요?</span></div>'
        '<div style="position:absolute;left:0;top:640px;width:1080px;text-align:center;">'
        '<span class="pill" style="font-size:30px;"><b>30,000</b>원</span></div>'
        '<div class="note" style="top:1054px;text-align:center;left:0;width:1080px;">'
        '전남친·전여친 카톡 한 번 올리면, 우리가 왜 헤어졌는지<br>'
        'EX-RAY가 끝까지 읽고 정리해줄게요.</div>'
        f'<div class="cta" style="top:1188px;left:0;width:1080px;text-align:center;">'
        '지금 분석하기 · exray.kr</div>'
        '</div>'
    )
    return out


def build_html(slide_list):
    return (
        '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">'
        '<title>EX-RAY · 리포트 미리보기</title>'
        f'<link rel="stylesheet" href="{PRETENDARD}">'
        '<style>' + CSS +
        'body{background:#e9e6dd;display:flex;flex-direction:column;align-items:center;'
        'gap:32px;padding:48px;}.slide{box-shadow:0 4px 24px rgba(0,0,0,0.12);}</style>'
        '</head><body>' + "".join(slide_list) + '</body></html>'
    )


PAGE = ('<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">'
        '<link rel="stylesheet" href="{font}"><style>{css}'
        'html,body{{margin:0;padding:0;background:transparent;display:block;}}'
        '.slide{{box-shadow:none!important;}}</style></head><body>{slide}</body></html>')


# ── 편집형 HTML ─────────────────────────────────────────────────────────────
def _data_uri(path, mime):
    import base64
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


EDITOR_CSS = f"""
body{{background:#1b1b1d;margin:0;padding:40px 20px 120px;font-family:'Pretendard',sans-serif;}}
.bar{{position:fixed;left:0;top:0;right:0;z-index:50;display:flex;align-items:center;gap:16px;
  padding:14px 22px;background:rgba(20,20,22,0.92);backdrop-filter:blur(8px);
  border-bottom:1px solid #2c2c30;color:#eaeaea;font-size:14px;}}
.bar b{{color:{ACCENT};}}
.bar .sp{{flex:1;}}
.bar button{{background:{ACCENT};color:#fff;border:0;border-radius:999px;
  padding:10px 18px;font-size:14px;font-weight:700;cursor:pointer;font-family:inherit;}}
.bar input[type=range]{{accent-color:{ACCENT};}}
.tip{{color:#9a9a9e;font-size:13px;}}
.frames{{display:flex;flex-direction:column;align-items:center;gap:28px;margin-top:64px;}}
.frame{{display:flex;flex-direction:column;align-items:center;gap:12px;}}
.holder{{width:calc(1080px * var(--z,0.5));height:calc(1350px * var(--z,0.5));}}
.holder .slide{{transform:scale(var(--z,0.5));transform-origin:top left;
  box-shadow:0 10px 40px rgba(0,0,0,0.5);border-radius:6px;}}
.frame .dl{{background:#26262a;color:#eaeaea;border:1px solid #3a3a40;border-radius:999px;
  padding:8px 16px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;}}
[contenteditable]{{outline:none;cursor:text;border-radius:4px;transition:box-shadow .12s;}}
[contenteditable]:hover{{box-shadow:0 0 0 2px {ACCENT}55;}}
[contenteditable]:focus{{box-shadow:0 0 0 2px {ACCENT};}}
"""

EDITOR_JS = f"""
import h2c from 'https://cdn.jsdelivr.net/npm/html2canvas-pro@1.5.11/+esm';

const SEL = '.h,.note,.cta,.kicker,.plab,.toc-title,.quote,.quote-meta,.verdict,'
  + '.tl-lab,.tl-call,.gsub,.pill,.rank-title,.rank-pct,.rank-ev,.mtag,.mq,'
  + '.fname,.fpct,.fchip,.tag';
document.querySelectorAll('.slide').forEach(s => {{
  s.querySelectorAll(SEL).forEach(el => {{ el.contentEditable = 'true'; el.spellcheck = false; }});
}});

const sandbox = document.createElement('div');
sandbox.style.cssText = 'position:fixed;left:-100000px;top:0;width:1080px;height:0;overflow:visible;';
document.body.appendChild(sandbox);
const pad = n => String(n).padStart(2, '0');

async function shoot(slide, name) {{
  await document.fonts.ready;
  const bg = getComputedStyle(slide).backgroundColor || '{BG}';
  const clone = slide.cloneNode(true);
  clone.style.transform = 'none';
  clone.style.boxShadow = 'none';
  clone.style.borderRadius = '0';
  sandbox.innerHTML = '';
  sandbox.appendChild(clone);
  await new Promise(r => setTimeout(r, 20));
  const canvas = await h2c(clone, {{ scale: 2, width: 1080, height: 1350,
    backgroundColor: bg, useCORS: true, logging: false }});
  sandbox.innerHTML = '';
  const blob = await new Promise(res => canvas.toBlob(res, 'image/png'));
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}}

document.querySelectorAll('.frame .dl').forEach((btn, i) => {{
  btn.onclick = () => shoot(btn.parentElement.querySelector('.slide'), `exray-feature-${{pad(i+1)}}.png`);
}});
document.getElementById('all').onclick = async () => {{
  const slides = [...document.querySelectorAll('.frame .slide')];
  for (let i = 0; i < slides.length; i++) {{
    await shoot(slides[i], `exray-feature-${{pad(i+1)}}.png`);
    await new Promise(r => setTimeout(r, 400));
  }}
}};
const z = document.getElementById('zoom');
const setZ = () => document.documentElement.style.setProperty('--z', z.value);
z.oninput = setZ; setZ();
"""


def build_editor(slide_list):
    font = _data_uri(os.path.join(HERE, "assets", "Pretendard.woff2"), "font/woff2")
    font_face = (f"@font-face{{font-family:'Pretendard';font-weight:45 920;"
                 f"font-style:normal;font-display:swap;src:url({font}) format('woff2');}}")
    frames = []
    for i, s in enumerate(slide_list, start=1):
        frames.append(f'<div class="frame"><div class="holder">{s}</div>'
                      f'<button class="dl">{i:02d} · 이 장 PNG 저장</button></div>')
    bar = ('<div class="bar"><b>EX-RAY 리포트 미리보기 편집기</b>'
           '<span class="tip">글자를 클릭해서 바로 고치세요. 다 고치면 저장 버튼 ›</span>'
           '<span class="sp"></span>'
           '<label class="tip">보기 크기 <input id="zoom" type="range" min="0.25" max="1" step="0.05" value="0.5"></label>'
           '<button id="all">전체 8장 PNG 저장</button></div>')
    return (
        '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>EX-RAY 리포트 미리보기 편집기</title>'
        '<style>' + font_face + CSS + EDITOR_CSS + '</style></head><body>'
        + bar + '<div class="frames">' + "".join(frames) + '</div>'
        + '<script type="module">' + EDITOR_JS + '</script></body></html>'
    )


def export_png(slide_list, scale=2, prefix="exray-feature"):
    chrome = chrome_path()
    if not chrome:
        sys.exit("Chrome 실행파일을 찾지 못했습니다.")
    outdir = os.path.join(HERE, "png")
    os.makedirs(outdir, exist_ok=True)
    made = []
    for i, slide_html in enumerate(slide_list, start=1):
        page = PAGE.format(font=PRETENDARD, css=CSS, slide=slide_html)
        html_path = os.path.join(HERE, f".tmp-slide-{i:02d}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page)
        out = os.path.join(outdir, f"{prefix}-{i:02d}.png")
        cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
               "--no-sandbox", f"--force-device-scale-factor={scale}",
               "--window-size=1080,1350", "--default-background-color=00000000",
               "--virtual-time-budget=5000", f"--screenshot={out}",
               "file://" + html_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        os.remove(html_path)
        if not os.path.exists(out):
            sys.stderr.write(res.stderr[-800:] + "\n")
            sys.exit(f"슬라이드 {i} 캡처 실패")
        made.append(out)
    print(f"PNG {len(made)}장 → {outdir} ({1080*scale}x{1350*scale})", file=sys.stderr)


if __name__ == "__main__":
    sl = slides()
    with open(os.path.join(HERE, "feature-intro.html"), "w", encoding="utf-8") as f:
        f.write(build_html(sl))
    print(f"HTML 생성: feature-intro.html ({len(sl)}장)", file=sys.stderr)
    with open(os.path.join(HERE, "editor.html"), "w", encoding="utf-8") as f:
        f.write(build_editor(sl))
    print("편집기 생성: editor.html", file=sys.stderr)
    if "--png" in sys.argv:
        export_png(sl)
