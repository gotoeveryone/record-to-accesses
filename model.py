""" モデル """


class Result(object):
    """ 結果オブジェクト格納用 """

    def __init__(self, obj):
        self.obj = obj

    def __getstate__(self):
        return self.obj.items()

    def __setstate__(self, items):
        if not hasattr(self, 'obj'):
            self.obj = {}
        for key, val in items:
            self.obj[key] = val

    def __getattr__(self, name):
        name.split('')
        if name in self.obj:
            return self.obj.get(name)
        else:
            return None

    def is_cleared(self):
        """ すべて実施済みかを判定 """
        return self.slot.get('success') \
            and self.roulette.get('success') \
            and self.scratch.get('success')

    @property
    def slot(self):
        """ スロット結果 """
        return self.obj.get('slot', {})

    @slot.setter
    def slot(self, data):
        self.obj['slot'] = data

    @property
    def roulette(self):
        """ ルーレット結果 """
        return self.obj.get('roulette', {})

    @roulette.setter
    def roulette(self, data):
        self.obj['roulette'] = data

    @property
    def scratch(self):
        """ スクラッチ結果 """
        return self.obj.get('scratch', {})

    @scratch.setter
    def scratch(self, data):
        self.obj['scratch'] = data

    def fields(self):
        """ 結果オブジェクトを返却 """
        return self.obj

    def keys(self):
        """ 結果オブジェクトのキー一覧を返却 """
        return self.obj.keys()
