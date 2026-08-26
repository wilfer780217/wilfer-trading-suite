import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Wilfer Trading Suite - Total Pro", layout="wide", page_icon="⚡")

# Estado de la sesión para la bitácora
if "bitacora" not in st.session_state:
    st.session_state.bitacora = []

class WilferTradingEngineTotal:
    def __init__(self, capital_inicial=1000.0):
        self.capital_inicial = capital_inicial
        self.config_mercados = {
            "BTCUSD": {"sma": 50, "atr_p": 14, "sl_mult": 3.0, "rr": 2.5, "riesgo_pct": 0.02},
            "ETHUSD": {"sma": 50, "atr_p": 14, "sl_mult": 2.5, "rr": 2.5, "riesgo_pct": 0.02},
            "EURUSD": {"sma": 50, "atr_p": 14, "sl_mult": 2.0, "rr": 2.0, "riesgo_pct": 0.015}
        }

    def calcular_mercado(self, nombre_activo, df):
        cfg = self.config_mercados[nombre_activo]
        df['sma'] = df['close'].rolling(window=cfg["sma"]).mean()
        hl = df['high'] - df['low']
        hc = np.abs(df['high'] - df['close'].shift())
        lc = np.abs(df['low'] - df['close'].shift())
        df['atr'] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(window=cfg["atr_p"]).mean()
        df['swing_high'] = df['high'].rolling(window=20, min_periods=1).max()
        df['swing_low'] = df['low'].rolling(window=20, min_periods=1).min()
        rango_fib = df['swing_high'] - df['swing_low']
        df['fib_500'] = df['swing_high'] - (rango_fib * 0.500)
        df['fib_618'] = df['swing_high'] - (rango_fib * 0.618)
        return df

st.title("⚡ WILFER TRADING SUITE - MOTOR Y GESTIÓN TOTAL")

# Pestañas principales para tener todo a la mano sin perder espacio
tab_motor, tab_grafico, tab_bitacora = st.tabs([
    "📊 Motor de Escaneo & Señales", 
    "📈 Gráfico Vivo TradingView", 
    "📖 Bitácora & Historial"
])

# --- PESTAÑA 1: MOTOR DE CÁLCULO Y GESTIÓN DE RIESGO ---
with tab_motor:
    st.sidebar.header("⚙️ Configuración General")
    capital = st.sidebar.number_input("Capital Inicial de la Cuenta ($)", value=10000.0, step=500.0)

    # Generación de Datos de Mercado
    np.random.seed(999)
    n = 150
    p_btc = 64000 + np.cumsum(np.random.randn(n) * 150)
    df_btc = pd.DataFrame({'open': p_btc, 'high': p_btc + 200, 'low': p_btc - 200, 'close': p_btc + np.random.randn(n)*50})
    p_eth = 3100 + np.cumsum(np.random.randn(n) * 25)
    df_eth = pd.DataFrame({'open': p_eth, 'high': p_eth + 40, 'low': p_eth - 40, 'close': p_eth + np.random.randn(n)*10})
    p_eur = 1.0850 + np.cumsum(np.random.randn(n) * 0.0008)
    df_eur = pd.DataFrame({'open': p_eur, 'high': p_eur + 0.002, 'low': p_eur - 0.002, 'close': p_eur + np.random.randn(n)*0.0005})

    mercados_activos = {"BTCUSD": df_btc, "ETHUSD": df_eth, "EURUSD": df_eur}
    motor = WilferTradingEngineTotal(capital_inicial=capital)

    sub_tabs = st.tabs(list(mercados_activos.keys()))

    for sub_tab, (activo, df) in zip(sub_tabs, mercados_activos.items()):
        with sub_tab:
            df_calc = motor.calcular_mercado(activo, df)
            idx = len(df_calc) - 1
            precio = df_calc['close'].iloc[idx]
            f500 = df_calc['fib_500'].iloc[idx]
            f618 = df_calc['fib_618'].iloc[idx]
            sma = df_calc['sma'].iloc[idx]
            atr = df_calc['atr'].iloc[idx]
            cfg = motor.config_mercados[activo]
            en_zona = (precio <= f500) and (precio >= f618)
            es_alcista = precio > sma

            st.subheader(f"Análisis Técnico de {activo}")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Precio Actual", f"{precio:.5f}")
            c2.metric(f"Tendencia (SMA {cfg['sma']})", f"{sma:.5f}")
            c3.metric("Volatilidad (ATR)", f"{atr:.5f}")
            c4.metric("Rango Fib (61.8% - 50%)", f"[{f618:.4f} - {f500:.4f}]")

            if en_zona:
                tipo = "LONG (COMPRA ALCISTA)" if es_alcista else "SHORT (VENTA BAJISTA)"
                if es_alcista:
                    sl = precio - (atr * cfg["sl_mult"])
                    riesgo_unitario = precio - sl
                    tp = precio + (riesgo_unitario * cfg["rr"])
                else:
                    sl = precio + (atr * cfg["sl_mult"])
                    riesgo_unitario = sl - precio
                    tp = precio - (riesgo_unitario * cfg["rr"])
                
                capital_a_arriesgar = motor.capital_inicial * cfg["riesgo_pct"]
                ganancia_proyectada = capital_a_arriesgar * cfg["rr"]
                
                st.success(f"🚨 ¡SEÑAL CONFIRMADA: {tipo}!")
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Entrada Exacta", f"{precio:.5f}")
                m2.metric("Stop Loss (SL)", f"{sl:.5f}")
                m3.metric("Take Profit (TP)", f"{tp:.5f}")
                m4.metric("Ganancia Esperada", f"${ganancia_proyectada:,.2f} USD")

                # Botón Guardar en Bitácora
                if st.button(f"💾 Guardar {activo} en Bitácora", key=f"btn_{activo}"):
                    st.session_state.bitacora.append({
                        "Activo": activo,
                        "Tipo": tipo,
                        "Entrada": f"{precio:.5f}",
                        "SL": f"{sl:.5f}",
                        "TP": f"{tp:.5f}",
                        "Ganancia ($)": f"${ganancia_proyectada:.2f}"
                    })
                    st.success("¡Operación guardada en la bitácora general!")

                # Botones Compartir Redes
                mensaje_senal = (
                    f"🚨 *WILFER TRADING SUITE - SEÑAL* 🚨\n\n"
                    f"📌 *Activo:* {activo}\n"
                    f"📈 *Dirección:* {tipo}\n"
                    f"🎯 *Entrada:* {precio:.5f}\n"
                    f"🛑 *Stop Loss:* {sl:.5f}\n"
                    f"🏆 *Take Profit:* {tp:.5f}\n"
                    f"💵 *Ganancia Proyectada:* ${ganancia_proyectada:,.2f} USD"
                )
                msg_encoded = urllib.parse.quote(mensaje_senal)
                link_wa = f"https://api.whatsapp.com/send?text={msg_encoded}"
                link_tg = f"https://t.me/share/url?url=&text={msg_encoded}"

                st.markdown("##### Compartir Señal Operativa:")
                col_w, col_t = st.columns(2)
                with col_w:
                    st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><button style="width:100%;background-color:#25D366;color:white;border:none;padding:10px;border-radius:5px;font-weight:bold;cursor:pointer;">📲 WhatsApp</button></a>', unsafe_allow_html=True)
                with col_t:
                    st.markdown(f'<a href="{link_tg}" target="_blank" style="text-decoration:none;"><button style="width:100%;background-color:#0088cc;color:white;border:none;padding:10px;border-radius:5px;font-weight:bold;cursor:pointer;">✈️ Telegram</button></a>', unsafe_allow_html=True)
            else:
                st.info("⏳ [ESTADO]: Fuera de zona áurea. Esperando retroceso matemático...")

# --- PESTAÑA 2: GRÁFICO EN VIVO TRADINGVIEW ---
with tab_grafico:
    st.subheader("📈 Gráfico Profesional en Vivo")
    simbolo_input = st.text_input("Seleccionar Símbolo para el Gráfico", value="BTCUSD").upper().strip()
    ticker_tv = f"BINANCE:{simbolo_input}T" if simbolo_input in ["BTCUSD", "ETHUSD"] else f"FOREXCOM:{simbolo_input}"

    tv_widget = f"""
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
    """
    components.html(tv_widget, height=560)

# --- PESTAÑA 3: BITÁCORA ---
with tab_bitacora:
    st.subheader("📖 Historial y Bitácora de Operaciones")
    if st.session_state.bitacora:
        st.dataframe(pd.DataFrame(st.session_state.bitacora), use_container_width=True)
        if st.button("🗑️ Vaciar Bitácora"):
            st.session_state.bitacora = []
            st.rerun()
    else:
        st.info("No hay operaciones registradas en la bitácora todavía.")
