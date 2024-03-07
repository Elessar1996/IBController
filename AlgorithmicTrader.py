from Central import Trader


class AlgorithmicTrader(Trader):

    def __init__(self, tickness, begining, ticker, stop_loss):

        Trader.__init__(self, tickness, begining, ticker)

        self.stop_loss = stop_loss
        self.open_long_price = None
        self.close_long_price = None
        self.open_short_price = None
        self.close_short_price = None
        self.allowed = True

    def measure_loss(self, price):

        diff_percent = None

        if self.in_long:

            diff_percent = ((price - self.open_long_price) / self.open_long_price) * 100

        elif self.in_short:

            diff_percent = ((self.open_short_price - price) / self.open_short_price) * 100

        return diff_percent

    def is_stop_loss_triggered(self, price):

        if abs(self.measure_loss(price=price)) >= self.stop_loss:
            print(f'stop loss triggered for the ticker {self.ticker}')
            self.allowed = False

    def multiple_sma(self, list_smas, price):

        self.is_stop_loss_triggered(price)
        if self.allowed:

            if self.long(list_smas):

                if self.in_short:

                    if not self.short(list_smas):
                        self.in_long = True
                        self.in_short = False
                        self.close_short_price = price
                        self.open_long_price = price
                        return "close and go long"

                    else:

                        return "hold"

                elif self.in_long:

                    return "hold"

                else:
                    self.in_long = True
                    self.in_short = False
                    self.open_long_price = price
                    return "long"

            elif self.short(list_smas):

                if self.in_long:

                    if not self.long(list_smas):

                        self.in_long = True
                        self.in_short = False
                        self.close_long_price = price
                        self.open_short_price = price
                        return "close and go short"
                    else:
                        return "hold"
                elif self.in_short:
                    return "hold"

                else:
                    self.in_short = True
                    self.in_long = False
                    self.open_short_price = price
                    return "short"
            else:

                if self.in_long:

                    self.in_long = False
                    self.in_short = False
                    self.close_long_price = price
                    return "close long"
                elif self.in_short:
                    self.in_long = False
                    self.in_short = False
                    self.close_short_price = price
                    return "close short"
                else:
                    return "hold"
