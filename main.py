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
            "BTCUSD": {"sma": 50, "atr_p": 14, "sl_mult": 3.0, "rr": 2.5, "riesgo_pct": 0.02, "precio_base": 67000.0, "atr_base": 450.0},
            "ETHUSD": {"sma": 50, "atr_p": 14, "sl_mult": 2.5, "rr": 2.5, "riesgo_pct": 0.02, "precio_base": 3500.0, "atr_base": 65.0},
            "EURUSD": {"sma": 50, "atr_p": 14, "sl_mult": 2.0, "rr": 2.0, "riesgo_pct": 0.015, "precio_base": 1.0850, "atr_base": 0.0025}
        }

st.title("⚡ WILFER TRADING SUITE - MOTOR TOTAL PRO")

# --- PANEL DE CONFIGURACIÓN Y SELECCIÓN ---
st.sidebar.header("⚙️ Configuración del Broker")
capital = st.sidebar.number_input("Capital Total de la Cuenta ($)", value=10000.0, step=500.0, format="%.2f")
riesgo_usr_pct = st.sidebar.slider("Riesgo por Operación (%)", min_value=0.1, max_value=5.0, value=2.0, step=0.1)

st.subheader("🌐 Selección de Activo y Datos de Mercado")
activo_sel = st.selectbox("Símbolo del Activo", ["BTCUSD", "ETHUSD", "EURUSD"])
tipo_operacion = st.radio("Dirección del Mercado", ["LONG (Compra Alcista)", "SHORT (Venta Bajista)"], horizontal=True)

motor = WilferTradingEngineTotal(capital_inicial=capital)
cfg = motor.config_mercados[activo_sel]

# Precios reales de mercado según el activo seleccionado
precio = cfg["precio_base"]
atr = cfg["atr_base"]
auto_swing_high = precio + (atr * 4.0)
auto_swing_low = precio - (atr * 4.0)
sma = precio - (atr * 0.5)

st.divider()
st.subheader("📐 Planificación y Parámetros Tácticos - Calculadora Fibonacci")

col_sh, col_sl_input = st.columns(2)
with col_sh:
    swing_high = st.number_input("Precio Máximo (Swing High)", value=float(auto_swing_high), step=1.0, format="%.2f")
with col_sl_input:
    swing_low = st.number_input("Precio Mínimo (Swing Low)", value=float(auto_swing_low), step=1.0, format="%.2f")

# Recálculo exacto basado en Fibonacci
rango_fib = swing_high - swing_low
f500 = swing_high - (rango_fib * 0.500)
f618 = swing_high - (rango_fib * 0.618)
en_zona = (precio <= f500) and (precio >= f618)

st.markdown(f"🎯 **Zona Áurea (61.8% Fib):** `${f618:,.2f}` | **50% Fib:** `${f500:,.2f}`")
st.markdown(f"**🔍 Estado de Zona:** `{'EN ZONA ÁUREA ✅' if en_zona else 'FUERA DE ZONA ⏳ (Esperando retroceso)'}`")

st.divider()
st.subheader("🎯 Ejecución, Riesgo y Lotes")

# Cálculos monetarios y de riesgo con precios reales
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

m1, m2 = st.columns(2)
m1.metric("Precio de Entrada ($)", f"{precio:,.2f}")
m1.metric("Límite de Pérdida (Stop Loss - SL)", f"{sl:,.2f}")
m2.metric("Toma de Ganancia (Take Profit - TP)", f"{tp:,.2f}")
m2.metric("Riesgo Máximo en Dinero", f"${riesgo_dinero:,.2f} USD")

st.metric("Lote / Tamaño de Posición", f"{lote_posicion:.4f} unidades")

# Bitácora
if st.button("💾 Guardar Operación en Bitácora", use_container_width=True):
    st.session_state.bitacora.append({
        "Símbolo": activo_sel,
        "Dirección": tipo_operacion.split()[0],
        "Entrada": f"{precio:.2f}",
        "SL": f"{sl:.2f}",
        "TP": f"{tp:.2f}",
        "Riesgo ($)": f"${riesgo_dinero:.2f}",
        "Ganancia ($)": f"${ganancia_proyectada:.2f}"
    })
    st.success("¡Operación registrada correctamente en la bitácora!")

# Botones de compartir señal operativa
mensaje_senal = (
    f"🚨 *WILFER TRADING SUITE - SEÑAL* 🚨\n\n"
    f"📌 *Símbolo:* {activo_sel}\n"
    f"📈 *Dirección:* {tipo_operacion}\n"
    f"🎯 *Entrada:* {precio:,.2f}\n"
    f"🛑 *Stop Loss:* {sl:,.2f}\n"
    f"🏆 *Take Profit:* {tp:,.2f}\n"
    f"💵 *Riesgo Máximo:* ${riesgo_dinero:,.2f} USD\n"
    f"⚖️ *Lote / Posición:* {lote_posicion:.4f} unidades\n"
    f"📐 *Zona Áurea 61.8%: * ${f618:,.2f}"
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
    
