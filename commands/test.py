import functools
import json
from threading import Lock


class AtmoicResource:
    __slots__ = ['mutex']
    def __init__(self):
        self.mutex = Lock()

    def wrap(func):
        @functools.wraps(func)
        def decorate(self, *args, **kwargs):
            self.mutex.acquire(1)
            res = func(self, *args, **kwargs)
            self.mutex.release()
            if res is not None: return res

        return decorate

class Myjson(AtmoicResource):
    __slots__ = ['file']
    def __init__(self, file_path):
        super().__init__()
        self.file = file_path

    @AtmoicResource.wrap
    def get(self, key = False):
        with open(self.file, encoding = 'utf8') as json_file:
            data = json.load(json_file)
            if not key:
                return data
            elif key in data:
                return data[key]
            return None

    @AtmoicResource.wrap
    def set(self, key, value):
        with open(self.file, encoding = 'utf8') as json_file:
            data = json.load(json_file)
            data[key] = value
        with open(self.file, 'w', encoding = 'utf8') as outfile:
            json.dump(data, outfile, indent=2)

x = Myjson('res/cl.json')
x.set('kaki', 'kaka')

