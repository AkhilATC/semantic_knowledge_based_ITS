from pymemcache.client import base
import json


class HistoryManager:

    @staticmethod
    def bind_cache():
        return base.Client(('localhost', 11211))

    @staticmethod
    def store_cache(base_store, data={}):
        base_store.set("history", data)

    @staticmethod
    def store_specfic(base_store, key, inner):
        data = base_store.get('history')
        parsed_json = eval(data)
        parsed_json[key] = inner
        base_store.set('history', parsed_json)

    @staticmethod
    def get_store_cache(base_store, key=None):
        data = base_store.get("history")
        parsed_json = eval(data)
        return parsed_json.get(key) if key else parsed_json

    @staticmethod
    def clear_cache(base_store):
        base_store.set("history", {})

    @staticmethod
    def display_store(base_store):
        data = base_store.get("history", {})
        parsed_json = eval(data)
        print(f"DATA IN STORE -->> {parsed_json}")
