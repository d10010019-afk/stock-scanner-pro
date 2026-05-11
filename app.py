import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="五星共振系統", layout="wide")
st.title("🌟 五星共振量化選股系統")

symbol = st.sidebar.text_input("代碼 (例: 2330.TW)", "2330.TW")

@st.cache_data
def get_data(ticker):
    df = yf.download(ticker, period="6m", interval="1d")
    # 手動計算指標，不依賴外掛套件
    df['MA5'] = df['Close'].rolling(window=5).mean()
    # RSI 計算
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    # MACD 計算
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = exp1 - exp2
    df['MACD_Line'] = df['DIF'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['DIF'] - df['MACD_Line']
    return df

try:
    df = get_data(symbol)
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    score = 0
    results = []
    
    # 1. K線與5日線
    if last['Close'] > last['MA5']:
        score += 1
        results.append("✅ 股價在5日線上")
    
    # 2. MACD 動能
    if last['MACD_Hist'] > 0 and last['MACD_Hist'] > prev['MACD_Hist']:
        score += 1
        results.append("✅ MACD 紅柱增長")
    
    # 3. RSI 區間
    if 40 < last['RSI'] < 75:
        score += 1
        results.append(f"✅ RSI 分數 {last['RSI']:.1f}")
    
    # 4. 當日收紅
    if last['Close'] > last['Open']:
        score += 1
        results.append("✅ 當日量能收紅")
        
    # 5. 量能爆發
    if last['Volume'] > df['Volume'].tail(5).mean():
        score += 1
        results.append("✅ 量能超過均量")

    st.header(f"量化評分：{score} / 5")
    for res in results: st.write(res)
    
    # 繪圖
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1)
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='K線'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], line=dict(color='orange'), name='5日線'), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], name='MACD'), row=2, col=1)
    fig.update_layout(height=600, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

except:
    st.error("代碼錯誤或資料抓取失敗")
  
