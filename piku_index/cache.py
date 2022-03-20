import os
from cachy import CacheManager


cache_dir = os.path.join(os.path.dirname(__file__), '../data/cache')
config = {
    'default': 'file',
    'serializer': 'json',
    'stores': {
        'file': {
            'driver': 'file',
            'path': cache_dir
        },
    }
}

cache = CacheManager(config)
