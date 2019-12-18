from factory import fuzzy


class FuzzyDjangoChoices(fuzzy.FuzzyChoice):

    def fuzz(self):
        value = super(FuzzyDjangoChoices, self).fuzz()
        return value[0]
