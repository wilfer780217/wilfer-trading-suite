import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import pandas as pd
import random

st.set_page_config(page_title="Wilfer Trading Suite - Terminal Pro Auditada", layout="wide", page_icon="⚡")

# Inicializar estados de sesión
if "bitacora" not in st.session_state:
    st.session_state.bitacora = []
if "ordenes_activas" not in st.session_state:
    st.session_state.ordenes_activas = []
if "posicion_activa" not in st.session_state:
    st.session_state.posicion_activa = False

st.title("⚡ WILFER TRADING SUITE - TERMINAL PRO (AUDITADA & BLINDADA)")

# --- PANEL DE CONFIGURACIÓN Y GESTIÓN DE CUENTA ---
st.sidebar.header("⚙️ Configuración del Trader")
capital = st.sidebar.number_input("Capital Total de la Cuenta ($)", value=10000.0, step=500.0, format="%.2f")
riesgo_usr_pct = st.sidebar.slider("Riesgo por Operación (%)", min_value=0.1, max_value=5.0, value=2.0, step=0.1)
apalancamiento = st.sidebar.selectbox("Apalancamiento del Broker", [1, 5, 10, 20, 50, 100], index=3)

st.sidebar.divider()
st.sidebar.markdown("### 🛡️ Estado del Sistema de Auditoría")
if st.session_state.ordenes_activas:
    st.sidebar.error(f"🔴 ESTADO: {len(st.session_state.ordenes_activas)} Orden(es) Activa(s)")
else:
    st.sidebar.success("🟢 ESTADO: Sistema Libre de Riesgo")

st.subheader("🌐 Selección de Activo y Mercado")
activo_sel = st.selectbox("Símbolo del Activo", ["BTCUSD", "ETHUSD", "EURUSD"])
tipo_operacion = st.radio("Dirección Táctica", ["LONG (Compra Alcista)", "SHORT (Venta Bajista)"], horizontal=True)

st.divider()
st.subheader("📐 Planificación y Niveles de Precisión")

col_e1, col_e2 = st.columns(2)
with col_e1:
    precio_manual = st.number_input("Precio de Entrada ($)", value=67000.00, step=1.0, format="%.2f")
    sl_manual = st.number_input("Stop Loss - SL ($)", value=66500.00, step=1.0, format="%.2f")
with col_e2:
    tp_manual = st.number_input("Take Profit - TP ($)", value=68250.00, step=1.0, format="%.2f")

# --- ESCUDO DE VALIDACIÓN DE ERRORES (AUDITORÍA LÓGICA) ---
error_logica = False
mensaje_error = ""

if "LONG" in tipo_operacion:
    if sl_manual >= precio_manual:
        error_logica = True
        mensaje_error = "⚠️ ERROR DE AUDITORÍA: En un LONG, el Stop Loss debe estar por DEBAJO del Precio de Entrada."
    if tp_manual <= precio_manual:
        error_logica = True
        mensaje_error = "⚠️ ERROR DE AUDITORÍA: En un LONG, el Take Profit debe estar por ENCIMA del Precio de Entrada."
else:  # SHORT
    if sl_manual <= precio_manual:
        error_logica = True
        mensaje_error = "⚠️ ERROR DE AUDITORÍA: En un SHORT, el Stop Loss debe estar por ENCIMA del Precio de Entrada."
    if tp_manual >= precio_manual:
        error_logica = True
        mensaje_error = "⚠️ ERROR DE AUDITORÍA: En un SHORT, el Take Profit debe estar por DEBAJO del Precio de Entrada."

if error_logica:
    st.error(mensaje_error)

# Cálculos matemáticos avanzados del motor
riesgo_dinero = capital * (riesgo_usr_pct / 100.0)
riesgo_unitario = abs(precio_manual - sl_manual)
lote_posicion = riesgo_dinero / riesgo_unitario if riesgo_unitario > 0 else 0.0
valor_nocional = lote_posicion * precio_manual
margen_requerido = valor_nocional / apalancamiento

if "LONG" in tipo_operacion:
    ganancia_proyectada = lote_posicion * abs(tp_manual - precio_manual)
    rr_actual = abs(tp_manual - precio_manual) / riesgo_unitario if riesgo_unitario > 0 else 0.0
else:
    ganancia_proyectada = lote_posicion * abs(precio_manual - tp_manual)
    rr_actual = abs(precio_manual - tp_manual) / riesgo_unitario if riesgo_unitario > 0 else 0.0

st.divider()

# --- PANEL DE CONTROL Y MÉTRICAS CLAVE ---
st.subheader("🎯 Panel de Control y Auditoría de Riesgo")

col_n1, col_n2, col_n3 = st.columns(3)
col_n1.metric("Puntos de Riesgo (SL)", f"{riesgo_unitario:,.2f} USD")
col_n2.metric("Ratio Beneficio/Riesgo (R:R)", f"1 : {rr_actual:.2f}")
col_n3.metric("Ganancia Proyectada (TP)", f"${ganancia_proyectada:,.2f} USD")

st.markdown("---")

m1, m2, m3 = st.columns(3)
m1.metric("Riesgo Máximo en Dinero", f"${riesgo_dinero:,.2f} USD")
m2.metric("Lote / Tamaño de Posición", f"{lote_posicion:.4f} unidades")
m3.metric("Margen Requerido (Ap. x{apalancamiento})", f"${margen_requerido:,.2f} USD")

st.divider()

# --- BOTONES DE EJECUCIÓN INTERACTIVA BLINDADOS ---
st.subheader("🚀 Terminal de Disparo y Órdenes")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🟢 EJECUTAR COMPRA (LONG)", use_container_width=True, type="primary"):
        if error_logica:
            st.error("No se puede ejecutar la orden: corrige los errores lógicos de SL o TP primero.")
        else:
            nueva_orden = {
                "ID": len(st.session_state.ordenes_activas) + len(st.session_state.bitacora) + 1,
                "Símbolo": activo_sel,
                "Tipo": "LONG",
                "Entrada": f"{precio_manual:.2f}",
                "SL": f"{sl_manual:.2f}",
                "TP": f"{tp_manual:.2f}",
                "Lote": f"{lote_posicion:.4f}",
                "Riesgo ($)": f"${riesgo_dinero:.2f}"
            }
            st.session_state.ordenes_activas.append(nueva_orden)
            st.session_state.posicion_activa = True
            st.success("¡Orden LONG validada y enviada a la bandeja de órdenes!")

with col_btn2:
    if st.button("🔴 EJECUTAR VENTA (SHORT)", use_container_width=True, type="primary"):
        if error_logica:
            st.error("No se puede ejecutar la orden: corrige los errores lógicos de SL o TP primero.")
        else:
            nueva_orden = {
                "ID": len(st.session_state.ordenes_activas) + len(st.session_state.bitacora) + 1,
                "Símbolo": activo_sel,
                "Tipo": "SHORT",
                "Entrada": f"{precio_manual:.2f}",
                "SL": f"{sl_manual:.2f}",
                "TP": f"{tp_manual:.2f}",
                "Lote": f"{lote_posicion:.4f}",
                "Riesgo ($)": f"${riesgo_dinero:.2f}"
            }
            st.session_state.ordenes_activas.append(nueva_orden)
            st.session_state.posicion_activa = True
            st.success("¡Orden SHORT validada y enviada a la bandeja de órdenes!")

st.divider()

# --- BANDEJA DE ÓRDENES ACTIVAS ---
st.subheader("📋 Bandeja de Órdenes Activas en el Mercado")

if st.session_state.ordenes_activas:
    df_ordenes = pd.DataFrame(st.session_state.ordenes_activas)
    st.dataframe(df_ordenes, use_container_width=True)
    
    col_acc1, col_acc2 = st.columns(2)
    with col_acc1:
        if st.button("✅ Cerrar con Éxito (TP Tocado)"):
            orden_cerrada = st.session_state.ordenes_activas.pop(0)
            pnl_cierre = round(ganancia_proyectada, 2)
            orden_cerrada["P&L ($)"] = pnl_cierre
            orden_cerrada["Estado"] = "CERRADA CON GANANCIA 🟢"
            st.session_state.bitacora.append(orden_cerrada)
            if not st.session_state.ordenes_activas:
                st.session_state.posicion_activa = False
            st.success("¡Orden cerrada por TP y registrada en la bitácora!")
            st.rerun()
            
    with col_acc2:
        if st.button("❌ Cerrar en Pérdida (SL Tocado)"):
            orden_cerrada = st.session_state.ordenes_activas.pop(0)
            pnl_cierre = -round(riesgo_dinero, 2)
            orden_cerrada["P&L ($)"] = pnl_cierre
            orden_cerrada["Estado"] = "CERRADA EN SL 🔴"
            st.session_state.bitacora.append(orden_cerrada)
            if not st.session_state.ordenes_activas:
                st.session_state.posicion_activa = False
            st.warning("¡Orden cerrada por SL y registrada en la bitácora!")
            st.rerun()
else:
    st.info("No hay órdenes activas. Ejecuta una operación arriba para gestionarla aquí.")

st.divider()

# --- PANEL DE GANANCIAS Y PÉRDIDAS (P&L ACUMULADO) ---
st.subheader("📊 Panel de Ganancias y Pérdidas (P&L Acumulado)")

if st.session_state.bitacora:
    df_bitacora = pd.DataFrame(st.session_state.bitacora)
    if "P&L ($)" in df_bitacora.columns:
        pnl_total = df_bitacora["P&L ($)"].sum()
        ganadas = len(df_bitacora[df_bitacora["P&L ($)"] > 0])
        perdidas = len(df_bitacora[df_bitacora["P&L ($)"] < 0])
        
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("P&L Total Acumulado", f"${pnl_total:,.2f} USD")
        col_p2.metric("Operaciones Ganadoras", f"{ganadas}")
        col_p3.metric("Operaciones Perdedoras", f"{perdidas}")
else:
    st.info("El balance P&L se actualizará cuando cierres tus órdenes.")

st.divider()

# Botones de compartir señal por WhatsApp y Telegram
mensaje_senal = (
    f"🚨 *WILFER TRADING SUITE - SEÑAL TERMINAL* 🚨\n\n"
    f"📌 *Símbolo:* {activo_sel}\n"
    f"📈 *Dirección:* {tipo_operacion}\n"
    f"🎯 *Entrada:* {precio_manual:,.2f}\n"
    f"🛑 *Stop Loss:* {sl_manual:,.2f}\n"
    f"🏆 *Take Profit:* {tp_manual:,.2f}\n"
    f"💵 *Riesgo Máximo:* ${riesgo_dinero:,.2f} USD\n"
    f"⚖️ *Lote / Posición:* {lote_posicion:.4f} unidades\n"
    f"📊 *R:R:* 1:{rr_actual:.2f}"
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

# --- BITÁCORA GENERAL DE HISTORIAL ---
st.subheader("📖 Bitácora General (Historial de Operaciones Cerradas)")
if st.session_state.bitacora:
    st.dataframe(pd.DataFrame(st.session_state.bitacora), use_container_width=True)
    if st.button("🗑️ Limpiar Historial de Bitácora"):
        st.session_state.bitacora = []
        st.rerun()
else:
    st.info("No hay operaciones cerradas registradas en la bitácora todavía.")
