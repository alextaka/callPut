This program prints out the cost and ITM barriers when buying both
a call and a put on a stock. It also calculates the maximum loss,
which can be lower than the cost of options if the call/put strike
prices overlap.

To find the prices, go to yahoo finance and select a stock. Open the
options page and copy the url. You can pass that url to this program
using the -U/--url option. You will also need to enter the stock price
using the -P/--price option. The program will default to Jan 2022 Uber
options with a current price as of Dec 7 2019

You can optionally enter constraints such as total cost, floor, and
ceiling to filter returned results

You will need to install the required python packages (requests, bs4)
