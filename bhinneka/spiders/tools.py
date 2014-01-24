from scrapy.exceptions import CloseSpider


def v(values):
    s = ' '.join(values)
    return s.strip()

def get_key_values(c):
    r = []        
    for g in c.xpath('div/ul/li/i'):
        s = v(g.xpath('text()').extract())
        r.append(s)        
    for g in c.xpath('div/ul/li'):
        s = v(g.xpath('text()').extract())
        r.append(s)
    s = v(c.xpath('text()').extract())
    if s:
        r.append(s)
    return r
 
def get_images(sel, url):
    images = sel.xpath('//div[@id="slider1"]/div/img')
    links = []
    for image in images:
        url = v(image.xpath('@src').extract())
        links.append(url)
    if links:
        return links
    images = sel.xpath('//img[@itemprop="image"]').xpath('@src').extract()
    if images:
        return [images[0]]
    raise CloseSpider('%s: Image not found.' % url)

