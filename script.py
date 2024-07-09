import yfinance as yf

historical_data = yf.download("USDIDR=X", start="2020-01-01", end="2020-12-31")
print(historical_data)
