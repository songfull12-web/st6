import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 디자인 설정
st.set_page_config(page_title="Global CANSLIM Scanner", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0a0e14; color: #e2e8f0; }
    .stMetric { background-color: #111722; padding: 15px; border-radius: 10px; border: 1px solid #1e2d44; }
    .score-box { text-align:center; padding:15px; border-radius:12px; background-color:#1a2233; border: 1px solid #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 실시간 글로벌 주식 분석기")
st.write("엑셀 업로드 없이, 티커나 종목번호만 입력하면 즉시 분석합니다.")

# 2. 검색창 (여기에서 검색하면 바로 나옵니다)
search_input = st.text_input("종목 검색 (예: NVDA, 005930)", "NVDA").strip()

def get_analysis(symbol):
    if symbol.isdigit() and len(symbol) == 6:
        target = f"{symbol}.KS"
    else:
        target = symbol.upper()
    
    try:
        ticker = yf.Ticker(target)
        info = ticker.info
        if not info or 'regularMarketPrice' not in info:
            if target.endswith('.KS'):
                target = target.replace('.KS', '.KQ')
                ticker = yf.Ticker(target)
                info = ticker.info
        
        hist = ticker.history(period="1y")
        if hist.empty: return None

        # 주요 지표 추출
        price = info.get('regularMarketPrice', hist['Close'].iloc[-1])
        eps_g = info.get('earningsQuarterlyGrowth', 0) * 100
        roe = info.get('returnOnEquity', 0) * 100
        rs = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
        high_52w = hist['High'].max()
        near_high = (price / high_52w) * 100
        
        # 점수 계산 (100점 만점)
        score = round((min(eps_g, 30)*0.8) + (min(roe, 20)*0.8) + (min(rs, 30)*0.8) + (near_high*0.2), 1)

        return {"name": info.get('shortName', target), "price": price, "score": score, "eps": eps_g, "roe": roe, "rs": rs, "high": near_high}
    except: return None

# 3. 결과 표시
if search_input:
    with st.spinner('데이터를 가져오는 중...'):
        d = get_analysis(search_input)
        if d:
            c1, c2 = st.columns([2, 1])
            with c1:
                st.subheader(f"{d['name']} 분석 결과")
                st.metric("현재가", f"{d['price']:,.2f}")
            with c2:
                st.markdown(f"<div class='score-box'><h3>최종 점수</h3><h1>{d['score']}</h1></div>", unsafe_allow_html=True)
            
            st.divider()
            cols = st.columns(4)
            cols[0].metric("EPS 성장률", f"{d['eps']:.1f}%")
            cols[1].metric("ROE", f"{d['roe']:.1f}%")
            cols[2].metric("RS Score", f"{d['rs']:.1f}")
            cols[3].metric("신고가 근접도", f"{d['high']:.1f}%")
        else:
            st.error("종목을 찾을 수 없습니다.")
