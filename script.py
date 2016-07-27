#!/usr/bin/env python3
import sys
import billboard
from jwp.jwmultithreaded import *
from jwp.jwcache import *
from datetime import date, timedelta

cache = {}


def get_thing(chart, d):
    if chart in cache:
        if d in cache[chart]:
            print(chart, d, 'retrieved from cache')
            return {}
    print('Downloading', chart, d)
    return {chart: {d: billboard.ChartData(chart, d).to_JSON()}}


def main(c):
    start = date(1958, 8, 9)
    delta = date.today() - start

    ds = []
    for x in range(0, delta.days + 11, 7):
        d = start + timedelta(days=x)
        ds.append([c, str(d)])

    results = multithread(get_thing, ds)
    for result in results:
        for chart in result:
            if chart not in cache:
                cache[chart] = {}
            cache[chart].update(result[chart])

    write_cache('bbCache.json', cache)

if __name__ == "__main__":
    cache = load_cache('bbCache.json')
    print
    main(sys.argv[1])
