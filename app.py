import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 페이지 설정 및 디자인
# ==========================================
st.set_page_config(page_title="국가 경영 시뮬레이션 v6.7", layout="centered", initial_sidebar_state="collapsed")

def display_stats():
    st.markdown("---")
    st.markdown("<div style='margin-bottom:10px; font-weight:bold; color:#666;'>📊 실시간 국가 지표</div>", unsafe_allow_html=True)
    st_cols = st.columns(5)
    keys = list(st.session_state.stats.keys())
    for i in range(10):
        val = st.session_state.stats[keys[i]]
        status_style = "background-color: #ff0000; color: white; animation: pulse 0.8s infinite; border: 2px solid white;" if val <= -40 else "background-color: #f1f5f9; color: #334155;"
        st_cols[i%5].markdown(f"""
            <div class='stats-card' style='{status_style}'>
                <div style='font-size:0.8rem;'>{keys[i]}</div>
                <div style='font-size:1.2rem; font-weight:900;'>{val}</div>
            </div>
        """, unsafe_allow_html=True)

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
    .stats-card { background-color: #ffffff; padding: 10px; border-radius: 12px; text-align: center; border: 1px solid #eee; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 데이터 및 세션 초기화 (1~18번 시나리오 전체 수록)
# ==========================================
if 'step' not in st.session_state:
    st.session_state.step = 0
    st.session_state.stats = {k: 20 for k in ["사회통합", "경제력", "국방력", "사회복지", "교육연구", "환경지속성", "개인의 자유", "법질서", "국민행복", "외교"]}
    st.session_state.history = []
    st.session_state.student_info = {"id": "", "name": "", "nation": ""}

scenarios = [
    {"title": "📍 상황 1. AI 판사 도입", "desc": "[속보] 최근 사법부의 판결이 일관성이 없다는 비판이 커지며 국민적 불신이 극에 달했습니다. 이에 정부는 감정에 휘둘리지 않고 법전 그대로 판결하는 'AI 판사' 시스템 도입을 검토 중입니다. 공정한 판결이냐, 인간적 고뇌가 담긴 판결이냐의 기로에 섰습니다.", "choices": {"A": "**💡 AI 판사를 전면 도입하여 공정한 판결을 보장하자!**", "B": "**⚖️ 인간 판사의 고유한 가치와 양심을 고수해야 한다!**"}, "eff": {"A": {"법질서": 15, "국민행복": 10, "개인의 자유": -12, "사회통합": -8}, "B": {"개인의 자유": 15, "사회통합": 12, "법질서": -10, "경제력": -5}}},
    {"title": "📍 상황 2. 탄소세 강력 도입", "desc": "[환경 리포트] 기록적인 폭염과 폭우로 전 세계적 재난이 이어지고 있습니다. 국제 사회는 탄소 배출량이 많은 기업에 막대한 세금을 물리는 '강력한 탄소세' 도입을 압박하고 있습니다. 환경을 위해 경제 성장을 잠시 멈춰야 할까요, 아니면 기업의 생존을 먼저 챙겨야 할까요?", "choices": {"A": "**🌿 미래 세대를 위해 탄소 배출을 강력하게 규제하자!**", "B": "**🏭 규제를 완화하여 기업의 경제 성장을 최우선하자!**"}, "eff": {"A": {"환경지속성": 15, "교육연구": 10, "경제력": -15, "국민행복": -8}, "B": {"경제력": 15, "국민행복": 12, "환경지속성": -15, "교육연구": -10}}},
    {"title": "📍 상황 3. 지능형 CCTV 전국 설치", "desc": "[사회 뉴스] 최근 도심지 내 강력 범죄가 잇따라 발생하면서 시민들의 불안감이 커지고 있습니다. 정부는 범죄자의 안면을 즉각 인식하고 동선을 추적하는 '지능형 CCTV'를 전국 모든 골목에 설치하려 합니다. 안전한 거리일까요, 아니면 일거수일투족을 감시당하는 사회일까요?", "choices": {"A": "**📸 24시간 감시망을 구축하여 범죄 없는 도시을 만들자!**", "B": "**❌ 사생활 침해를 방지하기 위해 설치를 엄격히 제한하자!**"}, "eff": {"A": {"법질서": 15, "국방력": 8, "개인의 자유": -15, "국민행복": -10}, "B": {"개인의 자유": 15, "사회통합": 10, "법질서": -12, "국방력": -8}}},
    {"title": "📍 상황 4. 보편적 기본소득", "desc": "[경제 전망] AI와 로봇이 일자리를 대체하면서 소득 불평등이 심화되고 있습니다. 모든 국민에게 조건 없이 매달 생활비를 지급하여 소비를 살리자는 '기본소득' 안이 제안되었습니다. 당장의 복지일까요, 아니면 기술 격차를 벌리기 위한 미래 투자일까요?", "choices": {"A": "**💰 보편적 기본소득을 통해 국민의 삶을 보장하자!**", "B": "**🔬 그 예산을 미래 기술과 인재 양성에 집중 투자하자!**"}, "eff": {"A": {"사회복지": 15, "국민행복": 12, "경제력": -15, "교육연구": -10}, "B": {"교육연구": 15, "경제력": 10, "사회복지": -12, "국민행복": -8}}},
    {"title": "📍 상황 5. 동맹국 파병 요청", "desc": "[외교 시보] 우리 국가와 혈맹 관계인 우방국이 갑작스러운 침공을 받아 전쟁에 휘말렸습니다. 동맹국은 우리에게 즉각적인 전투 부대 파병을 요청해왔습니다. 국제적인 의리를 지켜야 할까요, 아니면 우리 청년들의 고귀한 생명을 보호해야 할까요?", "choices": {"A": "**🎖️ 국제 신뢰와 동맹 강화를 위해 파병을 결정하자!**", "B": "**🙅 자국민의 생명을 위해 파병 요청을 정중히 거부하자!**"}, "eff": {"A": {"외교": 15, "국방력": 10, "국민행복": -15, "사회통합": -12}, "B": {"국민행복": 12, "사회통합": 10, "외교": -15, "국방력": -10}}},
    {"title": "📍 상황 6. 외국인 노동자 수용", "desc": "[심층 보도] 저출생 여파로 산업 현장에서 일할 사람이 없어 공장이 멈춰 서고 있습니다. 정부는 이민 문턱을 낮추어 외국인 노동자를 대거 수용하는 방안을 검토 중입니다. 경제 활력을 선택할 것인가, 사회적 갈등을 최소화할 것인가의 문제입니다.", "choices": {"A": "**🌍 국경을 개방하여 노동력을 확보하고 경제를 살리자!**", "B": "**🔒 사회적 갈등을 방지하기 위해 수용을 제한하자!**"}, "eff": {"A": {"경제력": 15, "사회복지": 8, "사회통합": -15, "법질서": -10}, "B": {"사회통합": 15, "법질서": 10, "경제력": -12, "외교": -8}}},
    {"title": "📍 상황 7. 징병제 vs 모병제", "desc": "[국방 논평] 청년 인구가 줄어들면서 현재의 강제 징병 시스템을 유지하기가 어려워졌습니다. 군대를 가고 싶은 사람만 가는 '모병제'로 전환하여 군의 전문성을 높여야 한다는 주장과, 국가 안보를 위해 징병제를 유지해야 한다는 의견이 팽팽합니다.", "choices": {"A": "**🛡️ 강력한 안보를 위해 징병제 시스템을 유지하자!**", "B": "**🦅 개인의 선택권을 존중하는 모병제로 전환하자!**"}, "eff": {"A": {"국방력": 15, "법질서": 10, "개인의 자유": -15, "국민행복": -12}, "B": {"개인의 자유": 15, "국민행복": 10, "국방력": -15, "경제력": -10}}},
    {"title": "📍 상황 8. 부동산 가격 상한제", "desc": "[민생 현보] 평범한 월급으로는 평생 벌어도 집을 살 수 없을 정도로 부동산 가격이 폭등했습니다. 정부가 집값을 강제로 지정하는 '상한제'를 실시해 주거 불안을 해소하려 합니다. 서민의 주거권 보호가 먼저일까요, 시장의 자율성이 먼저일까요?", "choices": {"A": "**🏠 정부가 직접 개입하여 서민의 주거권을 보호하자!**", "B": "**📈 시장 원리에 맡기고 공급 확대로 해결하자!**"}, "eff": {"A": {"사회복지": 15, "사회통합": 10, "경제력": -15, "개인의 자유": -12}, "B": {"경제력": 15, "개인의 자유": 10, "사회복지": -12, "사회통합": -10}}},
    {"title": "📍 상황 9. 원자력 발전소 증설", "desc": "[에너지 속보] 경제 발전에 따라 전력 수요가 폭증하면서 전력 부족 사태가 우려되고 있습니다. 정부는 탄소 배출이 적고 전기가 싼 원자력 발전소를 추가로 지으려 합니다. 안정적인 에너지 공급일까요, 혹시 모를 재앙에 대한 대비일까요?", "choices": {"A": "**☢️ 원전을 늘려 안정적인 에너지를 공급하자!**", "B": "**🍃 위험을 감수하기보다 신재생 에너지로 전환하자!**"}, "eff": {"A": {"경제력": 15, "국방력": 8, "환경지속성": -15, "국민행복": -10}, "B": {"환경지속성": 15, "국민행복": 12, "경제력": -15, "사회복지": -8}}},
    {"title": "📍 상황 10. 온라인 처벌법 도입", "desc": "[IT 기획] 익명성 뒤에 숨은 악성 댓글과 가짜뉴스가 개인의 삶을 파괴하고 사회적 혼란을 야기하고 있습니다. 국가가 직접 온라인상의 표현을 단속하고 강력 처벌하는 법안이 상정되었습니다. 정의로운 인터넷일까요, 검열의 시작일까요?", "choices": {"A": "**⚖️ 엄격한 처벌로 깨끗하고 정의로운 인터넷 사회를 만들자!**", "B": "**📢 표현의 자유를 침해할 수 있으니 민간 자율에 맡기자!**"}, "eff": {"A": {"법질서": 15, "사회통합": 10, "개인의 자유": -15, "국민행복": -8}, "B": {"개인의 자유": 15, "국민행복": 10, "법질서": -12, "사회통합": -10}}},
    {"title": "📍 상황 11. 무상 교육/급식 전면 확대", "desc": "[교육 행정] 가난이 대물림되지 않도록 모든 학생에게 고등학교까지 교복, 급식, 학용품을 전면 무상으로 지원하자는 정책이 나왔습니다. 모든 아이에게 공평한 기회를 줄 것인가, 예산의 효율성을 위해 꼭 필요한 곳에만 지원할 것인가의 선택입니다.", "choices": {"A": "**🍱 보편적 복지를 통해 교육의 평등을 실현하자!**", "B": "**📉 필요한 곳에만 선별 지원하여 재정 건전성을 지키자!**"}, "eff": {"A": {"사회복지": 15, "국민행복": 12, "경제력": -15, "교육연구": -8}, "B": {"경제력": 15, "교육연구": 10, "사회복지": -12, "사회통합": -10}}},
    {"title": "📍 상황 12. 우주 개발 프로젝트", "desc": "[과학 저널] 세계 강대국들이 우주의 자원을 선점하기 위해 화성 탐사 경쟁에 뛰어들었습니다. 우리나라도 막대한 예산을 들여 독자적인 우주 프로젝트를 시작하려 합니다. 인류의 원대한 꿈에 투자할 것인가, 현실의 복지 문제 해결에 집중할 것인가?", "choices": {"A": "**🚀 인류의 미래를 위해 우주 강국으로 도약하자!**", "B": "**🏥 그 돈으로 당장 시급한 공공 의료 시스템을 개선하자!**"}, "eff": {"A": {"교육연구": 15, "국방력": 10, "사회복지": -15, "경제력": -10}, "B": {"사회복지": 15, "국민행복": 12, "교육연구": -12, "외교": -8}}},
    {"title": "📍 상황 13. 고교 학점제 도입", "desc": "[교실 현장] 공통된 과목을 공부하는 대신, 학생이 원하는 과목을 직접 선택해서 듣는 '고교 학점제' 도입이 눈앞에 있습니다. 학생의 꿈과 자율성을 응원해야 할까요, 아니면 기초 학력이 떨어지는 부작용을 막기 위해 필수 학습을 강화해야 할까요?", "choices": {"A": "**🏫 학생 개개인의 적성과 자율성을 최우선으로 존중하자!**", "B": "**📔 기초 학력 저하 방지를 위해 필수 과목을 강화하자!**"}, "eff": {"A": {"개인의 자유": 15, "국민행복": 10, "교육연구": -12, "법질서": -10}, "B": {"교육연구": 15, "법질서": 10, "개인의 자유": -15, "사회통합": -8}}},
    {"title": "📍 상황 14. 독자 핵무장 결정", "desc": "[군사 브리핑] 주변국들의 위협이 날로 거세지며 국가의 존립이 위태로워지고 있습니다. 일각에서는 타국에 의존하지 않는 독자적인 핵무기 개발만이 진정한 평화를 가져올 것이라고 주장합니다. 강력한 힘에 의한 평화냐, 국제적 고립의 위험이냐의 선택입니다.", "choices": {"A": "**💥 누구도 넘볼 수 없는 강력한 국방 자립을 선언하자!**", "B": "**🤝 국제 협력을 유지하고 동맹을 통해 안보를 지키자!**"}, "eff": {"A": {"국방력": 25, "법질서": 10, "외교": -25, "경제력": -20}, "B": {"외교": 15, "경제력": 12, "국방력": -15, "국민행복": -8}}},
    {"title": "📍 상황 15. 국가 미래 비전 선포", "desc": "[정치 대담] 건국 기념일을 맞아 우리 국가가 앞으로 100년 동안 지향할 최우선 가치를 국민 앞에 선포해야 합니다. 개인이 마음껏 경쟁하며 성장하는 나라를 만들 것인가, 조금 늦더라도 모두가 함께 손을 잡고 가는 나라를 만들 것인가?", "choices": {"A": "**🦅 개인의 자유와 경쟁을 통한 폭발적 성장이 우선이다!**", "B": "**🏠 모두가 함께 나누고 돌보는 따뜻한 공동체가 우선이다!**"}, "eff": {"A": {"경제력": 15, "개인의 자유": 12, "사회복지": -15, "사회통합": -12}, "B": {"사회복지": 15, "사회통합": 12, "경제력": -15, "개인의 자유": -10}}},
    {"title": "📍 상황 16. 국가 운영 카지노 도입", "desc": "[지방 경제] 극심한 불황으로 정부 예산이 부족해지면서 복지 혜택이 중단될 위기에 처했습니다. 정부는 세수를 확보하기 위해 국가가 직접 카지노 단지를 운영하는 방안을 추진 중입니다. 경제적 이득일까요, 도박으로 인한 사회적 타락일까요?", "choices": {"A": "**🎰 확실한 세수 확보와 관광 활성화를 선택하자!**", "B": "**🚫 도박의 위험성으로부터 국민의 도덕성을 보호하자!**"}, "eff": {"A": {"경제력": 15, "외교": 8, "법질서": -15, "국민행복": -10}, "B": {"법질서": 15, "사회통합": 10, "경제력": -15, "사회복지": -8}}},
    {"title": "📍 상황 17. 대형 산불 피해 지원", "desc": "[재난 속보] 역대 최대 규모의 산불이 발생하여 수많은 주민이 하루아침에 삶의 터전을 잃었습니다. 정부는 당장 쓸 돈이 급한 이재민에게 전액 현금 보상을 할지, 아니면 무너진 산림을 복구하고 안전 시설을 짓는 데 집중할지 결정해야 합니다.", "choices": {"A": "**💸 고통받는 이재민에게 즉각 전액 현금 보상을 실시하자!**", "B": "**🏗️ 장기적인 안전을 위해 산림 복구와 방재 시설에 투자하자!**"}, "eff": {"A": {"사회복지": 15, "국민행복": 12, "경제력": -15, "환경지속성": -10}, "B": {"환경지속성": 15, "교육연구": 10, "국민행복": -12, "경제력": -10}}},
    {"title": "📍 상황 18. 노키즈존 규제 법안", "desc": "[시민 광장] 식당과 카페에서 아이들의 출입을 금지하는 '노키즈존'이 확산되며 차별 논란이 일고 있습니다. 국가가 법으로 이를 금지하여 누구나 차별받지 않게 할까요, 아니면 조용히 쉬고 싶은 다른 손님과 업주의 운영권을 존중해야 할까요?", "choices": {"A": "**📜 차별 없는 공동체를 위해 노키즈존을 금지하자!**", "B": "**🏢 업주의 자율적인 영업권과 손님의 휴식을 존중하자!**"}, "eff": {"A": {"사회통합": 15, "사회복지": 10, "개인의 자유": -15, "경제력": -12}, "B": {"개인의 자유": 15, "경제력": 10, "사회통합": -15, "법질서": -8}}}
]

@st.dialog("📋 국정 운영 결과 분석 보고서")
def show_result_popup(changes):
    st.markdown("#### **📊 이번 정책 결정에 따른 지표 변화**")
    for k, v in changes.items():
        color = "#FF4B4B" if v > 0 else "#4A90E2"
        st.markdown(f"**{k}**: <span style='color:{color}; font-weight:bold;'>{v}점 {'▲' if v>0 else '▼'}</span>", unsafe_allow_html=True)
    if st.button("내용을 확인했습니다", use_container_width=True):
        st.session_state.step += 1
        st.rerun()

# ==========================================
# 3. 메인 실행 로직
# ==========================================

# [1] 패망 체크 (게임 중일 때만 작동)
if st.session_state.step >= 1:
    failed_stat = next((k for k, v in st.session_state.stats.items() if v <= -45), None)
    if failed_stat:
        # 💀 멸망 화면 구성
        st.markdown(f"""
            <div class='death-screen'>
                <h1 style='font-size:4rem;'>💀 국가 멸망</h1>
                <p style='font-size:1.5rem;'><b>{failed_stat}</b> 지표가 고갈되어 정권이 붕괴되었습니다.</p>
                <div style='margin-top: 30px;'></div>
            </div>
        """, unsafe_allow_html=True)
        
        # 버튼은 HTML 밖에 배치해야 클릭이 가능합니다.
        if st.button("🔄 처음부터 다시 시작하기", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
        st.stop()

# [2] 단계별 UI 구성
if st.session_state.step == 0:
    st.title("🏛️ 국가 경영 시뮬레이션 v6.7")
    with st.form("login"):
        sid = st.text_input("학번 (4자리)"); sname = st.text_input("성명"); snation = st.text_input("국가 명칭")
        if st.form_submit_button("국정 운영 시작"):
            if sid and sname and snation:
                st.session_state.student_info = {"id": sid, "name": sname, "nation": snation}
                st.session_state.step = 0.5
                st.rerun()

elif st.session_state.step == 0.5:
    st.markdown(f"<div style='background-color:#121212; color:white; padding:30px; border-radius:20px; border:4px solid #ff4b4b; text-align:center;'><h2>⚠️ 국가 경영 위기 경보</h2><p><b>{st.session_state.student_info['name']} 지도자님,</b><br>지표가 <b>-45점</b>에 도달하면 즉각 정권이 붕괴됩니다.</p></div>", unsafe_allow_html=True)
    if st.button("🚨 집무실 입장 (시작)", use_container_width=True):
        st.session_state.step = 1
        st.rerun()

elif 1 <= st.session_state.step <= len(scenarios):
    # ⭐ [스크롤 상단 고정 강화 스크립트]
    st.components.v1.html("""<script>
        function sc(){ window.parent.document.querySelector('section.main').scrollTo(0, 0); window.parent.window.scrollTo(0,0); }
        sc(); setTimeout(sc, 10); setTimeout(sc, 50);
    </script>""", height=0)
    
    q = scenarios[int(st.session_state.step) - 1]
    st.progress(st.session_state.step / len(scenarios))
    st.markdown(f"<div class='scenario-container'><div style='color:#4A90E2; font-size:0.9rem;'>상황 {st.session_state.step} / {len(scenarios)}</div><h3>{q['title']}</h3><hr><p>{q['desc']}</p></div>", unsafe_allow_html=True)

    cols = st.columns(2)
    for i, (key, text) in enumerate(q['choices'].items()):
        if cols[i].button(text, key=f"btn_{st.session_state.step}_{key}"):
            eff = q['eff'][key]
            st.session_state.history.append({"key": key})
            for k, v in eff.items(): st.session_state.stats[k] += v
            show_result_popup(eff)
    display_stats()

else:
    # 🏆 엔딩 및 차트 결과 화면
    st.balloons()
    st.title("🏆 국정 운영 완료 분석 보고서")
    total_score = sum(st.session_state.stats.values())
    st.markdown(f"<div style='font-size:2.5rem; text-align:center; font-weight:900;'>최종 국가 점수: {total_score}</div>", unsafe_allow_html=True)
    
    df = pd.DataFrame(dict(r=list(st.session_state.stats.values()), theta=list(st.session_state.stats.keys())))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[-150, 150])
    fig.update_traces(fill='toself', line_color='#1E3A8A')
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})

    lib_votes = len([h for h in st.session_state.history if h['key'] == 'B'])
    eq_votes = len([h for h in st.session_state.history if h['key'] == 'A'])
    if lib_votes > eq_votes:
        st.info(f"**{st.session_state.student_info['name']} 지도자님은 '자유와 성장'의 가치를 추구하십니다.**")
    else:
        st.success(f"**{st.session_state.student_info['name']} 지도자님은 '평등과 공동체'의 가치를 추구하십니다.**")

    if st.button("🔄 새로운 역사 시작하기"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()