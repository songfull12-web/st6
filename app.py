import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="Pro Quant Analyzer", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0a0e14; color: #e2e8f0; }
    .stMetric { background-color: #111722; padding: 15px; border-radius: 10px; border: 1px solid #1e2d44; }
    .info-card { background-color: #161b22; padding: 20px; border-radius: 15px; border: 1px solid #30363d; margin-bottom: 20px; }
    .buy-signal { color: #22c55e; font-weight: bold; font-size: 20px; }
    .sell-signal { color: #ef4444; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 호출 함수
def get_analysis_data(symbol):
    target = f"{symbol}.KS" if symbol.isdigit() and len(symbol) == 6 else symbol.upper()
    tk = yf.Ticker(target)
    hist = tk.history(period="1y")
    if hist.empty and ".KS" in target:
        target = target.replace(".KS", ".KQ")
        tk = yf.Ticker(target)
        hist = tk.history(period="1y")
    return tk, tk.info, hist

# 3. 사이드바 - 설정
st.sidebar.title("🛠 분석 설정")
symbol = st.sidebar.text_input("종목 코드", "NVDA").strip()

if symbol:
    tk, info, hist = get_analysis_data(symbol)
    if not hist.empty:
        price = hist['Close'].iloc[-1]
        
        # --- 계산 로직 추가 ---
        # ATR 기반 손절가 (대략적 변동성 계산)
        atr = (hist['High'] - hist['Low']).rolling(14).mean().iloc[-1]
        stop_loss = price - (atr * 2)
        target_price = price + (atr * 4)
        
        # RSI 계산
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        # --- 메인 화면 ---
        st.title(f"🚀 {info.get('shortName', symbol)} 정밀 진단")
        
        # 상단 요약 섹션 (이미지의 '진입 타이밍' 느낌)
        col_sum1, col_sum2, col_sum3 = st.columns(3)
        with col_sum1:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.write("🎯 **권장 가이드라인**")
            if rsi > 70: st.markdown("<span class='sell-signal'>⚠️ 과매수 구간 (관망)</span>", unsafe_allow_html=True)
            elif rsi < 30: st.markdown("<span class='buy-signal'>✅ 과매도 구간 (분할매수)</span>", unsafe_allow_html=True)
            else: st.markdown("<span style='color:#eab308; font-weight:bold;'>⚖️ 추세 지속 중</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_sum2:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.write("💰 **목표가 / 손절가**")
            st.write(f"1차 익절: <span style='color:#22c55e'>{target_price:,.2f}</span>", unsafe_allow_html=True)
            st.write(f"강제 손절: <span style='color:#ef4444'>{stop_loss:,.2f}</span>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_sum3:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.write("📊 **기술적 확신도**")
            score = 0
            if price > hist['Close'].rolling(200).mean().iloc[-1]: score += 40
            if rsi < 60: score += 30
            if info.get('earningsQuarterlyGrowth', 0) > 0.2: score += 30
            st.write(f"종합 점수: **{score}점**")
            st.markdown('</div>', unsafe_allow_html=True)

        # 차트 섹션
        st.subheader("📈 주가 및 기술적 지표")
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Price'))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(50).mean(), name='50 MA', line=dict(color='yellow', width=1)))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'].rolling(200).mean(), name='200 MA', line=dict(color='purple', width=1)))
        fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # 재무 섹션 (이미지 하단 느낌)
        st.subheader("📋 핵심 재무/성장 지표")
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        f_col1.metric("EPS 성장률", f"{info.get('earningsQuarterlyGrowth', 0)*100:+.1f}%")
        f_col2.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.1f}%")
        f_col3.metric("매출 성장률", f"{info.get('revenueGrowth', 0)*100:+.1f}%")
        f_col4.metric("시가총액", f"{info.get('marketCap', 0)/1e12:.1f}T")

    else:
        st.error("데이터를 찾을 수 없습니다.")
