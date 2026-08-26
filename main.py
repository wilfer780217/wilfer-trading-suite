import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import pandas as pd
import ccxt  # Librería estándar para conectar con Binance y otros exchanges

st.set_page_config(page_title="Wilfer Trading Suite - Total Pro", layout="wide", page_icon="⚡")

if "bitacora" not in st.session_state:
    st.session_state.bitacora = []

st.title("⚡ WILFER TRADING SUITE - MOTOR TOTAL PRO (CONEXIÓN BINANCE)")

# --- PANEL DE CONFIGURACIÓN Y CREDENCIALES API ---
st.sidebar.header("⚙️ Configuración del Broker & API")
capital = st.sidebar.number_input("Capital Total de la Cuenta ($)", value=10000.0, step=500.0, format="%.2f")
riesgo_usr_pct = st.sidebar.slider("Riesgo por Operación (%)", min_value=0.1, max_value=5.0, value=2.0, step=0.1)

st.sidebar.divider()
st.sidebar.subheader("🔑 Credenciales de Binance")
binance_api_key = st.sidebar.text_input("Binance API Key", type="password")
binance_secret_key = st.sidebar.text_input("Binance Secret Key", type="password")
modo_testnet = st.sidebar.checkbox("Usar Binance Testnet (Modo Pruebas / Sin Dinero Real)", value=True)

st.subheader("🌐 Selección de Activo y Datos de Mercado")
# Usamos símbolos compatibles con Binance Futures o Spot (ej: BTC/USDT)
activo_sel = st.selectbox("Símbolo del Activo", ["BTC/USDT", "ETH/USDT"])
tipo_operacion = st.radio("Dirección del Mercado", ["LONG (Compra Alcista)", "SHORT (Venta Bajista)"], horizontal=True)

st.divider()
st.subheader("📐 Planificación y Parámetros Manuales (Tus Niveles Exactos)")

# Campos manuales para definir la operación
col_e1, col_e2 = st.columns(2)
with col_e1:
    precio_manual = st.number_input("Precio de Entrada ($)", value=67000.00, step=1.0, format="%.2f")
    sl_manual = st.number_input("Stop Loss - SL ($)", value=66500.00, step=1.0, format="%.2f")
with col_e2:
    tp_manual = st.number_input("Take Profit - TP ($)", value=68250.00, step=1.0, format="%.2f")

# Cálculos matemáticos de riesgo y lotes
riesgo_dinero = capital * (riesgo_usr_pct / 100.0)
riesgo_unitario = abs(precio_manual - sl_manual)
lote_posicion = riesgo_dinero / riesgo_unitario if riesgo_unitario > 0 else 0.0

if "LONG" in tipo_operacion:
    ganancia_proyectada = lote_posicion * abs(tp_manual - precio_manual)
    rr_actual = abs(tp_manual - precio_manual) / riesgo_unitario if riesgo_unitario > 0 else 0.0
    side_binance = "buy"
else:
    ganancia_proyectada = lote_posicion * abs(precio_manual - tp_manual)
    rr_actual = abs(precio_manual - tp_manual) / riesgo_unitario if riesgo_unitario > 0 else 0.0
    side_binance = "sell"

st.divider()

# --- PANEL DE CONTROL Y NIVELES EXACTOS ---
st.subheader("🎯 Panel de Control y Niveles Exactos (Bot v6.64)")

col_n1, col_n2, col_n3 = st.columns(3)
col_n1.metric("Puntos de Riesgo (SL)", f"{riesgo_unitario:,.2f} USD")
col_n2.metric("Ratio Beneficio/Riesgo (R:R)", f"1 : {rr_actual:.2f}")
col_n3.metric("Ganancia Proyectada (TP)", f"${ganancia_proyectada:,.2f} USD")

st.markdown("---")

m1, m2 = st.columns(2)
m1.metric("Riesgo Máximo en Dinero", f"${riesgo_dinero:,.2f} USD")
m2.metric("Tamaño de Posición / Lote", f"{lote_posicion:.4f} unidades")

st.divider()

# --- BOTÓN DE EJECUCIÓN REAL EN BINANCE ---
st.subheader("🚀 Ejecución Directa en el Mercado")

if st.button("⚡ ENVIAR ORDEN REAL A BINANCE", use_container_width=True, type="primary"):
    if not binance_api_key or not binance_secret_key:
        st.error("⚠️ Por favor, ingresa tu API Key y Secret Key de Binance en la barra lateral.")
    else:
        try:
            # Inicializar conexión con Binance a través de CCXT
            exchange = ccxt.binance({
                'apiKey': binance_api_key,
                'secret': binance_secret_key,
                'enableRateLimit': True,
            })
            
            if modo_testnet:
                exchange.set_sandbox_mode(True)  # Activa entorno de pruebas seguro de Binance
            
            # Ejecutar orden de mercado o límite según prefieras (aquí enviamos orden de mercado base)
            # Nota: Para órdenes OCO con Stop Loss y Take Profit automáticos en Binance:
            orden = exchange.create_order(
                symbol=activo_sel,
                type='market',
                side=side_binance,
                amount=lote_posicion
            )
            
            st.success(f"¡Orden ejecutada con éxito en Binance! ID de orden: {orden['id']}")
            
            # Guardar en bitácora automáticamente
            st.session_state.bitacora.append({
                "Símbolo": activo_sel,
                "Dirección": tipo_operacion.split()[0],
                "Entrada": f"{precio_manual:.2f}",
                "SL": f"{sl_manual:.2f}",
                "TP": f"{tp_manual:.2f}",
                "Riesgo ($)": f"${riesgo_dinero:.2f}",
                "Ganancia ($)": f"${ganancia_proyectada:.2f}",
                "Estado": "EJECUTADA EN BINANCE ✅"
            })
            
        except Exception as e:
            st.error(f"❌ Error al conectar o ejecutar la orden en Binance: {e}")

# Bitácora manual tradicional
if st.button("💾 Guardar Solo en Bitácora (Sin Ejecutar)", use_container_width=True):
    st.session_state.bitacora.append({
        "Símbolo": activo_sel,
        "Dirección": tipo_operacion.split()[0],
        "Entrada": f"{precio_manual:.2f}",
        "SL": f"{sl_manual:.2f}",
        "TP": f"{tp_manual:.2f}",
        "Riesgo ($)": f"${riesgo_dinero:.2f}",
        "Ganancia ($)": f"${ganancia_proyectada:.2f}",
        "Estado": "PLANIFICADA 📝"
    })
    st.success("¡Operación registrada correctamente en la bitácora!")

st.divider()

# --- GRÁFICO TRADINGVIEW EN VIVO ---
st.subheader(f"📈 Gráfico Profesional en Vivo: {activo_sel}")
# Adaptar formato de símbolo para TradingView (ej: BTCUSDT)
simbolo_tv = activo_sel.replace("/", "")
ticker_tv = f"BINANCE:{simbolo_tv}"

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
