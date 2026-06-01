"""
==============================================================
 통찰적 사고를 위한 비계설정(Scaffolding) 수학 학습 플랫폼
 대상 문항: 2023학년도 수능 수학 영역 (기하 / 도형) 기출
 구동 방법: streamlit run app.py
==============================================================
"""

import streamlit as st
import plotly.graph_objects as go
import time
from datetime import datetime

# ─────────────────────────────────────────────
# 0. 페이지 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="수학 비계설정 플랫폼",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 1. 문항 Mock Data  (실제 2022학년도 수능 기하 유사 문항)
# ─────────────────────────────────────────────
PROBLEM_DATA = {
    # ── 문제 발문 (LaTeX 포함) ──────────────────
    "title": "2023학년도 수능 수학 (기하) — 도형의 성질 활용",
    "statement": r"""
삼각형 $ABC$ 의 내부의 점 $P$ 에 대하여

$$PA = PB = PC = 5, \quad \sin(\angle APB) = \dfrac{4}{5}$$

일 때, 삼각형 $ABC$ 의 외접원의 반지름 $R$ 을 구하고,
삼각형 $ABC$ 의 넓이를 구하시오.

단, $\angle APB$ 는 점 $P$ 를 공유하는 두 선분 $PA$, $PB$ 가 이루는 각이다.
""",
    # ── 정답 ────────────────────────────────────
    "answer": 6,          # 외접원 반지름 R (사인법칙 적용 결과)
    "answer_label": "외접원의 반지름 R",

    # ── 단계별 비계 (힌트) ──────────────────────
    "scaffolds": {
        1: {
            "title": "1단계 · 조건의 재발견",
            "emoji": "🔍",
            "color": "#4A90D9",
            "content": r"""
**[조건을 다시 읽어보자]**

문제에서 제시한 세 조건에 주목해 봐.

$$PA = PB = PC = 5$$

이 조건이 의미하는 것은 무엇일까?
점 $P$ 에서 세 꼭짓점 $A$, $B$, $C$ 까지의 **거리가 모두 동일**하다는 뜻이야.

> 💡 어떤 점이 세 꼭짓점으로부터 등거리에 있을 때,
> 그 점은 삼각형에서 어떤 특별한 점일까?
""",
        },
        2: {
            "title": "2단계 · 개념적 통찰",
            "emoji": "💡",
            "color": "#F5A623",
            "content": r"""
**[핵심 개념: 외심(外心)]**

세 꼭짓점으로부터 등거리에 있는 점 → 삼각형의 **외심(Circumcenter)** 이야!

$$\therefore \; P \text{ 는 삼각형 } ABC \text{ 의 외심}$$

외심은 외접원의 **중심**이기도 해. 즉,

$$\text{외접원의 반지름} \; R = PA = PB = PC = 5$$

이제 $R = 5$ 임을 알았어.

> 💡 다음으로, 주어진 $\sin(\angle APB)$ 를 어디에 활용할 수 있을까?
> 변과 각의 관계를 연결하는 법칙을 떠올려봐.
""",
        },
        3: {
            "title": "3단계 · 관계적 비계설정",
            "emoji": "🧮",
            "color": "#7ED321",
            "content": r"""
**[사인법칙 적용]**

외심 $P$ 에서 이루는 중심각과 호의 관계를 이용해.
$\angle APB$ 는 호 $AB$ 에 대한 **중심각**이고,
원주각은 중심각의 절반이므로

$$\angle ACB = \dfrac{1}{2} \angle APB$$

사인법칙에 의해

$$\dfrac{AB}{\sin(\angle ACB)} = 2R$$

$\angle APB$ 에 대해 코사인 법칙으로 $AB$ 를 구하고,
$\sin(\angle ACB) = \sin\!\left(\dfrac{\angle APB}{2}\right)$ 를 반각 공식으로 풀면

$$R = 5, \quad AB = 6 \quad \Rightarrow \quad \sin(\angle ACB) = \dfrac{1}{2}$$

> ✅ 이제 넓이는 $\frac{1}{2} \cdot AB \cdot AC \cdot \sin(\angle BAC)$ 또는
> 사인법칙·코사인법칙 조합으로 완성할 수 있어!
""",
        },
    },
}

# ─────────────────────────────────────────────
# 2. Session State 초기화
# ─────────────────────────────────────────────
def init_session():
    """앱 최초 진입 시 세션 변수를 초기화한다."""
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()          # 앱 진입 시각 (Unix)
    if "scaffold_log" not in st.session_state:
        # 타임스탬프 로그: [(경과_초, 비계_레벨), ...]
        # 초기값: 시간=0, 레벨=0 (힌트 미사용 상태)
        st.session_state.scaffold_log = [(0.0, 0)]
    if "opened_levels" not in st.session_state:
        st.session_state.opened_levels = set()             # 이미 열람한 레벨 집합
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "answer_correct" not in st.session_state:
        st.session_state.answer_correct = None
    if "user_answer" not in st.session_state:
        st.session_state.user_answer = 0.0

init_session()

# ─────────────────────────────────────────────
# 3. 헬퍼 함수
# ─────────────────────────────────────────────
def elapsed() -> float:
    """앱 진입 시각으로부터 경과한 시간(초)을 반환한다."""
    return round(time.time() - st.session_state.start_time, 1)


def log_scaffold(level: int):
    """
    비계 버튼 클릭 시 호출.
    - 현재 경과 시간과 클릭한 레벨을 로그에 append.
    - 동일 레벨을 다시 열어도 중복 기록하지 않는다.
    """
    if level not in st.session_state.opened_levels:
        st.session_state.scaffold_log.append((elapsed(), level))
        st.session_state.opened_levels.add(level)


def build_insight_graph() -> go.Figure:
    """
    누적된 scaffold_log 를 기반으로 Insight Flow Graph 를 생성한다.
    X축: 경과 시간(초), Y축: 비계 의존도 레벨(0~3)
    """
    log = st.session_state.scaffold_log

    # 그래프에 표시할 시간·레벨 시퀀스 추출
    x_vals = [entry[0] for entry in log]
    y_vals = [entry[1] for entry in log]

    # 마지막 점 이후 현재 시각까지 수평선 연장 (실시간 느낌)
    x_vals_ext = x_vals + [elapsed()]
    y_vals_ext = y_vals + [y_vals[-1]]

    # ── 마커 색상: 레벨별 구분 ──────────────────
    color_map = {0: "#AAAAAA", 1: "#4A90D9", 2: "#F5A623", 3: "#7ED321"}
    marker_colors = [color_map.get(lv, "#AAAAAA") for lv in y_vals]

    fig = go.Figure()

    # 꺾은선 (step 스타일 — 레벨이 올라가는 순간 계단식으로 표현)
    fig.add_trace(go.Scatter(
        x=x_vals_ext,
        y=y_vals_ext,
        mode="lines",
        line=dict(color="#4A90D9", width=2, shape="hv"),   # 'hv' = 수평 후 수직
        name="비계 의존도 흐름",
        hovertemplate="경과 %{x}초<br>레벨 %{y}<extra></extra>",
    ))

    # 이벤트 마커 (힌트를 열람한 시점)
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="markers+text",
        marker=dict(size=10, color=marker_colors, line=dict(width=1.5, color="white")),
        text=[f"Lv{lv}" if lv > 0 else "시작" for lv in y_vals],
        textposition="top center",
        textfont=dict(size=11),
        name="힌트 열람 시점",
        hovertemplate="경과 %{x}초 · 비계 레벨 %{y}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text="📊 Insight Flow Graph — 실시간 사고 흐름 추적",
            font=dict(size=15),
        ),
        xaxis=dict(
            title="경과 시간 (초)",
            ticksuffix="s",
            gridcolor="#EEEEEE",
            zeroline=False,
        ),
        yaxis=dict(
            title="비계 의존도 (Level)",
            tickvals=[0, 1, 2, 3],
            ticktext=["0 · 독립", "1 · 조건재발견", "2 · 개념통찰", "3 · 관계적비계"],
            range=[-0.3, 3.5],
            gridcolor="#EEEEEE",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=60, b=40),
        height=300,
    )
    return fig

# ─────────────────────────────────────────────
# 4. 사이드바 — 학습 진행 현황
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📐 학습 현황 대시보드")
    st.divider()

    # 경과 시간
    st.metric("⏱ 경과 시간", f"{elapsed()} 초")

    # 열람한 비계 단계
    opened = sorted(st.session_state.opened_levels)
    if opened:
        st.metric("🔓 열람한 비계 단계", f"{len(opened)} / 3 단계")
        st.write("열람 순서:", " → ".join([f"Lv{lv}" for lv in opened]))
    else:
        st.metric("🔓 열람한 비계 단계", "0 / 3 단계")
        st.caption("아직 힌트를 사용하지 않았어요 🎯")

    st.divider()

    # 자가 점검 체크리스트
    st.markdown("### ✅ 자가 점검")
    st.checkbox("$PA=PB=PC$ 의 기하학적 의미를 파악했나요?")
    st.checkbox("외심과 외접원의 관계를 이해했나요?")
    st.checkbox("사인법칙을 적용할 준비가 됐나요?")

    st.divider()
    # 초기화 버튼
    if st.button("🔄 처음부터 다시 풀기", width='stretch'):
        for key in ["start_time", "scaffold_log", "opened_levels",
                    "submitted", "answer_correct", "user_answer"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ─────────────────────────────────────────────
# 5. 메인 화면
# ─────────────────────────────────────────────

# ── 5-A. 헤더 ──────────────────────────────────
st.markdown(
    "<h1 style='font-size:1.6rem; font-weight:700; margin-bottom:0.2rem;'>"
    "🔭 통찰적 사고를 위한 비계설정 수학 학습 플랫폼"
    "</h1>",
    unsafe_allow_html=True,
)
st.caption("평가원 기출 · 도형의 성질 | 비계설정(Scaffolding) 단계별 힌트 제공")
st.divider()

# ── 5-B. 문제 발문 + 도형 이미지 (2-column) ──────
col_prob, col_img = st.columns([3, 2], gap="large")

with col_prob:
    st.markdown(f"### 📝 {PROBLEM_DATA['title']}")
    st.markdown(PROBLEM_DATA["statement"])

with col_img:
    # 실제 이미지가 없을 경우 안내 박스로 대체
    st.info(
        "📐 **도형 이미지 영역**\n\n"
        "평가원 기출 문항의 기하학적 도형 그림을 여기에 부착합니다.\n\n"
        "삼각형 $ABC$ 내부에 외심 $P$ 가 위치하며,\n"
        "$PA = PB = PC = 5$ 인 외접원이 그려진 도형입니다."
    )
    # 실제 이미지가 있다면 아래 주석 해제 후 경로 지정:
    # st.image("assets/problem_figure.png", caption="출처: 2023학년도 수능", width='stretch')

st.divider()

# ── 5-C. 정답 입력 영역 ────────────────────────
st.markdown("### 💬 정답 입력")

with st.form(key="answer_form", clear_on_submit=False):
    answer_col, btn_col = st.columns([3, 1])
    with answer_col:
        user_val = st.number_input(
            label=f"**{PROBLEM_DATA['answer_label']}** 를 입력하세요",
            min_value=0.0,
            max_value=1000.0,
            step=0.5,
            value=float(st.session_state.user_answer),
            format="%.1f",
            help="소수점 입력도 가능합니다.",
        )
    with btn_col:
        submitted = st.form_submit_button("✅ 제출", width='stretch')

    if submitted:
        st.session_state.submitted = True
        st.session_state.user_answer = user_val
        # 정답 판별 (소수점 허용: 0.5 오차 이내 정답 처리)
        st.session_state.answer_correct = (
            abs(user_val - PROBLEM_DATA["answer"]) <= 0.5
        )

# 제출 결과 표시
if st.session_state.submitted:
    if st.session_state.answer_correct:
        st.success(
            f"🎉 **정답입니다!** 외접원의 반지름 $R = {PROBLEM_DATA['answer']}$ 이 맞아요.\n\n"
            f"열람한 비계: {len(st.session_state.opened_levels)}단계 / "
            f"소요 시간: {elapsed()}초"
        )
    else:
        st.error(
            f"❌ 아직 아니에요. 입력값: **{st.session_state.user_answer}**\n\n"
            "아래 비계설정 힌트를 단계적으로 활용해보세요!"
        )

st.divider()

# ── 5-D. 단계별 비계설정 영역 ────────────────────
st.markdown("### 🪜 단계별 비계설정 (Scaffolding)")
st.caption(
    "💬 힌트는 순서대로 열어보세요. 각 단계를 열 때마다 사고 흐름 그래프가 업데이트됩니다."
)

scaffold_cols = st.columns(3, gap="medium")

for col, (level, data) in zip(scaffold_cols, PROBLEM_DATA["scaffolds"].items()):
    with col:
        # 이미 열람한 단계는 배지 표시
        already_opened = level in st.session_state.opened_levels
        badge = "✅ 열람함" if already_opened else "🔒 미열람"

        # st.expander 로 구현 — 클릭 감지는 버튼으로 처리
        with st.expander(
            f"{data['emoji']} **{data['title']}**  ·  {badge}",
            expanded=already_opened,
        ):
            st.markdown(data["content"])
            if not already_opened:
                if st.button(
                    f"이 비계 기록하기",
                    key=f"btn_scaffold_{level}",
                    help="클릭하면 현재 시각과 레벨이 사고 흐름 그래프에 기록됩니다.",
                    width='stretch',
                ):
                    log_scaffold(level)
                    st.rerun()
            else:
                st.caption(f"열람 시각: {elapsed()}초 경과 시점에 기록됨")

st.divider()

# ── 5-E. Insight Flow Graph ──────────────────────
st.markdown("### 📊 Insight Flow Graph — 실시간 사고 흐름 추적")
st.caption(
    "X축: 앱 진입 후 경과 시간(초) | Y축: 비계 의존도 레벨(0=독립, 3=최대 지원)\n"
    "힌트를 열람하지 않고 정답을 맞힐수록 Level 0에 가까운 직선이 그려집니다."
)

# 그래프 렌더링
fig = build_insight_graph()
st.plotly_chart(fig, width='stretch')

# 로그 상세 테이블 (접기/펴기)
with st.expander("📋 상세 로그 보기", expanded=False):
    log_display = [
        {
            "순서": i + 1,
            "경과 시간(초)": entry[0],
            "비계 레벨": entry[1],
            "설명": (
                "앱 시작" if entry[1] == 0
                else PROBLEM_DATA["scaffolds"][entry[1]]["title"]
            ),
        }
        for i, entry in enumerate(st.session_state.scaffold_log)
    ]
    st.dataframe(log_display, width='stretch', hide_index=True)

# ─────────────────────────────────────────────
# 6. 푸터
# ─────────────────────────────────────────────
st.divider()
st.caption(
    "🏫 통찰적 사고를 위한 비계설정 수학 학습 플랫폼 · 프로토타입 v0.1\n\n"
    "문항 출처: 2023학년도 수능 수학 기출 유사 문항 | "
    "Scaffolding 이론 기반 설계 (Wood, Bruner & Ross, 1976)"
)