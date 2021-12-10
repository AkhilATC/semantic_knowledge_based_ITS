from pymemcache.client import base


class HistoryManager:

    @staticmethod
    def bind_cache():
        return base.Client(('localhost', 11211))

    @staticmethod
    def store_cache(base_store, data={}):
        base_store.set('history', data)

    @staticmethod
    def store_specfic(base_store, key, inner):
        data = base_store.get('history')
        print(f"Cahed data -- {data}{}")
        data[key] = inner
        base_store.set('history', data)

    @staticmethod
    def get_store_cache(base_store, key=None):
        data = base_store.get('history')
        return data.get(key) if key else data

    @staticmethod
    def clear_cache(base_store):
        base_store.set('history', {})
