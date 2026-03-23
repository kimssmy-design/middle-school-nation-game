import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 페이지 설정 및 디자인
# ==========================================
st.set_page_config(page_title="국가 경영 시뮬레이션 v6.8", layout="centered", initial_sidebar_state="collapsed")

# 세션 상태 초기화
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.stats = {k: 20 for k in ["사회통합", "경제력", "국방력", "사회복지", "교육연구", "환경지속성", "개인의 자유", "법질서", "국민행복", "외교"]}
    st.session_state.history = []
    st.session_state.student_info = {"id": "", "name": "", "nation": ""}
    st.session_state.processing = False  # ⭐ 중복 클릭 방지 변수

# 디자인 CSS
st.markdown("""
<style>
    html, body, [class*="st-"] { font-size: 1.1rem !important; font-family: 'Pretendard', sans-serif; }
    .scenario-container {
        background-color: #f8faff; padding: 30px; border-radius: 25px;
        border: 4px solid #4A90E2; margin-bottom: 20px; line-height: 1.8;
        box-shadow: 0 10px 25px rgba(74,144,226,0.1); white-space: pre-wrap;
    }
    .stButton>button { width: 100%; height: 5em; font-size: 1.2rem !important; font-weight: bold; border-radius: 15px; }
    .death-screen {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #000000; color: #ff3333; text-align: center;
        z-index: 99999; display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    .stats-card { background-color: #ffffff; padding: 10px; border-radius: 12px; text-align: center; border: 1px solid #eee; transition: 0.3s; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.05); } 100% { transform: scale(1); } }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 시나리오 데이터 (A/B 몰빵 시 패망하도록 조정)
# ==========================================
scenarios = [
    {"title": "📍 상황 1. AI 판사 도입", "desc": "공정한 판결이냐, 인간적 고뇌냐?", 
     "choices": {"A": "AI 판사 전면 도입", "B": "인간 판사 고유 가치 고수"}, 
     "eff": {"A": {"법질서": 10, "사회통합": -12}, "B": {"개인의 자유": 10, "법질서": -12}}},
    
    {"title": "📍 상황 2. 탄소세 강력 도입", "desc": "미래 환경이냐, 당장의 기업 생존이냐?", 
     "choices": {"A": "탄소 배출 강력 규제", "B": "기업 성장 우선(규제 완화)"}, 
     "eff": {"A": {"환경지속성": 12, "경제력": -15}, "B": {"경제력": 12, "환경지속성": -15}}},

    {"title": "📍 상황 3. 지능형 CCTV 전국 설치", "desc": "24시간 안전 도시냐, 사생활 보호 사회냐?", 
     "choices": {"A": "CCTV 전국 설치", "B": "설치 엄격 제한"}, 
     "eff": {"A": {"법질서": 15, "개인의 자유": -15}, "B": {"개인의 자유": 15, "법질서": -15}}},

    {"title": "📍 상황 4. 보편적 기본소득", "desc": "당장의 복지냐, 미래 기술 투자냐?", 
     "choices": {"A": "기본소득 전면 실시", "B": "미래 기술/인재 집중 투자"}, 
     "eff": {"A": {"사회복지": 15, "경제력": -15}, "B": {"교육연구": 15, "사회복지": -15}}},

    {"title": "📍 상황 5. 동맹국 파병 요청", "desc": "국제적 의리냐, 자국민의 생명이냐?", 
     "choices": {"A": "전투 부대 파병 결정", "B": "파병 요청 정중히 거부"}, 
     "eff": {"A": {"외교": 15, "국민행복": -15}, "B": {"국민행복": 15, "외교": -15}}},

    {"title": "📍 상황 6. 외국인 노동자 수용", "desc": "노동력 확보냐, 사회적 갈등 방지냐?", 
     "choices": {"A": "외국인 노동자 대거 수용", "B": "수용 제한 및 국민 일자리 보호"}, 
     "eff": {"A": {"경제력": 15, "사회통합": -15}, "B": {"사회통합": 15, "경제력": -15}}},

    {"title": "📍 상황 7. 징병제 유지 vs 모병제 전환", "desc": "강력한 국가 안보냐, 개인의 자율권이냐?", 
     "choices": {"A": "징병 시스템 고수", "B": "전문 모병제로 전환"}, 
     "eff": {"A": {"국방력": 15, "개인의 자유": -15}, "B": {"개인의 자유": 15, "국방력": -15}}},

    {"title": "📍 상황 8. 부동산 가격 상한제", "desc": "서민 주거권 보호냐, 시장의 자율성이냐?", 
     "choices": {"A": "정부 직접 가격 통제", "B": "시장 원리에 따른 공급 확대"}, 
     "eff": {"A": {"사회복지": 15, "경제력": -18}, "B": {"경제력": 15, "사회복지": -18}}},

    {"title": "📍 상황 9. 원자력 발전소 증설", "desc": "안정적 에너지 공급이냐, 환경 재앙 대비냐?", 
     "choices": {"A": "원전 증설 및 전력 확보", "B": "신재생 에너지로 완전 전환"}, 
     "eff": {"A": {"경제력": 15, "환경지속성": -18}, "B": {"환경지속성": 15, "경제력": -18}}},

    # --- 후반부 (변화폭 커짐: ±18~20) ---
    {"title": "📍 상황 10. 온라인 처벌법 도입", "desc": "깨끗한 인터넷 사회냐, 표현의 자유 수호냐?", 
     "choices": {"A": "악플/가짜뉴스 강력 처벌", "B": "민간 자율 정화에 위임"}, 
     "eff": {"A": {"법질서": 18, "개인의 자유": -20}, "B": {"개인의 자유": 18, "법질서": -20}}},

    {"title": "📍 상황 11. 무상 교육/급식 전면 확대", "desc": "공평한 기회냐, 재정 건전성이냐?", 
     "choices": {"A": "고교까지 전면 무상 실시", "B": "취약계층 집중 선별 지원"}, 
     "eff": {"A": {"사회복지": 20, "경제력": -20}, "B": {"경제력": 20, "사회복지": -20}}},

    {"title": "📍 상황 12. 우주 개발 프로젝트", "desc": "미래 선점 투자냐, 당장 시급한 의료 복지냐?", 
     "choices": {"A": "독자 우주 프로젝트 시작", "B": "공공 의료 시스템 혁신"}, 
     "eff": {"A": {"교육연구": 20, "사회복지": -20}, "B": {"사회복지": 20, "교육연구": -20}}},

    {"title": "📍 상황 13. 고교 학점제 도입", "desc": "꿈을 향한 자율성이냐, 기초 학력 책임 교육이냐?", 
     "choices": {"A": "학생 선택권 전면 보장", "B": "필수 기초 과목 이수 강화"}, 
     "eff": {"A": {"개인의 자유": 20, "교육연구": -18}, "B": {"교육연구": 20, "개인의 자유": -18}}},

    {"title": "📍 상황 14. 독자 핵무장 결정", "desc": "강력한 자립 국방이냐, 국제 협력 유지냐?", 
     "choices": {"A": "자주 국방 핵무기 개발", "B": "국제 공조 및 동맹 강화"}, 
     "eff": {"A": {"국방력": 25, "외교": -25}, "B": {"외교": 18, "국방력": -20}}},

    {"title": "📍 상황 15. 국가 미래 비전 선포", "desc": "무한 경쟁의 성장이냐, 함께 가는 공동체냐?", 
     "choices": {"A": "개인의 성장이 국가의 힘이다", "B": "누구도 소외되지 않는 공동체"}, 
     "eff": {"A": {"경제력": 20, "사회복지": -20}, "B": {"사회복지": 20, "경제력": -20}}},

    {"title": "📍 상황 16. 국가 운영 카지노 도입", "desc": "부족한 예산 확보냐, 국민 도덕성 보호냐?", 
     "choices": {"A": "카지노 단지 운영 추진", "B": "사행성 산업 규제 강화"}, 
     "eff": {"A": {"경제력": 18, "법질서": -18}, "B": {"법질서": 18, "경제력": -18}}},

    {"title": "📍 상황 17. 대형 산불 피해 지원", "desc": "이재민 즉각 보상이냐, 장기적 방재 투자냐?", 
     "choices": {"A": "피해 가구 전액 현금 보상", "B": "산림 복구 및 안전시설 강화"}, 
     "eff": {"A": {"국민행복": 18, "환경지속성": -18}, "B": {"환경지속성": 18, "국민행복": -18}}},

    {"title": "📍 상황 18. 노키즈존 규제 법안", "desc": "공동체 차별 금지냐, 업주 운영권 존중이냐?", 
     "choices": {"A": "모든 노키즈존 법적 금지", "B": "민간 영업 자율성 존중"}, 
     "eff": {"A": {"사회통합": 20, "개인의 자유": -20}, "B": {"개인의 자유": 20, "사회통합": -20}}}
]

def display_stats():
    st.markdown("---")
    st.markdown("<div style='margin-bottom:10px; font-weight:bold; color:#666;'>📊 실시간 국가 지표 (위험 한계치: -30)</div>", unsafe_allow_html=True)
    st_cols = st.columns(5)
    keys = list(st.session_state.stats.keys())
    for i in range(10):
        val = st.session_state.stats[keys[i]]
        # 멸망 임계점 근처일 때 빨간색 애니메이션
        status_style = "background-color: #ff3333; color: white; animation: pulse 1s infinite; border: 2px solid white;" if val <= -25 else "background-color: #f1f5f9; color: #334155;"
        st_cols[i%5].markdown(f"""
            <div class='stats-card' style='{status_style}'>
                <div style='font-size:0.75rem;'>{keys[i]}</div>
                <div style='font-size:1.2rem; font-weight:900;'>{val}</div>
            </div>
        """, unsafe_allow_html=True)

@st.dialog("📋 정책 결정 분석 보고서")
def show_result_popup(changes):
    st.markdown("#### **📊 이번 정책 결정에 따른 지표 변화**")
    for k, v in changes.items():
        color = "#FF4B4B" if v > 0 else "#4A90E2"
        st.markdown(f"**{k}**: <span style='color:{color}; font-weight:bold;'>{v}점 {'▲' if v>0 else '▼'}</span>", unsafe_allow_html=True)
    
    st.warning("결과를 확인한 후 '승인' 버튼을 누르면 다음 상황으로 넘어갑니다.")
    if st.button("정책 시행 승인", use_container_width=True):
        st.session_state.step += 1
        st.session_state.processing = False  # 처리 완료 (잠금 해제)
        st.rerun()

# ==========================================
# 3. 메인 실행 로직
# ==========================================

# [1] 패망 체크 (멸망 기준 -30점)
if st.session_state.step >= 1:
    failed_stat = next((k for k, v in st.session_state.stats.items() if v <= -30), None)
    if failed_stat:
        st.markdown(f"""
            <div class='death-screen'>
                <h1 style='font-size:4.5rem;'>💀 국가 패망</h1>
                <p style='font-size:1.5rem;'>당신이 이끌던 국가는 <b>'{failed_stat}'</b> 지표가 바닥나며 붕괴되었습니다.</p>
                <div style='margin-top: 30px;'></div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 새로운 역사 쓰기 (다시 시작)", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()
        st.stop()

# [2] 화면 구성
if st.session_state.step == 0:
    st.title("🏛️ 국가 경영 시뮬레이션 v6.8")
    with st.form("login"):
        sid = st.text_input("학번 (4자리)"); sname = st.text_input("성명"); snation = st.text_input("국가 명칭")
        if st.form_submit_button("국정 운영 시작"):
            if sid and sname and snation:
                st.session_state.student_info = {"id": sid, "name": sname, "nation": snation}
                st.session_state.step = 0.5
                st.rerun()

elif st.session_state.step == 0.5:
    st.markdown(f"<div style='background-color:#121212; color:white; padding:30px; border-radius:20px; border:4px solid #ff4b4b; text-align:center;'><h2>⚠️ 국정 책임자 임명</h2><p><b>{st.session_state.student_info['name']} 지도자님,</b><br>어떤 지표라도 <b>-30점</b>에 도달하면 즉각 정권이 축출됩니다.</p></div>", unsafe_allow_html=True)
    if st.button("🚨 집무실 입장 (시작)", use_container_width=True):
        st.session_state.step = 1
        st.rerun()

elif 1 <= st.session_state.step <= len(scenarios):
    st.components.v1.html("""<script>
        function sc(){ window.parent.document.querySelector('section.main').scrollTo(0, 0); window.parent.window.scrollTo(0,0); }
        sc(); setTimeout(sc, 50);
    </script>""", height=0)
    
    q = scenarios[int(st.session_state.step) - 1]
    st.progress(st.session_state.step / len(scenarios))
    st.markdown(f"<div class='scenario-container'><div style='color:#4A90E2; font-size:0.9rem;'>상황 {st.session_state.step} / {len(scenarios)}</div><h3>{q['title']}</h3><hr><p>{q['desc']}</p></div>", unsafe_allow_html=True)

    cols = st.columns(2)
    for i, (key, text) in enumerate(q['choices'].items()):
        # ⭐ 중복 클릭 방지 로직: processing이 True면 버튼 무력화
        if cols[i].button(text, key=f"btn_{st.session_state.step}_{key}", disabled=st.session_state.processing):
            st.session_state.processing = True # 처리 시작 (버튼 잠금)
            eff = q['eff'][key]
            st.session_state.history.append({"key": key})
            for k, v in eff.items(): st.session_state.stats[k] += v
            show_result_popup(eff)
            
    display_stats()

else:
    # 🏆 엔딩 화면
    st.balloons()
    st.title("🏆 국정 운영 완료 보고서")
    total_score = sum(st.session_state.stats.values())
    st.markdown(f"<div style='font-size:2.5rem; text-align:center; font-weight:900;'>최종 국력 지수: {total_score}</div>", unsafe_allow_html=True)
    
    df = pd.DataFrame(dict(r=list(st.session_state.stats.values()), theta=list(st.session_state.stats.keys())))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[-50, 100])
    fig.update_traces(fill='toself', line_color='#1E3A8A')
    st.plotly_chart(fig, use_container_width=True)

    # 성향 분석
    a_votes = len([h for h in st.session_state.history if h['key'] == 'A'])
    b_votes = len([h for h in st.session_state.history if h['key'] == 'B'])
    
    if a_votes > b_votes:
        st.success(f"**{st.session_state.student_info['name']} 지도자님은 '혁신과 변화'를 중시하는 리더입니다.**")
    else:
        st.info(f"**{st.session_state.student_info['name']} 지도자님은 '안정과 조화'를 중시하는 리더입니다.**")

    if st.button("🔄 새로운 통치 시작하기"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()