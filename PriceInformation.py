class PriceInformation:

    def __init__(self, contract):
        self.contract = contract
        self.bid = None
        self.ask = None
        self.high = None
        self.low = None
        self.open = None
        self.close = None
        self.last_price = None
        self.volume = None
        self.ask_size = None
        self.bid_size = None
        self.last_size = None

    def __str__(self):
        return f'bid: {str(self.bid)}\nask: {str(self.ask)}\nhigh: {str(self.high)}\nlow: {str(self.low)}\nopen: {str(self.open)}\nclose: {str(self.close)}\nvolume: {str(self.volume)}\nask_size: {self.ask_size}\nbid_size: {self.bid_size}\nlast_size: {self.last_size}'
