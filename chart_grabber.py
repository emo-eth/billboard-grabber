import billboard
from billboard_iter import billboard_iter
import csv
import json
from multiprocessing.pool import ThreadPool
from datetime import date as date

__author__ = "James Wenzel"
__license__ = "MIT"
__email__ = "wenzel.james.r@gmail.com"

'''
TODO:
    -- Make more modular subclasses?
    -- Maybe append featured artists to song name? Need to consult Echo Nest
'''


class chart_grabber(object):

    '''This doesn't do much on its own, but provides the base for more modular
    subclasses'''

    cache_updated = False  # keeps track of whether or not to writeout

    def __init__(self, start_date='1958-08-09', end_date=str(date.today()),
                 charts_to_load=('hot-100',), cache_enabled=True):
        self.dates = billboard_iter(start_date, end_date)
        self.charts_to_load = charts_to_load
        if cache_enabled:
            self.load_cache('bbCache.json')
        else:
            self.cache = {}
        self.multithread(self.get_chart, ThreadPool,
                         self.pool_args)
        if cache_enabled:
            self.write_cache('bbCache.json')

    @property
    def pool_args(self):
        '''Arguments to pass into ThreadPool'''
        args = []
        for bb_date in self.dates:
            for chart in self.charts_to_load:
                args.append([bb_date, chart])
        return args
        # can this be done with a comprehension?

    @property
    def weekly_charts(self):
        '''Gets charts from cache'''
        self.dates.reset()
        charts = []
        for bb_date in self.dates:
            for chart in self.charts_to_load:
                charts.append(self.cache[str(bb_date)][chart])
        return charts

    def write_csv(self, name, results):
        '''Basis for writing out csv in a subclass'''
        with open('%s.csv' % self.outfile, 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(results)

    def load_cache(self, name):
        try:
            with open(name) as data_file:
                self.cache = json.load(data_file)
        except Exception:
            self.cache = {}
            with open(name, 'w') as outfile:
                json.dump(self.cache, outfile)

    def write_cache(self, name):
        if self.cache_updated:
            with open(name, 'w') as outfile:
                json.dump(self.cache, outfile)

    def multithread(self, fn, poolType, args=[[]]):
        '''Generic multithreading helper function'''
        pool = poolType(processes=4)
        thread_result = []
        for elem in args:
            thread_result.append(pool.apply_async(fn, elem))
        for r in thread_result:
            try:
                r.get()
            except Exception as e:
                print(type(e), e)
                self.cache_updated = False
                # don't writeout bad cache

    def get_chart(self, date, chartName):
        dateStr = str(date)
        if dateStr in self.cache and chartName in self.cache[dateStr]:
            print('%s cached' % (dateStr + ' ' + chartName))
            # if the chart for the date has been cached, load it
            return self.cache[dateStr][chartName]
        elif dateStr not in self.cache:
            self.cache[dateStr] = {}
            self.cache[dateStr][chartName] = []
        elif chartName not in self.cache[dateStr]:
            self.cache[dateStr][chartName] = []
        print(dateStr + ' ' + chartName + ' downloading')
        chartData_object = billboard.ChartData(chartName, dateStr)
        if chartData_object:
            # convert to json
            chartData = json.loads(chartData_object.to_JSON())
            self.cache[dateStr][chartName] = chartData
            self.cache_updated = True
            return self.cache[dateStr][chartName]


class top_songs(chart_grabber):

    '''This particular subclass gets a set of all of the top xx percent of
    songs from included charts for a span of weeks'''

    def __init__(self, start_date='1958-08-09', end_date=str(date.today()),
                 charts_to_load=('hot-100',), top_percent_of_chart=40,
                 outfile='results', cache_enabled=True):
        super(top_songs, self).__init__(start_date, end_date, charts_to_load,
                                        cache_enabled)
        self.outfile = outfile
        self.top = list(set(self.get_top(self.weekly_charts,
                                         top_percent_of_chart)))
        self.top.sort(key=lambda x: x[1])
        self.write_csv(self.outfile, self.top)

    def get_top(self, charts, percent):
        '''Creates a list of title/name tuples.
        Can be converted into a set of unique songs'''
        assert percent < 1 or percent < 100
        if percent >= 1:
            percent = percent / 100
        top = []
        for chart in charts:
            entries = chart['entries']
            for entry in range(int(len(entries) * percent)):
                song = entries[entry]
                top.append((self.clean_song_name(song['title']),
                            self.clean_artist_name(song['artist'])))
        return top

    def clean_artist_name(self, artist_name):
        '''Echonest is picky about featured artists'''
        artist_name = artist_name.strip()
        result = artist_name.split('Featuring')[0]
        result = result.split('Feat.')[0]
        result = result.split('Duet')[0]
        result = result.split('+')[0]
        result = result.split(',')[0]
        result = result.split('  ')[0]
        result = result.split('&')[0]
        if result == 'Sublime With Rome':
            return artist_name
        result = result.split('With')[0]
        result = result.strip()
        if result == 'fun.':
            return 'fun'
        return result

    def clean_song_name(self, song_name):
        result = song_name.replace('F**k', 'Fuck')
        return result
