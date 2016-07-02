from datetime import date, timedelta
import billboard

__author__ = "James Wenzel"
__license__ = "MIT"
__email__ = "wenzel.james.r@gmail.com"

try:
    today = billboard.ChartData('hot-100').date
except:
    today = str(date.today())


class ChartDates(object):

    '''Iterator over valid chart weeks'''

    def __init__(self, start_date, end_date=today):
        assert type(start_date) is date
        assert type(end_date) is date or type(end_date) is str, "date or str"
        self.end_date = end_date
        if type(end_date) is not date:
            self.end_date = self.str_to_date(end_date)
        self.current_date = start_date

    def __iter__(self):
        return self

    def __next__(self):
        '''Python 3 support'''
        if self.compare_dates(self.end_date) > 0:
            raise StopIteration
        current = self.current_date
        self.increment()
        return current

    def next(self):
        '''Python 2 support'''
        if self.compare_dates(self.end_date) > 0:
            raise StopIteration
        current = self.current_date
        self.increment()
        return current

    def __repr__(self):
        return str(self.current_date)

    def str_to_date(self, string):
        year, month, day = string.split('-')
        return date(int(year), int(month), int(day))

    def increment(self, days=7):
        '''Serves as an abstraction barrier'''
        self.current_date = self.current_date + timedelta(days)

    def compare_dates(self, dateObj):
        '''Returns 1 if current date is larger, 0 if equal, -1 if smaller'''
        # check year first
        if self.current_date > dateObj:
            return 1
        elif self.current_date < dateObj:
            return -1
        return 0  # if they are equal


class BillboardDates(ChartDates):

    '''Iterator over valid Billboard chart dates'''

    def __init__(self, end_date=today):
        super(BillboardDates, self).__init__(date(1958, 8, 9), end_date)


class SpotifyDates(ChartDates):

    '''Iterator over valid Spotify chart dates'''

    def __init__(self, end_date=today):
        super(SpotifyDates, self).__init__(date(2013, 4, 28), end_date)


class BillboardIter(BillboardDates):

    '''Iterator over valid Billboard Chart weeks, which
    quantizes the start to the next valid date'''

    def __init__(self, start_date, end_date=today,
                 dateIter=BillboardDates):
        assert type(start_date) is str or type(start_date) is date
        super(BillboardIter, self).__init__(end_date)
        self._dates = dateIter()
        self.init_date = start_date
        if type(self.init_date) is not date:
            self.init_date = self.str_to_date(self.init_date)
        self.current_date = self.init_date
        self.quantize_start()
        self.init_date = self.current_date

    def reset(self):
        self.current_date = self.init_date

    def quantize_start(self):
        '''Quantizes starting date to the closest following Billboard chart'''
        bb_date = self._dates.current_date
        while self.compare_dates(bb_date) >= 0:  # get BB date up to start
            bb_date = next(self._dates)
        while self.compare_dates(bb_date) < 0:  # get start up to valid BB date
            self.increment(1)


class SpotifyIter(BillboardIter):

    def __init__(self, start_date, end_date=today):
        super(SpotifyIter, self).__init__(start_date, end_date, SpotifyDates)
