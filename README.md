# Quant_Momentum_Trading

Project of predicting an investment porfolio based on the momentum of the stocks at moment of testing. Using API sclaping data off of https://sandbox.iexapis.com/ in a sandbox, an up-to-date solution can be found.

The project consists of calculating the momentum of the stock price (via looking at the pricing increase of the stock) over a chosen number of days. A parameter of chosen days can be chosen accordingly to fit the investor purpose. 

Then calculate a percentile of portfolio in how much momentum the individual stocks have, rank them and take the top 50 from the S&P500. Once this is done, the amount of investment (given inital sum) will be calucated to make an informed investment decision about how much an investor should be spending on an individual stock.

Project idea taken from:
https://www.freecodecamp.org/news/algorithmic-trading-using-python-course/

