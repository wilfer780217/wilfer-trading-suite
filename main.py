import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Wilfer Trading Suite Pro", layout="wide", page_icon="📊")

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

# --- INTERFAZ COMPLETA LIMPIA ---
st.title("⚡ WILFER TRADING SUITE PRO")

st.sidebar.header("⚙️ Gestión de Cuenta")
capital = st.sidebar.number_input("Capital Inicial ($)", value=1000.0, step=100.0)

# Simulación de datos exactos de tu motor
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

tabs = st.tabs(list(mercados_activos.keys()))

for tab, (activo, df) in zip(tabs, mercados_activos.items()):
    with tab:
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

        st.subheader(f"📊 Panel de Análisis: {activo}")
        
        # Bloques Métricos Principales
        c1, c2 = st.columns(2)
        c1.metric("Precio Actual", f"{precio:.5f}")
        c2.metric(f"Tendencia (SMA {cfg['sma']})", f"{sma:.5f}")
        
        c3, c4 = st.columns(2)
        c3.metric("Volatilidad (ATR)", f"{atr:.5f}")
        c4.metric("Rango Fibonacci (61.8% - 50%)", f"[{f618:.4f} - {f500:.4f}]")

        st.divider()

        # Evaluación de Señales de Entrada
        if en_zona:
            tipo = "LONG (COMPRA)" if es_alcista else "SHORT (VENTA)"
            if es_alcista:
                sl = precio - (atr * cfg["sl_mult"])
                riesgo_unitario = precio - sl
                tp = precio + (riesgo_unitario * cfg["rr"])
            else:
                sl = precio + (atr * cfg["sl_mult"])
                riesgo_unitario = sl - precio
                tp = precio - (riesgo_unitario * cfg["rr"])
            capital_a_arriesgar = motor.capital_inicial * cfg["riesgo_pct"]
            
            st.success(f"🚨 ¡SEÑAL CONFIRMADA: {tipo}!")
            
            m1, m2 = st.columns(2)
            m1.metric("Entrada Exacta", f"{precio:.5f}")
            m1.metric("Stop Loss (SL)", f"{sl:.5f}")
            m2.metric("Take Profit (TP)", f"{tp:.5f}")
            m2.metric("Riesgo Monetario", f"${capital_a_arriesgar:.2f} ({cfg['riesgo_pct']*100}%)")
        else:
            st.info("⏳ [ESTADO]: Fuera de zona áurea. Esperando retroceso matemático...")

        st.divider()
        st.write("📋 **Tabla de Historial Técnico Reciente**")
        st.dataframe(df_calc[['close', 'sma', 'atr', 'fib_500', 'fib_618']].tail(10), use_container_width=True)
