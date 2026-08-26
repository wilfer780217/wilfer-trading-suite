import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Wilfer Trading Suite Pro", layout="wide", page_icon="📈")

st.title("🛡️ WILFER TRADING SUITE PRO")
st.caption("Comando Estratégico de Trading - Fibonacci & Gestión de Riesgo 24/7")

# Sidebar - Configuración
st.sidebar.header("Configuración de la Operación")
activo = st.sidebar.text_input("Activo / Par", value="BTCUSD")
capital = st.sidebar.number_input("Capital de la Cuenta ($)", value=1000.0, step=100.0)
riesgo_pct = st.sidebar.number_input("Riesgo por Operación (%)", value=2.0, step=0.5)

riesgo_usd = capital * (riesgo_pct / 100.0)
st.sidebar.info(f"Riesgo Máximo Definido: ${riesgo_usd:.2f} USD")

# Secciones Principales
col1, col2 = st.columns(2)

with col1:
    st.subheader("📐 Calculadora Fibonacci & Entrada")
    alto = st.number_input("Precio Máximo (Swing High)", value=82000.0, step=100.0)
    bajo = st.number_input("Precio Mínimo (Swing Low)", value=75000.0, step=100.0)
    
    # Validación de escala para Bitcoin (Candado anti-error)
    if "BTC" in activo.upper() and (alto < 10000 or bajo < 10000):
        st.error("🚨 ERROR DE ESCALA: El precio ingresado para BTCUSD es demasiado bajo (< $10,000). Revisa ceros y decimales.")
    
    dif = alto - bajo
    fib_618 = bajo + (dif * 0.618)
    st.success(f"🔵 Zona Entrada Fib 61.8%: ${fib_618:,.2f}")

with col2:
    st.subheader("🛡️ Gestión de Riesgo y Posición")
    precio_entrada = st.number_input("Precio de Entrada Real ($)", value=fib_618, step=100.0)
    stop_loss = st.number_input("Stop Loss ($)", value=bajo, step=100.0)
    take_profit = st.number_input("Take Profit ($)", value=alto, step=100.0)
    
    # Validaciones de seguridad
    es_valido = True
    if "BTC" in activo.upper() and (precio_entrada < 10000 or stop_loss < 10000):
        st.error("🚨 ERROR DE PRECIO: BTCUSD debe ingresarse con la escala de precio completa (ej. 79500).")
        es_valido = False
    
    distancia_sl = abs(precio_entrada - stop_loss)
    
    if distancia_sl == 0:
        st.warning("El Stop Loss no puede ser igual al precio de entrada.")
    elif es_valido:
        lotes = riesgo_usd / distancia_sl
        distancia_tp = abs(take_profit - precio_entrada)
        rr_ratio = distancia_tp / distancia_sl if distancia_sl > 0 else 0
        
        st.metric("Tamaño de Posición (Lotes / Unidades)", f"{lotes:.4f}")
        st.metric("Ratio Riesgo / Beneficio (R:R)", f"1 : {rr_ratio:.2f}")

# Botón para registrar en Bitácora
if st.button("💾 Guardar en Bitácora"):
    if es_valido and distancia_sl > 0:
        nueva_op = pd.DataFrame([{
            "Activo": activo,
            "Entrada": precio_entrada,
            "SL": stop_loss,
            "TP": take_profit,
            "Riesgo_USD": riesgo_usd,
            "Lotes": lotes
        }])
        try:
            bitacora = pd.read_csv("bitacora_wilfer.csv")
            bitacora = pd.concat([bitacora, nueva_op], ignore_index=True)
        except FileNotFoundError:
            bitacora = nueva_op
        bitacora.to_csv("bitacora_wilfer.csv", index=False)
        st.success("¡Operación registrada con éxito en bitacora_wilfer.csv!")
