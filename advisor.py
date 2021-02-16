"""Decides how to act after analysing a month's worth of history"""

from pandas import DataFrame

std_dev = 1.3
window_size = 20


def advise(last_month_closes, curPrice):
	# Bollinger Bands
	def bb(price, window_size, num_of_std):
		rolling = price.rolling(window=window_size)
		rolling_mean = rolling.mean()
		rolling_std = rolling.std(ddof=0)
		a = rolling_std * num_of_std
		lower_band = rolling_mean - a
		upper_band = rolling_mean + a
		return lower_band[0].iloc[-1], upper_band[0].iloc[-1]

	last_month = DataFrame(last_month_closes)
	lower_val, upper_val = bb(last_month, window_size, std_dev)

	if curPrice <= lower_val:  # buy signal
		return True
	elif curPrice >= upper_val:  # sell signal
		return False
	else:  # hold signal
		return None


