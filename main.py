import streamlit as st
import streamlit.components.v1 as components
import requests

st.set_page_config(page_title="Wilfer Trading Terminal", layout="wide", page_icon="⚡")

st.title("⚡ WILFER TRADING TERMINAL - ESTACIÓN TÁCTICA")

activo_sel = st.selectbox("Símbolo del Activo", ["BTCUSDT", "ETHUSDT"])

def obtener_precio_binance(symbol):
    try:
        url = f"https://data.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return float(response.json()["price"])
    except:
        pass
    return 0.00

precio_en_vivo = obtener_precio_binance(activo_sel)
st.metric(label=f"Precio Actual en Vivo ({activo_sel})", value=f"${precio_en_vivo:,.2f}")

st.divider()

ticker_tv = f"BINANCE:{activo_sel}"

# Gráfico configurado con indicadores técnicos nativos precargados
widget_tv = f"""
<div style="height:700px;width:100%">
  <div id="tv_chart" style="height:700px;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true,
    "symbol": "{ticker_tv}",
    "interval": "60",
    "timezone": "Etc/UTC",
    "theme": "dark",
    "style": "1",
    "locale": "es",
    "toolbar_bg": "#1e222d",
    "enable_publishing": false,
    "allow_symbol_change": true,
    "container_id": "tv_chart",
    "studies": [
      "BB@tv-basicstudies",
      "MASimple@tv-basicstudies"
    ]
  }});
  </script>
</div>
"""
components.html(widget_tv, height=710)
