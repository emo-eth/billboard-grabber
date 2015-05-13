from datetime import date, timedelta

__author__ = "James Wenzel"
__license__ = "MIT"
__email__ = "wenzel.james.r@gmail.com"


class BillboardDates():

    '''Iterator over valid Billboard Chart weeks, which is
    supposed to be a per-class singleton for start quantization'''

    def __init__(self, endDate=date.today()):
        assert type(endDate) is str or type(endDate) is date
        self.endDate = endDate
        if type(endDate) is not date:
            self.endDate = self.str_to_date(endDate)
        self.currentDate = date(1958, 8, 9)

    def __iter__(self):
        return self

    def __next__(self):
        if self.compare_dates(self.endDate) >= 0:
            raise StopIteration
        current = self.currentDate
        self.increment()
        return current

    def str_to_date(self, string):
        year, month, day = string.split('-')
        return date(int(year), int(month), int(day))

    def increment(self, days=7):
        '''Serves as an abstraction barrier'''
        self.currentDate = self.currentDate + timedelta(days)

    def __repr__(self):
        return str(self.currentDate)

    def compare_dates(self, dateObj):
        '''Returns 1 if current date is larger, 0 if equal, -1 if smaller'''
        # check year first
        if self.currentDate > dateObj:
            return 1
        elif self.currentDate < dateObj:
            return -1
        return 0  # if they are equal


class BillboardIter(BillboardDates):

    '''Iterator over valid Billboard Chart weeks, which
    quantizes the start to the next valid date'''
    _BillboardDates = BillboardDates()

    def __init__(self, startDate, endDate=date.today()):
        assert type(startDate) is str or type(startDate) is date
        super().__init__(endDate)
        self.initDate = startDate
        if type(self.initDate) is not date:
            self.initDate = self.str_to_date(self.initDate)
        self.currentDate = self.initDate
        self.quantizeStart()

    def reset(self):
        self.currentDate = self.initDate
        self.quantizeStart()

    def quantizeStart(self):
        '''Quantizes starting date to the closest following Billboard chart'''
        bbDate = self._BillboardDates.currentDate
        while self.compare_dates(bbDate) >= 0:  # get BB date up to start
            bbDate = next(self._BillboardDates)
        while self.compare_dates(bbDate) < 0:  # get start up to valid BB date
            self.increment(1)
