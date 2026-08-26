(
echo import numpy as np
echo import pandas as pd
echo.
echo class WilferTradingEngineTotal:
echo     def __init__(self, capital_inicial=1000.0):
echo         self.capital_inicial = capital_inicial
echo         self.config_mercados = {
echo             "BTCUSD": {"sma": 50, "atr_p": 14, "sl_mult": 3.0, "rr": 2.5, "riesgo_pct": 0.02},
echo             "ETHUSD": {"sma": 50, "atr_p": 14, "sl_mult": 2.5, "rr": 2.5, "riesgo_pct": 0.02},
echo             "EURUSD": {"sma": 50, "atr_p": 14, "sl_mult": 2.0, "rr": 2.0, "riesgo_pct": 0.015}
echo         }
echo.
echo     def calcular_mercado(self, nombre_activo, df):
echo         cfg = self.config_mercados[nombre_activo]
echo         df['sma'] = df['close'].rolling(window=cfg["sma"]).mean()
echo         hl = df['high'] - df['low']
echo         hc = np.abs(df['high'] - df['close'].shift())
echo         lc = np.abs(df['low'] - df['close'].shift())
echo         df['atr'] = pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(window=cfg["atr_p"]).mean()
echo         df['swing_high'] = df['high'].rolling(window=20, min_periods=1).max()
echo         df['swing_low'] = df['low'].rolling(window=20, min_periods=1).min()
echo         rango_fib = df['swing_high'] - df['swing_low']
echo         df['fib_500'] = df['swing_high'] - (rango_fib * 0.500)
echo         df['fib_618'] = df['swing_high'] - (rango_fib * 0.618)
echo         return df
echo.
echo     def analizar_todos(self, diccionario_datos):
echo         print("========================================================================")
echo         print("     WILFER TRADING SUITE - ESCANEO Y CÁLCULO TOTAL DE MERCADOS")
echo         print("========================================================================")
echo         for activo, df in diccionario_datos.items():
echo             df_calculado = self.calcular_mercado(activo, df)
echo             idx = len(df_calculado) - 1
echo             precio = df_calculado['close'].iloc[idx]
echo             f500 = df_calculado['fib_500'].iloc[idx]
echo             f618 = df_calculado['fib_618'].iloc[idx]
echo             sma = df_calculado['sma'].iloc[idx]
echo             atr = df_calculado['atr'].iloc[idx]
echo             cfg = self.config_mercados[activo]
echo             en_zona = (precio <= f500) and (precio >= f618)
echo             es_alcista = precio > sma
echo             print(f"\n📊 MERCADO: {activo}")
echo             print(f"   • Precio Actual      : {precio:.5f}")
echo             print(f"   • Rango Fibonacci    : [{f618:.5f}  ---  {f500:.5f}]")
echo             print(f"   • Tendencia (SMA {cfg['sma']}): {sma:.5f}")
echo             print(f"   • Volatilidad (ATR)  : {atr:.5f}")
echo             if en_zona:
echo                 tipo = "LONG (COMPRA)" if es_alcista else "SHORT (VENTA)"
echo                 if es_alcista:
echo                     sl = precio - (atr * cfg["sl_mult"])
echo                     riesgo_unitario = precio - sl
echo                     tp = precio + (riesgo_unitario * cfg["rr"])
echo                 else:
echo                     sl = precio + (atr * cfg["sl_mult"])
echo                     riesgo_unitario = sl - precio
echo                     tp = precio - (riesgo_unitario * cfg["rr"])
echo                 capital_a_arriscar = self.capital_inicial * cfg["riesgo_pct"]
echo                 print(f"   🚨 ¡SEÑAL CONFIRMADA: {tipo}!")
echo                 print(f"      - Entrada Exacta  : {precio:.5f}")
echo                 print(f"      - Stop Loss (SL)  : {sl:.5f}")
echo                 print(f"      - Take Profit (TP): {tp:.5f}")
echo                 print(f"      - Riesgo Monetario: ${capital_a_arriscar:.2f} ({cfg['riesgo_pct']*100}% del capital)")
echo             else:
echo                 print(f"   ⏳ [ESTADO]: Fuera de zona áurea. Esperando retroceso matemático...")
echo         print("\n========================================================================")
echo.
echo if __name__ == "__main__":
echo     np.random.seed(999)
echo     n = 150
echo     p_btc = 64000 + np.cumsum(np.random.randn(n) * 150)
echo     df_btc = pd.DataFrame({'open': p_btc, 'high': p_btc + 200, 'low': p_btc - 200, 'close': p_btc + np.random.randn(n)*50})
echo     p_eth = 3100 + np.cumsum(np.random.randn(n) * 25)
echo     df_eth = pd.DataFrame({'open': p_eth, 'high': p_eth + 40, 'low': p_eth - 40, 'close': p_eth + np.random.randn(n)*10})
echo     p_eur = 1.0850 + np.cumsum(np.random.randn(n) * 0.0008)
echo     df_eur = pd.DataFrame({'open': p_eur, 'high': p_eur + 0.002, 'low': p_eur - 0.002, 'close': p_eur + np.random.randn(n)*0.0005})
echo     mercados_activos = {"BTCUSD": df_btc, "ETHUSD": df_eth, "EURUSD": df_eur}
echo     motor = WilferTradingEngineTotal(capital_inicial=1000.0)
echo     motor.analizar_todos(mercados_activos)
) > main.py