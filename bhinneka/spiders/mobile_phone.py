import os
from types import ListType
from bhinneka.items import MobilePhone
from .tools import (
    CommonSpider,
    regex_compile,
    c_regex_search,
    clean,
    REGEX_UNITS,
    should_int,
    regex_get_original_words,
    )


MEMORY_REGEXS = regex_compile([
    # 8 GB Storage, 1 GB RAM
    '(\d*) %s ram' % REGEX_UNITS,
    # 32GB Storage, 2GB RAM
    '(\d*)%s ram' % REGEX_UNITS,
    # 4 GB storage, 1GB
    'storage, (\d*)%s' % REGEX_UNITS,
    # RAM 256MB, ROM 512MB
    'ram (\d*)%s' % REGEX_UNITS, 
    # RAM 1 GB   
    'ram (\d*) %s' % REGEX_UNITS, 
    ])
    
def parse_unit_(values, regexs):
    for value in values:
        s = clean(value).lower()
        for rc in regexs:
            match = c_regex_search(rc, s)
            if not match:
                continue
            amount = match.group(1)
            if not amount:
                continue
            unit = match.group(2)
            return [value, int(amount), unit]
            
def parse_memory(values):
    return parse_unit_(values, MEMORY_REGEXS)
       
def parse_unit_from_other_(values, regexs):
    for value in values:
        value = clean(value)
        s = value.lower()
        for rc in regexs:
            match = c_regex_search(rc, s)
            if not match:
                continue
            amount = match.group(1)
            if not amount:
                continue
            unit = match.group(2)
            value = regex_get_original_words(rc.pattern, s, value)
            return [value, int(amount), unit]
       
def parse_memory_from_description(values):
    return parse_unit_from_other_(values, MEMORY_REGEXS)       
       
STORAGE_REGEXS = regex_compile([
    # 8 GB Storage, 1 GB RAM
    '(\d*) %s storage' % REGEX_UNITS,
    # 16 GB ROM, 2 GB RAM
    '(\d*) %s rom' % REGEX_UNITS,
    # 16GB EMMC + 2GB RAM    
    '(\d*)%s emmc' % REGEX_UNITS,    
    # 32GB Storage, 2GB RAM
    '(\d*)%s storage,' % REGEX_UNITS,
    # 16 GB (8 GB user-available)
    '^(\d*) %s \(' % REGEX_UNITS,
    # 4 GB, 1 GB RAM
    '^(\d*) %s, (\d*) %s ram' % (REGEX_UNITS, REGEX_UNITS),
    # 8GB, 2GB RAM'
    '^(\d*)%s, (\d*)%s ram' % (REGEX_UNITS, REGEX_UNITS),
    # 16GB
    '^(\d*)%s$' % REGEX_UNITS,
    ])
    
def parse_storage(values):
    return parse_unit_(values, STORAGE_REGEXS)
    
STORAGE_REGEXS_FROM_DESCRIPTION = regex_compile([    
    # 512MB ROM, 256MB RAM
    '(\d*)%s rom' % REGEX_UNITS,
    # 8 GB Storage
    '(\d*) %s storage' % REGEX_UNITS,
    # 8GB Storage
    '(\d*)%s storage' % REGEX_UNITS,
    # ROM 4 GB    
    'rom (\d*) %s' % REGEX_UNITS,
    # 8 GB Internal
    '(\d*) %s internal' % REGEX_UNITS,
    # 4GB Internal
    '(\d*)%s internal' % REGEX_UNITS,
    ])
        
def parse_storage_from_description(values):
    return parse_unit_from_other_(values, STORAGE_REGEXS_FROM_DESCRIPTION)
    
MONITOR_REGEXS = regex_compile([
    '(\d*\.\d) inch', # 5.0 inch
    '(\d*\.\d)inch', # 5.0 inches
    '(\d*) inch', # 5 inch
    '(\d*\.\d)-inch', # 4.0-inch
    '^(\d\.\d)$', # 4.5
    ])
    
def parse_amount_(values, regexs):
    for value in values:
        s = clean(value).lower()
        for rc in regexs:
            match = c_regex_search(rc, s)
            if not match:
                continue
            amount = match.group(1)
            if amount:
                return [value, should_int(float(amount))]

def parse_monitor(values):
    return parse_amount_(values, MONITOR_REGEXS)    
    
RESOLUTION_REGEXS = regex_compile([
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
    ])
    
RESOLUTION_NAMES = dict(
    qvga=(240, 320),
    hvga=(320, 480),
    wvga=(480, 800),
    fwvga=(480, 854),
    )
    
def parse_resolution(values):
    for value in values:
        s = clean(value).lower()
        for rc in RESOLUTION_REGEXS:
            match = c_regex_search(rc, s)
            if not match:
                continue
            count = len(match.groups())
            if not count:
                if s in RESOLUTION_NAMES:
                    width, height = RESOLUTION_NAMES[s]
                    return [value, width, height]
                return
            if count > 1:
                width = int(match.group(1))
                height = int(match.group(2))
            else:
                height = int(match.group(1))
                width = None
            return [value, width, height]

BATTERY_REGEXS = regex_compile([
    '(\d*) mah', # 2300 mAh
    '(\d*)mah', # 2300mAh    
    ])

def parse_battery(values):
    return parse_amount_(values, BATTERY_REGEXS)
    
BATTERY_REGEXS_FROM_DESCRIPTION = regex_compile([
    '(\d*)mah', # Battery 1100mAh
    ])

def parse_battery_from_description(values):
    return parse_amount_from_other_(values, BATTERY_REGEXS_FROM_DESCRIPTION)

CAMERA_REGEXS = regex_compile([
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
    # Primary : 20.7 MP'   
    'primary : (\d*\.\d) m',     
    # Primer : 8 MP, 3264 x 2448 pixels, Autofocus, LED Flash
    'primer : (\d*) m',
    # Primer : 8.0 MP with Auto Focus and Flash Light
    'primer : (\d*\.\d) m',
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
    ])
                    
def parse_camera(values):
    return parse_amount_(values, CAMERA_REGEXS)

CAMERA_REGEXS_FROM_DESCRIPTION = regex_compile([
    # 5MP Camera
    '(\d*)mp camera',
    # Camera 8MP+2MP,
    'camera (\d*)mp\+',        
    ])
    
def parse_amount_from_other_(values, regexs):
    for value in values:
        value = clean(value)
        s = value.lower()
        for rc in regexs:
            match = c_regex_search(rc, s)
            if not match:
                continue
            amount = match.group(1)
            if amount:
                value = regex_get_original_words(rc.pattern, s, value)            
                return [value, should_int(float(amount))]
    
def parse_camera_from_description(values):
    return parse_amount_from_other_(values, CAMERA_REGEXS_FROM_DESCRIPTION)
    
FRONT_CAMERA_REGEXS = regex_compile([
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
    # Secondary; 5.0MP
    'secondary; (\d*\.\d)mp',
    # Secondary: 0.MP    
    'secondary: (\d\.)mp',
    # Secondary: 1.3 Megapixels
    'secondary: (\d*\.\d) mega',
    # Secondary : 2 MP
    'secondary : (\d*) mp',
    # Secondary : 2.2 MP
    'secondary : (\d*\.\d) mp',    
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
    # Depan : 5.0 MP
    'depan : (\d*\.\d) mp',
    # Depan : 2 MP
    'depan : (\d*) mp',
    # Depan : 3.7MP
    'depan : (\d*.\d)m',
    # Depan : 2MP, 720p video recording
    'depan : (\d*)mp',
    # 2MP fixed-focus
    '(\d*)mp fix',
    ])
        
def parse_front_camera(values):
    return parse_amount_(values, FRONT_CAMERA_REGEXS)

FRONT_CAMERA_REGEXS_FROM_DESCRIPTION = regex_compile([    
    # 5 MP + 2 MP Camera
    # 5 MP + 0.3 MP Camera    
    '\+ ([\d\.]*) mp camera',
    # Camera 8MP+2MP,
    # Camera 2MP+1.3MP    
    '\+([\d\.]*)mp,',    
    ])
    
def parse_front_camera_from_description(values):
    return parse_amount_from_other_(values, FRONT_CAMERA_REGEXS_FROM_DESCRIPTION)    

    
class MobilePhoneSpider(CommonSpider):
    name = 'mobile_phone'
    start_urls = ['http://www.bhinneka.com/category/smart_phone_android.aspx']
    specs = dict(
        processor=('Tipe Prosessor', 'Kecepatan Prosessor'),
        memory=('Memori Internal',),
        battery=('Kapasitas Baterai',),
        monitor=('Ukuran Layar',),
        resolution=('Resolusi Layar',),
        camera=('Kamera',),
        operating_system=('Sistem Operasi',),
        )
    product_class = MobilePhone
    blacklist_brand_file = os.path.join('blacklist', 'brand',
        'mobile_phone.txt')
    
    def parse_product(self, response):
        i = super(MobilePhoneSpider, self).parse_product(response)
        if not i:
            return
        i = self.parse_processor(response, i)
        i = self.parse_operating_system(response, i)            
        i = self.parse_storage(response, i)        
        i = self.parse_memory(response, i)
        i = self.parse_monitor(response, i)
        i = self.parse_resolution(response, i)
        i = self.parse_battery(response, i)
        i = self.parse_front_camera(response, i)        
        i = self.parse_camera(response, i)
        return i
        
    def parse_text_(self, response, i, key):
        if key in i:
            i[key] = ', '.join(i[key])
        return i
        
    def parse_processor(self, response, i):
        return self.parse_text_(response, i, 'processor')
        
    def parse_operating_system(self, response, i):
        return self.parse_text_(response, i, 'operating_system')
                
    def parse_multi_source_(self, response, i, key, sources, func):
        s = []
        for source in sources:
            if source in i:
                if type(i[source]) is ListType:
                    s += i[source]
                else:
                    s.append(i[source])
        if not s:
            return i
        r = func(s)
        if r:
            i[key] = r
        else:
            if key in i:
                del i[key]
            self.logger.warning('{url} {k} {v} tidak dipahami.'.format(
                url=response.url, k=key, v=s))
        return i
                        
    def parse_memory(self, response, i):
        i = self.parse_multi_source_(response, i, 'memory',
                    ['memory'], parse_memory)
        if 'memory' not in i:
            i = self.parse_multi_source_(response, i, 'memory',
                    ['description'], parse_memory_from_description)
        return i
        
    def parse_storage(self, response, i):
        i = self.parse_multi_source_(response, i, 'storage',
                    ['memory'], parse_storage)
        if 'storage' not in i:
            i = self.parse_multi_source_(response, i, 'storage',
                    ['description'], parse_storage_from_description)
        return i
        
    def parse_monitor(self, response, i):
        return self.parse_multi_source_(response, i, 'monitor',
                    ['monitor'], parse_monitor)

    def parse_resolution(self, response, i):
        return self.parse_multi_source_(response, i, 'resolution',
                    ['resolution'], parse_resolution)
        
    def parse_battery(self, response, i):
        i = self.parse_multi_source_(response, i, 'battery',
                ['battery'], parse_battery)
        if 'battery' in i:
            return i
        i = self.parse_multi_source_(response, i, 'battery',
                ['description'], parse_battery_from_description)
        return i
        
    def parse_camera(self, response, i):
        vals = []
        if 'camera' in i:
            r = parse_camera(i['camera'])
            if r:
                i['camera'] = r
                return i
            vals += i['camera']
        if 'description' in i:
            r = parse_camera_from_description([i['description']])
            if r:
                i['camera'] = r
                return i
            vals += [i['description']]
        if 'camera' in i:
            del i['camera']
            self.logger.warning('{url} camera {v} tidak dipahami.'.format(
                url=response.url, v=vals))
        return i
        
    def parse_front_camera(self, response, i):
        i = self.parse_multi_source_(response, i, 'front_camera',
                ['camera'], parse_front_camera)
        if 'front_camera' in i:
            return i
        return self.parse_multi_source_(response, i, 'front_camera',
                ['description'], parse_front_camera_from_description)
