import json
from types import ListType
from tools import (
    REGEX_UNITS,
    copy_text,
    regex_compile,
    c_regex_search,
    clean,
    price,
    key_not_found,
    unknown_values,
    parse,
    )


MEMORY_REGEXS = [
    '(\d*) %s' % REGEX_UNITS, # 2 GB DDR-3
    '(\d*)%s' % REGEX_UNITS, # 8GB of 1600MHz LPDDR3 onboard memory
    ]

STORAGE_REGEXS = [
    '(\d*) %s' % REGEX_UNITS, # 500 GB HDD
    '(\d*)%s' % REGEX_UNITS, # 256GB PCIe-based onboard flash storage
    ]

RESOLUTION_REGEXS = [
    '(\d*)-by-(\d*)', # 2304-by-1440 resolution at 226 pixels per inch with support for millions of colors
    '(\d*) x (\d*)', # 1366 x 768
    '(\d*)x(\d*)', # 1920x1200
    ]

MONITOR_REGEXS = [
    '(\d*\.\d) inch', # 12.5 inch
    '(\d*\.\d)"', # 12.5"
    '(\d*\.\d)" wxga', # 10.1" wxga
    '(\d*\.\d) wxga', # 10.1 wxga
    '(\d*)" wxga', # 12" wxga
    '(\d*) inch', # 12 inch
    '(\d*)"', # 12"
    '(\d*\.\d)', # 20.0 
    '(\d*)', # 20.0 
    ]


class NotebookCleaner(object):
    memory_regexs = MEMORY_REGEXS
    storage_regexs = STORAGE_REGEXS
    resolution_regexs = RESOLUTION_REGEXS
    monitor_regexs = MONITOR_REGEXS

    def __init__(self):
        self.memory_regexs_compiled = regex_compile(self.memory_regexs)
        self.storage_regexs_compiled = regex_compile(self.storage_regexs)
        self.resolution_regexs_compiled = regex_compile(self.resolution_regexs)
        self.monitor_regexs_compiled = regex_compile(self.monitor_regexs)

    def parse(self, data):
        def parse_(keys, func):
            vals = parse(keys, data, func)
            if vals is None or vals is False:
                return
            first_key = keys[0]
            r[first_key] = vals
                
        r = copy_text(data)
        parse_(['stock', 'price'], self.parse_stock)
        parse_(['price'], self.parse_price)
        parse_(['memory'], self.parse_memory)
        parse_(['storage'], self.parse_storage)
        parse_(['resolution'], self.parse_resolution)
        parse_(['monitor', 'description'], self.parse_monitor)
        return r
        
    def parse_stock(self, values):
        for value in values:
            if value:
                return False
            return 0

    def parse_price(self, values):
        for value in values:
            if not value:
                return False
            s = clean(value)
            vals = price(value)
            if vals:
                amount, currency = vals
                return [value, amount, currency]

    def parse_memory(self, values):
        for value in values:
            s = clean(value).lower()
            for rc in self.memory_regexs_compiled:
                match = c_regex_search(rc, s)
                if match:
                    amount = match.group(1)
                    unit = match.group(2)
                    return [value, int(amount), unit]

    def parse_storage(self, values):
        for value in values:
            s = clean(value).lower()
            for rc in self.storage_regexs_compiled:
                match = c_regex_search(rc, s)
                if match:
                    amount = match.group(1)
                    unit = match.group(2)
                    return [value, int(amount), unit]

    def parse_resolution(self, values):
        for value in values:
            s = clean(value).lower()
            for rc in self.resolution_regexs_compiled:
                match = c_regex_search(rc, s)
                if not match:
                    continue
                count = len(match.groups())
                if not count:
                    return [value, None, None]
                if count > 1:
                    width = int(match.group(1))
                    height = int(match.group(2))
                else:
                    height = int(match.group(1))
                    width = None
                try:
                    return [value, width, height]
                except ValueError, err:
                    print(err)
                    return

    def parse_monitor(self, values):
        for value in values:
            s = clean(value).lower()
            for rc in self.monitor_regexs_compiled:
                match = c_regex_search(rc, s)
                if match:
                    amount = match.group(1)
                    if amount:
                        return [value, float(amount)]

    def parse_json(self, f):
        results = []
        rows = json.load(f)
        for row in rows:
            r = self.parse(row)
            s = json.dumps(r)
            results.append(s)
        return '[%s]' % ',\n'.join(results)


if __name__ == '__main__':
    import sys
    from optparse import OptionParser
    pars = OptionParser()
    pars.add_option('-i', '--input', help='JSON file')
    pars.add_option('-o', '--output', help='JSON file')
    option, remain = pars.parse_args(sys.argv[1:])
    if not option.output:
        print('--output harus diisi.')
        sys.exit()
    input_file = option.input
    output_file = option.output
    cleaner = NotebookCleaner()
    f = open(input_file)
    s = cleaner.parse_json(f)
    f.close()
    f = open(output_file, 'w')
    f.write(s)
    f.close()
