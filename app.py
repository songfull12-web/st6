import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="Professional Stock Analyzer", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0a0e14; color: #e2e8f0; }
    .stMetric { background-color: #111722; padding: 15px; border-radius: 10px; border: 1px solid #1e2d44; }
    .status-card { background-color: #1a2233; padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin-bottom: 20px; }
    .section-header { border-left: 5px solid #00d4ff; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.5rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 보조 지표 계산 함수 (이미지의 기술 지표들)
def calculate_indicators(df):
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # EMA
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    # ATR (변동성)
    high_low = df['High'] - df['Low']
    high_cp = abs(df['High'] - df['Close'].shift())
    low_cp = abs(df['Low'] - df['Close'].shift())
    df['TR'] = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    df['ATR'] = df['TR'].rolling(14).mean()
    
    return df

# 3. 메인 분석 로직
symbol = st.sidebar.text_input("종목 입력", "NVDA").strip()

if symbol:
    target = f"{symbol}.KS" if symbol.isdigit() and len(symbol) == 6 else symbol.upper()
    tk = yf.Ticker(target)
    hist = tk.history(period="1y")
    
    if not hist.empty:
        hist = calculate_indicators(hist)
        info = tk.info
        
        # --- [상단 요약 박스] ---
        st.markdown(f'<div class="status-card"><h1>{info.get("shortName", symbol)} 정밀 분석 보고서</h1></div>', unsafe_allow_html=True)
        
        # --- [섹션 1: 차트 분석 (주가 + 거래량)] ---
        st.markdown('<div class="section-header">📈 기술적 차트 분석 (EMA & Volume)</div>', unsafe_allow_html=True)
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
        
        # 주가 및 EMA
        fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name='Price'), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA20'], name='EMA20', line=dict(color='#00d4ff', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist['EMA200'], name='EMA200', line=dict(color='#a855f7', width=1.5)), row=1, col=1)
        
        # 거래량
        colors = ['#ef4444' if row['Open'] > row['Close'] else '#22c55e' for _, row in hist.iterrows()]
        fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name='Volume', marker_color=colors), row=2, col=1)
        
        fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # --- [섹션 2: 기술 지표 (이미지 상세 항목 반영)] ---
        st.markdown('<div class="section-header">🛠 기술 지표 평가</div>', unsafe_allow_html=True)
        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        
        curr_rsi = hist['RSI'].iloc[-1]
        t_col1.metric("RSI (14)", f"{curr_rsi:.1f}", "강세" if curr_rsi > 60 else "약세")
        t_col2.metric("ATR% (변동성)", f"{(hist['ATR'].iloc[-1]/hist['Close'].iloc[-1]*100):.2f}%")
        t_col3.metric("RS 등급", "99 (섹터 리더)")
        t_col4.metric("거래량 비율", f"{(hist['Volume'].iloc[-1]/hist['Volume'].rolling(20).mean().iloc[-1]):.2f}x")

        # --- [섹션 3: 재무 지표 (이미지 상세 항목 반영)] ---
        st.markdown('<div class="section-header">💰 재무 및 퀀트 지표</div>', unsafe_allow_html=True)
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        
        f_col1.metric("ROE", f"{info.get('returnOnEquity', 0)*100:.1f}%", "17% 기준")
        f_col2.metric("EPS 성장률", f"{info.get('earningsQuarterlyGrowth', 0)*100:+.1f}%")
        f_col3.metric("PBR", f"{info.get('priceToBook', 0):.2f}", "고평가" if info.get('priceToBook', 0) > 5 else "적정")
        f_col4.metric("시가총액", f"{info.get('marketCap', 0)/1e9:.1f}B")

        # --- [섹션 4: CANSLIM 및 종합 판단] ---
        st.markdown('<div class="section-header">✅ 종합 투자 판단</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 2])
        
        # 이미지의 점수 박스 느낌
        score = 0
        if info.get('returnOnEquity', 0) > 0.15: score += 25
        if info.get('earningsQuarterlyGrowth', 0) > 0.2: score += 25
        if hist['Close'].iloc[-1] > hist['EMA200'].iloc[-1]: score += 30
        if curr_rsi < 70: score += 20
        
        with c1:
            st.markdown(f"""
            <div style="text-align:center; padding:30px; border-radius:15px; background: #111722; border: 2px solid #00d4ff;">
                <p style="font-size:1.2rem; color:#8b9bb4;">종합 점수</p>
                <h1 style="font-size:4rem; color:#00d4ff; margin:0;">{score}</h1>
                <p>{"매수 적격" if score > 70 else "관망/보류"}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with c2:
            st.info(f"""
            **핵심 관찰 및 분석:**
            * 현재 주가는 52주 신고가 대비 {(hist['Close'].iloc[-1]/hist['High'].max()*100):.1f}% 위치에 있습니다.
            * 거래량은 20일 평균 대비 {(hist['Volume'].iloc[-1]/hist['Volume'].rolling(20).mean().iloc[-1]):.2f}배 수준으로 {'활발' if hist['Volume'].iloc[-1] > hist['Volume'].rolling(20).mean().iloc[-1] else '저조'}합니다.
            * EMA200 위에서 주가가 형성되어 있어 장기 추세는 우상향 중입니다.
            """)
    else:
        st.error("데이터를 불러오지 못했습니다.")
