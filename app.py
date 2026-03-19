import streamlit as st
import pandas as pd
import plotly.express as px
import time

# 1. 페이지 설정 및 CSS
st.set_page_config(page_title="국가 경영 시뮬레이션", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main .block-container { padding-top: 1rem; max-width: 700px; }
    .scenario-container {
        background-color: #ffffff; padding: 25px; border-radius: 20px;
        border-top: 10px solid #1E3A8A; border: 1px solid #e0e0e0;
        margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%; height: 70px !important; font-size: 18px !important;
        font-weight: bold; border-radius: 12px !important; margin-bottom: 8px;
    }
    .stats-card {
        background-color: #f1f3f5; padding: 8px; border-radius: 10px;
        text-align: center; font-size: 12px; font-weight: bold;
    }
    .danger-stat { background-color: #ff4b4b !important; color: white; animation: pulse 0.6s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }
    
    .warning-box {
        background-color: #001529; color: white; padding: 30px; 
        border-radius: 20px; border: 3px solid #ff4b4b; margin-bottom: 20px;
    }
    .score-display {
        font-size: 50px; font-weight: 900; color: #1E3A8A; text-align: center;
        margin: 20px 0; font-family: 'Courier New', Courier, monospace;
    }
    .rain { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999; }
    .drop { position: absolute; width: 2px; height: 15px; background: rgba(0, 100, 255, 0.4); animation: fall 0.7s linear infinite; }
    @keyframes fall { to { transform: translateY(100vh); } }
    </style>
    """, unsafe_allow_html=True)

def rain_effect():
    rain_html = '<div class="rain">'
    for i in range(40):
        left = i * 2.5; delay = (i % 5) * 0.2
        rain_html += f'<div class="drop" style="left: {left}%; animation-delay: {delay}s;"></div>'
    rain_html += '</div>'
    st.markdown(rain_html, unsafe_allow_html=True)

# 2. 세션 데이터 관리
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.stats = {"사회통합": 10, "경제력": 10, "국방력": 10, "사회복지": 10, "교육연구": 10, "외교": 10, "국민행복": 10, "환경지속성": 10, "개인의 자유": 10, "법질서": 10}
    st.session_state.history = []
    st.session_state.student_info = {"id": "", "name": "", "nation": ""}
    st.session_state.game_over = False

# 3. 시나리오 데이터 (trigger_title 방식 적용)
scenarios = [
    {"title": "📍 상황 1. AI 판사 도입", "desc": "사법 신뢰 회복을 위해 판결을 기계에 맡길까요?", "choices": {"A": "💡 도입 (공정성)", "B": "⚖️ 고수 (존엄성)"}, "eff": {"A": {"법질서": 45, "국민행복": 20, "개인의 자유": -25}, "B": {"개인의 자유": 40, "사회통합": 25, "법질서": -20}}, "type": "normal"},
    {"title": "📍 상황 2. 탄소세 강력 도입", "desc": "환경 보호를 위해 기업에 환경 부담금을 매길까요?", "choices": {"A": "🌿 강력 규제", "B": "🏭 규제 완화"}, "eff": {"A": {"환경지속성": 50, "교육연구": 25, "경제력": -35}, "B": {"경제력": 45, "국민행복": 20, "환경지속성": -30}}, "type": "normal"},
    {"title": "📍 상황 3. 지능형 CCTV 전국 설치", "desc": "치안을 위해 모든 거리에 감시 카메라를 설치할까요?", "choices": {"A": "📸 전국 설치", "B": "❌ 설치 제한"}, "eff": {"A": {"법질서": 45, "국민행복": 20, "개인의 자유": -30}, "B": {"개인의 자유": 40, "사회통합": 25, "법질서": -25}}, "type": "normal"},
    {"title": "📍 상황 4. 보편적 기본소득", "desc": "모든 국민에게 매달 일정 금액을 지급하시겠습니까?", "choices": {"A": "💰 보편 지급", "B": "🔬 인재 투자"}, "eff": {"A": {"사회복지": 55, "국민행복": 35, "경제력": -40}, "B": {"경제력": 50, "교육연구": 45, "사회복지": -25}}, "type": "normal"},
    {"title": "📍 상황 5. 동맹국 파병 요청", "desc": "동맹국이 전쟁 중입니다. 우리 군을 보낼까요?", "choices": {"A": "🎖️ 파병 결정", "B": "🙅 파병 거부"}, "eff": {"A": {"외교": 55, "국방력": 40, "국민행복": -35}, "B": {"국민행복": 35, "사회통합": 30, "외교": -40}}, "type": "normal"},
    {"title": "🚨 돌발 1. 기술 혁신의 결실", "desc": "국가 정책의 영향으로 예상치 못한 결과가 발생했습니다!", "type": "event", "trigger_title": "📍 상황 4. 보편적 기본소득", "A_res": "기본소득이 소비 진작으로 이어져 경제가 활성화됩니다!", "B_res": "집중 투자한 인재들이 세계적인 발명을 해냈습니다!", "effA": {"경제력": 40, "국민행복": 25}, "effB": {"교육연구": 50, "경제력": 35}},
    {"title": "📍 상황 6. 외국인 노동자 대거 수용", "desc": "노동력 확보를 위해 이민 문턱을 낮출까요?", "choices": {"A": "🌍 적극 수용", "B": "🔒 수용 제한"}, "eff": {"A": {"경제력": 40, "사회복지": 20, "사회통합": -45}, "B": {"사회통합": 35, "법질서": 25, "경제력": -40}}, "type": "normal"},
    {"title": "📍 상황 7. 징병제 vs 모병제", "desc": "국가 안보 시스템의 방향을 선택하세요.", "choices": {"A": "🛡️ 징병제 유지", "B": "🦅 모병제 전환"}, "eff": {"A": {"국방력": 35, "법질서": 15, "개인의 자유": -35}, "B": {"개인의 자유": 40, "국민행복": 25, "국방력": -45}}, "type": "normal"},
    {"title": "🚨 돌발 2. 국경 무력 충돌", "desc": "접경 지역에서 교전이 발생했습니다!", "type": "event", "trigger_title": "📍 상황 7. 징병제 vs 모병제", "A_res": "탄탄한 병력으로 적을 즉각 퇴치하고 승리했습니다.", "B_res": "병력 부족으로 영토 일부가 점령당하는 수모를 겪습니다.", "effA": {"국방력": 30, "국민행복": 20}, "effB": {"국방력": -60, "국민행복": -55}},
    {"title": "📍 상황 8. 부동산 가격 상한제", "desc": "정부가 집값의 한도를 정해 강제 통제할까요?", "choices": {"A": "🏠 강력 개입", "B": "📈 시장 자율"}, "eff": {"A": {"사회복지": 35, "사회통합": 20, "경제력": -45}, "B": {"경제력": 40, "개인의 자유": 25, "사회복지": -40}}, "type": "normal"},
    {"title": "📍 상황 9. 원자력 발전소 건설", "desc": "에너지 확보를 위해 원전을 더 지을까요?", "choices": {"A": "☢️ 원전 증설", "B": "🍃 신재생 전환"}, "eff": {"A": {"경제력": 45, "국방력": 15, "환경지속성": -50}, "B": {"환경지속성": 45, "국민행복": 20, "경제력": -45}}, "type": "normal"},
    {"title": "🚨 돌발 3. 에너지 대란", "desc": "국제 에너지 가격이 폭등했습니다!", "type": "event", "trigger_title": "📍 상황 9. 원자력 발전소 건설", "A_res": "원전의 안정적 공급 덕분에 위기를 무사히 넘깁니다.", "B_res": "전력 부족으로 순환 정전이 발생해 국가 기능이 마비됩니다.", "effA": {"경제력": 30, "국민행복": 10}, "effB": {"경제력": -60, "사회복지": -45}},
    {"title": "📍 상황 10. 온라인 처벌법 도입", "desc": "악플과 가짜뉴스를 국가가 직접 처벌할까요?", "choices": {"A": "⚖️ 엄격 처벌", "B": "📢 표현 보호"}, "eff": {"A": {"사회통합": 30, "법질서": 25, "개인의 자유": -45}, "B": {"개인의 자유": 40, "국민행복": 20, "사회통합": -40}}, "type": "normal"},
    {"title": "📍 상황 11. 무상 교육/급식 확대", "desc": "세금을 더 걷어 모든 학생에게 무상 혜택을 줄까요?", "choices": {"A": "🍱 전면 무상", "B": "📉 선별 지원"}, "eff": {"A": {"사회복지": 40, "국민행복": 25, "경제력": -45}, "B": {"경제력": 35, "교육연구": 25, "사회복지": -40}}, "type": "normal"},
    {"title": "📍 상황 12. 우주 개발 프로젝트", "desc": "막대한 예산을 들여 화성 탐사에 도전할까요?", "choices": {"A": "🚀 우주 투자", "B": "🏥 의료 투자"}, "eff": {"A": {"교육연구": 50, "국방력": 25, "경제력": -45}, "B": {"사회복지": 40, "국민행복": 30, "교육연구": -40}}, "type": "normal"},
    {"title": "🚨 돌발 4. 전염병 팬데믹", "desc": "신종 바이러스가 전국으로 확산되고 있습니다!", "type": "event", "trigger_title": "📍 상황 12. 우주 개발 프로젝트", "A_res": "미래 기술 인프라를 활용해 백신 개발에 성공합니다.", "B_res": "탄탄한 공공 의료망 덕분에 피해를 최소화하며 막아냅니다.", "effA": {"교육연구": 35, "경제력": 20}, "effB": {"사회복지": 35, "사회통합": 25}},
    {"title": "📍 상황 13. 고교 학점제", "desc": "학생들에게 완전한 과목 선택권을 보장할까요?", "choices": {"A": "🏫 자율 선택", "B": "📔 필수 지정"}, "eff": {"A": {"개인의 자유": 35, "국민행복": 25, "교육연구": -40}, "B": {"교육연구": 35, "법질서": 25, "개인의 자유": -45}}, "type": "normal"},
    {"title": "📍 상황 14. 독자 핵무장", "desc": "국가 생존을 위해 핵무기 개발을 시작할까요?", "choices": {"A": "💥 핵개발 시작", "B": "🤝 동맹 강화"}, "eff": {"A": {"국방력": 75, "외교": -80, "경제력": -50}, "B": {"외교": 50, "경제력": 25, "국방력": -55}}, "type": "normal"},
    {"title": "📍 상황 15. 국가의 미래 비전", "desc": "우리 나라는 어떤 가치를 최우선으로 해야 할까요?", "choices": {"A": "🦅 자유와 성장", "B": "🏠 평등과 공생"}, "eff": {"A": {"경제력": 65, "개인의 자유": 45, "사회복지": -55}, "B": {"사회복지": 65, "사회통합": 45, "경제력": -55}}, "type": "normal"},
    {"title": "🚨 돌발 5. 외교적 마찰", "desc": "우리의 비전 선포 이후 주변국의 반응이 엇갈립니다.", "type": "event", "trigger_title": "📍 상황 15. 국가의 미래 비전", "A_res": "성장 잠재력을 높이 평가한 외국 자본이 유입됩니다.", "B_res": "국제 사회에서 인도주의적 리더로 찬사받습니다.", "effA": {"경제력": 40, "외교": 20}, "effB": {"사회통합": 30, "외교": 40}},
    {"title": "📍 상황 16. 국가 운영 카지노 도입", "desc": "세수 확보를 위해 국가 카지노를 운영할까요?", "choices": {"A": "🎰 전면 허용", "B": "🎟️ 제한 허용", "C": "🚫 절대 금지"}, "eff": {"A": {"경제력": 55, "법질서": -60}, "B": {"경제력": 30, "법질서": -35, "국민행복": 10}, "C": {"법질서": 40, "경제력": -50}}, "type": "normal"},
    {"title": "📍 상황 17. 대형 산불 피해 지원", "desc": "피해 지역을 어떻게 지원할까요?", "choices": {"A": "💸 전액 현금 보상", "B": "🏗️ 시설 복구 지원", "C": "🛡️ 보험 의무화"}, "eff": {"A": {"사회복지": 50, "경제력": -55}, "B": {"사회복지": 30, "환경지속성": 25, "경제력": -45}, "C": {"법질서": 30, "경제력": -35}}, "type": "normal"},
    {"title": "📍 상황 18. 노키즈존 규제 법안", "desc": "업체의 노키즈존 설정을 규제할까요?", "choices": {"A": "📜 규제 도입", "B": "🏢 자율 운영", "C": "👶 혜택 부여"}, "eff": {"A": {"사회통합": 45, "사회복지": 25, "개인의 자유": -50}, "B": {"개인의 자유": 45, "경제력": 25, "사회통합": -55}, "C": {"사회복지": 35, "경제력": -40}}, "type": "normal"},
    {"title": "🚨 돌발 6. 재난 예산 고갈", "desc": "연이은 지원책으로 재정이 바닥났습니다!", "type": "event", "trigger_title": "📍 상황 17. 대형 산불 피해 지원", "A_res": "현금 보상안이 독이 되어 물가가 폭등하고 재정이 위태롭습니다.", "B_res": "시설 복구에 집중하느라 현금이 부족해 신용이 하락합니다.", "C_res": "미리 도입한 보험 시스템 덕분에 타격 없이 위기를 넘깁니다!", "effA": {"경제력": -65, "사회통합": -40}, "effB": {"경제력": -55, "국민행복": -40}, "effC": {"경제력": 25, "법질서": 25}}
]

def check_game_over():
    for k, v in st.session_state.stats.items():
        if v <= -120: return k
    return None

# --- 실행 로직 ---

if st.session_state.game_over:
    failed_reason = check_game_over()
    st.markdown(f"<div style='background:black; color:red; padding:50px; text-align:center;'><h1>☠️ 패 망</h1><p>{st.session_state.student_info['nation']} 붕괴 (원인: {failed_reason})</p></div>", unsafe_allow_html=True)
    if st.button("과거로 회귀하여 다시 도전"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

elif st.session_state.step == 0:
    st.markdown("<h1 style='text-align:center;'>🏛️ 국가 경영 시뮬레이션</h1>", unsafe_allow_html=True)
    with st.form("login"):
        sid = st.text_input("학번 (4자리)"); sname = st.text_input("성명"); snation = st.text_input("국가 명칭")
        if st.form_submit_button("국정 운영 시작"):
            if sid and sname and snation:
                st.session_state.student_info = {"id": sid, "name": sname, "nation": snation}; st.session_state.step = 0.5; st.rerun()

elif st.session_state.step == 0.5:
    st.markdown(f"""
    <div class='warning-box'>
        <p style='font-size:22px; color:#ff4b4b; font-weight:bold;'>⚠️ 경고: 난이도가 대폭 상승했습니다!</p>
        <p style='font-size:18px;'><b>{st.session_state.student_info['name']} 지도자님,</b><br>
        이제 더 이상 관용은 없습니다. 한 번의 실수가 국가의 운명을 결정합니다.</p>
        <hr style='border:1px solid #333;'>
        <ul style='font-size:16px; color:#ffcccc;'>
            <li><b>멸망 조건:</b> 단 하나라도 <b>-120점</b>에 도달하면 즉각 패망합니다.</li>
            <li><b>분석:</b> 마지막 단계에서 당신의 통치 스타일을 <b>자유와 평등</b>의 가치를 중심으로 정밀 분석해 드립니다.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    if st.button("지옥의 국정 운영 시작"): st.session_state.step = 1; st.rerun()

elif 1 <= st.session_state.step <= len(scenarios):
    if check_game_over(): st.session_state.game_over = True; st.rerun()
    q = scenarios[int(st.session_state.step) - 1]
    
    # 🚨 돌발 상황 처리
    if q.get("type") == "event":
        trigger_title = q['trigger_title']
        user_choice_record = next((h for h in st.session_state.history if h['title'] == trigger_title), None)
        
        if user_choice_record:
            trigger_choice = user_choice_record['key']
            res_text = q.get(f"{trigger_choice}_res", "분석 중...")
            eff = q.get(f"eff{trigger_choice}", {})
        else:
            res_text = "기록을 찾을 수 없습니다."; eff = {}
        
        st.markdown(f"<div class='scenario-container' style='border-top: 10px solid #ff4b4b;'><h4>{q['title']}</h4><hr><p style='font-size:19px;'><b>{res_text}</b></p></div>", unsafe_allow_html=True)
        
        if st.button("상황 수습 및 계속"):
            # 🔔 돌발 상황 스탯 변화 팝업
            toast_msg = "🚨 [돌발 상황 결과] " + ", ".join([f"{k} {v:+}" for k, v in eff.items()])
            st.toast(toast_msg)
            
            for k, v in eff.items(): st.session_state.stats[k] += v
            st.session_state.step += 1; st.rerun()
            
    # 📍 일반 상황 처리
    else:
        st.progress(st.session_state.step / len(scenarios))
        st.markdown(f"<div class='scenario-container'><h4>상황 {st.session_state.step}</h4><h3>{q['title']}</h3><hr><p style='font-size:19px;'>{q['desc']}</p></div>", unsafe_allow_html=True)

        choice_keys = list(q['choices'].keys())
        cols = st.columns(len(choice_keys))
        for i, key in enumerate(choice_keys):
            if cols[i].button(q['choices'][key]):
                eff = q['eff'][key]
                st.session_state.history.append({"title": q['title'], "choice": q['choices'][key], "key": key})
                
                # 🔔 일반 상황 스탯 변화 팝업
                toast_msg = "📊 [국정 지표 변화] " + ", ".join([f"{k} {v:+}" for k, v in eff.items()])
                st.toast(toast_msg)
                
                if sum(eff.values()) >= 0: st.balloons()
                else: rain_effect()
                
                for k, v in eff.items(): st.session_state.stats[k] += v
                st.session_state.step += 1; time.sleep(0.4); st.rerun()

    # 하단 스탯 표시
    st.markdown("---")
    st_cols = st.columns(5); stats_keys = list(st.session_state.stats.keys())
    for i in range(10):
        val = st.session_state.stats[stats_keys[i]]; cls = "danger-stat" if val <= -90 else ""
        st_cols[i%5].markdown(f"<div class='stats-card {cls}'>{stats_keys[i]}<br>{val}</div>", unsafe_allow_html=True)

# 🌟 결과 페이지
else:
    st.markdown("## 🏆 국정 운영 결과 분석")
    
    # 점수 타이핑 애니메이션
    total_score = sum(st.session_state.stats.values())
    placeholder = st.empty()
    step_val = max(1, abs(total_score) // 20)
    
    for i in range(0, total_score, step_val if total_score >= 0 else -step_val):
        placeholder.markdown(f"<div class='score-display'>최종 국가 스코어: {i}</div>", unsafe_allow_html=True)
        time.sleep(0.05)
    placeholder.markdown(f"<div class='score-display'>최종 국가 스코어: {total_score}</div>", unsafe_allow_html=True)
    
    st.balloons()
    
    # 그래프 시각화
    df = pd.DataFrame(dict(r=list(st.session_state.stats.values()), theta=list(st.session_state.stats.keys())))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[-150, 150])
    fig.update_traces(fill='toself', line_color='#1E3A8A')
    st.plotly_chart(fig)

    st.markdown("---")
    st.subheader("⚖️ 도덕적 가치 지향성 분석")
    
    lib_votes = len([h for h in st.session_state.history if h['key'] == 'B'])
    eq_votes = len([h for h in st.session_state.history if h['key'] == 'A'])
    
    if lib_votes > eq_votes:
        st.info(f"**{st.session_state.student_info['name']} 지도자님은 '자유주의' 가치를 최우선으로 하십니다.**\n\n모든 선택의 저변에는 개인의 권리와 자율이 국가의 통제보다 중요하다는 신념이 깔려 있군요. {lib_votes}번의 선택에서 당신은 개인이 스스로의 삶을 결정할 자유를 수호했습니다.")
    else:
        st.success(f"**{st.session_state.student_info['name']} 지도자님은 '공동체적 평등' 가치를 최우선으로 하십니다.**\n\n당신은 사회적 약자를 보호하고 평등한 기회를 제공하는 것이 국가의 존재 이유라고 믿고 계시군요. {eq_votes}번의 선택에서 당신은 우리 사회가 함께 나아가는 가치를 선택했습니다.")

    st.markdown(f"""
    > **선생님의 한 마디:** {st.session_state.student_info['name']}님, 이 시뮬레이션을 통해 당신이 지키고자 했던 가치는 무엇이며, 
    > 점수를 위해 어쩔 수 없이 포기해야 했던 가치는 무엇이었나요? 
    > 결과 페이지의 스탯 그래프를 보고, **가장 낮은 점수를 기록한 분야**가 왜 그렇게 되었는지 학습지에 성찰해 보세요.
    """)

    if st.button("새로운 역사 시작"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()