import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import pandas as pd

st.set_page_config(page_title="Wilfer Trading Suite - Total Pro", layout="wide", page_icon="⚡")

if "bitacora" not in st.session_state:
    st.session_state.bitacora = []

st.title("⚡ WILFER TRADING SUITE - MOTOR TOTAL PRO")

# --- PANEL DE CONFIGURACIÓN Y SELECCIÓN ---
st.sidebar.header("⚙️ Configuración del Broker")
capital = st.sidebar.number_input("Capital Total de la Cuenta ($)", value=10000.0, step=500.0, format="%.2f")
riesgo_usr_pct = st.sidebar.slider("Riesgo por Operación (%)", min_value=0.1, max_value=5.0, value=2.0, step=0.1)

st.subheader("🌐 Selección de Activo y Datos de Mercado")
activo_sel = st.selectbox("Símbolo del Activo", ["BTCUSD", "ETHUSD", "EURUSD"])
tipo_operacion = st.radio("Dirección del Mercado", ["LONG (Compra Alcista)", "SHORT (Venta Bajista)"], horizontal=True)

st.divider()
st.subheader("📐 Planificación y Parámetros Manuales")

# Campos totalmente manuales para que pongas el precio exacto que quieras
col_e1, col_e2 = st.columns(2)
with col_e1:
    precio_manual = st.number_input("Precio de Entrada ($)", value=67000.00, step=1.0, format="%.2f")
    sl_manual = st.number_input("Stop Loss - SL ($)", value=66500.00, step=1.0, format="%.2f")
with col_e2:
    tp_manual = st.number_input("Take Profit - TP ($)", value=68250.00, step=1.0, format="%.2f")

# Cálculos de riesgo y lote basados en tus números exactos
riesgo_dinero = capital * (riesgo_usr_pct / 100.0)
riesgo_unitario = abs(precio_manual - sl_manual)
lote_posicion = riesgo_dinero / riesgo_unitario if riesgo_unitario > 0 else 0.0

if "LONG" in tipo_operacion:
    ganancia_proyectada = lote_posicion * abs(tp_manual - precio_manual)
else:
    ganancia_proyectada = lote_posicion * abs(precio_manual - tp_manual)

st.divider()
st.subheader("🎯 Resumen de Ejecución y Lotes")

m1, m2 = st.columns(2)
m1.metric("Riesgo Máximo en Dinero", f"${riesgo_dinero:,.2f} USD")
m2.metric("Lote / Tamaño de Posición", f"{lote_posicion:.4f} unidades")

st.metric("Ganancia Proyectada Estimada", f"${ganancia_proyectada:,.2f} USD")

# Bitácora
if st.button("💾 Guardar Operación en Bitácora", use_container_width=True):
    st.session_state.bitacora.append({
        "Símbolo": activo_sel,
        "Dirección": tipo_operacion.split()[0],
        "Entrada": f"{precio_manual:.2f}",
        "SL": f"{sl_manual:.2f}",
        "TP": f"{tp_manual:.2f}",
        "Riesgo ($)": f"${riesgo_dinero:.2f}",
        "Ganancia ($)": f"${ganancia_proyectada:.2f}"
    })
    st.success("¡Operación registrada correctamente en la bitácora!")

# Botones de compartir señal operativa
mensaje_senal = (
    f"🚨 *WILFER TRADING SUITE - SEÑAL* 🚨\n\n"
    f"📌 *Símbolo:* {activo_sel}\n"
    f"📈 *Dirección:* {tipo_operacion}\n"
    f"🎯 *Entrada:* {precio_manual:,.2f}\n"
    f"🛑 *Stop Loss:* {sl_manual:,.2f}\n"
    f"🏆 *Take Profit:* {tp_manual:,.2f}\n"
    f"💵 *Riesgo Máximo:* ${riesgo_dinero:,.2f} USD\n"
    f"⚖️ *Lote / Posición:* {lote_posicion:.4f} unidades"
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

# --- ASISTENTE TÉCNICO INTEGRADO (Basado en tu Bot v6.64) ---
st.subheader("🤖 Asistente Técnico Wilfer Pro (Bot v6.64)")
with st.container():
    st.info(f"""
    **Diagnóstico del Asistente para {activo_sel}:**
    * **Filtro ADX (Tendencia / Ruido):** Se requiere un ADX $\\ge 25.0$ para validar mercado con fuerza.
    * **Estructura y Niveles:** Monitoreando quiebres estructurales (**BOS** / **CHoCH**) y zonas de retroceso **Fibonacci (50% y 61.8%)**.
    * **Gestión de Riesgo Activa:** Relación beneficio/riesgo configurada en $2.5$ con multiplicador ATR de $3.0$.
    * **Validación de Posición:** Distancia actual al Stop Loss de `${abs(precio_manual - sl_manual):,.2f}` con un lote asignado de `{lote_posicion:.4f}` unidades bajo tu control estricto de riesgo del `{riesgo_usr_pct}%`.
    """)

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
