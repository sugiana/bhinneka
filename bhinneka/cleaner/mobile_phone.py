from types import ListType
from tools import (
    REGEX_UNITS,
    copy_text,
    c_regex_search,
    regex_compile,
    clean,
    parse,
    )
from notebook import NotebookCleaner


U2 = (REGEX_UNITS, REGEX_UNITS)

STORAGE_REGEXS = [
    # 8 GB Storage, 1 GB RAM
    '(\d*) %s storage' % REGEX_UNITS,
    # 32GB Storage, 2GB RAM
    '(\d*)%s storage,' % REGEX_UNITS,
    # 16 GB (8 GB user-available)
    '^(\d*) %s \(' % REGEX_UNITS,
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
    '(\d*)%s ram' % REGEX_UNITS,
    # 4 GB storage, 1GB
    'storage, (\d*)%s' % REGEX_UNITS,
    # RAM 256MB, ROM 512MB
    'ram (\d*)%s' % REGEX_UNITS,    
    # 16 GB (8 GB user-available)
    '16 gb \(8 gb user-available\)',
    ####################
    # Dari description #
    ####################
    # 16 GB, 3 GB RAM,
    ]

RESOLUTION_REGEXS = [
    '(\d*)\*(\d*)', # HD (1280*720 pixels), pixel density: 294 PPI
    '(\d*) x \((\d*)', # Quad HD 2560 X (1440+160) (~524 ppi pixel density)
    '(\d*) x (\d*)', # 1280 x 720 piksel (267 ppi )
    '(\d*)x(\d*)', # 1280x720 px
    '^(\d*)p$', # 480p
    'ips screen', # IPS Screen
    '16m colors', # 16M Colors
    'qvga',
    'hvga',
    'wvga',
    'fwvga',
    ]

RESOLUTION_NAMES = dict(
    qvga=(240, 320),
    hvga=(320, 480),
    wvga=(480, 800),
    fwvga=(480, 854),
    )

MONITOR_REGEXS = [
    '(\d*\.\d) inch', # 5.0 inch
    '(\d*\.\d)inch', # 5.0 inches
    '(\d*) inch', # 5 inch
    '(\d*\.\d)-inch', # 4.0-inch
    '^(\d\.\d)$', # 4.5
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
    'primary: (\d*\.\d*) mp',
    # Primary:13MP (Auto Focus, LED Flash, F2.0 Aperture, 5 -element lens)
    'primary:(\d*)mp',    
    # Primary: 5.0MP
    'primary: (\d*\.\d)m',
    # Primary : 5MP    
    'primary : (\d*)m',
    # Primary : 8 MP, 3264 x 2448 pixels, autofocus
    'primary : (\d*) mp',
    # Primary : 8.0MP, LED Flash, HDR, Panorama, Beauty
    'primary : (\d*\.\d)m',
    # Primer : 8 MP, 3264 x 2448 pixels, Autofocus, LED Flash
    'primer : (\d*) m',
    # Primer : 8.0 MP with Auto Focus and Flash Light
    'primer ; (\d*\.\d) m',
    # Main Camera : 13.0 MP
    'main camera : (\d*\.\d) mp',
    # Single Camera: 0.3MP
    'single camera: (\d*\.\d)mp',
    # Camera 5MP+5MP
    'camera (\d*)mp',
    # Rear: 8MP
    'rear: (\d*)mp',
    # Rear: 8 MP 3264x2448 pixels, autofocus, LED flash
    'rear: (\d*) mp',
    # Belakang : 13 MP, Sensor CMOS, LED Flashlight, Auto focus
    'belakang : (\d*) mp',
    # Belakang : 16M
    'belakang : (\d*)m',
    # Belakang : 13.1 MP
    'belakang : (\d*\.\d) mp',
    # Belakang :13 MP
    'belakang :(\d*) mp',
    # Belakang: 5MP (dapat ditambah sampai to 8MP) Auto Focus, LED Flash
    'belakang: (\d*)m',
    # 3.15 MP, 2048x1536 pixels
    '^(\d*\.\d*) mp,',
    # 8.0MP Rotation Auto Focus With Flash Light
    '^(\d*\.\d)m',
    # 8MP auto-focus with LED flash
    '^(\d*)m',
    # 2 MP
    '^(\d*) m',
    # 256MB RAM, 2 MP Camera (rear) and Front Camera
    '(\d*) mp camera \(rear',
    # Primary: VGA
    '^primary: vga$',
    # Yes
    '^yes$',
    ####################
    # Dari description #
    ####################
    # 5MP Camera
    '(\d*)mp camera',
    # microSD slot, Camera, Android 4.2
    'camera,'
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
    # Secondary: 1.3 Megapixels
    'secondary: (\d*\.\d) mega',
    # Secondary: VGA
    '^secondary: vga$',
    # Secondary : 2 MP
    'secondary : (\d*) mp',
    # Secondary : VGA
    'secondary : vga',
    # Secondary 0.3MP
    'secondary (\d*\.\d)mp',
    # Sekunder : 5 MP
    'sekunder : (\d*) m',
    # Sekunder : 2MP
    'sekunder : (\d*)mp',
    # Front Camera : 5.0 MP 
    'front camera : (\d*\.\d) mp',
    # Front: 2MP
    'front: (\d*)mp',
    # Front: VGA
    'front: vga',
    # 5 MP Rear Auto Focus Camera With Flash And Front Camera
    'front camera',
    # Depan : 5.0 MP
    'depan : (\d*\.\d) mp',
    # Depan : 2 MP
    'depan : (\d*) mp',
    # Depan : 3.7MP
    'depan : (\d*.\d)m',
    # Depan : 2MP, 720p video recording
    'depan : (\d*)mp',
    # Depan : VGA
    'depan : vga',
    # 2MP fixed-focus
    '(\d*)mp fix',
    ]    

class MobilePhoneCleaner(NotebookCleaner):
    storage_regex = STORAGE_REGEXS
    memory_regexs = MEMORY_REGEXS
    resolution_regexs = RESOLUTION_REGEXS
    monitor_regexs = MONITOR_REGEXS
    battery_regexs = BATTERY_REGEXS
    camera_regexs = CAMERA_REGEXS
    front_camera_regexs = FRONT_CAMERA_REGEXS

    def __init__(self, spesific_url=None):
        super(MobilePhoneCleaner, self).__init__()
        self.spesific_url = spesific_url
        self.battery_regexs_compiled = regex_compile(self.battery_regexs)
        self.camera_regexs_compiled = regex_compile(self.camera_regexs)
        self.front_camera_regexs_compiled = regex_compile(
            self.front_camera_regexs)
        
    def parse(self, data):
        def parse_(keys, func):
            vals = parse(keys, data, func)
            if vals is None or vals is False:
                return
            first_key = keys[0]
            r[first_key] = vals

        if self.spesific_url and self.spesific_url != data['url']:
            return dict()
        r = copy_text(data)
        parse_(['price'], self.parse_price)
        parse_(['stock', 'price'], self.parse_stock)        
        parse_(['memory', 'description'], self.parse_memory)
        parse_(['storage', 'memory', 'description'], self.parse_storage)
        parse_(['resolution'], self.parse_resolution)
        parse_(['monitor'], self.parse_monitor)
        parse_(['battery'], self.parse_battery)
        parse_(['camera', 'description'], self.parse_camera)
        parse_(['front_camera', 'camera'], self.parse_front_camera)
        return r

    def parse_memory(self, values):
        for value in values:
            s = clean(value).lower()
            for rc in self.memory_regexs_compiled:
                match = c_regex_search(rc, s)
                if not match:
                    continue
                if not match.groups():
                    return [value, None, None]
                amount = match.group(1)
                unit = match.group(2)
                return [value, int(amount), unit]

    def parse_battery(self, values):
        for value in values:
            s = clean(value).lower()
            for rc in self.battery_regexs_compiled:
                match = c_regex_search(rc, s)
                if match:
                    amount = match.group(1)
                    if amount:
                        return [value, int(amount)]

    def parse_resolution(self, values):
        for value in values:
            s = clean(value).lower()
            for rc in self.resolution_regexs_compiled:
                match = c_regex_search(rc, s)
                if not match:
                    continue
                count = len(match.groups())
                if not count:
                    if s in RESOLUTION_NAMES:
                        width, height = RESOLUTION_NAMES[s]
                        return [value, width, height]
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

    def parse_camera(self, values):
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
    pars.add_option('-u', '--url', help='Spesific URL')
    option, remain = pars.parse_args(sys.argv[1:])
    if not option.output:
        print('--output harus diisi.')
        sys.exit()
    input_file = option.input
    output_file = option.output
    cleaner = MobilePhoneCleaner(option.url)
    f = open(input_file)
    s = cleaner.parse_json(f)
    f.close()
    f = open(output_file, 'w')
    f.write(s)
    f.close()
