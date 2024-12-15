import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import json
from bs4 import BeautifulSoup
import streamlit as st
from streamlit_lottie import st_lottie
def fetch_trending_stocks_html():
    """ Fetch raw HTML data of trending stocks from Yahoo Finance."""
    url = "https://finance.yahoo.com/markets/stocks/trending/"
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch data. HTTP Status: {response.status_code}")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup
def extract_trending_stock_data(soup):
    """Extract the stock name, price, change percentage, and market time from the JSON data inside the <script> tag."""
    stocks_data = []
    script_tag = soup.find('script',{'id':'fin-trending-tickers'})
    if not script_tag:
        st.warning("Could not find the <script> tag with the stock data.")
        return None
    json_data = script_tag.string.strip()
    try:
        data = json.loads(json_data)
    except json.JSONDecodeError:
        st.error("Failed to parse JSON data.")
        return None


    
    for stock in data:
        stock_name =stock.get('longName','N/A')  
        stock_symbol =stock.get('symbol', 'N/A')  
        stock_price = stock.get('regularMarketPrice',{}).get('fmt','N/A')
        change_percentage= stock.get('regularMarketChangePercent',{}).get('fmt','N/A') 
        market_time=stock.get('regularMarketTime',{}).get('fmt', 'N/A') 
        stocks_data.append({
            'name':stock_name,
            'symbol': stock_symbol,
            'price':stock_price,
            'change_percentage':change_percentage,
            'market_time': market_time
        })
    return stocks_data



def load_lottie_url(url):
    """
    Load a Lottie animation from a URL.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_random_dark_gradient():
    """Generate a random dark gradient background for each card. """
    gradients = [
        "linear-gradient(135deg,#2c3e50,#34495e)",  
        "linear-gradient(135deg, #1a1a2e, #16213e)",  
        "linear-gradient(135deg,#4b4b4b,   #1c1c1c)", 
        "linear-gradient(135deg,#2d3436,#1c2833)",  
        "linear-gradient(135deg,#28313b,#485461)" 
    ]
    return gradients[hash(str(gradients)) % len(gradients)] 
def display_stocks_in_grid(stocks):
    """Display stocks data in a grid format with styled cards.
    """
    rows =[stocks[i:i+5] for i in range(0,len(stocks),5)]
    for row in rows:
        cols = st.columns(len(row))
        for col,stock in zip(cols,row):
            with col:
                gradient=get_random_dark_gradient() 
                stock_url= f"https://finance.yahoo.com/quote/{stock['symbol']}"
                st.markdown(f"""
                    <a href="{stock_url}" target="_blank" style="text-decoration: none;">
                    <div style="width: 100%; height: 300px; border: 1px solid #ddd; border-radius: 15px; padding: 20px; text-align: center; background: {gradient}; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.3); display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 30px;">
                            <h4 style="color: #fff; font-weight: bold;">{stock['name']} ({stock['symbol']})</h4>
                            <p style="font-size: 18px; color: #4caf50;"><strong>Price:</strong> {stock['price']}</p>
                            <p style="font-size: 16px; color: {('#d32f2f' if '-' in stock['change_percentage'] else '#388e3c')};"><strong>Change:</strong> {stock['change_percentage']}</p>
                            <p style="font-size: 14px; color: #fff;"><strong>Market Time:</strong> {stock['market_time']}</p>
                        </div> </a>""",
                    unsafe_allow_html=True
                )

def plot_enhanced_stock_chart(stock_data, ticker_symbol, time_period):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=stock_data.index,
        open=stock_data['Open'],
        high=stock_data['High'],
        low=stock_data['Low'],
        close=stock_data['Close'],
        name=f'{ticker_symbol} Candlestick'
    ))
    stock_data['50_MA'] =stock_data['Close'].rolling(window=50).mean()
    stock_data['200_MA']= stock_data['Close'].rolling(window=200).mean()
    fig.add_trace(go.Scatter(
        x=stock_data.index,
        y=stock_data['50_MA'],
        mode='lines',
        name=f'50-day MA',
        line=dict(color='blue')
    ))
    fig.add_trace(go.Scatter(
        x=stock_data.index,
        y=stock_data['200_MA'],
        mode='lines',
        name=f'200-day MA',
        line=dict(color='red')
    ))


    
    fig.add_trace(go.Bar(
        x=stock_data.index,
        y=stock_data['Volume'],
        name='Volume',
        marker=dict(color='rgba(0, 0, 255, 0.3)'),
        yaxis='y2'
    ))

    
    fig.update_layout(
        title=f'{ticker_symbol} Stock Price Over {time_period}',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_dark', 
        showlegend=True,
        xaxis_rangeslider_visible=False, 
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right'
        ),
        hovermode='x unified', 
        plot_bgcolor='rgba(0, 0, 0, 0)', 
    )
    st.plotly_chart(fig)
def display_stock_information(ticker_symbol, time_period):
    try:
        stock = yf.Ticker(ticker_symbol)
        st.subheader(f"Basic Stock Information about{ticker_symbol}:")
        st.write(f"**Name**:{stock.info.get('longName','N/A')}")
        st.write(f"**Symbol**:{stock.info.get('symbol','N/A')}")
        st.write(f"**Sector**:    {stock.info.get('sector','N/A')}")
        st.write(f"**Industry**: {stock.info.get('industry',   'N/A')}")
        st.write(f"**Market Cap**:     {stock.info.get('marketCap',   'N/A')}")
        st.write(f"**PE Ratio**:{stock.info.get('trailingPE', 'N/A')}")
        st.write(f"**Dividend Yield**:{stock.info.get('dividendYield','N/A')}")
        st.write(f"**Previous Close**:{stock.info.get('previousClose','N/A')}")
        st.write(f"**Open**:{stock.info.get('open', 'N/A')}")
        st.write(f"**Day's Range**:   {stock.info.get('dayLow',   'N/A')} - {stock.info.get('dayHigh', 'N/A')}")
        st.write(f"**52 Week Range**: {stock.info.get('fiftyTwoWeekLow','N/A')} - {stock.info.get('fiftyTwoWeekHigh', 'N/A')}")
        st.write(f"**Volume**: {stock.info.get('volume','N/A')}")
        st.write(f"**Country**:   {stock.info.get('country','N/A')}")
        st.write(f"**Currency**:{stock.info.get('currency','N/A')}")
        st.write(f"**Website**:{stock.info.get('website','N/A')}")
        logo_url = stock.info.get('logo_url', None)
        if logo_url:
            st.image(logo_url, width=200)
        st.subheader(f"Historical Data ({time_period}):")
        hist = stock.history(period=time_period)
        st.dataframe(hist)
        st.subheader(f"Dividend Data:")        
        dividends = stock.dividends
        if not dividends.empty:
            st.dataframe(dividends)
        else:
            st.write("No dividends data available.")
        st.subheader(f"Corporate Actions (splits, dividends):")
        actions = stock.actions
        if not actions.empty:
            st.dataframe(actions)
        else:
            st.write("No corporate actions data available.")
        st.subheader(f"Balance Sheet:")
        st.write(stock.balance_sheet)
        st.subheader(f"Financials:")
        st.write(stock.financials)
        st.subheader(f"Cashflow Statement:")
        st.write(stock.cashflow)
        time_period = st.selectbox(
            "Select Time Period for Stock Data:",
            ("1day", "1week", "1month", "3month", "6month", "1year"),
            index=2
        )
        plot_enhanced_stock_chart(hist, ticker_symbol, time_period)
    
    except Exception as e:
        st.error(f"Error fetching data for ticker {ticker_symbol}: {e}")
def analyze_stock(ticker_symbol, start_date, end_date):
    # Fetch historical stock data
    stock = yf.Ticker(ticker_symbol)
    data = stock.history(start=start_date, end=end_date)

    if data.empty:
        st.error("No data found for the given stock symbol or date range.")
        return
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'], mode='lines', name='Closing Price', line=dict(color='royalblue', width=2)
    ))
    fig.update_layout(
        title=f'{ticker_symbol} Price Trend from {start_date} to {end_date}',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        legend=dict(x=0, y=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig)
    data['SMA_50'] = data['Close'].rolling(window=50).mean()  
    data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean() 

    # Plot Moving Averages
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'], mode='lines', name='Closing Price', line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=data['SMA_50'], mode='lines', name='50-Day SMA', line=dict(color='tomato', dash='dash', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=data['EMA_50'], mode='lines', name='50-Day EMA', line=dict(color='forestgreen', dash='dot', width=2)
    ))
    fig.update_layout(
        title=f'{ticker_symbol} Price with Moving Averages',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        legend=dict(x=0, y=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig)
    price_diff = data['Close'].pct_change() * 100 
    significant_changes = price_diff[price_diff.abs() > 3]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'], mode='lines', name='Closing Price', line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=significant_changes.index, y=data.loc[significant_changes.index, 'Close'], mode='markers',
        name='Significant Changes (>3%)', marker=dict(color='darkgreen', size=10, symbol='circle')
    ))
    fig.update_layout(
        title=f'{ticker_symbol} Price with Significant Changes',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        legend=dict(x=0, y=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig)

    # Step 6: Calculate and Plot RSI (Relative Strength Index)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    data['RSI'] = rsi

    # Plot RSI
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data['RSI'], mode='lines', name='RSI (14)', line=dict(color='orange', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=np.full_like(data.index, 70), mode='lines', name='Overbought (70)', line=dict(color='red', dash='dash', width=1.5)
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=np.full_like(data.index, 30), mode='lines', name='Oversold (30)', line=dict(color='green', dash='dash', width=1.5)
    ))
    fig.update_layout(
        title=f'{ticker_symbol} RSI (14) Indicator',
        xaxis_title='Date',
        yaxis_title='RSI',
        template='plotly_dark',
        legend=dict(x=0, y=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig)

    # Step 7: Calculate and Plot MACD (Moving Average Convergence Divergence)
    data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

    # Plot MACD and Signal Line
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data['MACD'], mode='lines', name='MACD', line=dict(color='royalblue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=data['MACD_Signal'], mode='lines', name='MACD Signal', line=dict(color='red', dash='dash', width=2)
    ))
    fig.update_layout(
        title=f'{ticker_symbol} MACD and Signal Line',
        xaxis_title='Date',
        yaxis_title='MACD Value',
        template='plotly_dark',
        legend=dict(x=0, y=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig)
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['Std_20'] = data['Close'].rolling(window=20).std()
    data['Upper_Band'] = data['SMA_20'] + (data['Std_20'] * 2)
    data['Lower_Band'] = data['SMA_20'] - (data['Std_20'] * 2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Close'], mode='lines', name='Closing Price', line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Upper_Band'], mode='lines', name='Upper Bollinger Band', line=dict(color='green', dash='dash', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Lower_Band'], mode='lines', name='Lower Bollinger Band', line=dict(color='red', dash='dash', width=2)
    ))
    fig.update_layout(
        title=f'{ticker_symbol} Bollinger Bands',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        legend=dict(x=0, y=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig)

    # Step 9: Cumulative Returns Plot
    data['Daily_Return'] = data['Close'].pct_change()
    data['Cumulative_Returns'] = (1 + data['Daily_Return']).cumprod() - 1

    # Plot Cumulative Returns
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data['Cumulative_Returns'], mode='lines', name='Cumulative Returns', line=dict(color='purple', width=2)
    ))
    fig.update_layout(
        title=f'{ticker_symbol} Cumulative Returns',
        xaxis_title='Date',
        yaxis_title='Cumulative Returns',
        template='plotly_dark',
        legend=dict(x=0, y=1),
        hovermode="x unified"
    )
    st.plotly_chart(fig)
    sp500 = yf.Ticker('^GSPC')
    sp500_data = sp500.history(start=start_date, end=end_date)
    sp500_data['Daily_Return'] = sp500_data['Close'].pct_change()
    correlation = data['Daily_Return'].corr(sp500_data['Daily_Return'])
    st.write(f"\nCorrelation between {ticker_symbol} and S&P 500: {correlation:.4f}")
def main():
    st.set_page_config(page_title="Stock Information Viewer", layout="wide")

    page_bg_img = """
    <style>
    .stApp {
        background-image: url('https://pixabay.com/photos/business-stock-finance-market-1730089/');
        background-size: cover;
    }

    /* CSS animation for the title */
    @keyframes slideIn {
        0% {
            transform: translateX(-100%);
            opacity: 0;
        }
        100% {
            transform: translateX(0);
            opacity: 1;
        }
    }

    h1 {
        animation: slideIn 2s ease-out;
    }
    </style>
    """



    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    st.title("REAL-TIME STOCK TRACKER")
    sidebar_options = ["Trends","Search", "Analysis"]
    sidebar_selection = st.sidebar.radio("Select a Section", sidebar_options)

    lottie_url = "https://assets9.lottiefiles.com/packages/lf20_u4yrau.json" 
    lottie_animation = load_lottie_url(lottie_url)

    if lottie_animation:
        st_lottie(lottie_animation, height=200)

    if sidebar_selection == "Trends":
        st.write("### Trending Stocks")
        st.write("Fetching trending stocks data...")
        soup = fetch_trending_stocks_html()
        if soup:
            trending_stocks = extract_trending_stock_data(soup)

            if trending_stocks:
                display_stocks_in_grid(trending_stocks)
            else:
                st.warning("No trending stocks data found.")
        else:
            st.error("Failed to retrieve data.")
    elif sidebar_selection == "Search":
        st.write("### Stock Search")
        st.write("Enter the stock symbol to search for detailed information.")
        stock_symbol = st.text_input("Stock Symbol", "")
        if stock_symbol:
            st.write(f"Searching for stock: {stock_symbol}")
            display_stock_information(stock_symbol, "1mo")
    elif sidebar_selection == "Analysis":
        st.write("### Stock Analysis")
        st.write("Enter the stock ticker and date range for analysis.")
        ticker_symbol = st.text_input("Enter Stock Symbol", "")
        start_date = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
        end_date = st.date_input("End Date", pd.to_datetime("2024-01-01"))
        if ticker_symbol:
            analyze_stock(ticker_symbol, start_date, end_date)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Contact Me")
    st.sidebar.markdown("**Phone**: +9179886475")
    st.sidebar.markdown("**Gmail**: vedantchhetri64@gmail.com")
if __name__ == "__main__":
    main()
