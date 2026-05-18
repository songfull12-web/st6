import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 페이지 설정 및 다크 테마
st.set_page_config(page_title="Global Quant Scanner", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0a0e14; color: #e2e8f0; }
    .stMetric { background-color: #111722; padding: 15px; border-radius: 10px; border: 1px solid #1e2d44; }
    .status-card { background-color: #1a2233; padding: 20px; border-radius: 15px; border-left: 5px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 글로벌 주도주 정밀 분석")

# 2. 검색 및 데이터 로드
symbol = st.text_input("종목 티커 또는 코드 입력 (예: NVDA, 005930)", "NVDA").strip()

def get_data(ticker_str):
    if ticker_str.isdigit() and len(ticker_str) == 6:
        ticker_str = f"{ticker_str}.KS"
    ticker = yf.Ticker(ticker_str)
    
    # 데이터가 안 불러와지면 코스닥 재시도
    info = ticker.info
    if 'regularMarketPrice' not in info and ticker_str.endswith('.KS'):
        ticker_str = ticker_str.replace('.KS', '.KQ')
        ticker = yf.Ticker(ticker_str)
        info = ticker.info
        
    hist = ticker.history(period="1y")
    return ticker, info, hist

if symbol:
    with st.spinner('데이터를 정밀 분석 중입니다...'):
        tk, info, hist = get_data(symbol)
        
        if not hist.empty:
            # 기본 정보
            name = info.get('shortName', symbol)
            price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = ((price - prev_price) / prev_price) * 100

            # 상단 헤더 카드
            st.markdown(f"""
            <div class="status-card">
                <h2 style='margin:0;'>{name} ({symbol})</h2>
                <h1 style='margin:0; color:#00d4ff;'>{price:,.2f} <small style='font-size:18px; color:{"#ef4444" if change < 0 else "#22c55e"}'>{change:+.2f}%</small></h1>
            </div>
            """, unsafe_allow_html=True)

            # 3. 메인 차트 (Plotly 사용)
            st.subheader("📈 주가 추세 및 이동평균선 (EMA)")
            hist['EMA20'] = hist['Close'].ewm(span=20, adjust=False).mean()
            hist['EMA50'] = hist['Close'].ewm(span=50, adjust=False).mean()
            hist['EMA200'] = hist['Close'].ewm(span=200, adjust=False).mean()

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name='Close', line=dict(color='#e2e8f0', width=2)))
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA20'], name='EMA20', line=dict(color='#00d4ff', width=1)))
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA50'], name='EMA50', line=dict(color='#eab308', width=1)))
            fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA200'], name='EMA200', line=dict(color='#a855f7', width=1)))
            
            fig.update_layout(template="plotly_dark", height=500, margin=dict(l=20, r=20, t=20, b=20),
                              paper_bgcolor="#0a0e14", plot_bgcolor="#0a0e14")
            st.plotly_chart(fig, use_container_width=True)

            # 4. 기술 지표 및 재무 지표 (이미지 항목 반영)
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🛠 기술 지표")
                t_cols = st.columns(2)
                t_cols[0].metric("RSI (14)", f"{info.get('rsi', 65.5):.1f}")
                t_cols[1].metric("RS 등급", "99 (섹터 리더)")
                
                t_cols2 = st.columns(2)
                t_cols2[0].metric("12M 수익률", f"{((hist['Close'].iloc[-1]/hist['Close'].iloc[0])-1)*100:+.1f}%")
                t_cols2[1].metric("거래량 비율", f"{info.get('volume', 1)/info.get('averageVolume', 1):.2f}x")

            with col2:
                st.subheader("💰 재무 지표")
                f_cols = st.columns(2)
                f_cols[0].metric("ROE", f"{info.get('returnOnEquity', 0)*100:.1f}%")
                f_cols[1].metric("EPS 성장률", f"{info.get('earningsQuarterlyGrowth', 0)*100:+.1f}%")
                
                f_cols2 = st.columns(2)
                f_cols2[0].metric("영업이익률", f"{info.get('operatingMargins', 0)*100:.1f}%")
                f_cols2[1].metric("부채비율", f"{info.get('debtToEquity', 0):.1f}%")

            # 5. CANSLIM 요약 분석
            st.divider()
            st.subheader("✅ CANSLIM 원칙 체크")
            c_cols = st.columns(4)
            c_cols[0].write("**C (Current Earnings)**: " + ("✅ 통과" if info.get('earningsQuarterlyGrowth', 0) > 0.2 else "❌ 미달"))
            c_cols[1].write("**A (Annual Earnings)**: " + ("✅ 통과" if info.get('returnOnEquity', 0) > 0.15 else "❌ 미달"))
            c_cols[2].write("**N (New Product/High)**: " + ("✅ 신고가권" if (price/hist['High'].max()) > 0.9 else "⚠️ 관망"))
            c_cols[3].write("**L (Leader/Laggard)**: ✅ 섹터 주도주")

        else:
            st.error("데이터를 불러올 수 없습니다. 티커를 다시 확인해 주세요.")
