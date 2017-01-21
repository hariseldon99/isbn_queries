#!/usr/bin/env python
from __future__ import division, print_function
import sys, urllib2, json, csv
import argparse
from tabulate import tabulate
#Enter your API key below:
APIKEY = 'XXXXXX'
desc = """
       Downloads the minimum prices from an input of book ISBN
       numbers.
       Usage:
       ./isbn_query.py -i ISBN_FILE -o OUTPUT_CSV
       """
#Try to import progressbars if available
try:
    from progressbar import Bar, ETA, Percentage
    pbar_avail = True
    isbndb_widgets = \
        ['Downoading price info: ', Percentage(), ' ', Bar(), ' ', ETA()]
except ImportError:
    pbar_avail = False
    isbndb_widgets = 'Downoading price info: '  
try:
    import progressbar
except ImportError:
    pass    


isbndb_json_url = 'http://isbndb.com/api/v2/json'
isbndb_widgets = ['Downloading price data: ',\
      Percentage(), ' ', Bar(), ' ', ETA()]

def input():
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-i', '--input',\
      help="input file containing isbn numbers in a column")
    parser.add_argument('-o', '--output',\
      help="output file containing isbn numbers and prices in csv")  

    return parser.parse_args()

def get_min_price(isbn, apikey):
    isbn_url = isbndb_json_url + '/' + apikey + '/prices/' + str(isbn)
    res = urllib2.urlopen(isbn_url)
    dictres = json.load(res) 
    if dictres.has_key(u'error') or dictres[u'data'] == []:
        minprice = None
    else:
        prices =  [(float(item[u'price']), item[u'currency_code'])\
                                            for item in dictres[u'data']]
        minprice = min(prices, key = lambda t: t[0])
    return minprice

if __name__ == '__main__':
    args_in = input()
    isbnlist = open(args_in.input).read().splitlines()
    isbnlist = map(int, isbnlist)
    if pbar_avail:
        pbar_max = len(isbnlist)
        bar = progressbar.ProgressBar(widgets=isbndb_widgets,\
                              max_value=pbar_max, redirect_stdout=False)
        bar_pos = 0
        bar.update(bar_pos)
    else:
        print(isbndb_widgets)   
    minprices = []
    for isbn in isbnlist:
        minp = get_min_price(isbn, APIKEY)
        if pbar_avail:
            bar.update(bar_pos)
            bar_pos += 1
        if minp is not None:
            minprices.append(minp[0])
        else:
            minprices.append('None')
    writedata = zip(isbnlist, minprices)
    print("Downloaded Prices:")
    print(tabulate(writedata, headers=['ISBN', 'Min. Price (USD)'], \
                                                tablefmt='fancy_grid'))
    with open(args_in.output,'wb') as r:
        wr = csv.writer(r, dialect='excel')
        for row in writedata:
            wr.writerow(row)
