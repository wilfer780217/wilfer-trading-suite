import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import pandas as pd
import numpy as np

st.set_page_config(page_title="Wilfer Trading Suite - Terminal Pro", layout="wide", page_icon="⚡")

# Inicializar estados de sesión
if "bitacora" not in st.session_state:
    st.session_state.bitacora = []
if "ordenes_activas" not in st.session_state:
    st.session_state.ordenes_activas = []

st.title("⚡ WILFER TRADING SUITE - TERMINAL TÁCTICA AVANZADA")

# --- BARRA LATERAL: GESTIÓN DE CUENTA ---
st.sidebar.header("⚙️ Configuración del Trader")
capital = st.sidebar.number_input("Capital Total ($)", value=10000.0, step=500.0, format="%.2f")
riesgo_usr_pct = st.sidebar.slider("Riesgo por Operación (%)", min_value=0.1, max_value=5.0, value=2.0, step=0.1)

st.sidebar.divider()
st.sidebar.markdown("### 🛡️ Estado del Sistema")
if st.session_state.ordenes_activas:
    st.sidebar.error(f"🔴 {len(st.session_state.ordenes_activas)} Orden(es) Activa(s)")
else:
    st.sidebar.success("🟢 Sistema Libre de Riesgo")

# --- SELECCIÓN DE ACTIVO ---
st.subheader("🌐 Selección de Activo y Lectura Técnica")
activo_sel = st.selectbox("Símbolo del Activo", ["BTCUSD", "ETHUSD", "EURUSD"])

# Precios base y simulación técnica de Bandas de Bollinger y Fibonacci
if activo_sel == "BTCUSD":
    precio_base, sl_base, tp_base = 67000.00, 66500.00, 68250.00
    # Simulación de Bandas de Bollinger dinámicas
    upper_bb, lower_bb, sma_bb = 68000.00, 66000.00, 67000.00
elif activo_sel == "ETHUSD":
    precio_base, sl_base, tp_base = 3500.00, 3450.00, 3620.00
    upper_bb, lower_bb, sma_bb = 3580.00, 3420.00, 3500.00
else:  # EURUSD
    precio_base, sl_base, tp_base = 1.0850, 1.0810, 1.0930
    upper_bb, lower_bb, sma_bb = 1.0900, 1.0800, 1.0850

tipo_operacion = st.radio("Dirección Táctica", ["LONG (Compra Alcista)", "SHORT (Venta Bajista)"], horizontal=True)

st.divider()

# --- PANEL DE NIVELES Y FIBONACCI AUTOMÁTICO ---
st.subheader(f"📐 Niveles de Precisión y Fibonacci para {activo_sel}")

col_e1, col_e2, col_e3 = st.columns(3)
with col_e1:
    precio_manual = st.number_input("Precio de Entrada ($)", value=precio_base, step=0.0001 if activo_sel=="EURUSD" else 1.0, format="%.4f" if activo_sel=="EURUSD" else "%.2f")
with col_e2:
    sl_manual = st.number_input("Stop Loss - SL ($)", value=sl_base, step=0.0001 if activo_sel=="EURUSD" else 1.0, format="%.4f" if activo_sel=="EURUSD" else "%.2f")
with col_e3:
    # Cálculo automático de Fibonacci (Proyección de niveles 0.618 y 1.618 basados en el riesgo)
    rango_fib = abs(precio_manual - sl_manual)
    tp_fib_sugerido = precio_manual + (rango_fib * 1.618) if "LONG" in tipo_operacion else precio_manual - (rango_fib * 1.618)
    
    tp_manual = st.number_input("Take Profit - TP (Fib 1.618)", value=tp_fib_sugerido, step=0.0001 if activo_sel=="EURUSD" else 1.0, format="%.4f" if activo_sel=="EURUSD" else "%.2f")

# --- LECTURA TÉCNICA DE BANDAS DE BOLLINGER ---
st.markdown("##### 📊 Lectura de Bandas de Bollinger y Estado del Mercado:")
col_b1, col_b2, col_b3 = st.columns(3)
col_b1.metric("Banda Superior (Resistencia)", f"{upper_bb:,.2f}" if activo_sel!="EURUSD" else f"{upper_bb:,.4f}")
col_b2.metric("Media Móvil Central (SMA)", f"{sma_bb:,.2f}" if activo_sel!="EURUSD" else f"{sma_bb:,.4f}")
col_b3.metric("Banda Inferior (Soporte)", f"{lower_bb:,.2f}" if activo_sel!="EURUSD" else f"{lower_bb:,.4f}")

if precio_manual >= upper_bb:
    st.warning("⚠️ Alerta Bollinger: El precio está tocando la Banda Superior (Zona de Posible Sobrecompra). Cuidado con los LONGs.")
elif precio_manual <= lower_bb:
    st.info("💡 Alerta Bollinger: El precio está tocando la Banda Inferior (Zona de Posible Sobreventa). Oportunidad para LONGs.")
else:
    st.success("✅ Estado Bollinger: El precio opera neutral dentro del canal central.")

st.divider()

# --- CÁLCULOS MATEMÁTICOS DE RIESGO ---
riesgo_dinero = capital * (riesgo_usr_pct / 100.0)
riesgo_unitario = abs(precio_manual - sl_manual)
lote_posicion = riesgo_dinero / riesgo_unitario if riesgo_unitario > 0 else 0.0

if "LONG" in tipo_operacion:
    ganancia_proyectada = lote_posicion * abs(tp_manual - precio_manual)
    rr_actual = abs(tp_manual - precio_manual) / riesgo_unitario if riesgo_unitario > 0 else 0.0
else:
    ganancia_proyectada = lote_posicion * abs(precio_manual - tp_manual)
    rr_actual = abs(precio_manual - tp_manual) / riesgo_unitario if riesgo_unitario > 0 else 0.0

# --- PANEL DE CONTROL Y MÉTRICAS CLAVE ---
st.subheader("🎯 Panel de Control y Métricas de Riesgo")

col_n1, col_n2, col_n3 = st.columns(3)
col_n1.metric("Puntos de Riesgo (SL)", f"{riesgo_unitario:,.4f}" if activo_sel=="EURUSD" else f"{riesgo_unitario:,.2f} USD")
col_n2.metric("Ratio Beneficio/Riesgo (R:R)", f"1 : {rr_actual:.2f}")
col_n3.metric("Ganancia Proyectada (TP)", f"${ganancia_proyectada:,.2f} USD")

m1, m2 = st.columns(2)
m1.metric("Riesgo Máximo en Dinero", f"${riesgo_dinero:,.2f} USD")
m2.metric("Tamaño de Lote Exacto", f"{lote_posicion:.4f} unidades")

st.divider()

# --- BOTONES DE EJECUCIÓN ---
st.subheader("🚀 Terminal de Disparo")
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🟢 EJECUTAR COMPRA (LONG)", use_container_width=True, type="primary"):
        nueva_orden = {
            "ID": len(st.session_state.ordenes_activas) + len(st.session_state.bitacora) + 1,
            "Símbolo": activo_sel,
            "Tipo": "LONG",
            "Entrada": f"{precio_manual:.4f}" if activo_sel=="EURUSD" else f"{precio_manual:.2f}",
            "SL": f"{sl_manual:.4f}" if activo_sel=="EURUSD" else f"{sl_manual:.2f}",
            "TP": f"{tp_manual:.4f}" if activo_sel=="EURUSD" else f"{tp_manual:.2f}",
            "Lote": f"{lote_posicion:.4f}",
            "Riesgo ($)": f"${riesgo_dinero:.2f}"
        }
        st.session_state.ordenes_activas.append(nueva_orden)
        st.success("¡Orden LONG ejecutada y enviada a la bandeja!")

with col_btn2:
    if st.button("🔴 EJECUTAR VENTA (SHORT)", use_container_width=True, type="primary"):
        nueva_orden = {
            "ID": len(st.session_state.ordenes_activas) + len(st.session_state.bitacora) + 1,
            "Símbolo": activo_sel,
            "Tipo": "SHORT",
            "Entrada": f"{precio_manual:.4f}" if activo_sel=="EURUSD" else f"{precio_manual:.2f}",
            "SL": f"{sl_manual:.4f}" if activo_sel=="EURUSD" else f"{sl_manual:.2f}",
            "TP": f"{tp_manual:.4f}" if activo_sel=="EURUSD" else f"{tp_manual:.2f}",
            "Lote": f"{lote_posicion:.4f}",
            "Riesgo ($)": f"${riesgo_dinero:.2f}"
        }
        st.session_state.ordenes_activas.append(nueva_orden)
        st.success("¡Orden SHORT ejecutada y enviada a la bandeja!")

st.divider()

# --- BANDEJA DE ÓRDENES Y GESTIÓN ---
st.subheader("📋 Bandeja de Órdenes Activas")

if st.session_state.ordenes_activas:
    st.dataframe(pd.DataFrame(st.session_state.ordenes_activas), use_container_width=True)
    
    col_acc1, col_acc2 = st.columns(2)
    with col_acc1:
        if st.button("✅ Cerrar con Éxito (TP Tocado)"):
            orden_cerrada = st.session_state.ordenes_activas.pop(0)
            orden_cerrada["P&L ($)"] = round(ganancia_proyectada, 2)
            orden_cerrada["Estado"] = "CERRADA CON GANANCIA 🟢"
            st.session_state.bitacora.append(orden_cerrada)
            st.success("¡Orden cerrada por TP y registrada en la bitácora!")
            st.rerun()
            
    with col_acc2:
        if st.button("❌ Cerrar en Pérdida (SL Tocado)"):
            orden_cerrada = st.session_state.ordenes_activas.pop(0)
            orden_cerrada["P&L ($)"] = -round(riesgo_dinero, 2)
            orden_cerrada["Estado"] = "CERRADA EN SL 🔴"
            st.session_state.bitacora.append(orden_cerrada)
            st.warning("¡Orden cerrada por SL y registrada en la bitácora!")
            st.rerun()
else:
    st.info("No hay órdenes activas en este momento.")

st.divider()

# --- GRÁFICO TRADINGVIEW EN VIVO SINCRONIZADO ---
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
st.subheader("📖 Bitácora General (Historial de Operaciones)")
if st.session_state.bitacora:
    st.dataframe(pd.DataFrame(st.session_state.bitacora), use_container_width=True)
    if st.button("🗑️ Limpiar Bitácora"):
        st.session_state.bitacora = []
        st.rerun()
else:
    st.info("Aún no hay operaciones registradas en el historial.")
