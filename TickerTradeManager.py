
class TickerTradeManager:

    def __init__(self, ib, ticker, ticker_type, is_shortable):

        self.ib = ib
        self.ticker = ticker
        self.ticker_type = ticker_type
        self.is_shortable = is_shortable
        self.placed_orders = []
        self.fulfilled_orders = []

    def check_order_fulfillment(self):
        pass

    def handle_unfulfilled_order(self):
        pass

    def go_long(self):
        pass

    def go_short(self):
        pass

    def close_position(self):
        pass

    def run_command(self):
        pass
