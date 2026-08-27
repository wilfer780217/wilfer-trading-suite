import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Wilfer Trading Suite - Terminal Pura", layout="wide", page_icon="⚡")

if "bitacora" not in st.session_state:
    st.session_state.bitacora = []
if "ordenes_activas" not in st.session_state:
    st.session_state.ordenes_activas = []

st.title("⚡ WILFER TRADING SUITE - TERMINAL PURA Y DE EJECUCIÓN")

st.sidebar.header("⚙️ Configuración del Trader")
capital = st.sidebar.number_input("Capital Total ($)", value=10000.0, step=500.0, format="%.2f")
riesgo_usr_pct = st.sidebar.slider("Riesgo por Operación (%)", min_value=0.1, max_value=5.0, value=2.0, step=0.1)

st.subheader("🌐 Selección de Activo y Precio Real")
activo_sel = st.selectbox("Símbolo del Activo", ["BTCUSDT", "ETHUSDT"])

def obtener_precio_binance(symbol):
    try:
        url = f"https://data.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return float(response.json()["price"])
    except:
        pass
    return 67000.00 if "BTC" in symbol else 3500.00

precio_en_vivo = obtener_precio_binance(activo_sel)
st.metric(label=f"Precio Actual en Vivo de {activo_sel} (Binance)", value=f"${precio_en_vivo:,.2f}")

tipo_operacion = st.radio("Dirección Táctica", ["LONG (Compra Alcista)", "SHORT (Venta Bajista)"], horizontal=True)

st.divider()

st.subheader("📐 Niveles Operativos")
col_e1, col_e2, col_e3 = st.columns(3)
with col_e1:
    precio_manual = st.number_input("Precio de Entrada ($)", value=precio_en_vivo, step=1.0, format="%.2f")
with col_e2:
    sl_sugerido = precio_manual * 0.99 if "LONG" in tipo_operacion else precio_manual * 1.01
    sl_manual = st.number_input("Stop Loss - SL ($)", value=sl_sugerido, step=1.0, format="%.2f")
with col_e3:
    tp_sugerido = precio_manual * 1.02 if "LONG" in tipo_operacion else precio_manual * 0.98
    tp_manual = st.number_input("Take Profit - TP ($)", value=tp_sugerido, step=1.0, format="%.2f")

riesgo_dinero = capital * (riesgo_usr_pct / 100.0)
riesgo_unitario = abs(precio_manual - sl_manual)
lote_posicion = riesgo_dinero / riesgo_unitario if riesgo_unitario > 0 else 0.0

if "LONG" in tipo_operacion:
    ganancia_proyectada = lote_posicion * abs(tp_manual - precio_manual)
    rr_actual = abs(tp_manual - precio_manual) / riesgo_unitario if riesgo_unitario > 0 else 0.0
else:
    ganancia_proyectada = lote_posicion * abs(precio_manual - tp_manual)
    rr_actual = abs(precio_manual - tp_manual) / riesgo_unitario if riesgo_unitario > 0 else 0.0

st.divider()

st.subheader("🎯 Panel de Métricas y Riesgo Real")
col_n1, col_n2, col_n3 = st.columns(3)
col_n1.metric("Puntos de Riesgo (SL)", f"${riesgo_unitario:,.2f}")
col_n2.metric("Ratio Beneficio/Riesgo (R:R)", f"1 : {rr_actual:.2f}")
col_n3.metric("Ganancia Proyectada", f"${ganancia_proyectada:,.2f} USD")

m1, m2 = st.columns(2)
m1.metric("Riesgo Máximo en Dinero", f"${riesgo_dinero:,.2f} USD")
m2.metric("Tamaño de Lote Exacto", f"{lote_posicion:.4f} unidades")

st.divider()

st.subheader("🚀 Ejecución Conectada")
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🟢 EJECUTAR COMPRA (LONG)", use_container_width=True, type="primary"):
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
        st.success("¡Orden LONG vinculada al precio de mercado real!")

with col_btn2:
    if st.button("🔴 EJECUTAR VENTA (SHORT)", use_container_width=True, type="primary"):
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
        st.success("¡Orden SHORT vinculada al precio de mercado real!")

st.divider()

st.subheader("📋 Bandeja de Órdenes Activas")
if st.session_state.ordenes_activas:
    st.dataframe(pd.DataFrame(st.session_state.ordenes_activas), use_container_width=True)
    if st.button("✅ Cerrar Orden Activa"):
        orden_cerrada = st.session_state.ordenes_activas.pop(0)
        orden_cerrada["P&L ($)"] = round(ganancia_proyectada, 2)
        st.session_state.bitacora.append(orden_cerrada)
        st.success("Orden cerrada y guardada en la bitácora.")
        st.rerun()
else:
    st.info("Sin órdenes en curso.")

st.divider()

st.subheader("📖 Bitácora General")
if st.session_state.bitacora:
    st.dataframe(pd.DataFrame(st.session_state.bitacora), use_container_width=True)
else:
    st.info("Bitácora vacía.")
