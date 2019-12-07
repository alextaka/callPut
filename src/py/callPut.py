import argparse
import math
import requests
from bs4 import BeautifulSoup

PROGRAM_DESCRIPTION = """
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
"""

FILTER_PARAMETERS = ["Strike", "Bid", "Ask"]

def formatPrice(price, currentPrice):
    diff = price - currentPrice
    percentage = math.floor(100 * diff / currentPrice)
    return str(price) + " (" + str(percentage) + "%)"

def printSpreads(calls, puts, args):
    count = 0
    for call in calls:
        for put in puts:
            cost = getCost(call) + getCost(put)
            ceilingBreakenven = call['Strike'] + cost
            floorBreakeven = put['Strike'] - cost
            maxLoss = cost - max(0, (put['Strike'] - call['Strike']))

            if (ceilingBreakenven < float(args.ceil) and
                floorBreakeven > float(args.floor) and
                cost < float(args.cost)):
                count += 1
                print("Call:", call['Strike'], "Put:", put['Strike'])
                print("Cost:", cost)
                print("ITM Boundary:",
                      "Low:", formatPrice(floorBreakeven, float(args.price)),
                      "High:", formatPrice(ceilingBreakenven, float(args.price)))
                print("Max Loss:", maxLoss)
                print()
    print("found", count, "possible contracts that fit the criteria")

# Input: contract - Object with the following fields:
# 'Strike': float
# 'Bid': float
# 'Ask': float
# Output: cost - float
def getCost(contract):
    return (contract['Bid'] + contract['Ask']) / 2

def filterTable(header, table, params=FILTER_PARAMETERS):
    filteredTable = []
    for row in table:
        data = {}
        for param in params:
            try:
                i = header.index(param)
                data[header[i]] = float(row[i])
            except ValueError:
                print(ValueError)
        filteredTable.append(data)
    return filteredTable

def parseTableHeader(header_html):
    header = []
    for th in header_html:
        header.append(th.text)

    return header

def parseTableRow(row):
    parsedRow = []
    for td in row:
        parsedRow.append(td.text)

    return parsedRow

def parseTable(table_html):
    table = []
    for row_html in table_html:
        table.append(parseTableRow(row_html))
    return table

def scrape(data_html):
    content = BeautifulSoup(data_html, "html.parser")
    tables = content.find_all("table")

    header_html = tables[0].find_all("tr")[0]
    calls_html = tables[0].find_all("tr")[1:]
    puts_html = tables[1].find_all("tr")[1:]

    header = parseTableHeader(header_html)
    calls_raw = parseTable(calls_html)
    puts_raw = parseTable(puts_html)

    calls = filterTable(header, calls_raw)
    puts = filterTable(header, puts_raw)

    return (calls, puts)

def main():
    ceilHelp = "Maximum price at which your call will cover costs"
    floorHelp = "Minimum price at which your put will cover costs"
    defaultUrl = "https://finance.yahoo.com/quote/UBER/options?date=1642723200"
    priceHelp = """Enter the current price of the ticker
    (I can't scrape it for some reason)"""
    urlHelp = """The yahoo finance url for the options you want to buy.
    For example: """ + defaultUrl
    argumentParser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
    argumentParser.add_argument("--cost", "-C", help="Maximum cost", default=float("inf"))
    argumentParser.add_argument("--ceil", "-T", help=ceilHelp, default=float("inf"))
    argumentParser.add_argument("--floor", "-F", help=floorHelp, default=float("-inf"))
    argumentParser.add_argument("--price", "-P", help=priceHelp, default=27.86)
    argumentParser.add_argument("--url", "-U", help=urlHelp, default=defaultUrl)
    args = argumentParser.parse_args()

    data_html = requests.get(args.url).content
    (calls, puts) = scrape(data_html)

    printSpreads(calls, puts, args)

if __name__ == "__main__":
    main()
