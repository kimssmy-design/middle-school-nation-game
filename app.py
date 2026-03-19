import streamlit as st
import pandas as pd
import plotly.express as px
import time

# 1. 페이지 설정 및 디자인 (태블릿 최적화)
st.set_page_config(page_title="국가 경영 게임", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main .block-container { padding-top: 1rem; max-width: 700px; }
    .scenario-container {
        background-color: #ffffff; padding: 25px; border-radius: 20px;
        border-top: 10px solid #1E3A8A; border: 1px solid #e0e0e0;
        margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%; height: 90px !important; font-size: 20px !important;
        font-weight: bold; border-radius: 15px !important; margin-bottom: 10px;
    }
    .stats-card {
        background-color: #f1f3f5; padding: 8px; border-radius: 10px;
        text-align: center; font-size: 13px; font-weight: bold;
    }
    .warning-flash {
        background-color: #ff4b4b; height: 15px; width: 100%;
        border-radius: 10px; margin-bottom: 10px; animation: blink 0.5s 2;
    }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .analysis-box {
        padding: 20px; border-radius: 15px; background-color: #f8f9fa;
        border-left: 8px solid #1E3A8A; margin-top: 20px; line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 세션 초기화
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.stats = {
        "사회통합": 10, "경제력": 10, "국방력": 10, "사회복지": 10, "교육연구": 10,
        "외교": 10, "국민행복": 10, "환경지속성": 10, "개인의 자유": 10, "법질서": 10
    }
    st.session_state.history = []
    st.session_state.student_info = {"id": "", "name": "", "nation": ""}

# 3. 전체 시나리오 데이터 (15개 상황 + 6개 돌발)
scenarios = [
    {"title": "📍 상황 1. AI 판사 도입", "desc": "사법 신뢰 회복을 위해 판결을 기계에 맡길까요?", "A": "💡 AI 판사 도입 (공정성)", "B": "⚖️ 인간 판사 고수 (존엄성)", "effA": {"법질서": 15, "개인의 자유": -15}, "effB": {"개인의 자유": 15, "법질서": -10}, "type": "normal"},
    {"title": "🚨 돌발 1. 알고리즘 오류", "desc": "이전 선택의 결과입니다.", "type": "event", "trigger_idx": 0, "A_res": "AI가 특정 지역 거주자에게 가혹한 판결을 내려 시위가 발생했습니다!", "B_res": "재판 지연으로 범죄자들이 활개를 친다는 여론이 형성됩니다.", "effA": {"사회통합": -20, "국민행복": -15}, "effB": {"법질서": -10}},
    {"title": "📍 상황 2. 탄소세 강력 도입", "desc": "환경 보호를 위해 기업에 막대한 세금을 매길까요?", "A": "🌿 강력 규제 (환경 우선)", "B": "🏭 규제 완화 (경제 우선)", "effA": {"환경지속성": 20, "경제력": -15}, "effB": {"경제력": 20, "환경지속성": -20}, "type": "normal"},
    {"title": "📍 상황 3. 지능형 CCTV 전국 설치", "desc": "범죄 예방을 위해 모든 거리에 감시 카메라를 설치할까요?", "A": "📸 전국 설치 (치안 강화)", "B": "❌ 설치 제한 (사생활 보호)", "effA": {"법질서": 20, "개인의 자유": -20}, "effB": {"개인의 자유": 15, "법질서": -15}, "type": "normal"},
    {"title": "🚨 돌발 2. 사생활 침해 스캔들", "desc": "CCTV 설치 여부에 따른 여론입니다.", "type": "event", "trigger_idx": 3, "A_res": "정부가 CCTV로 야당 정치인을 사찰했다는 의혹이 터졌습니다!", "B_res": "CCTV 사각지대에서 강력 범죄가 발생해 국민들이 불안해합니다.", "effA": {"개인의 자유": -20, "사회통합": -15}, "effB": {"국민행복": -15, "법질서": -10}},
    {"title": "📍 상황 4. 보편적 기본소득", "desc": "모든 국민에게 매달 일정 금액을 지급하시겠습니까?", "A": "💰 전 국민 지급 (복지 확대)", "B": "🔬 인재 집중 투자 (국가 성장)", "effA": {"사회복지": 25, "사회통합": 15, "경제력": -20}, "effB": {"경제력": 20, "교육연구": 20, "사회통합": -15}, "type": "normal"},
    {"title": "📍 상황 5. 동맹국 파병 요청", "desc": "동맹국이 전쟁 중입니다. 우리 군을 보낼까요?", "A": "🎖️ 파병 결정 (외교 의리)", "B": "🙅 파병 거부 (국민 안전)", "effA": {"외교": 20, "국방력": 15, "국민행복": -25}, "effB": {"국민행복": 15, "외교": -20}, "type": "normal"},
    {"title": "🚨 돌발 3. 파병 장병 희생", "desc": "파병 결정에 따른 긴급 속보입니다.", "type": "event", "trigger_idx": 6, "A_res": "파병지에서 안타까운 인명 피해 소식이 들려와 반전 시위가 일어납니다.", "B_res": "외교적 고립으로 인해 주요 자원 수입 가격이 폭등합니다.", "effA": {"사회통합": -25, "국민행복": -15}, "effB": {"경제력": -20, "외교": -10}},
    {"title": "📍 상황 6. 외국인 노동자 대거 수용", "desc": "부족한 노동력을 채우기 위해 이민 문턱을 낮출까요?", "A": "🌍 적극 수용 (경제 활성화)", "B": "🔒 수용 제한 (사회적 안정)", "effA": {"경제력": 20, "외교": 10, "사회통합": -20}, "effB": {"사회통합": 15, "경제력": -15}, "type": "normal"},
    {"title": "📍 상황 7. 징병제 vs 모병제 전환", "desc": "국가 안보와 개인의 선택권 중 무엇을 고르시겠습니까?", "A": "🛡️ 징병제 유지 (강력한 국방)", "B": "🦅 모병제 전환 (직업의 자유)", "effA": {"국방력": 20, "개인의 자유": -15}, "effB": {"개인의 자유": 20, "국방력": -25}, "type": "normal"},
    {"title": "🚨 돌발 4. 국경 인근 무력 충돌", "desc": "현재 국방력 수치에 따른 결과입니다.", "type": "event", "trigger_idx": 9, "A_res": "강력한 군사력으로 도발을 즉각 제압하고 안정을 찾았습니다.", "B_res": "대비 부족으로 주요 시설이 점령당하고 국가 비상사태가 선포됩니다.", "effA": {"법질서": 15, "외교": 10}, "effB": {"국방력": -20, "국민행복": -25}},
    {"title": "📍 상황 8. 부동산 가격 상한제", "desc": "집값을 잡기 위해 정부가 가격을 통제할까요?", "A": "🏠 강력 개입 (주거 복지)", "B": "📈 시장 자율 (자유 경제)", "effA": {"사회복지": 20, "사회통합": 10, "경제력": -20}, "effB": {"경제력": 20, "개인의 자유": 10, "사회복지": -15}, "type": "normal"},
    {"title": "📍 상황 9. 원자력 발전소 건설", "desc": "값싼 에너지 공급을 위해 원전을 추가로 지을까요?", "A": "☢️ 원전 증설 (에너지 안보)", "B": "🍃 신재생 에너지 (지속 가능성)", "effA": {"경제력": 20, "환경지속성": -25}, "effB": {"환경지속성": 25, "경제력": -20}, "type": "normal"},
    {"title": "🚨 돌발 5. 에너지 공급 위기", "desc": "현재 경제력/환경 수치에 따른 결과입니다.", "type": "event", "trigger_idx": 12, "A_res": "충분한 전력 공급 덕분에 공장들이 풀가동되며 수출이 늘어납니다.", "B_res": "전력 부족으로 순환 정전이 발생하여 국가 마비 사태가 일어납니다.", "effA": {"경제력": 15}, "effB": {"경제력": -30, "사회복지": -10}},
    {"title": "📍 상황 10. 온라인 처벌법 도입", "desc": "악플과 가짜뉴스를 정부가 직접 처벌하게 할까요?", "A": "⚖️ 엄격 처벌 (사회 정화)", "B": "📢 표현 보호 (자유 보장)", "effA": {"사회통합": 15, "법질서": 15, "개인의 자유": -20}, "effB": {"개인의 자유": 20, "사회통합": -15}, "type": "normal"},
    {"title": "📍 상황 11. 무상 교육/급식 확대", "desc": "세금을 높여 모든 학생에게 혜택을 줄까요?", "A": "🍱 전면 무상 (평등 가치)", "B": "📉 선별 지원 (재정 건전성)", "effA": {"사회복지": 20, "사회통합": 15, "경제력": -15}, "effB": {"경제력": 15, "사회복지": -10}, "type": "normal"},
    {"title": "📍 상황 12. 우주 개발 프로젝트", "desc": "미래를 보고 우주 정거장 건설에 투자할까요?", "A": "🚀 우주 투자 (미래 기술)", "B": "🏥 공공 의료 (당장의 복지)", "effA": {"교육연구": 25, "경제력": 10, "사회복지": -15}, "effB": {"사회복지": 20, "교육연구": -15}, "type": "normal"},
    {"title": "🚨 돌발 6. 전염병 대유행", "desc": "사회복지/의료 수치에 따른 결과입니다.", "type": "event", "trigger_idx": 17, "A_res": "미래 기술과 연구 인프라 덕분에 백신을 빠르게 개발했습니다.", "B_res": "탄탄한 공공 의료망 덕분에 의료 붕괴 없이 위기를 넘겼습니다.", "effA": {"교육연구": 20, "국민행복": 10}, "effB": {"사회복지": 20, "사회통합": 10}},
    {"title": "📍 상황 13. 고교 학점제 전면 실시", "desc": "학생들에게 과목 선택권을 완전히 줄까요?", "A": "🏫 자율 선택 (학생 중심)", "B": "📔 필수 지정 (기초 학력)", "effA": {"개인의 자유": 15, "교육연구": 10, "법질서": -10}, "effB": {"교육연구": 15, "법질서": 10, "개인의 자유": -15}, "type": "normal"},
    {"title": "📍 상황 14. 독자 핵무장 논의", "desc": "국가 생존을 위해 독자적인 핵개발을 시작할까요?", "A": "💥 핵무기 개발 (자주 국방)", "B": "🤝 동맹 강화 (외교적 해결)", "effA": {"국방력": 40, "외교": -40, "경제력": -20}, "effB": {"외교": 25, "경제력": 10, "국방력": -20}, "type": "normal"},
    {"title": "📍 상황 15. 마지막 선택: 국가의 미래", "desc": "우리 나라는 어떤 방향으로 나아가야 할까요?", "A": "🦅 강한 성장과 자유", "B": "🏠 따뜻한 분배와 평등", "effA": {"경제력": 30, "개인의 자유": 20, "사회복지": -20}, "effB": {"사회복지": 30, "사회통합": 20, "경제력": -20}, "type": "normal"}
]

# --- 실행 로직 ---

if st.session_state.step == 0:
    st.markdown("<h1 style='text-align:center;'>🏛️ 국가 경영 게임</h1>", unsafe_allow_html=True)
    with st.form("login"):
        sid = st.text_input("학번 (4자리)", max_chars=4)
        sname = st.text_input("이름")
        snation = st.text_input("국가 명칭")
        if st.form_submit_button("운영 시작", use_container_width=True):
            if len(sid) == 4 and sname and snation:
                st.session_state.student_info = {"id": sid, "name": sname, "nation": snation}
                st.session_state.step = 1; st.rerun()

elif 1 <= st.session_state.step <= len(scenarios):
    q = scenarios[st.session_state.step - 1]
    st.progress(st.session_state.step / len(scenarios))
    st.markdown(f"<div class='scenario-container'><h3>{q['title']}</h3><hr><p style='font-size:21px; line-height:1.6;'>{q['desc']}</p></div>", unsafe_allow_html=True)

    if q['type'] == "normal":
        col_a, col_b = st.columns(1), st.columns(1) # 태블릿용 단일 컬럼
        if st.button(q['A']):
            eff = q['effA']; score_sum = sum(eff.values()); res_txt = ", ".join([f"{k} {v:+d}" for k, v in eff.items()])
            if score_sum >= 0: st.balloons(); st.toast(f"✅ 완료: {res_txt}", icon="🎉")
            else: st.markdown("<div class='warning-flash'></div>", unsafe_allow_html=True); st.toast(f"⚡ 경보: {res_txt}", icon="⚠️")
            for k, v in eff.items(): st.session_state.stats[k] += v
            st.session_state.history.append("A"); st.session_state.step += 1; time.sleep(1.2); st.rerun()
        if st.button(q['B']):
            eff = q['effB']; score_sum = sum(eff.values()); res_txt = ", ".join([f"{k} {v:+d}" for k, v in eff.items()])
            if score_sum >= 0: st.balloons(); st.toast(f"✅ 완료: {res_txt}", icon="🎉")
            else: st.markdown("<div class='warning-flash'></div>", unsafe_allow_html=True); st.toast(f"⚡ 경보: {res_txt}", icon="⚠️")
            for k, v in eff.items(): st.session_state.stats[k] += v
            st.session_state.history.append("B"); st.session_state.step += 1; time.sleep(1.2); st.rerun()

    elif q['type'] == "event":
        try: prev = st.session_state.history[q['trigger_idx']]
        except: prev = st.session_state.history[-1] if st.session_state.history else "A"
        msg = q['A_res'] if prev == "A" else q['B_res']
        eff = q['effA'] if prev == "A" else q['effB']
        res_txt = ", ".join([f"{k} {v:+d}" for k, v in eff.items()])
        if prev == "A": st.error(f"### ⚡ 긴급 상황!\n{msg}\n\n**변화:** {res_txt}"); st.markdown("<div class='warning-flash'></div>", unsafe_allow_html=True)
        else: st.info(f"### ℹ️ 국정 보고\n{msg}\n\n**변화:** {res_txt}")
        if st.button("상황을 확인했습니다 🆗", use_container_width=True):
            for k, v in eff.items(): st.session_state.stats[k] += v
            st.session_state.history.append("EVENT"); st.session_state.step += 1; st.rerun()

    st.markdown("---")
    st_cols = st.columns(5)
    keys = list(st.session_state.stats.keys())
    for i in range(10): st_cols[i%5].markdown(f"<div class='stats-card'>{keys[i]}<br>{st.session_state.stats[keys[i]]}</div>", unsafe_allow_html=True)

# [3단계: 최종 결과 및 심층 분석]
else:
    st.balloons()
    total = sum(st.session_state.stats.values())
    
    # 1. 상단 점수 대시보드
    st.markdown(f"""
        <div style='text-align:center; background-color:#EBF5FF; padding:40px; border-radius:30px; border: 2px solid #1E3A8A;'>
            <p style='font-size:20px; color:#1E3A8A; margin-bottom:5px;'>{st.session_state.student_info['id']} {st.session_state.student_info['name']} 지도자</p>
            <h1 style='font-size:60px; margin:0;'>{st.session_state.student_info['nation']} 국력 점수: {total}점</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. 방사형 그래프
    df = pd.DataFrame(dict(r=list(st.session_state.stats.values()), theta=list(st.session_state.stats.keys())))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself', line_color='#1E3A8A')
    st.plotly_chart(fig, use_container_width=True)

    # 3. 가치관 심층 분석 (A/B 선택 성향 분석)
    # A선택: 성장, 효율, 국방, 기술중심, 자유주의
    # B선택: 분배, 인권, 환경, 인간중심, 공동체주의
    choices = [c for c in st.session_state.history if c in ["A", "B"]]
    a_count = choices.count("A")
    b_count = choices.count("B")
    total_choices = len(choices)
    
    a_ratio = (a_count / total_choices * 100) if total_choices > 0 else 50
    b_ratio = 100 - a_ratio

    st.markdown("## 🧐 국정 운영 철학 보고서")
    
    # 성향 바 차트 시각화
    st.write(f"**성장·효율 지향 (A)** {a_ratio:.1f}% vs **형평·인권 지향 (B)** {b_ratio:.1f}%")
    st.progress(a_ratio / 100)

    # (1) 메인 국가관 분석
    col1, col2 = st.columns(2)
    with col1:
        if a_ratio > b_ratio:
            st.markdown(f"""<div class='analysis-box' style='border-left-color: #007bff;'>
            <h4>🚀 성장과 효율 중심의 리더</h4>
            {st.session_state.student_info['name']}님은 국가의 덩치를 키우고 미래 기술을 확보하는 데 집중했습니다. 
            <b>'파이를 먼저 키워야 한다'</b>는 신념으로 경쟁력을 강화한 결과, 강력한 국력을 가진 국가의 토대를 닦으셨네요!
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class='analysis-box' style='border-left-color: #28a745;'>
            <h4>🤝 형평과 인권 중심의 리더</h4>
            {st.session_state.student_info['name']}님은 사회적 약자를 보호하고 환경과 인간의 존엄성을 지키는 데 집중했습니다. 
            <b>'함께 가야 멀리 간다'</b>는 신념으로 국민의 삶의 질을 높인 따뜻한 복지 국가를 지향하셨군요!
            </div>""", unsafe_allow_html=True)

    with col2:
        # (2) 정책 스타일 요약
        if st.session_state.stats["법질서"] + st.session_state.stats["국방력"] > st.session_state.stats["개인의 자유"] + st.session_state.stats["환경지속성"]:
            st.markdown(f"""<div class='analysis-box' style='border-left-color: #dc3545;'>
            <h4>🛡️ 강력한 원칙주의 스타일</h4>
            치안과 국방, 법질서를 확립하여 사회를 안정시키는 것을 우선시했습니다. 
            혼란을 막고 국가의 기틀을 바로잡는 <b>'강한 지도자'</b>의 면모가 돋보입니다.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class='analysis-box' style='border-left-color: #ffc107;'>
            <h4>🔓 유연한 자율주의 스타일</h4>
            개인의 선택권과 환경, 시민의 목소리를 경청하는 것을 우선시했습니다. 
            다양성을 존중하고 지속 가능한 성장을 고민하는 <b>'민주적 지도자'</b>의 성향이 강합니다.
            </div>""", unsafe_allow_html=True)

    # (3) 핵심 성찰 질문 (수업 마무리용)
    st.info(f"""
    **💡 {st.session_state.student_info['name']} 지도자를 위한 질문:**
    1. 가장 고민되었던 선택은 무엇인가요? 그때 포기한 가치는 무엇이었나요?
    2. 국가의 점수가 높다고 해서 반드시 모든 국민이 행복할까요?
    3. 우리 사회에서 'A'와 'B'의 가치가 충돌할 때, 지도자는 어떤 역할을 해야 할까요?
    """)

    if st.button("처음으로 돌아가기", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()