import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="Wilfer Trading Suite Pro", layout="wide")

# Nombre del archivo local para guardar la bitácora permanentemente
ARCHIVO_BITACORA = "bitacora_wilfer.csv"

# Función para cargar la bitácora guardada en disco
def cargar_bitacora():
    if os.path.exists(ARCHIVO_BITACORA):
        return pd.read_csv(ARCHIVO_BITACORA)
    else:
        return pd.DataFrame(columns=["Fecha", "Activo", "Tipo", "Entrada", "Stop Loss", "Take Profit", "Nivel Fib 61.8%", "Lotes", "Riesgo USD"])

st.title("🛡️ WILFER TRADING SUITE PRO")
st.caption("Comando Estratégico de Trading - Panel Institucional con Fibonacci y Bitácora Permanente")
st.markdown("---")

# --- BARRA LATERAL: GESTIÓN DE RIESGO ---
st.sidebar.header("⚙️ Gestión de Capital y Riesgo")
capital = st.sidebar.number_input("Capital Total de la Cuenta ($)", value=10000.0, step=500.0)
riesgo_pct = st.sidebar.slider("Riesgo por Operación (%)", 0.5, 5.0, 1.0, 0.1)
riesgo_usd = capital * (riesgo_pct / 100.0)

st.sidebar.markdown("---")
st.sidebar.metric(label="Riesgo Máximo en Dinero", value=f"${riesgo_usd:.2f} USD")

# --- SELECCIÓN DE ACTIVO Y BROKER UNIVERSAL ---
st.sidebar.markdown("---")
st.sidebar.header("🌐 Selección de Activo y Mercado")

simbolo_input = st.sidebar.text_input("Símbolo del Activo (Ej: BTCUSD, GULF, XAUUSD, EURUSD)", value="BTCUSD").upper()
broker_origen = st.sidebar.selectbox("Origen de Datos / Broker", ["BINANCE", "OANDA", "CAPITALCOM", "FXCM", "FOREXCOM"])

# --- DISPOSICIÓN PRINCIPAL: TRADINGVIEW + CALCULADORA FIBONACCI Y RIESGO ---
col_grafico, col_panel = st.columns([2, 1])

with col_grafico:
    st.subheader(f"📈 Gráfico Real de Mercado ({simbolo_input} en {broker_origen})")
    
    symbol_full = f"{broker_origen}:{simbolo_input}" if broker_origen != "BINANCE" else f"BINANCE:{simbolo_input}T"
    
    tradingview_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:520px;width:100%;">
      <div id="tradingview_chart" style="height:520px;width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
      "autosize": true,
      "symbol": "{symbol_full}",
      "interval": "D",
      "timezone": "Etc/UTC",
      "theme": "dark",
      "style": "1",
      "locale": "es",
      "toolbar_bg": "#f1f3f6",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "container_id": "tradingview_chart"
    }}
      );
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    components.html(tradingview_html, height=540)

with col_panel:
    st.subheader("🎯 Planificación y Parámetros Tácticos")
    
    tipo_posicion = st.radio("Dirección del Mercado", ["COMPRA (Alcista)", "VENTA (Bajista)"], horizontal=True)
    
    # --- MÓDULO FIBONACCI ---
    st.markdown("**📐 Calculadora de Niveles Fibonacci**")
    col_fib1, col_fib2 = st.columns(2)
    with col_fib1:
        precio_max = st.number_input("Precio Máximo (Swing High)", value=105.00, format="%.2f")
    with col_fib2:
        precio_min = st.number_input("Precio Mínimo (Swing Low)", value=90.00, format="%.2f")
    
    rango_fib = precio_max - precio_min
    if "COMPRA" in tipo_posicion:
        fib_618 = precio_max - (rango_fib * 0.618)
        fib_500 = precio_max - (rango_fib * 0.500)
        fib_382 = precio_max - (rango_fib * 0.382)
    else:
        fib_618 = precio_min + (rango_fib * 0.618)
        fib_500 = precio_min + (rango_fib * 0.500)
        fib_382 = precio_min + (rango_fib * 0.382)
        
    st.info(f"🎯 **Zona Áurea (61.8% Fib):** ${fib_618:.2f}")
    
    st.markdown("---")
    
    # --- NIVELES DE ORDEN ---
    precio_entrada = st.number_input("Precio de Entrada ($)", value=float(fib_618), format="%.2f")
    precio_sl = st.number_input("Límite de Pérdida (Stop Loss - SL)", value=float(precio_min if "COMPRA" in tipo_posicion else precio_max), format="%.2f")
    precio_tp = st.number_input("Toma de Ganancia (Take Profit - TP)", value=float(precio_max if "COMPRA" in tipo_posicion else precio_min), format="%.2f")
    
    distancia = abs(precio_entrada - precio_sl)
    lotes_sugeridos = riesgo_usd / distancia if distancia > 0 else 0.0
    
    st.success(f"**Lote / Tamaño de Posición:** {lotes_sugeridos:.2f} unidades")
    
    if st.button("🚀 GUARDAR OPERACIÓN EN LA BITÁCORA"):
        nueva_op = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Activo": simbolo_input,
            "Tipo": tipo_posicion,
            "Entrada": round(precio_entrada, 2),
            "Stop Loss": round(precio_sl, 2),
            "Take Profit": round(precio_tp, 2),
            "Nivel Fib 61.8%": round(fib_618, 2),
            "Lotes": round(lotes_sugeridos, 2),
            "Riesgo USD": round(riesgo_usd, 2)
        }])
        
        df_actual = cargar_bitacora()
        df_nuevo = pd.concat([df_actual, nueva_op], ignore_index=True)
        df_nuevo.to_csv(ARCHIVO_BITACORA, index=False)
        st.toast("¡Operación guardada permanentemente en el disco!", icon="✅")

# --- BITÁCORA DE HISTORIAL PERMANENTE ---
st.markdown("---")
st.subheader("📜 Bitácora Permanente de Registro (Guardada en Laptop)")

df_bitacora = cargar_bitacora()

if not df_bitacora.empty:
    st.dataframe(df_bitacora, use_container_width=True)
    
    # Botón de descarga a Excel/CSV
    csv_data = df_bitacora.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Bitácora Completa (CSV / Excel)",
        data=csv_data,
        file_name=f"bitacora_trading_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )
else:
    st.info("Sin registros en la bitácora. Completa tus niveles y presiona **GUARDAR OPERACIÓN**.")

# --- DIFUSIÓN MULTI-CANAL ---
st.markdown("---")
st.subheader("📲 Compartir Señal Operativa")

mensaje = (
    f"🚨 SEÑAL OPERATIVA - WILFER TRADING SUITE 🚨\n\n"
    f"📊 Activo: {simbolo_input}\n"
    f"📈 Dirección: {tipo_posicion}\n"
    f"🔵 Precio Entrada (Zona Fib 61.8%): ${precio_entrada:.2f}\n"
    f"🔴 Stop Loss (SL): ${precio_sl:.2f}\n"
    f"🟢 Take Profit (TP): ${precio_tp:.2f}\n"
    f"⚖️ Tamaño de Posición: {lotes_sugeridos:.2f} Lotes\n"
    f"🛡️ Gestión de Riesgo: ${riesgo_usd:.2f} USD"
)

st.text_area("Texto formateado para redes sociales:", mensaje, height=150)
texto_encoded = urllib.parse.quote(mensaje)

col_wa, col_tg = st.columns(2)
with col_wa:
    st.markdown(f"[📲 Compartir en WhatsApp](https://api.whatsapp.com/send?text={texto_encoded})")
with col_tg:
    st.markdown(f"[✈️ Compartir en Telegram](https://t.me/share/url?url=&text={texto_encoded})")