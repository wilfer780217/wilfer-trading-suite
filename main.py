import numpy as np
import pandas as pd

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

    def analizar_todos(self, diccionario_datos):
        print("========================================================================")
        print("     WILFER TRADING SUITE - ESCANEO Y CÁLCULO TOTAL DE MERCADOS")
        print("========================================================================")
        for activo, df in diccionario_datos.items():
            df_calculado = self.calcular_mercado(activo, df)
            idx = len(df_calculado) - 1
            precio = df_calculado['close'].iloc[idx]
            f500 = df_calculado['fib_500'].iloc[idx]
            f618 = df_calculado['fib_618'].iloc[idx]
            sma = df_calculado['sma'].iloc[idx]
            atr = df_calculado['atr'].iloc[idx]
            cfg = self.config_mercados[activo]
            en_zona = (precio <= f500) and (precio >= f618)
            es_alcista = precio > sma
            print(f"\n📊 MERCADO: {activo}")
            print(f"   • Precio Actual      : {precio:.5f}")
            print(f"   • Rango Fibonacci    : [{f618:.5f}  ---  {f500:.5f}]")
            print(f"   • Tendencia (SMA {cfg['sma']}): {sma:.5f}")
            print(f"   • Volatilidad (ATR)  : {atr:.5f}")
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
                capital_a_arriscar = self.capital_inicial * cfg["riesgo_pct"]
                print(f"   🚨 ¡SEÑAL CONFIRMADA: {tipo}!")
                print(f"      - Entrada Exacta  : {precio:.5f}")
                print(f"      - Stop Loss (SL)  : {sl:.5f}")
                print(f"      - Take Profit (TP): {tp:.5f}")
                print(f"      - Riesgo Monetario: ${capital_a_arriscar:.2f} ({cfg['riesgo_pct']*100}% del capital)")
            else:
                print(f"   ⏳ [ESTADO]: Fuera de zona áurea. Esperando retroceso matemático...")
        print("\n========================================================================")

if __name__ == "__main__":
    np.random.seed(999)
    n = 150
    p_btc = 64000 + np.cumsum(np.random.randn(n) * 150)
    df_btc = pd.DataFrame({'open': p_btc, 'high': p_btc + 200, 'low': p_btc - 200, 'close': p_btc + np.random.randn(n)*50})
    p_eth = 3100 + np.cumsum(np.random.randn(n) * 25)
    df_eth = pd.DataFrame({'open': p_eth, 'high': p_eth + 40, 'low': p_eth - 40, 'close': p_eth + np.random.randn(n)*10})
    p_eur = 1.0850 + np.cumsum(np.random.randn(n) * 0.0008)
    df_eur = pd.DataFrame({'open': p_eur, 'high': p_eur + 0.002, 'low': p_eur - 0.002, 'close': p_eur + np.random.randn(n)*0.0005})
    mercados_activos = {"BTCUSD": df_btc, "ETHUSD": df_eth, "EURUSD": df_eur}
    motor = WilferTradingEngineTotal(capital_inicial=1000.0)
    motor.analizar_todos(mercados_activos)
