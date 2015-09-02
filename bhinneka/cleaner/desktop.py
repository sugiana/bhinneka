from tools import (
    REGEX_UNITS,
    copy_text,
    c_regex_search,
    clean,
    )
from notebook import NotebookCleaner


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
    'include', # Include
    ]


class DesktopCleaner(NotebookCleaner):
    memory_regexs = MEMORY_REGEXS
    storage_regexs = STORAGE_REGEXS
    resolution_regexs = RESOLUTION_REGEXS
    monitor_regexs = MONITOR_REGEXS

    def parse_monitor(self, values):
        for value in values:
            s = clean(value).lower()
            for rc in self.monitor_regexs_compiled:
                match = c_regex_search(rc, s)
                if not match:
                    continue
                if not match.groups():
                    return [value, None]
                amount = match.group(1)
                if amount:
                    return [value, float(amount)]


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
    cleaner = DesktopCleaner()
    f = open(input_file)
    s = cleaner.parse_json(f)
    f.close()
    f = open(output_file, 'w')
    f.write(s)
    f.close()
