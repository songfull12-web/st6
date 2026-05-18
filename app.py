import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. 이전의 세련된 다크 테마 디자인 그대로 적용
st.set_page_config(page_title="Global Quant Scanner", layout="wide")

st.markdown("""
    <style>
    /* 메인 배경 및 글자색 */
    .main { background-color: #0a0e14; color: #e2e8f0; }
    
    /* 메트릭 박스 스타일 (이전 디자인) */
    div[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 700; color: #00d4ff; }
    div[data-testid="stMetricLabel"] { font-size: 1rem !important; color: #8b9bb4; }
    .stMetric { background-color: #111722; padding: 20px; border-radius: 12px; border: 1px solid #1e2d44; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }

    /* 등급 박스 스타일 (이전 디자인) */
    .grade-box { text-align: center; padding: 20px; border-radius: 15px; background: linear-gradient(145deg, #1a2233, #111722); border: 2px solid #00d4ff; box-shadow: 0 0 15px rgba(0, 212, 255, 0.3); }
    .grade-t1 { font-size: 1.2rem; color: #8b9bb4; margin-bottom: 5px; }
    .grade-t2 { font-size: 4rem; font-weight: 900; color: #00d4ff; margin: 0; line-height: 1; }
    .grade-t3 { font-size: 1.1rem; color: #e2e8f0; margin-top: 10px; }
    
    /* 입력창 및 기타 스타일 */
    .stTextInput>div>div>input { background-color: #1a2233; color: #e2e8f0; border: 1px solid #30363d !important; border-radius: 8px; }
    h1, h2, h3 { color: #e2e8f0; font-weight: 700; }
    stMarkdown { color: #8b9bb4; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 글로벌 주도주 정밀 분석기")

# 2. 검색창
symbol = st.text_input("종목 티커 또는 한국 코드 입력", "NVDA").strip()

def get_data(ticker_str):
    if ticker_str.isdigit() and len(ticker_str) == 6:
        ticker_str = f"{ticker_str}.KS"
    ticker = yf.Ticker(ticker_str)
    
    info = ticker.info
    # 데이터 미검색 시 코스닥 재시도
    if 'regularMarketPrice' not in info and ticker_str.endswith('.KS'):
        ticker_str = ticker_str.replace('.KS', '.KQ')
        ticker = yf.Ticker(ticker_str)
        info = ticker.info
        
    hist = ticker.history(period="1y")
    return ticker, info, hist

if symbol:
    with st.spinner('데이터를 정밀 분석 중...'):
        tk, info, hist = get_data(symbol)
        
        if not hist.empty:
            # --- 이전의 데이터 가공 및 등급 계산 로직 그대로 ---
            price = hist['Close'].iloc[-1]
            eps_g = info.get('earningsQuarterlyGrowth', 0) * 100
            roe = info.get('returnOnEquity', 0) * 100
            
            # RS (Relative Strength) 대략적 계산 (1년 수익률)
            rs_raw = ((price - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
            
            # 신고가 근접도
            high_52w = hist['High'].max()
            near_high = (price / high_52w) * 100
            
            # 이전 점수 계산 로직
            score = round((min(eps_g, 40)*0.7) + (min(roe, 25)*0.8) + (min(rs_raw, 40)*0.7) + (near_high*0.2), 1)
            
            # 등급 결정
            if score >= 85: grade = "S"; desc = "슈퍼 주도주 후보"
            elif score >= 70: grade = "A"; desc = "강력한 성장주"
            elif score >= 55: grade = "B"; desc = "관심 종목"
            else: grade = "C"; desc = "추세 관망 필요"

            # 3. 레이아웃 배치 시작 (이전 스타일 유지)
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"{info.get('shortName', symbol)}")
                st.write(f"현재가: **{price:,.2f} {info.get('currency', 'USD')}**")
            
            with col2:
                # 이전의 멋진 등급 박스
                st.markdown(f"""
                <div class="grade-box">
                    <p class="grade-t1">CANSLIM 등급</p>
                    <p class="grade-t2">{grade}</p>
                    <p class="grade-t3">{desc} ({score}점)</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()

            # 4. 새로 추가된 차트 섹션 (이동평균선 포함)
            st.subheader("📈 주가 추세 및 이동평균선 (EMA)")
            
            # 지수이동평균선 계산
            hist['EMA20'] = hist['Close'].ewm(span=20, adjust=False).mean()
            hist['EMA50'] = hist['Close'].ewm(span=50, adjust=False).mean()
            hist['EMA200'] = hist['Close'].ewm(span=200, adjust=False).mean()

            # Plotly로 다크 테마 차트 그리기
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='종가', line=dict(color='#e2e8f0', width=2)))
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA20'], name='EMA20 (단기)', line=dict(color='#00d4ff', width=1, dash='dot')))
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA50'], name='EMA50 (중기)', line=dict(color='#eab308', width=1)))
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA200'], name='EMA200 (장기)', line=dict(color='#a855f7', width=1)))
            
            fig.update_layout(
                template="plotly_dark",
                height=500,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="#0a0e14",
                plot_bgcolor="#0a0e14",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#1e2d44')
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()

            # 5. 하단 주요 메트릭 (이전 디자인)
            st.subheader("📊 핵심 퀀트 지표")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("EPS 성장률 (C)", f"{eps_g:+.1f}%")
            m_col2.metric("ROE (A)", f"{roe:.1f}%")
            m_col3.metric("상대강도 (L)", f"{rs_raw:+.1f}")
            m_col4.metric("신고가 근접도", f"{near_high:.1f}%")

        else:
            st.error("종목을 찾을 수 없습니다. 티커나 코드를 다시 확인해 주세요.")
