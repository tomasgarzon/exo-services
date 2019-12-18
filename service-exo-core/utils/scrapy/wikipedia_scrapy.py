import scrapy

# scrapy runspider wikipedia_scrapy.py -o technologies.json


class WikipediaSpider(scrapy.Spider):
    name = 'wikipedia'
    start_urls = ['https://en.wikipedia.org/wiki/List_of_emerging_technologies']
    extra_techs = [
        '3D Printing',
        'Drones',
        'Mixed Reality',
        'Robotics',
        'Artificial Intelligence',
    ]
    exclude_techs = [
        'Artificial General Intelligence',
        'Immersive Virtual Reality',
        'X-53 Active Aeroelastic Wing'
    ]

    def parse(self, response):

        for title in response.css('table.wikitable'):
            for row in title.css('tr'):
                value = row.css('td a::text').extract_first()
                if value:
                    value_parsed = value.title()
                    if value_parsed not in self.exclude_techs:
                        yield {'title': value_parsed}

        for tech in self.extra_techs:
            yield {'title': tech.title()}
