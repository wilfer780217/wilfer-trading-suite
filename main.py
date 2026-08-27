import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests

st.set_page_config(page_title="Wilfer Trading Terminal Pro", layout="wide", page_icon="⚡")

if "bitacora" not in st.session_state:
    st.session_state.bitacora = []
if "ordenes_activas" not in st.session_state:
    st.session_state.ordenes_activas = []

st.title("⚡ WILFER TRADING TERMINAL - ESTACIÓN TÁCTICA")

# --- CONFIGURACIÓN LATERAL DE RIESGO Y CAPITAL ---
st.sidebar.header("⚙️ Gestión de Riesgo")
capital = st.sidebar.number_input("Capital Total ($)", value=10000.0, step=500.0, format="%.2f")
riesgo_usr_pct = st.sidebar.slider("Riesgo por Operación (%)", min_value=0.1, max_value=5.0, value=2.0, step=0.1)

# Selección de activo
activo_sel = st.sidebar.selectbox("Símbolo del Activo", ["BTCUSDT", "ETHUSDT"])

# Función de precio real Binance
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

# --- DISTRIBUCIÓN DE PANTALLA: GRÁFICO A UN LADO, CALCULADORA AL OTRO ---
col_grafico, col_panel = st.columns([1.7, 1.3])

with col_grafico:
    st.subheader(f"📊 Gráfico en Vivo: {activo_sel}")
    ticker_tv = f"BINANCE:{activo_sel}"
    widget_tv = f"""
    <div style="height:650px;width:100%">
      <div id="tv_chart" style="height:650px;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{ticker_tv}",
        "interval": "60",
        "timezone": "Etc/UTC",
        "theme": "dark",
        "style": "1",
        "locale": "es",
        "toolbar_bg": "#1e222d",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tv_chart",
        "studies": [
          "BB@tv-basicstudies",
          "MASimple@tv-basicstudies"
        ]
      }});
      </script>
    </div>
    """
    components.html(widget_tv, height=660)

with col_panel:
    st.subheader("🎯 Panel de Cálculo y Niveles")
    
    st.metric(label=f"Precio Actual Binance", value=f"${precio_en_vivo:,.2f}")
    
    tipo_operacion = st.radio("Dirección", ["LONG", "SHORT"], horizontal=True)

    precio_manual = st.number_input("Precio de Entrada ($)", value=precio_en_vivo, step=1.0, format="%.2f")
    
    sl_sugerido = precio_manual * 0.99 if tipo_operacion == "LONG" else precio_manual * 1.01
    sl_manual = st.number_input("Stop Loss - SL ($)", value=sl_sugerido, step=1.0, format="%.2f")
    
    tp_sugerido = precio_manual * 1.02 if tipo_operacion == "LONG" else precio_manual * 0.98
    tp_manual = st.number_input("Take Profit - TP ($)", value=tp_sugerido, step=1.0, format="%.2f")

    # Cálculos matemáticos de riesgo
    riesgo_dinero = capital * (riesgo_usr_pct / 100.0)
    riesgo_unitario = abs(precio_manual - sl_manual)
    lote_posicion = riesgo_dinero / riesgo_unitario if riesgo_unitario > 0 else 0.0

    if tipo_operacion == "LONG":
        ganancia_proyectada = lote_posicion * abs(tp_manual - precio_manual)
        rr_actual = abs(tp_manual - precio_manual) / riesgo_unitario if riesgo_unitario > 0 else 0.0
    else:
        ganancia_proyectada = lote_posicion * abs(precio_manual - tp_manual)
        rr_actual = abs(precio_manual - tp_manual) / riesgo_unitario if riesgo_unitario > 0 else 0.0

    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.metric("Lote Exacto", f"{lote_posicion:.4f}")
    c2.metric("Riesgo ($)", f"${riesgo_dinero:,.2f}")
    
    c3, c4 = st.columns(2)
    c3.metric("Ratio R:R", f"1 : {rr_actual:.2f}")
    c4.metric("Ganancia Proyectada", f"${ganancia_proyectada:,.2f}")

    if st.button("📝 Registrar en Bitácora", use_container_width=True, type="primary"):
        nueva_orden = {
            "ID": len(st.session_state.ordenes_activas) + len(st.session_state.bitacora) + 1,
            "Símbolo": activo_sel,
            "Tipo": tipo_operacion,
            "Entrada": f"{precio_manual:.2f}",
            "SL": f"{sl_manual:.2f}",
            "TP": f"{tp_manual:.2f}",
            "Lote": f"{lote_posicion:.4f}",
            "Riesgo ($)": f"${riesgo_dinero:.2f}"
        }
        st.session_state.ordenes_activas.append(nueva_orden)
        st.success("¡Operación registrada correctamente!")

st.divider()

st.subheader("📋 Historial y Bitácora Activa")
if st.session_state.ordenes_activas:
    st.dataframe(pd.DataFrame(st.session_state.ordenes_activas), use_container_width=True)
    if st.button("Cerrar y Archivar Operación"):
        archivada = st.session_state.ordenes_activas.pop(0)
        st.session_state.bitacora.append(archivada)
        st.rerun()
else:
    st.info("No hay operaciones activas en este momento.")
