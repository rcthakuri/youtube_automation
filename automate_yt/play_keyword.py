import random

KEYWORD = ['Walking tour of city st', 'unique things to do in city st', 'real estate in city st',
           'city st travel guide', 'things to do city st', 'top tourist attractions', 'best neighborhoods in city st',
           'worst neighborhoods in city st', 'driving tour of city st', 'downtown city st tour', 'a day in city st',
           'is city st a good place to live', 'living in city st', 'moving to city st',
           'most expensive neighborhoods in city st', 'cost of living in city st', 'history of city st',
           'this is city st', 'hidden gems in city st', 'real estate market update city st', 'new construction city fl']


class PlayKeyword:
    def __init__(self):
        self.keyword = KEYWORD

    def shuffle_keyword_list(self):
        random.shuffle(self.keyword)

