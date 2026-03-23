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
    {
        "title": "📍 상황 1. 사법부의 대변혁, AI 판사 도입", 
        "desc": "[사회면 뉴스] '판사마다 형량이 제각각'이라는 국민적 불신이 임계점에 도달했습니다. 최근 비슷한 범죄임에도 판사의 성향에 따라 판결이 크게 갈리자, 정부는 감정이나 편견 없이 법전 그대로 판결하는 'AI 판사' 도입을 검토 중입니다. \n\n일부 시민단체는 '기계적 공정성'을 환영하지만, 법조계는 '인간의 고뇌와 양심이 사라진 판결은 정의가 아니다'라며 거세게 반발하고 있습니다. 당신의 선택은?", 
        "choices": {"A": "💡 AI 판사를 전면 도입하여 절대적 공정성을 보장하자!", "B": "⚖️ 판사의 인간적 양심과 고유한 가치를 고수해야 한다!"}, 
        "eff": {"A": {"법질서": 10, "사회통합": -12}, "B": {"개인의 자유": 10, "법질서": -12}}
    },
    {
        "title": "📍 상황 2. 탄소세 강력 도입과 산업계의 비명", 
        "desc": "[경제 브리핑] 기록적인 폭염과 폭우로 인해 전 국가적 재난 비용이 기하급수적으로 늘고 있습니다. 국제 사회는 탄소 배출량이 많은 기업에 막대한 세금을 물리는 '탄소세' 도입을 강하게 압박하고 있습니다. \n\n환경 단체는 '지금 멈추지 않으면 미래는 없다'고 외치지만, 주요 수출 기업들은 '세금 부담 때문에 공장을 해외로 옮겨야 할 판'이라며 울상입니다. 환경과 경제, 어느 쪽의 손을 들어주시겠습니까?", 
        "choices": {"A": "🌿 미래 세대를 위해 탄소 배출을 강력하게 규제하자!", "B": "🏭 기업의 생존이 우선! 규제를 완화하여 성장을 지키자!"}, 
        "eff": {"A": {"환경지속성": 12, "경제력": -15}, "B": {"경제력": 12, "환경지속성": -15}}
    },
    {
        "title": "📍 상황 3. 지능형 CCTV 전국 설치와 감시 사회", 
        "desc": "[경찰청 속보] 도심 내 강력 범죄가 잇따라 발생하면서 밤길 통행을 두려워하는 시민들이 늘고 있습니다. 정부는 범죄자의 안면을 실시간으로 인식하고 동선을 즉각 추적하는 '지능형 CCTV'를 전국 모든 골목에 촘촘히 설치하려 합니다. \n\n범죄 예방에는 탁월하겠지만, 모든 시민의 일거수일투족이 국가의 감시망 아래 놓이게 됩니다. 안전한 도시일까요, 아니면 숨 막히는 감시 사회일까요?", 
        "choices": {"A": "📸 24시간 감시망을 구축하여 범죄 없는 도시를 만들자!", "B": "❌ 사생활 침해를 막기 위해 CCTV 설치를 엄격히 제한하자!"}, 
        "eff": {"A": {"법질서": 15, "개인의 자유": -15}, "B": {"개인의 자유": 15, "법질서": -15}}
    },
    {
        "title": "📍 상황 4. 로봇 시대의 생존권, 보편적 기본소득", 
        "desc": "[IT/경제 뉴스] AI와 자동화 로봇이 단순 노동을 넘어 전문직 일자리까지 위협하고 있습니다. 소득 불평등이 심화되자, 모든 국민에게 조건 없이 매달 생활비를 지급하여 최소한의 삶을 보장하자는 '보편적 기본소득' 안이 제안되었습니다. \n\n당장의 빈곤을 해결할 복지 카드일까요, 아니면 국가 재정을 투입해 기술 격차를 벌려야 하는 미래 투자의 걸림돌일까요?", 
        "choices": {"A": "💰 기본소득을 통해 국민의 기본적인 삶을 보장하자!", "B": "🔬 그 예산을 AI 기술 개발과 미래 인재 양성에 쏟아붓자!"}, 
        "eff": {"A": {"사회복지": 15, "경제력": -15}, "B": {"교육연구": 15, "사회복지": -15}}
    },
    {
        "title": "📍 상황 5. 혈맹의 부름, 동맹국 파병 요청", 
        "desc": "[외교 안보 속보] 오랜 우방국이 갑작스러운 침공을 받아 전면전에 휘말렸습니다. 동맹국은 우리 국가에 즉각적인 전투 부대 파병을 간곡히 요청해 왔습니다. \n\n파병을 거부하면 국제적 고립과 신뢰 하락이 우려되고, 파병을 결정하면 우리 소중한 청년들이 전쟁터에서 피를 흘리게 됩니다. 국가의 의리와 자국민의 생명 중 무엇이 더 무겁습니까?", 
        "choices": {"A": "🎖️ 국제적 신뢰와 동맹 강화를 위해 파병을 결정하자!", "B": "🙅 자국민의 생명을 위해 파병 요청을 정중히 거부하자!"}, 
        "eff": {"A": {"외교": 15, "국민행복": -15}, "B": {"국민행복": 15, "외교": -15}}
    },
    {
        "title": "📍 상황 6. 인구 소멸 위기, 외국인 노동자 대거 수용", 
        "desc": "[인구 통계 리포트] 저출생과 고령화로 인해 산업 현장에 일할 사람이 없어 공장들이 멈춰 서고 있습니다. 정부는 이민 문턱을 낮추어 외국인 노동자를 대거 수용하는 파격적인 방안을 검토 중입니다. \n\n경제에는 활력이 돌겠지만, 서로 다른 문화로 인한 사회적 갈등과 범죄 우려도 커지고 있습니다. 경제적 생존을 위해 문을 여시겠습니까, 아니면 사회적 안정을 위해 빗장을 거시겠습니까?", 
        "choices": {"A": "🌍 국경을 과감히 개방하여 노동력을 확보하고 경제를 살리자!", "B": "🔒 사회적 혼란을 막기 위해 수용 정책을 엄격히 제한하자!"}, 
        "eff": {"A": {"경제력": 15, "사회통합": -15}, "B": {"사회통합": 15, "경제력": -15}}
    },
    {
        "title": "📍 상황 7. 징병제 유지냐, 모병제 전환이냐", 
        "desc": "[국방 논평] 청년 인구가 급감하면서 현재의 강제 징병 시스템을 유지하는 것이 불가능에 가까워지고 있습니다. 군대를 가고 싶은 사람만 가는 '모병제'로 전환하여 소수 정예 전문가 집단을 키워야 한다는 주장과, 안보 불안을 이유로 징병제를 고수해야 한다는 의견이 팽팽합니다. \n\n국가의 철통같은 안보와 개인의 선택권 사이에서 결단이 필요합니다.", 
        "choices": {"A": "🛡️ 강력한 국가 안보를 위해 징병제 시스템을 고수하자!", "B": "🦅 개인의 자유를 존중하고 전문적인 모병제로 전환하자!"}, 
        "eff": {"A": {"국방력": 15, "개인의 자유": -15}, "B": {"개인의 자유": 15, "국방력": -15}}
    },
    {
        "title": "📍 상황 8. 집값 광풍, 부동산 가격 상한제", 
        "desc": "[민생 현장] 평범한 직장인이 월급을 한 푼도 안 쓰고 수십 년을 모아도 집 한 채 살 수 없는 지경에 이르렀습니다. 분노한 여론이 들끓자 정부는 집값을 강제로 고정하는 '상한제' 카드를 꺼내 들었습니다. \n\n무주택 서민들은 환호하지만, 전문가들은 시장 원리를 무시한 처사라며 공급 절벽을 우려하고 있습니다. 서민의 주거권입니까, 시장 경제의 자율성입니까?", 
        "choices": {"A": "🏠 정부가 직접 개입하여 서민의 주거권을 철저히 보호하자!", "B": "📈 시장 자율에 맡기고 공급 확대를 통해 해결해야 한다!"}, 
        "eff": {"A": {"사회복지": 15, "경제력": -18}, "B": {"경제력": 15, "사회복지": -18}}
    },
    {
        "title": "📍 상황 9. 에너지 대란, 원자력 발전소 증설", 
        "desc": "[에너지 속보] 첨단 산업의 발달로 국가 전력 수요가 폭증하면서 대규모 정전 사태가 우려되고 있습니다. 정부는 탄소 배출이 적고 전기가 싼 원자력 발전소를 추가로 지어 에너지를 확보하려 합니다. \n\n경제 성장을 위한 저렴한 에너지 공급일까요, 아니면 혹시 모를 방사능 재앙에 대한 위험한 도박일까요? 환경 단체는 재생 에너지만이 답이라며 발전소 앞에서 단식 투쟁 중입니다.", 
        "choices": {"A": "☢️ 원전을 대폭 늘려 안정적이고 저렴한 전력을 공급하자!", "B": "🍃 위험을 감수하기보다 신재생 에너지로 완전히 전환하자!"}, 
        "eff": {"A": {"경제력": 15, "환경지속성": -18}, "B": {"환경지속성": 15, "경제력": -18}}
    },
    {
        "title": "📍 상황 10. 온라인 처벌법과 표현의 자유", 
        "desc": "[IT 기획 보도] 익명성 뒤에 숨은 악성 댓글과 가짜뉴스가 연예인과 정치인은 물론 일반인들의 삶까지 파괴하고 있습니다. 국가가 직접 온라인상의 표현을 단속하고 강력 처벌하는 이른바 '정의로운 인터넷법'이 상정되었습니다. \n\n깨끗한 온라인 세상을 만들 수 있겠지만, 정부를 향한 비판적인 목소리조차 '검열'당할 수 있다는 우려가 제기됩니다. 당신의 판단은?", 
        "choices": {"A": "⚖️ 강력한 처벌로 깨끗하고 정의로운 인터넷 사회를 만들자!", "B": "📢 표현의 자유를 침해할 수 있으니 민간의 자율에 맡기자!"}, 
        "eff": {"A": {"법질서": 18, "개인의 자유": -20}, "B": {"개인의 자유": 18, "법질서": -20}}
    },
    {
        "title": "📍 상황 11. 무상 교육/급식의 전면적인 확대", 
        "desc": "[교육 행정 리포트] '개천에서 용 나기 어렵다'는 말이 정설이 된 시대입니다. 가난이 대물림되지 않도록 모든 학생에게 고등학교까지 교복, 급식, 학용품을 전면 무상으로 지원하자는 정책이 발표되었습니다. \n\n모든 아이에게 평등한 기회를 주자는 이상과, 국가 재정 파탄을 막기 위해 정말 필요한 사람만 도와야 한다는 현실이 충돌하고 있습니다.", 
        "choices": {"A": "🍱 보편적 복지를 통해 교육의 평등을 확실히 실현하자!", "B": "📉 필요한 곳에만 선별 지원하여 국가 재정을 지켜내자!"}, 
        "eff": {"A": {"사회복지": 20, "경제력": -20}, "B": {"경제력": 20, "사회복지": -20}}
    },
    {
        "title": "📍 상황 12. 우주 개발과 화성 탐사 프로젝트", 
        "desc": "[과학 저널] 강대국들이 우주의 희귀 자원을 선점하기 위해 화성 탐사 전쟁에 뛰어들었습니다. 우리 국가도 막대한 예산을 투입해 독자적인 우주 프로젝트를 시작하려 합니다. \n\n인류의 원대한 꿈과 미래 자원을 선점하자는 주장과, 그 돈으로 당장 시급한 응급 의료 체계부터 개선하라는 서민들의 목소리가 엇갈립니다. 당신은 어디에 서명하시겠습니까?", 
        "choices": {"A": "🚀 인류의 미래를 위해 우주 강국으로 과감히 도약하자!", "B": "🏥 그 예산으로 당장 시급한 공공 의료 시스템을 혁신하자!"}, 
        "eff": {"A": {"교육연구": 20, "사회복지": -20}, "B": {"사회복지": 20, "교육연구": -20}}
    },
    {
        "title": "📍 상황 13. 교실의 변화, 고교 학점제 도입", 
        "desc": "[교실 현장] 획일적인 주입식 교육에서 벗어나, 학생이 원하는 과목을 직접 골라 듣는 '고교 학점제'가 본격 시행을 앞두고 있습니다. 학생의 적성과 자율성을 키워줄 혁명적인 제도라는 찬사와, 인기 없는 기초 학문이 사라질 것이라는 걱정이 공존합니다. \n\n학생의 꿈을 응원하는 자율성입니까, 아니면 기초 학력 저하를 막기 위한 필수 학습의 강화입니까?", 
        "choices": {"A": "🏫 학생 개개인의 적성과 수업 선택권을 전면 보장하자!", "B": "📔 기초 학력 저하를 막기 위해 필수 과목 학습을 강화하자!"}, 
        "eff": {"A": {"개인의 자유": 20, "교육연구": -18}, "B": {"교육연구": 20, "개인의 자유": -18}}
    },
    {
        "title": "📍 상황 14. 안보의 정점, 독자 핵무장 결정", 
        "desc": "[군사 브리핑] 주변국들이 핵 위협을 강화하며 국가의 존립이 위태로워지고 있습니다. 일각에서는 타국에 의존하지 않는 우리만의 독자적인 핵무기 개발만이 진정한 평화를 가져올 것이라고 주장합니다. \n\n강력한 자위권을 확보하여 누구도 넘볼 수 없는 나라가 될 것인가, 아니면 국제적인 제재와 고립의 위험을 피하며 평화 공조를 택할 것인가? 운명의 시간이 다가옵니다.", 
        "choices": {"A": "💥 누구도 넘볼 수 없는 강력한 국방 자립(핵무장)을 선언하자!", "B": "🤝 국제적 고립을 피하고 동맹을 통해 안보를 지켜내자!"}, 
        "eff": {"A": {"국방력": 25, "외교": -25}, "B": {"외교": 18, "국방력": -20}}
    },
    {
        "title": "📍 상황 15. 국가 미래 비전 선포", 
        "desc": "[정치 대담] 건국 기념일을 맞아 우리 국가가 향후 100년 동안 지향할 최우선 가치를 선포해야 합니다. \n\n누구든 능력껏 경쟁하고 승리하여 폭발적인 국가 성장을 이끄는 모델인가, 아니면 조금 늦더라도 약자를 돌보며 모두가 손잡고 가는 따뜻한 공동체 모델인가? 지도자님의 비전을 한 문장으로 결정해 주십시오.", 
        "choices": {"A": "🦅 개인의 자유와 공정한 경쟁을 통한 폭발적 성장이 우선이다!", "B": "🏠 모두가 함께 나누고 돌보는 따뜻한 공동체가 우선이다!"}, 
        "eff": {"A": {"경제력": 20, "사회복지": -20}, "B": {"사회복지": 20, "경제력": -20}}
    },
    {
        "title": "📍 상황 16. 국가 운영 카지노 도입", 
        "desc": "[지방 경제 속보] 극심한 경기 침체로 정부 예산이 바닥나면서 노인 복지와 육아 지원 혜택이 중단될 위기에 처했습니다. 정부는 막대한 세수를 확보하고 관광객을 유치하기 위해 국가가 직접 대규모 카지노 단지를 운영하는 방안을 추진 중입니다. \n\n확실한 돈줄이 될까요, 아니면 도박 중독과 범죄를 조장하는 사회적 타락의 시작일까요?", 
        "choices": {"A": "🎰 세수 확보와 지방 경제 활성화를 위해 카지노를 도입하자!", "B": "🚫 도박의 위험으로부터 국민의 도덕성과 삶을 보호하자!"}, 
        "eff": {"A": {"경제력": 18, "법질서": -18}, "B": {"법질서": 18, "경제력": -18}}
    },
    {
        "title": "📍 상황 17. 대형 산불 피해, 보상 vs 예방", 
        "desc": "[재난 현장 리포트] 역대 최대 규모의 산불이 산맥 전체를 휩쓸어 수천 명의 주민이 집을 잃고 떠돌고 있습니다. 정부는 당장 생계가 막막한 이재민들에게 전액 현금 보상을 할지, 아니면 무너진 산림을 복구하고 최첨단 방재 시설을 짓는 데 집중할지 정해야 합니다. \n\n이재민의 눈물을 닦아주는 즉각적인 구제입니까, 미래의 재난을 막는 장기적인 안전입니까?", 
        "choices": {"A": "💸 고통받는 이재민에게 즉각적인 전액 현금 보상을 실시하자!", "B": "🏗️ 다시는 이런 일이 없도록 산림 복구와 방재 시설에 투자하자!"}, 
        "eff": {"A": {"국민행복": 18, "환경지속성": -18}, "B": {"환경지속성": 18, "국민행복": -18}}
    },
    {
        "title": "📍 상황 18. 노키즈존 규제 법안 논란", 
        "desc": "[시민 광장] 식당과 카페에서 아이들의 출입을 금지하는 '노키즈존'이 확산되며 차별 논란이 뜨겁습니다. 국가가 법으로 이를 전면 금지하여 누구나 평등하게 시설을 이용하게 할까요, 아니면 조용히 쉴 권리를 원하는 손님과 업주의 영업권을 존중해야 할까요? \n\n시민사회의 갈등이 정점에 달했습니다. 마지막 결정을 내려주십시오.", 
        "choices": {"A": "📜 차별 없는 공동체를 위해 법으로 노키즈존을 금지하자!", "B": "🏢 영업의 자율성과 조용히 쉴 권리를 존중하여 자율에 맡기자!"}, 
        "eff": {"A": {"사회통합": 20, "개인의 자유": -20}, "B": {"개인의 자유": 20, "사회통합": -20}}
    }
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