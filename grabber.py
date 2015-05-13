import billboard
from BillboardIter import BillboardIter
import csv
import json
import FileNotFoundError
from multiprocessing.pool import ThreadPool

__author__ = "James Wenzel"
__license__ = "MIT"
__email__ = "wenzel.james.r@gmail.com"

'''
TODO:
    --turn into general grabber class that takes in arguments
    --output CSV or JSON for echonest/spotify
'''

# load cache; create cache if none
try:
    with open('bbCache.json') as data_file:
        cache = json.load(data_file)
except FileNotFoundError as e:
    cache = {}
    with open('bbCache.json', 'w') as outfile:
        json.dump(cache, outfile)

cache_updated = False  # keeps track of whether or not to writeout

# create the date iterator
dates = BillboardIter('2011-08-01', '2012-08-31')

# charts for us to load
chartNames = ('hot-100', 'dance-club-play-songs', 'alternative-songs')
weeklyCharts = []


def get_chart(date, chartName):
    global cache_updated
    dateStr = str(date)
    if dateStr in cache and chartName in cache[dateStr]:
        print('retrieving %s from cache' % (chartName + ' ' + dateStr))
        # if the chart for the date has been cached, load it
        return cache[chartName][dateStr]
    elif dateStr not in cache:
        cache[dateStr] = {}
        cache[dateStr][chartName] = []
    elif chartName not in cache[dateStr]:
        cache[dateStr][chartName] = []
    print('getting ' + chartName + ' ' + dateStr)
    chartData_object = billboard.ChartData(chartName, dateStr)
    if chartData_object:
        cache[dateStr][chartName] = [chartData_object.to_JSON()]
        cache_updated = True
        return cache[dateStr][chartName]

pool = ThreadPool(processes=4)
result = []
for date in dates:
    for name in chartNames:
        result.append(pool.apply_async(get_chart, [date, name]))

for r in result:
    try:
        res = r.get()
        weeklyCharts.append(res)
    except Exception as e:
        # print(e)
        cache_updated = False

if cache_updated:
    with open('bbCache.json', 'w') as outfile:
        json.dump(cache, outfile)
