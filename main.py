import alpaca_trade_api as tradeapi
import random
import time
import datetime
import requests
import advisor

API_KEY = "<api_key>"
API_SECRET = "<api_secret>"
APCA_API_BASE_URL = "https://paper-api.alpaca.markets"


class Alpaca:
	def __init__(self):
		self.alpaca = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')
		self.alpaca1 = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v1')

		def get_tradable_assets():
			assets = self.alpaca.list_assets()
			tradable = {}
			for asset in assets:
				if asset.tradable:
					entry = {'exchange': asset.exchange}
					tradable[asset.symbol] = entry
			return tradable

		stock_universe = list(get_tradable_assets())
		random.shuffle(stock_universe)

		# Get our account information.
		account = self.alpaca.get_account()

		# Check if our account is restricted from trading.
		if account.trading_blocked:
			print('Account is currently restricted from trading.')

		# Check how much money we can use to open new positions.
		print(f'${account.daytrading_buying_power} is available as buying power.')

		while True:
			print(datetime.datetime.now().strftime("%H:%M:%S"))
			for symbol in stock_universe:
				barset = self.alpaca1.get_barset(symbol, 'day', limit=30)
				last_month = [day.c for day in barset[symbol]]
				try:
					price = self.alpaca1.get_last_quote(symbol).askprice
				except requests.exceptions.HTTPError:
					continue
				if len(last_month) > 20:
					advice = advisor.advise(last_month, price)
					if price > 0 and advice:
						try:
							self.alpaca.get_position(symbol)
						except:
							buffer = 2000
							buying_power = float(self.alpaca.get_account().daytrading_buying_power)-buffer
							quantity = int(buying_power/5. / price)
							if quantity > 0:
								self.alpaca.submit_order(
									symbol=symbol,
									qty=quantity,
									side='buy',
									type='market',
									time_in_force='day'
								)
								print(f"Bought {quantity}x {symbol} for {price}$/share.")

					elif not advice:
						try:
							quantity = int(self.alpaca.get_position(symbol).qty)
							if quantity > 0:
								self.alpaca.submit_order(
									symbol=symbol,
									qty=quantity,
									side='sell',
									type='market',
									time_in_force='day'
								)
								print(f"Sold {quantity}x {symbol} for {price}$/share.")
						except Exception as e:
							print(e)
			time.sleep(60)


al = Alpaca()
