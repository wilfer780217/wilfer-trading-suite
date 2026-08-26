import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Wilfer Trading Suite Pro", layout="wide", page_icon="⚡")

if "bitacora" not in st.session_state:
    st.session_state.bitacora = []

class WilferTradingEngineTotal:
    def __init__(self, capital_inicial=1000.0):
        self.capital_inicial = capital_inicial
        self.config_mercados = {
            "BTCUSD": {"sma": 50, "atr_p": 14, "sl_mult": 3.0, "rr": 2.5, "riesgo_pct": 0.02},
            "ETHUSD": {"sma": 50, "atr_p": 14, "sl_mult": 2.5, "rr": 2.5, "riesgo_pct": 0.02},
            "EURUSD": {"sma": 50, "atr_p": 14, "sl_mult": 2.0, "rr": 2.0, "riesgo_pct": 0.015}
        }

    def calcular_mercado(self, nombre_activo, df):
        cfg = self.config_mercados[nombre_activo]
        df['sma'] = df['close'].rolling(window=cfg["sma"]).mean()
        hl = df['high'] - df['low']
        hc = np.abs(df['high'] - df['close'].shift())
        lc = np.abs(df['low'] - df['close'].shift())
        df['atr'] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(window=cfg["atr_p"]).mean()
        df['swing_high'] = df['high'].rolling(window=20, min_periods=1).max()
        df['swing_low'] = df['low'].rolling(window=20, min_periods=1).min()
        rango_fib = df['swing_high'] - df['swing_low']
        df['fib_500'] = df['swing_high'] - (rango_fib * 0.500)
        df['fib_618'] = df['swing_high'] - (rango_fib * 0.618)
        return df

st.title("⚡ WILFER TRADING SUITE - TOTAL PRO")

# 1. Selector de Activo General para todo
activo_sel = st.selectbox("🌐 Seleccionar Activo a Operar", ["BTCUSD", "ETHUSD", "EURUSD"])

st.sidebar.header("⚙️ Configuración Cuenta")
capital = st.sidebar.number_input("Capital Inicial ($)", value=10000.0, step=500.0)

# Simulación de datos
np.random.seed(999)
n = 150
p_btc = 64000 + np.cumsum(np.random.randn(n) * 150)
df_btc = pd.DataFrame({'open': p_btc, 'high': p_btc + 200, 'low': p_btc - 200, 'close': p_btc + np.random.randn(n)*50})
p_eth = 3100 + np.cumsum(np.random.randn(n) * 25)
df_eth = pd.DataFrame({'open': p_eth, 'high': p_eth + 40, 'low': p_eth - 40, 'close': p_eth + np.random.randn(n)*10})
p_eur = 1.0850 + np.cumsum(np.random.randn(n) * 0.0008)
df_eur = pd.DataFrame({'open': p_eur, 'high': p_eur + 0.002, 'low': p_eur - 0.002, 'close': p_eur + np.random.randn(n)*0.0005})

mercados_activos = {"BTCUSD": df_btc, "ETHUSD": df_eth, "EURUSD": df_eur}
motor = WilferTradingEngineTotal(capital_inicial=capital)

df = mercados_activos[activo_sel]
df_calc = motor.calcular_mercado(activo_sel, df)
idx = len(df_calc) - 1
precio = df_calc['close'].iloc[idx]
f500 = df_calc['fib_500'].iloc[idx]
f618 = df_calc['fib_618'].iloc[idx]
sma = df_calc['sma'].iloc[idx]
atr = df_calc['atr'].iloc[idx]
cfg = motor.config_mercados[activo_sel]
en_zona = (precio <= f500) and (precio >= f618)
es_alcista = precio > sma

st.divider()
st.subheader(f"📊 Análisis Técnico: {activo_sel}")

c1, c2 = st.columns(2)
c1.metric("Precio Actual", f"{precio:.5f}")
c2.metric(f"Tendencia (SMA {cfg['sma']})", f"{sma:.5f}")

c3, c4 = st.columns(2)
c3.metric("Volatilidad (ATR)", f"{atr:.5f}")
c4.metric("Rango Fib (61.8% - 50%)", f"[{f618:.4f} - {f500:.4f}]")

if en_zona:
    tipo = "LONG (COMPRA)" if es_alcista else "SHORT (VENTA)"
    if es_alcista:
        sl = precio - (atr * cfg["sl_mult"])
        riesgo_u = precio - sl
        tp = precio + (riesgo_u * cfg["rr"])
    else:
        sl = precio + (atr * cfg["sl_mult"])
        riesgo_u = sl - precio
        tp = precio - (riesgo_u * cfg["rr"])
    
    riesgo_dinero = motor.capital_inicial * cfg["riesgo_pct"]
    ganancia_esp = riesgo_dinero * cfg["rr"]
    
    st.success(f"🚨 ¡SEÑAL CONFIRMADA: {tipo}!")
    
    m1, m2 = st.columns(2)
    m1.metric("Entrada Exacta", f"{precio:.5f}")
    m1.metric("Stop Loss (SL)", f"{sl:.5f}")
    m2.metric("Take Profit (TP)", f"{tp:.5f}")
    m2.metric("Ganancia Est.", f"${ganancia_esp:,.2f}")

    if st.button("💾 Guardar en Bitácora", use_container_width=True):
        st.session_state.bitacora.append({
            "Activo": activo_sel, "Tipo": tipo, "Entrada": f"{precio:.5f}", 
            "SL": f"{sl:.5f}", "TP": f"{tp:.5f}", "Ganancia": f"${ganancia_esp:.2f}"
        })
        st.success("¡Guardado en la bitácora!")

    msg = f"🚨 SEÑAL WILFER TRADING 🚨\nActivo: {activo_sel}\nTipo: {tipo}\nEntrada: {precio:.5f}\nSL: {sl:.5f}\nTP: {tp:.5f}\nGanancia Est: ${ganancia_esp:.2f}"
    enc = urllib.parse.quote(msg)
    
    col_w, col_t = st.columns(2)
    with col_w:
        st.markdown(f'<a href="https://api.whatsapp.com/send?text={enc}" target="_blank"><button style="width:100%;background:#25D366;color:white;border:none;padding:12px;border-radius:6px;font-weight:bold;cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)
    with col_t:
        st.markdown(f'<a href="https://t.me/share/url?url=&text={enc}" target="_blank"><button style="width:100%;background:#0088cc;color:white;border:none;padding:12px;border-radius:6px;font-weight:bold;cursor:pointer;">✈️ Telegram</button></a>', unsafe_allow_html=True)
else:
    st.info("⏳ [ESTADO]: Fuera de zona áurea. Esperando retroceso matemático...")

st.divider()

# 2. Gráfico TradingView visible de inmediato abajo
st.subheader(f"📈 Gráfico Profesional: {activo_sel}")
ticker = f"BINANCE:{activo_sel}T" if activo_sel in ["BTCUSD", "ETHUSD"] else f"FOREXCOM:{activo_sel}"

widget_tv = f"""
<div style="height:500px;width:100%">
  <div id="tv_chart" style="height:500px;width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "autosize": true, "symbol": "{ticker}", "interval": "D",
    "timezone": "Etc/UTC", "theme": "dark", "style": "1",
    "locale": "es", "toolbar_bg": "#f1f3f6", "container_id": "tv_chart"
  }});
  </script>
</div>
"""
components.html(widget_tv, height=510)

st.divider()

# 3. Bitácora visible abajo del todo
st.subheader("📖 Bitácora de Operaciones Guardadas")
if st.session_state.bitacora:
    st.dataframe(pd.DataFrame(st.session_state.bitacora), use_container_width=True)
    if st.button("🗑️ Limpiar Bitácora"):
        st.session_state.bitacora = []
        st.rerun()
else:
    st.info("La bitácora está vacía por ahora.")
