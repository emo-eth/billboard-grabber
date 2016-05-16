#!/usr/bin/env python

import billboard
from ChartDateIters import BillboardIter
import json
from datetime import date
from jwp.jwcache import jwcache
from jwp.jwmultithreaded import jwmultithreaded
from jwp.jwcsv import jwcsv


__author__ = "James Wenzel"
__license__ = "MIT"
__email__ = "wenzel.james.r@gmail.com"

'''
TODO:
    -- Make more modular subclasses?
    -- Maybe append featured artists to song name? Need to consult Echo Nest
    -- Fix clean artist name to allow for numeric commas (at least)
    -- remove main methods from __init__

'''


class ChartGrabber(jwcsv, jwcache, jwmultithreaded):

    '''This doesn't do much on its own, but provides the base for more modular
    subclasses'''

    def __init__(self, start_date='1958-08-09', end_date=str(date.today()),
                 charts_to_load=('hot-100',), cache_enabled=True):
        self.dates = BillboardIter(start_date, end_date)
        self.charts_to_load = charts_to_load
        if cache_enabled:
            self.cache = self.load_cache('bbCache.json')
        else:
            self.cache = {}
        self.multithread(self.get_chart, self.pool_args, processes=32)
        if cache_enabled:
            self.write_cache('bbCache.json', self.cache)

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


class TopSongs(ChartGrabber):

    '''This particular subclass gets a set of all of the top xx percent of
    songs from included charts for a span of weeks'''

    def __init__(self, start_date='1958-08-09', end_date=str(date.today()),
                 charts_to_load=('hot-100',), top_percent=40,
                 outfile='results', cache_enabled=True):
        super(TopSongs, self).__init__(start_date, end_date, charts_to_load,
                                       cache_enabled)
        self.outfile = outfile
        # self.top_songs = list(set(self.get_top(self.weekly_charts,
        #                                        top_percent)))

    def get_top(self, charts, percent):
        '''Creates a list of title/name tuples.
        Can be converted into a set of unique songs'''
        assert percent < 1 or percent <= 100
        if percent >= 1:
            percent = percent / 100.0  # py 2 needs .0 for double conversion
        top_songs = []
        for chart in charts:
            entries = chart['entries']
            for entry in range(int(len(entries) * percent)):
                song = entries[entry]
                top_songs.append((self.clean_song_name(song['title']),
                                  self.clean_artist_name(song['artist'])))
        return top_songs


class ChartLyrics(TopSongs):
    ''' will maybe eventually remove featuring etc
    from song titles and artists '''

    def __init__(self, start_date='1958-08-09', end_date=str(date.today()),
                 charts_to_load=('hot-100',), top_percent=40,
                 outfile='results', cache_enabled=True):
        super(TopSongs, self).__init__(start_date, end_date, charts_to_load,
                                       cache_enabled)
        self.outfile = outfile
        self.top_songs = list(set(self.get_top(self.weekly_charts,
                                               top_percent)))

'''

Example caches specified charts since beginning of 2013.

ChartGrabber(start_date='2013-01-01',
             charts_to_load=('rap-song',
                             'r-b-hip-hop-songs',
                             'country-songs',
                             'alternative-songs',
                             'hot-100'))

'''
