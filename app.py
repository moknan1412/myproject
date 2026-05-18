import streamlit as st
import sqlite3
import pandas as pd

# ── 1. DB 초기화 ──────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect('creativity_study.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            risk_taking INTEGER,
            curiosity INTEGER,
            imagination INTEGER,
            complexity INTEGER,
            total_score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

conn = init_db()

# ── 2. 검사 문항 정의 (50문항) ────────────────────────────────
questions = {
    "모험심 (Risk-taking)": [
        "1. 나는 결과가 불확실하더라도 새로운 일을 시도하는 것을 좋아한다.",
        "2. 나는 실패할 위험이 있더라도 어려운 문제에 도전한다.",
        "3. 나는 내 생각이 남들과 다르더라도 당당하게 말한다.",
        "4. 나는 익숙한 길보다 가보지 않은 길로 가는 것을 좋아한다.",
        "5. 나는 틀릴 가능성이 있어도 내 의견을 발표한다.",
        "6. 나는 새로운 게임이나 놀이를 규칙을 몰라도 일단 시작해 본다.",
        "7. 나는 어려운 일을 끝마쳤을 때 뿌듯함을 느낀다.",
        "8. 나는 남들이 하지 않는 일을 해보는 것을 즐긴다.",
        "9. 나는 한 번도 해보지 않은 일을 할 때 가슴이 설렌다.",
        "10. 나는 문제가 풀리지 않아도 끝까지 혼자 힘으로 해보려 한다.",
        "11. 나는 새로운 장소에 가는 것을 두려워하지 않는다.",
        "12. 나는 모르는 사람들에게 먼저 말을 거는 편이다.",
        "13. 나는 위험 요소가 있어도 흥미로운 일이라면 참여한다."
    ],
    "호기심 (Curiosity)": [
        "14. 나는 사물이 어떻게 작동하는지 궁금해서 분해해 본 적이 있다.",
        "15. 나는 새로운 기계나 물건을 보면 직접 만져보고 싶어 한다.",
        "16. 나는 궁금한 것이 생기면 참지 못하고 질문하거나 찾아본다.",
        "17. 나는 '왜?'라는 질문을 자주 던지는 편이다.",
        "18. 나는 주변의 작은 변화도 잘 알아차린다.",
        "19. 나는 텔레비전이나 책에서 본 것을 실제로 확인해보고 싶어 한다.",
        "20. 나는 자연 현상(날씨, 동물 등)에 관심이 많다.",
        "21. 나는 새로운 소식이나 정보에 귀를 기울인다.",
        "22. 나는 모르는 단어가 나오면 그 뜻을 꼭 확인한다.",
        "23. 나는 신기한 물건을 수집하는 것을 좋아한다.",
        "24. 나는 여러 가지 일의 원인과 결과에 대해 생각하는 것을 즐긴다."
    ],
    "상상력 (Imagination)": [
        "25. 나는 눈을 감으면 가보지 않은 곳의 풍경이 머릿속에 그려진다.",
        "26. 나는 구름의 모양을 보고 동물이나 사물을 떠올린다.",
        "27. 나는 내가 만약 초능력이 있다면 어떨지 자주 상상한다.",
        "28. 나는 이야기의 결말을 내 마음대로 바꾸어 상상해 보곤 한다.",
        "29. 나는 미래의 세상이 어떻게 변할지 상상하는 것이 즐겁다.",
        "30. 나는 사물들이 말을 할 수 있다면 어떨지 생각한다.",
        "31. 나는 가끔 현실에 없는 나만의 가상 세계를 만든다.",
        "32. 나는 꿈속에서 본 내용을 기억해서 이야기하는 것을 좋아한다.",
        "33. 나는 그림을 그릴 때 실제와 다르게 그리는 것을 좋아한다.",
        "34. 나는 소설이나 영화 속 주인공이 된 나를 상상한다.",
        "35. 나는 아무것도 없는 백지를 볼 때 무엇을 그릴지 아이디어가 샘솟는다.",
        "36. 나는 소리나 음악을 들으면 특정한 색깔이나 장면이 떠오른다.",
        "37. 나는 만약 내가 동물이 된다면 어떤 동물이 될지 생각해 본 적이 있다."
    ],
    "복잡성 (Complexity)": [
        "38. 나는 정답이 하나뿐인 문제보다 여러 가지 답이 있는 문제가 좋다.",
        "39. 나는 복잡한 퍼즐이나 퀴즈를 푸는 것을 즐긴다.",
        "40. 나는 사물을 한 방향에서만 보지 않고 여러 각도에서 보려 노력한다.",
        "41. 나는 뒤섞여 있는 정보들을 정리하여 새로운 질서를 만드는 것을 좋아한다.",
        "42. 나는 어려운 책이나 내용을 이해했을 때 큰 기쁨을 느낀다.",
        "43. 나는 단순한 일보다는 머리를 많이 써야 하는 복잡한 일을 선호한다.",
        "44. 나는 하나를 배우면 그것을 다른 곳에도 적용해 보려 한다.",
        "45. 나는 완벽한 계획을 세우기 위해 세세한 부분까지 신경 쓴다.",
        "46. 나는 논리적으로 따져보는 것을 좋아한다.",
        "47. 나는 친구들과 토론하며 서로의 생각을 나누는 것을 즐긴다.",
        "48. 나는 어떤 현상의 이면에 숨겨진 의미를 찾으려 노력한다.",
        "49. 나는 규칙이 복잡한 게임일수록 더 흥미를 느낀다.",
        "50. 나는 한 가지 문제를 해결하기 위해 오랫동안 집중할 수 있다."
    ]
}

# ── 3. 세션 상태 초기화 ───────────────────────────────────────
# page : "home" | "survey"
if "page" not in st.session_state:
    st.session_state.page = "home"

# ══════════════════════════════════════════════════════════════
# PAGE 1 ─ 홈 (안내 페이지)
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "home":

    st.title("🎨 윌리엄스 창의적 인성 검사 (CFS)")
    st.markdown("---")

    st.subheader("📋 검사 안내")

    st.markdown("""
    **윌리엄스 창의적 인성 검사(Creativity Assessment Packet, CFS)** 는  
    Frank E. Williams가 개발한 창의성 측정 도구로,  
    개인의 창의적 성향을 4가지 영역으로 평가합니다.
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.info("🏔️ **모험심 (Risk-taking)**\n\n불확실한 상황에서도 새로운 것에 도전하고 위험을 감수하는 성향")
        st.info("🔬 **호기심 (Curiosity)**\n\n주변 현상에 의문을 품고 탐색하며 알아가려는 성향")
    with col2:
        st.info("💭 **상상력 (Imagination)**\n\n현실을 넘어 새로운 세계와 아이디어를 그려내는 성향")
        st.info("🧩 **복잡성 (Complexity)**\n\n복잡한 문제를 즐기고 다양한 관점에서 사고하는 성향")

    st.markdown("---")
    st.subheader("📌 검사 방법")
    st.markdown("""
    - 총 **50문항**으로 구성되어 있습니다.
    - 각 문항을 읽고 본인에게 해당하는 정도를 **1~4점** 중 선택합니다.

    | 점수 | 의미 |
    |------|------|
    | 1점 | 전혀 그렇지 않다 |
    | 2점 | 그렇지 않다 |
    | 3점 | 그렇다 |
    | 4점 | 매우 그렇다 |

    - 소요 시간은 약 **10~15분** 입니다.
    - 정답은 없으며, **솔직하게** 응답할수록 정확한 결과를 얻을 수 있습니다.
    - 검사 결과는 데이터베이스에 저장되어 연구 목적으로 활용될 수 있습니다.
    """)

    st.markdown("---")
    st.subheader("⚠️ 유의 사항")
    st.markdown("""
    - 본 검사는 **심리 진단 도구가 아니며**, 창의적 성향을 탐색하는 참고 자료입니다.
    - 검사 도중 페이지를 새로고침하면 **응답 내용이 초기화**됩니다.
    - 제출 후에는 응답을 수정할 수 없으니 신중하게 답변해 주세요.
    """)

    st.markdown("")
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("✅ 설문 참여하기", use_container_width=True, type="primary"):
            st.session_state.page = "survey"
            st.rerun()

# ══════════════════════════════════════════════════════════════
# PAGE 2 ─ 설문 페이지
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "survey":

    st.title("🎨 윌리엄스 창의적 인성 검사 (CFS)")

    # 홈으로 돌아가기
    if st.button("← 안내 페이지로 돌아가기"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown("""
    각 문항을 읽고 본인에게 가장 가깝다고 생각되는 정도를 선택해 주세요.
    - **1점: 전혀 그렇지 않다 / 2점: 그렇지 않다 / 3점: 그렇다 / 4점: 매우 그렇다**
    ---
    """)

    # ── 4. 검사 폼 ────────────────────────────────────────────
    with st.form("cfs_form"):
        user_name = st.text_input("검사 대상자 성함")

        user_responses = {}
        tabs = st.tabs(list(questions.keys()))

        for i, (category, q_list) in enumerate(questions.items()):
            with tabs[i]:
                st.subheader(f"📍 {category}")
                for q in q_list:
                    response = st.radio(q, [1, 2, 3, 4], index=2, horizontal=True, key=q)
                    user_responses[q] = response

        submitted = st.form_submit_button("검사 완료 및 결과 저장")

    # ── 5. 제출 처리 ──────────────────────────────────────────
    if submitted:
        if not user_name.strip():
            st.error("성함을 입력해 주세요!")
        else:
            scores = {
                cat: sum(user_responses[q] for q in q_list)
                for cat, q_list in questions.items()
            }
            total = sum(scores.values())

            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO results (name, risk_taking, curiosity, imagination, complexity, total_score) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    user_name,
                    scores["모험심 (Risk-taking)"],
                    scores["호기심 (Curiosity)"],
                    scores["상상력 (Imagination)"],
                    scores["복잡성 (Complexity)"],
                    total,
                ),
            )
            conn.commit()

            st.success(f"축하합니다, {user_name}님! 검사가 완료되었습니다.")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("모험심", f"{scores['모험심 (Risk-taking)']}점")
            col2.metric("호기심", f"{scores['호기심 (Curiosity)']}점")
            col3.metric("상상력", f"{scores['상상력 (Imagination)']}점")
            col4.metric("복잡성", f"{scores['복잡성 (Complexity)']}점")
            st.subheader(f"총점: {total} / 200")

    # ── 6. 전체 결과 현황 (항상 노출) ────────────────────────
    st.markdown("---")
    st.subheader("📊 전체 검사 결과 현황")

    df = pd.read_sql_query("SELECT * FROM results", conn)

    if df.empty:
        st.info("아직 저장된 검사 결과가 없습니다.")
    else:
        search_query = st.text_input("🔍 이름으로 검색", placeholder="검색할 이름을 입력하세요")
        if search_query.strip():
            filtered_df = df[df["name"].str.contains(search_query.strip(), case=False, na=False)]
            if filtered_df.empty:
                st.warning(f"'{search_query}'에 해당하는 결과가 없습니다.")
            else:
                st.write(f"검색 결과: **{len(filtered_df)}건**")
                st.markdown("---")
                st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)