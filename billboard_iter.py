from datetime import date, timedelta

__author__ = "James Wenzel"
__license__ = "MIT"
__email__ = "wenzel.james.r@gmail.com"


class billboard_dates():

    '''Iterator over valid Billboard Chart weeks, which is
    supposed to be a per-class singleton for start quantization'''

    def __init__(self, end_date=date.today()):
        assert type(end_date) is str or type(end_date) is date
        self.end_date = end_date
        if type(end_date) is not date:
            self.end_date = self.str_to_date(end_date)
        self.current_date = date(1958, 8, 9)

    def __iter__(self):
        return self

    def __next__(self):
        if self.compare_dates(self.end_date) > 0:
            raise StopIteration
        current = self.current_date
        self.increment()
        return current

    def str_to_date(self, string):
        year, month, day = string.split('-')
        return date(int(year), int(month), int(day))

    def increment(self, days=7):
        '''Serves as an abstraction barrier'''
        self.current_date = self.current_date + timedelta(days)

    def __repr__(self):
        return str(self.current_date)

    def compare_dates(self, dateObj):
        '''Returns 1 if current date is larger, 0 if equal, -1 if smaller'''
        # check year first
        if self.current_date > dateObj:
            return 1
        elif self.current_date < dateObj:
            return -1
        return 0  # if they are equal


class billboard_iter(billboard_dates):

    '''Iterator over valid Billboard Chart weeks, which
    quantizes the start to the next valid date'''
    _billboard_dates = billboard_dates()

    def __init__(self, start_date, end_date=date.today()):
        assert type(start_date) is str or type(start_date) is date
        super().__init__(end_date)
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
        bb_date = self._billboard_dates.current_date
        while self.compare_dates(bb_date) >= 0:  # get BB date up to start
            bb_date = next(self._billboard_dates)
        while self.compare_dates(bb_date) < 0:  # get start up to valid BB date
            self.increment(1)
