from types import ListType
from tools import (
    REGEX_UNITS,
    copy_text,
    c_regex_search,
    regex_compile,
    clean,
    key_not_found,
    unknown_values,
    )
from notebook import NotebookCleaner


U2 = (REGEX_UNITS, REGEX_UNITS)

STORAGE_REGEXS = [
    # 8 GB Storage, 1 GB RAM
    '(\d*) %s storage' % REGEX_UNITS,
    # 32GB Storage, 2GB RAM
    '(\d*)%s storage,' % REGEX_UNITS,
    ####################
    # Dari description #
    ####################    
    # 512MB ROM, 256MB RAM
    '(\d*)%s rom,' % REGEX_UNITS,    
    ]

MEMORY_REGEXS = [
    # 8 GB Storage, 1 GB RAM
    '(\d*) %s ram' % REGEX_UNITS,
    # 32GB Storage, 2GB RAM
    '(\d*)%s ram' % REGEX_UNITS    
    ]

RESOLUTION_REGEXS = [
    '(\d*) x (\d*)', # 1280 x 720 piksel (267 ppi )
    '(\d*)x(\d*)', # 1280x720 px
    '^(\d*)p$', # 480p
    'ips screen', # IPS Screen
    ]

MONITOR_REGEXS = [
    '(\d*\.\d) inch', # 5.0 inch
    '(\d*\.\d)inch', # 5.0 inches
    '(\d*) inch', # 5 inch
    ]

BATTERY_REGEXS = [
    '(\d*) mah', # 2300 mAh
    '(\d*)mah', # 2300mAh    
    ]
    
CAMERA_REGEXS = [
    # Primary: 13 MP, 4160 x 3120 pixels, autofocus, LED flash
    'primary: (\d*) mp',
    # Primary: 13MP auto-focus with LED Flash + PureCel\u2122 Sensor
    'primary: (\d*)m',
    # Primary: 13 Mega-Pixel, Auto Focus, PixelMaster
    'primary: (\d*) mega',
    # Primary: 8.0 MP with Flash
    'primary: (\d*\.\d) mp',
    # Primary:13MP (Auto Focus, LED Flash, F2.0 Aperture, 5 -element lens)
    'primary:(\d*)mp',    
    # Primary : 5MP    
    'primary : (\d*)m',
    # Primary : 8 MP, 3264 x 2448 pixels, autofocus
    'primary : (\d*) mp',
    # Primer : 8 MP, 3264 x 2448 pixels, Autofocus, LED Flash
    'primer : (\d*) m',
    # Main Camera : 13.0 MP
    'main camera : (\d*\.\d) mp',
    # Single Camera: 0.3MP
    'single camera: (\d*\.\d)mp',
    # Rear: 8MP
    'rear: (\d*)mp',
    # Belakang : 13 MP, Sensor CMOS, LED Flashlight, Auto focus
    'belakang : (\d*) mp',
    # Belakang : 16M
    'belakang : (\d*)m',
    # 3.15 MP, 2048x1536 pixels
    '^(\d*\.\d*) mp,',
    # 8.0MP Rotation Auto Focus With Flash Light
    '^(\d*\.\d)m',
    # 8MP auto-focus with LED flash
    '^(\d*)m',
    # 2 MP
    '^(\d*) m',
    # Primary: VGA
    '^primary: vga$',
    # Yes
    '^yes$',
    ####################
    # Dari description #
    ####################
    # 5MP Camera
    '(\d*)mp camera',
    ]
    
FRONT_CAMERA_REGEXS = [
    # Secondary: 5 MP
    'secondary: (\d*) mp',
    # Secondary: 5MP
    'secondary: (\d*)mp',
    # Secondary: 5 Mega-Pixel, Fix Focus, Wide View, PixelMaster
    'secondary: (\d*) mega',
    # Secondary: 5.0 MP with Flash
    'secondary: (\d*\.\d) mp',
    # Secondary: 1.3MP
    'secondary: (\d*\.\d)mp',
    # Secondary: 0.MP    
    'secondary: (\d\.)mp',
    # Secondary : 2 MP
    'secondary : (\d*) mp',
    # Sekunder : 5 MP
    'sekunder : (\d*) m',
    # Front Camera : 5.0 MP 
    'front camera : (\d*\.\d) mp',
    # Front: 2MP
    'front: (\d*)mp',
    # Depan : 5.0 MP
    'depan : (\d*\.\d) mp',
    # Depan : 2 MP
    'depan : (\d*) mp',
    # Depan : 3.7MP
    'depan : (\d*.\d)m',
    # 2MP fixed-focus
    '(\d*)mp fix',
    # Secondary: VGA
    '^secondary: vga$',
    ]    

class MobilePhoneCleaner(NotebookCleaner):
    storage_regex = STORAGE_REGEXS
    memory_regexs = MEMORY_REGEXS
    resolution_regexs = RESOLUTION_REGEXS
    monitor_regexs = MONITOR_REGEXS
    battery_regexs = BATTERY_REGEXS
    camera_regexs = CAMERA_REGEXS
    front_camera_regexs = FRONT_CAMERA_REGEXS

    def __init__(self):
        super(MobilePhoneCleaner, self).__init__()
        self.battery_regexs_compiled = regex_compile(self.battery_regexs)
        self.camera_regexs_compiled = regex_compile(self.camera_regexs)
        self.front_camera_regexs_compiled = regex_compile(
            self.front_camera_regexs)
        
    def parse(self, data):
        def parse_(key, func):
            if key in data:
                values = data[key]
                if not values:
                    return
                val = func(values)
                if not val:
                    print(data)
                    unknown_values(key, values)
                r[key] = val
                return True
            key_not_found(key, data['url'])

        def parse_for_other(key, other_key, func, allow_none=False):
            if key in data:
                values = data[key]
                if not values:
                    return
                val = func(values)
                if not val and not allow_none:
                    print(data)
                    unknown_values(key, values)
                if val:
                    r[other_key] = val
                return True
            key_not_found(other_key, data['url'])

        r = copy_text(data)
        parse_('price', self.parse_price)
        parse_('memory', self.parse_memory)
        if not parse_for_other('memory', 'storage', self.parse_storage):
            if parse_for_other('description', 'storage', self.parse_storage,
                True):
                print('  kini ada.')
        parse_('resolution', self.parse_resolution)
        parse_('monitor', self.parse_monitor)
        parse_('battery', self.parse_battery)
        if not parse_('camera', self.parse_camera):
            if parse_for_other('description', 'camera', self.parse_camera,
                True):
                print('  kini ada.')
        parse_for_other('camera', 'front_camera', self.parse_front_camera, True)
        return r

    def parse_battery(self, values):
        for value in values:
            s = clean(value).lower()
            for rc in self.battery_regexs_compiled:
                match = c_regex_search(rc, s)
                if match:
                    amount = match.group(1)
                    if amount:
                        return [value, int(amount)]

    def parse_camera(self, values):
        if type(values) != ListType:
            values = [values]
        for value in values:
            s = clean(value).lower()
            for rc in self.camera_regexs_compiled:
                match = c_regex_search(rc, s)
                if not match:
                    continue
                if not match.groups():
                    return [value, None]
                amount = match.group(1)
                if amount:
                    return [value, int(float(amount))]

    def parse_front_camera(self, values):
        for value in values:
            s = clean(value).lower()
            for rc in self.front_camera_regexs_compiled:
                match = c_regex_search(rc, s)
                if not match:
                    continue
                if not match.groups():
                    return [value, None]
                amount = match.group(1)
                if amount:
                    return [value, int(float(amount))]


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
    cleaner = MobilePhoneCleaner()
    f = open(input_file)
    s = cleaner.parse_json(f)
    f.close()
    f = open(output_file, 'w')
    f.write(s)
    f.close()
