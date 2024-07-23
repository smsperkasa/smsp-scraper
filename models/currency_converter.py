import yfinance as yf

from logger.logging_config import logger


class CurrencyConverter:

    def get_exchange_rates_historical(self, base, target, start_date, end_date):
        base_target = f"{base}{target}=X"
        historical_data = yf.download(base_target, start=start_date, end=end_date)
        logger.info(
            f"Obtained historical data for {base} to {target} from {start_date} to {end_date}"
        )
        return historical_data

    def get_exchange_rates_latest(self, base, target):
        base_target = f"{base}{target}=X"
        data = yf.Ticker(base_target)
        today_data = data.history(period="1d")
        current_rate = today_data["Close"].iloc[0]
        logger.info(f"Obtained today's currency rate from {base} to {target}")
        return float(current_rate)
