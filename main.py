import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Wilfer Trading Suite Pro", layout="wide", page_icon="⚙️")

st.markdown("""
    <style>
    .stMetric { background-color: #1e222d; padding: 10px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# Layout de 2 columnas principales
col_izq, col_der = st.columns([1, 2])

with col_izq:
    st.subheader("⚙️ Gestión de Capital y Riesgo")
    
    capital = st.number_input("Capital Total de la Cuenta ($)", value=10000.0, step=500.0)
    riesgo_pct = st.slider("Riesgo por Operación (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    
    riesgo_dinero = capital * (riesgo_pct / 100.0)
    
    st.markdown("##### Riesgo Máximo en Dinero")
    st.title(f"${riesgo_dinero:,.2f} USD")
    
    st.divider()
    
    st.subheader("🌐 Selección de Activo y Mercado")
    simbolo = st.text_input("Símbolo del Activo (Ej: BTCUSD, XAUUSD, EURUSD)", value="BTCUSD").upper().strip()

with col_der:
    st.subheader("📈 Gráfico en Vivo")
    
    # Formateo correcto de la variable para TradingView
    if simbolo in ["BTCUSD", "ETHUSD"]:
        ticker_tv = f"BINANCE:{simbolo}T"
    else:
        ticker_tv = f"FOREXCOM:{simbolo}"

    tv_widget = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:600px;width:100%">
      <div id="tradingview_chart" style="height:600px;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{ticker_tv}",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "es",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    components.html(tv_widget, height=620)
