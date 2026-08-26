import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Wilfer Trading Suite Pro", layout="wide", page_icon="⚡")

# Estado de la sesión para la bitácora
if "bitacora" not in st.session_state:
    st.session_state.bitacora = []

st.title("⚡ WILFER TRADING SUITE - SUITE COMPLETA")

col_izq, col_der = st.columns([1, 2])

# --- COLUMNA IZQUIERDA: PARÁMETROS, SEÑALES Y BITÁCORA ---
with col_izq:
    st.subheader("⚙️ Gestión de Capital y Riesgo")
    capital = st.number_input("Capital Total de la Cuenta ($)", value=10000.0, step=500.0)
    riesgo_pct = st.slider("Riesgo por Operación (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    riesgo_dinero = capital * (riesgo_pct / 100.0)
    
    st.metric("Riesgo Máximo en Dinero", f"${riesgo_dinero:,.2f} USD")
    st.divider()

    st.subheader("🌐 Selección de Activo y Mercado")
    simbolo = st.text_input("Símbolo del Activo (Ej: BTCUSD, ETHUSD, EURUSD)", value="BTCUSD").upper().strip()
    
    st.divider()
    st.subheader("🎯 Panel de Entrada y Parámetros Operativos")
    
    tipo_operacion = st.radio("Tipo de Operación", ["LONG (Compra Alcista)", "SHORT (Venta Bajista)"], horizontal=True)
    precio_entrada = st.number_input("Precio de Entrada ($)", value=65000.0, step=10.0)
    stop_loss = st.number_input("Límite de Pérdida - Stop Loss ($)", value=64000.0 if "LONG" in tipo_operacion else 66000.0, step=10.0)
    take_profit = st.number_input("Toma de Ganancia - Take Profit ($)", value=67500.0 if "LONG" in tipo_operacion else 62500.0, step=10.0)

    # Cálculos matemáticos de la operación
    if "LONG" in tipo_operacion:
        distancia_sl = precio_entrada - stop_loss
        distancia_tp = take_profit - precio_entrada
    else:
        distancia_sl = stop_loss - precio_entrada
        distancia_tp = precio_entrada - take_profit

    if distancia_sl > 0:
        ratio_rr = distancia_tp / distancia_sl
        unidades = riesgo_dinero / distancia_sl
    else:
        ratio_rr = 0.0
        unidades = 0.0

    st.markdown(f"**Ratio Riesgo:Beneficio:** `1:{ratio_rr:.2f}`")
    st.markdown(f"**Tamaño de Posición Recomendado:** `{unidades:.4f} unidades`")

    # Botón para guardar en Bitácora
    if st.button("💾 Guardar en Bitácora"):
        st.session_state.bitacora.append({
            "Activo": simbolo,
            "Tipo": tipo_operacion.split()[0],
            "Entrada": precio_entrada,
            "Stop Loss": stop_loss,
            "Take Profit": take_profit,
            "R:R": f"1:{ratio_rr:.2f}",
            "Riesgo ($)": f"${riesgo_dinero:.2f}"
        })
        st.success("¡Operación guardada en la bitácora!")

    st.divider()
    st.subheader("📲 Compartir Señal Operativa")
    
    # Mensaje formateado para redes
    mensaje_senal = (
        f"🚨 *SEÑAL OPERATIVA WILFER TRADING SUITE* 🚨\n\n"
        f"📌 *Activo:* {simbolo}\n"
        f"📈 *Dirección:* {tipo_operacion}\n"
        f"🎯 *Precio Entrada:* {precio_entrada}\n"
        f"🛑 *Stop Loss:* {stop_loss}\n"
        f"🏆 *Take Profit:* {take_profit}\n"
        f"⚖️ *Ratio R:R:* 1:{ratio_rr:.2f}\n"
        f"🛡️ *Riesgo:* ${riesgo_dinero:.2f} ({riesgo_pct}%)"
    )
    
    msg_encoded = urllib.parse.quote(mensaje_senal)
    link_wa = f"https://api.whatsapp.com/send?text={msg_encoded}"
    link_tg = f"https://t.me/share/url?url=&text={msg_encoded}"

    c_wa, c_tg = st.columns(2)
    with c_wa:
        st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="width:100%;background-color:#25D366;color:white;border:none;padding:10px;border-radius:5px;cursor:pointer;font-weight:bold;">📲 WhatsApp</button></a>', unsafe_allow_html=True)
    with c_tg:
        st.markdown(f'<a href="{link_tg}" target="_blank" style="text-decoration:none;"><button style="width:100%;background-color:#0088cc;color:white;border:none;padding:10px;border-radius:5px;cursor:pointer;font-weight:bold;">✈️ Telegram</button></a>', unsafe_allow_html=True)

# --- COLUMNA DERECHA: TRADINGVIEW Y BITÁCORA ---
with col_der:
    st.subheader(f"📈 Gráfico en Vivo: {simbolo}")
    
    ticker_tv = f"BINANCE:{simbolo}T" if simbolo in ["BTCUSD", "ETHUSD"] else f"FOREXCOM:{simbolo}"

    tv_widget = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:550px;width:100%">
      <div id="tradingview_chart" style="height:550px;width:100%"></div>
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
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    components.html(tv_widget, height=560)
    
    st.divider()
    st.subheader("📖 Bitácora de Operaciones")
    if st.session_state.bitacora:
        st.dataframe(pd.DataFrame(st.session_state.bitacora), use_container_width=True)
    else:
        st.info("La bitácora está vacía. Guarda una operación desde el panel izquierdo.")
