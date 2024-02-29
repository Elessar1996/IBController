class Trader:

    def __init__(self, tickness, begining, ticker):

        self.tickness = tickness
        self.in_long = False
        self.in_short = False
        self.begining = begining
        self.ticker = ticker
    def open_long_position(self, list_smas):

        for i in range(len(list_smas[:self.tickness + 1])):

            if i == 0:
                continue
            else:
                if list_smas[:self.tickness + 1][i - 1] <= list_smas[:self.tickness + 1][i]:
                    return False
        return True

    def open_short_position(self, list_of_smas):

        for i in range(len(list_of_smas[:self.tickness + 1])):

            if i == 0:
                continue
            else:
                if list_of_smas[:self.tickness + 1][i - 1] >= list_of_smas[:self.tickness + 1][i]:
                    return False
        return True

    def keep_long_open(self, list_of_smas):

        total = 0
        initial_point = 1

        sma_5 = list_of_smas[0]

        while len(list_of_smas[1:]) - initial_point >= self.tickness - 1:

            for i, j in enumerate(list_of_smas[initial_point:]):

                if i == 0:
                    if sma_5 <= j:
                        total = 0
                        initial_point += 1
                        break
                    else:
                        total += 1
                        continue
                else:
                    if list_of_smas[initial_point:][i - 1] >= list_of_smas[initial_point:][i]:
                        total += 1

                        if total >= self.tickness:
                            return True
                    else:
                        total = 0
                        initial_point += 1
                        break
        return False

    def keep_short_open(self, list_of_smas):

        total = 0
        initial_point = 1

        sma_5 = list_of_smas[0]

        while len(list_of_smas[1:]) - initial_point >= self.tickness - 1:

            for i, j in enumerate(list_of_smas[initial_point:]):

                if i == 0:
                    if sma_5 >= j:
                        total = 0
                        initial_point += 1
                        break
                    else:
                        total += 1
                        continue
                else:
                    if list_of_smas[initial_point:][i - 1] <= list_of_smas[initial_point:][i]:
                        total += 1

                        if total >= self.tickness:
                            return True
                    else:
                        total = 0
                        initial_point += 1
                        break
        return False

    def long(self, list_smas):

        if self.in_long:
            return self.keep_long_open(list_smas)
        else:
            return self.open_long_position(list_smas)

    def short(self, list_smas):

        if self.in_short:
            return self.keep_short_open(list_smas)
        else:
            return self.open_short_position(list_smas)

    def multiple_sma(self, list_smas):

        if self.long(list_smas):

            if self.in_short:

                if not self.short(list_smas):
                    self.in_long = True
                    self.in_short = False

                    return "close and go long"

                else:

                    return "hold"

            elif self.in_long:

                return "hold"

            else:
                self.in_long = True
                self.in_short = False
                return "long"

        elif self.short(list_smas):

            if self.in_long:

                if not self.long(list_smas):

                    self.in_long = True
                    self.in_short = False

                    return "close and go short"
                else:
                    return "hold"
            elif self.in_short:
                return "hold"

            else:
                self.in_short = True
                self.in_long = False

                return "short"
        else:

            if self.in_long:

                self.in_long = False
                self.in_short = False

                return "close long"
            elif self.in_short:
                self.in_long = False
                self.in_short = False

                return "close short"
            else:
                return "hold"





