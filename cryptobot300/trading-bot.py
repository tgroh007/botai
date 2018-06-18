import time
import sys, getopt
import datetime
from poloniex import poloniex

def main(argv):
	period = 300
	pair = "BTC_LTC"
	prices = []
	currentMovingAverage = 0;
	lengthOfMA = 0
	startTime = False
	endTime = False
	historicalData = False
	tradePlaced = False
	typeOfTrade = False
	dataDate = ""
	orderNumber = ""

	try:
		opts, args = getopt.getopt(argv,"hp:c:n:s:e:",["period=","currency=","points="])
	except getopt.GetoptError:
		print ('trading-bot.py -p <period length> -c <currency pair> -n <period of moving average>')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print ('trading-bot.py -p <period length> -c <currency pair> -n <period of moving average>')
			sys.exit()
		elif opt in ("-p", "--period"):
			if (int(arg) in [300,900,1800,7200,14400,86400]):
				period = arg
			else:
				print ('Poloniex requires periods in 300,900,1800,7200,14400, or 86400 second increments')
				sys.exit(2)
		elif opt in ("-c", "--currency"):
			pair = arg
		elif opt in ("-n", "--points"):
			lengthOfMA = int(arg)
		elif opt in ("-s"):
			startTime = arg
		elif opt in ("-e"):
			endTime = arg



	conn = poloniex('5NTVQ4P4-AIUEPN28-E57OXVUV-7C19OZCJ','b4182fec0b5c578563b6ebe9367c41d6609e06af8ef2960f0159a5338980e426ed3939c9e53f9afbcf3be279f26eb3a800da2c6b785dd2680764be16ee523323')

	if (startTime):
		historicalData = conn.api_query("returnChartData",{"currencyPair":pair,"start":startTime,"end":endTime,"period":period})

	while True:
		if (startTime and historicalData):
			nextDataPoint = historicalData.pop(0)
			lastPairPrice = nextDataPoint['weightedAverage']
			dataDate = datetime.datetime.fromtimestamp(int(nextDataPoint['date'])).strftime('%Y-%m-%d %H:%M:%S')
		elif(startTime and not historicalData):
			exit()
		else:
			currentValues = conn.api_query("returnTicker")
			lastPairPrice = currentValues[pair]["last"]
			dataDate = datetime.datetime.now()

		if (len(prices) > 0):
			currentMovingAverage = sum(prices) / float(len(prices))
			previousPrice = prices[-1]
			if (not tradePlaced):
				if ( (lastPairPrice > currentMovingAverage) and (lastPairPrice < previousPrice) ):
					print ("SELL ORDER")
					orderNumber = conn.sell(pair,lastPairPrice,.01)
					tradePlaced = True
					typeOfTrade = ("short")
				elif ( (lastPairPrice < currentMovingAverage) and (lastPairPrice > previousPrice) ):
					print ("BUY ORDER")
					orderNumber = conn.buy(pair,lastPairPrice,.01)
					tradePlaced = True
					typeOfTrade = "long"
			elif (typeOfTrade == "short"):
				if ( lastPairPrice < currentMovingAverage ):
					print ("EXIT TRADE")
					conn.cancel(pair,orderNumber)
					tradePlaced = False
					typeOfTrade = False
			elif (typeOfTrade == "long"):
				if ( lastPairPrice > currentMovingAverage ):
					print ("EXIT TRADE")
					conn.cancel(pair,orderNumber)
					tradePlaced = False
					typeOfTrade = False
		else:
			previousPrice = 0

		print ("%s Period: %ss %s: %s Moving Average: %s") % (dataDate,period,pair,lastPairPrice,currentMovingAverage)

		prices.append(float(lastPairPrice))
		prices = prices[-lengthOfMA:]
		if (not startTime):
			time.sleep(int(period))


if __name__ == "__main__":
	main(sys.argv[1:])
