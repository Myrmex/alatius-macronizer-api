class Macronizer:
    _text = ""

    def settext(self, text):
        self._text = text

    def gettext(self, macronize=True, maius=False, utov=False, itoj=False, markambigs=False):
        return self._text.upper()
