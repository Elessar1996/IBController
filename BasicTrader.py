from Central import Trader



class BasicTrader(Trader):


    def __init__(self, tickness, begining, ticker):

        Trader.__init__(self, tickness, begining, ticker)

        self.tickness = tickness
        self.in_long = False
        self.in_short = False
        self.begining = begining
        self.ticker = ticker

    def long(self, list_smas, list_cvds=None, list_cdvs=None):

        if self.in_long:

            smas = self.keep_long_open(list_smas) if list_smas is not None else True
            cvd = self.keep_long_open(list_cvds) if list_cvds is not None else True
            cdv = self.keep_long_open(list_cdvs) if list_cdvs is not None else True

            return smas and cvd and cdv

        else:

            smas = self.open_long_position(list_smas) if list_smas is not None else True
            cvd = self.open_long_position(list_cvds) if list_cvds is not None else True
            cdv = self.open_long_position(list_cdvs) if list_cdvs is not None else True

            return smas and cvd and cdv

    def short(self, list_smas, list_cvds=None, list_cdvs=None):

        if self.in_short:
            smas = self.keep_short_open(list_smas) if list_smas is not None else True
            cvd = self.keep_short_open(list_cvds) if list_cvds is not None else True
            cdv = self.keep_short_open(list_cdvs) if list_cdvs is not None else True

            return smas and cvd and cdv
        else:

            smas = self.open_short_position(list_smas) if list_smas is not None else True
            cvd = self.open_short_position(list_cvds) if list_cvds is not None else True
            cdv = self.open_short_position(list_cdvs) if list_cdvs is not None else True

            return smas and cvd and cdv






