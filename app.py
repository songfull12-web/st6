import streamlit as st
import pandas as pd

# 1. 페이지 설정 (넓은 화면 모드)
st.set_page_config(page_title="Personal Stock Analyzer", layout="wide")

# 2. 고퀄리티 디자인을 위한 커스텀 CSS (이미지 느낌 재현)
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: white; }
    .stMetric { background-color: #1e293b; padding: 20px; border-radius: 15px; border: 1px solid #334155; }
    [data-testid="stMetricValue"] { color: #facc15 !important; font-weight: 800; }
    .card { background-color: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; height: 100%; }
    .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
    .positive { background-color: #065f46; color: #34d399; }
    .negative { background-color: #7f1d1d; color: #f87171; }
    </style>
    """, unsafe_allow_html=True)

# 3. 사이드바 - 파일 업로드 및 보안
with st.sidebar:
    st.title("🔒 Private Access")
    uploaded_file = st.file_uploader("분석 엑셀 업로드", type=['xlsx', 'csv'])
    st.info("GitHub 저장소가 Private이면 이 화면은 본인만 볼 수 있습니다.")

# 4. 메인 대시보드 상단 (종목명 및 요약)
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    st.title("🛰️ Satellogic Inc. (SATL)")
    st.caption("Last Updated: 2026-05-18 | 분석 기준: 퀀트 및 CAN SLIM 전략")

    # 요약 지표 (이미지 상단 3개 지표)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("종합 점수", "53점", "상위 12%")
    with col2:
        st.metric("Conviction", "관망/보류", "Hold")
    with col3:
        st.metric("현재가", "$ 9.84", "+13.89%")
    with col4:
        st.metric("RS 등급", "99", "신고가 근접")

    st.divider()

    # 5. CAN SLIM 분석 섹션 (이미지의 격자형 레이아웃)
    st.subheader("📊 CAN SLIM 체크리스트")
    c_cols = st.columns(4)
    can_slim_data = [
        ("C", "Current Earnings", "15.0", "양호"),
        ("A", "Annual Earnings", "12.0", "주의"),
        ("N", "New Product/High", "96.0", "최상"),
        ("S", "Supply/Demand", "82.4", "양호"),
    ]
    
    for i, (char, title, val, status) in enumerate(can_slim_data):
        with c_cols[i % 4]:
            st.markdown(f"""
                <div class="card">
                    <h3 style="color:#60a5fa">{char}</h3>
                    <p style="font-size:12px; color:#94a3b8">{title}</p>
                    <p style="font-size:24px; font-weight:bold">{val}</p>
                    <span class="status-badge {'positive' if status=='양호' or status=='최상' else 'negative'}">{status}</span>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # 6. 기술적/재무 상세 지표 테이블
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("🛠️ 기술적 지표 (Technical)")
        st.table(df[['국문', '영문', '수치', '상태']].iloc[:5]) # 예시 데이터 5개
    with col_right:
        st.subheader("💎 재무 지표 (Fundamental)")
        st.table(df[['국문', '영문', '수치', '상태']].iloc[5:10])

else:
    st.warning("👈 사이드바에서 분석된 엑셀 파일을 업로드해주세요.")
    # 샘플 데이터 형식 안내
    st.info("엑셀 필수 컬럼: [국문, 영문, 수치, 상태]")
