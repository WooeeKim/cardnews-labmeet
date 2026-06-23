# 랩미 magazine 카드뉴스 디자인 시스템

> 인터뷰형 카드뉴스(캐러셀)를 만들 때 **이 문서를 먼저 확인하고 그대로** 제작한다.
> 기준 파일: `labme_raving_carousel.html`(민트 테마), `labme_wine_carousel.html`(와인 테마).
> 결과물은 인스타 캐러셀용 세로 슬라이드 묶음(HTML 1파일, 슬라이드 N장 세로 나열).

---

## 1. 캔버스 · 전역 토큰 (모든 테마 공통)

| 항목 | 값 |
|---|---|
| 슬라이드 크기 | `1080 × 1350px` (인스타 4:5 세로) |
| 폰트 | Pretendard (CDN: `https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css`) |
| 페이지 배경(슬라이드 바깥) | `#f2f0e9` (크림) |
| 슬라이드 그림자 | `box-shadow:0 4px 24px rgba(0,0,0,0.15)` |
| 좌우 여백 | 좌 `80px` / 우 `80px` → **본문 폭 920px** |
| 슬라이드 텍스트 | 흰색 계열, 위치는 전부 `position:absolute` + `top`/`left` 지정 |
| 페이지 레이아웃 | `body{background:#f2f0e9;display:flex;flex-direction:column;align-items:center;gap:32px;padding:48px;}` |

전역 CSS 보일러플레이트는 아래 그대로 사용 (테마 색 2곳만 교체):

```css
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Pretendard',sans-serif;}
.slide{width:1080px;height:1350px;background:VAR_BG;color:#fff;position:relative;overflow:hidden;}
.brand{position:absolute;left:80px;top:64px;font-size:42px;font-weight:500;}
.brand span{color:VAR_ACCENT;}
.counter{position:absolute;right:80px;top:72px;font-size:33px;color:rgba(255,255,255,0.4);}
.h{position:absolute;left:80px;font-weight:700;color:#fff;letter-spacing:-1px;}
.info{position:absolute;left:80px;font-size:32px;font-weight:500;color:rgba(255,255,255,0.5);}
.body{position:absolute;left:80px;width:920px;font-size:34px;line-height:1.74;color:rgba(255,255,255,0.8);}
body{background:#f2f0e9;display:flex;flex-direction:column;align-items:center;gap:32px;padding:48px;}
.slide{box-shadow:0 4px 24px rgba(0,0,0,0.15);}
```

---

## 2. 테마 (이벤트별 액센트 1색으로 전체 분위기 결정)

테마는 **슬라이드 배경 + 액센트 1색 + 말풍선 2색**으로 정의한다. 새 이벤트는 새 테마 1줄만 추가.

| 토큰 | 레이빙 (민트) | 와인 (로제) |
|---|---|---|
| `VAR_BG` 슬라이드 배경 | `#0e0e10` | `#120b0d` |
| `VAR_ACCENT` 액센트 | `#5DCAA5` | `#C97A86` |
| 말풍선(질문, 회색) bg | `#2a2a2e` | `#2a2226` |
| 말풍선(답변, 액센트) text색 | `#04342C` | `#3a0f17` |

규칙: 답변 말풍선 글자색은 **액센트의 아주 어두운 동계색**(가독성용). 액센트는 `.brand span`, `.counter` 화살표, 커버/마감 강조, CTA에 일관되게 재사용.

---

## 3. 타이포 스케일

| 역할 | 클래스 | size | weight | line-height | color |
|---|---|---|---|---|---|
| 브랜드 "랩미 magazine" | `.brand` | 42 | 500 | – | #fff(+span 액센트) |
| 페이지 카운터 "03 / 09" | `.counter` | 33 | – | – | rgba(255,255,255,0.4) |
| 카드 제목 | `.h` | 48–58(인터뷰) / 76–100(커버·마감) | 700 | 1.12–1.25 | #fff |
| 바이라인/라벨 | `.info` | 32 | 500 | – | rgba(255,255,255,0.5) |
| 본문(후기) | `.body` | 34(기본) / 31–32(긴 글) | 400 | 1.74(기본) / 1.64–1.68(긴 글) | rgba(255,255,255,0.8) |
| 마감 인용구 | inline | 37 | – | – | rgba(255,255,255,0.85) |
| 마감 인용 바이라인 | inline | 30 | – | – | rgba(255,255,255,0.4) |
| CTA(labmeet.love) | inline | 37–60 | 500–700 | – | 액센트 |

---

## 4. 공통 요소

- **브랜드**: 모든 슬라이드 좌상단 고정. `랩미 <span>magazine</span>`.
- **카운터**: 모든 슬라이드 우상단. `01 / 09` 형식(현재/총장수). 총장수는 마지막에 일괄 갱신.
- **다음 화살표 SVG**: 마지막 슬라이드를 제외한 **모든 슬라이드** 우하단 고정. 액센트색.
```html
<svg style="position:absolute;right:74px;top:1218px;" width="78" height="46" viewBox="0 0 78 46" fill="none"><path d="M6 23 H68 M48 7 L70 23 L48 39" stroke="VAR_ACCENT" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>
```

---

## 5. 슬라이드 템플릿

### A. 커버 (01)
브랜드 + 카운터 + **말풍선 대화 2개**(질문→답변, 이벤트 컨셉 한 줄로 후킹) + 큰 헤드라인 + 하단 라벨 + 화살표.
- 아바타 원: `left:80 top:300 64×64 border-radius:50% bg:rgba(255,255,255,0.18)`
- 질문 말풍선(회색): `left:168 top:300` · bg 회색 · color `#eee` · `font-size:36 padding:20px 30px` · `border-radius:34px 34px 34px 10px`
- 답변 말풍선(액센트): `right:80 top:415` · bg 액센트 · color 어두운 동계색 · `font-size:36 font-weight:500 padding:20px 34px` · `border-radius:34px 34px 10px 34px`
- 헤드라인 `.h`: `top:830~860` · `font-size:76~100`(짧을수록 크게) · `line-height:1.12~1.18` · 보통 `<br>`로 2줄
- 하단 라벨: `left:80 top:1170 font-size:36` 액센트색 (예: "레이빙 편 · 후기 싹 다 모음 ›")

### B. 인터뷰 카드 (본문 슬라이드, 02~끝-1) ★핵심 반복 단위
구성: 제목 `.h` → 바이라인 `.info` → 후기 `.body` → 화살표.

**세로 위치 공식** (이 공식대로 top 계산):
- 제목 `.h` : `top = 360`, `font-size`는 **한 줄에 맞게 48~58** 조정 + `white-space:nowrap`
- 바이라인 `.info` : `top = 360 + (제목 font-size) + 30`
  - 예: 제목 54 → info 444 / 제목 50 → 440 / 제목 58 → 448
- 후기 `.body` : `top = info_top + 78` (기본 본문 기준)

**긴 후기 처리**: 본문이 길면 `.body`를 `font-size:31~32`, `line-height:1.64~1.68`로 줄이고 시작 `top`을 `500` 부근까지 올린다(제목·바이라인은 그대로, 필요시 제목 top을 348까지 살짝 위로).

바이라인 형식: `익명 N · 성별 · 나이` (예: `익명 1 · 여 · 24`). 운영진 글은 `운영진 후기`.

### C. 마감 (마지막 슬라이드)
브랜드 + 카운터 + 큰 헤드라인 + (짧은 인용 모음 **또는** 안내 문단) + 하단 안내 + CTA. **화살표 없음.**
- 헤드라인 `.h`: `top:300~340 font-size:56~70 line-height:1.2~1.25` (`<br>` 2줄)
- 인용 모음형: 인용 텍스트(fs37, 0.85) + 바로 아래 바이라인(fs30, 0.4) 블록을 `top` 약 100px 간격으로 3개 (예: 550/602, 700/752, 850/902)
- 안내 문단형: `width:920 font-size:33~35 line-height:1.55~1.65` color 0.55~0.78
- CTA: 하단 좌측, 액센트색. `다음 파티는 @labmeet.love` 또는 `labmeet.love`

---

## 6. 카피 톤 규칙

- **실제 후기체 그대로**: 구어체 허용, `ㅎㅎ`/`ㅋㅋ`/`…` 자연스럽게 사용 (참가자 목소리니까).
- **em-dash(`—`) 금지** → 마침표·쉼표·콜론으로. (사용자 전역 규칙 `feedback_writing_style`)
- 운영진/마감 멘트는 담백하게, 과장·영업티 최소화. ("번창하세요!" 같은 참가자 발화는 OK)
- 헤드라인은 후기의 한 문장을 뽑아 후킹형으로 ("혼자 갔는데 둘이 나왔어요", "환불해주세요, 저 사귀어서요").

---

## 7. 제작 체크리스트

1. 이벤트 테마 색 2개(`VAR_BG`/`VAR_ACCENT`) + 말풍선 2색 결정 → 2장 섹션에 추가.
2. 전역 CSS 보일러플레이트 붙이고 색 치환.
3. 커버 → 인터뷰 카드 N장 → 마감 순으로 슬라이드 작성.
4. 인터뷰 카드는 **5장 위치 공식**대로 top 계산, 한 줄 제목은 nowrap+폰트 조정.
5. 모든 카드(마감 제외)에 화살표 SVG.
6. 카운터 `NN / 총장수` 일괄 갱신.
7. 카피 톤 규칙(6장) 확인.
