import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Wilfer Trading Suite - Total Pro", layout="wide", page_icon="⚡")

if "bitacora" not in st.session_state:
    st.session_state.bitacora = []

class WilferTradingEngineTotal:
    def __init__(self, capital_inicial=10000.0):
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

st.title("⚡ WILFER TRADING SUITE - MOTOR TOTAL PRO")

# --- PANEL DE CONFIGURACIÓN Y SELECCIÓN ---
st.sidebar.header("⚙️ Configuración del Broker")
capital = st.sidebar.number_input("Capital Total de la Cuenta ($)", value=10000.0, step=500.0)
riesgo_usr_pct = st.sidebar.slider("Riesgo por Operación (%)", min_value=0.1, max_value=5.0, value=2.0, step=0.1)

st.subheader("🌐 Selección de Activo y Datos de Mercado")
activo_sel = st.selectbox("Símbolo del Activo", ["BTCUSD", "ETHUSD", "EURUSD"])
tipo_operacion = st.radio("Dirección del Mercado", ["LONG (Compra Alcista)", "SHORT (Venta Bajista)"], horizontal=True)

# Simulación de datos técnicos del broker
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
swing_high = df_calc['swing_high'].iloc[idx]
swing_low = df_calc['swing_low'].iloc[idx]
f500 = df_calc['fib_500'].iloc[idx]
f618 = df_calc['fib_618'].iloc[idx]
sma = df_calc['sma'].iloc[idx]
atr = df_calc['atr'].iloc[idx]
cfg = motor.config_mercados[activo_sel]

en_zona = (precio <= f500) and (precio >= f618)

st.divider()
st.subheader("📊 Panel de Riesgo y Calculadora Fibonacci")

# Cálculos monetarios y de riesgo
riesgo_dinero = capital * (riesgo_usr_pct / 100.0)

if "LONG" in tipo_operacion:
    sl = precio - (atr * cfg["sl_mult"])
    riesgo_unitario = precio - sl
    tp = precio + (riesgo_unitario * cfg["rr"])
else:
    sl = precio + (atr * cfg["sl_mult"])
    riesgo_unitario = sl - precio
    tp = precio - (riesgo_unitario * cfg["rr"])

lote_posicion = riesgo_dinero / riesgo_unitario if riesgo_unitario > 0 else 0.0
ganancia_proyectada = lote_posicion * (tp - precio if "LONG" in tipo_operacion else precio - tp)

# Métricas visuales detalladas
c1, c2 = st.columns(2)
c1.metric("Riesgo Máximo en Dinero", f"${riesgo_dinero:,.2f} USD")
c2.metric("Lote / Tamaño de Posición", f"{lote_posicion:.4f} unidades")

c3, c4 = st.columns(2)
c3.metric("Precio Máximo Swing", f"{swing_high:,.5f}")
c4.metric("Precio Mínimo Swing", f"{swing_low:,.5f}")

st.markdown(f"**📐 Zona Áurea Fibonacci (61.8% - 50%):** `[{f618:,.5f}  ---  {f500:,.5f}]`")
st.markdown(f"**🔍 Estado de Zona:** `{'EN ZONA ÁUREA ✅' if en_zona else 'FUERA DE ZONA ⏳ (Esperando retroceso)'}`")

st.divider()
st.subheader("🎯 Ejecución, Ganancias y Alertas")

m1, m2 = st.columns(2)
m1.metric("Precio de Entrada", f"{precio:,.5f}")
m1.metric("Stop Loss (SL)", f"{sl:,.5f}")
m2.metric("Take Profit (TP)", f"{tp:,.5f}")
m2.metric("Ganancia Proyectada", f"${ganancia_proyectada:,.2f} USD", delta=f"R:R 1:{cfg['rr']}")

# Bitácora
if st.button("💾 Guardar Operación en Bitácora", use_container_width=True):
    st.session_state.bitacora.append({
        "Símbolo": activo_sel,
        "Dirección": tipo_operacion.split()[0],
        "Entrada": f"{precio:.5f}",
        "SL": f"{sl:.5f}",
        "TP": f"{tp:.5f}",
        "Riesgo ($)": f"${riesgo_dinero:.2f}",
        "Ganancia ($)": f"${ganancia_proyectada:.2f}"
    })
    st.success("¡Operación registrada correctamente en la bitácora!")

# Botones de compartir señal operativa
mensaje_senal = (
    f"🚨 *WILFER TRADING SUITE - SEÑAL* 🚨\n\n"
    f"📌 *Símbolo:* {activo_sel}\n"
    f"📈 *Dirección:* {tipo_operacion}\n"
    f"🎯 *Entrada:* {precio:,.5f}\n"
    f"🛑 *Stop Loss:* {sl:,.5f}\n"
    f"🏆 *Take Profit:* {tp:,.5f}\n"
    f"💵 *Riesgo Máximo:* ${riesgo_dinero:,.2f} USD\n"
    f"💰 *Ganancia Proyectada:* ${ganancia_proyectada:,.2f} USD\n"
    f"⚖️ *Lote / Posición:* {lote_posicion:.4f}"
)
msg_encoded = urllib.parse.quote(mensaje_senal)
link_wa = f"https://api.whatsapp.com/send?text={msg_encoded}"
link_tg = f"https://t.me/share/url?url=&text={msg_encoded}"

st.markdown("##### 📲 Compartir Señal Operativa:")
col_w, col_t = st.columns(2)
with col_w:
    st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="width:100%;background-color:#25D366;color:white;border:none;padding:12px;border-radius:6px;font-weight:bold;cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)
with col_t:
    st.markdown(f'<a href="{link_tg}" target="_blank" style="text-decoration:none;"><button style="width:100%;background-color:#0088cc;color:white;border:none;padding:12px;border-radius:6px;font-weight:bold;cursor:pointer;">✈️ Telegram</button></a>', unsafe_allow_html=True)

st.divider()

# --- GRÁFICO TRADINGVIEW EN VIVO ---
st.subheader(f"📈 Gráfico Profesional en Vivo: {activo_sel}")
ticker_tv = f"BINANCE:{activo_sel}T" if activo_sel in ["BTCUSD", "ETHUSD"] else f"FOREXCOM:{activo_sel}"

widget_tv = f"""
<div style="height:500px;width:100%">
  <div id="tv_chart" style="height:500px;width:100%"></div>
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
    "container_id": "tv_chart"
  }});
  </script>
</div>
"""
components.html(widget_tv, height=510)

st.divider()

# --- BITÁCORA GENERAL ---
st.subheader("📖 Bitácora e Historial Operativo")
if st.session_state.bitacora:
    st.dataframe(pd.DataFrame(st.session_state.bitacora), use_container_width=True)
    if st.button("🗑️ Limpiar Historial de Bitácora"):
        st.session_state.bitacora = []
        st.rerun()
else:
    st.info("No hay operaciones guardadas en la bitácora todavía.")
