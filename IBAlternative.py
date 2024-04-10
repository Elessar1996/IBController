from Constants import *
import time

class IBAlternative:

    def __init__(self, ib):
        self.ib = ib

    def place_order_ib(self, contract, order):
        self.ib.placeOrder(orderId=self.ib.get_order_id(), contract=contract, order=order)

    def ib_buy(self, ticker, asset_type, quantity, price):

        c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)

        price_information = self.ib.get_market_data(contract=c, data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE, ASK_SIZE, BID_SIZE], live_data=False)
        time.sleep(1)

        if quantity > price_information.ask_size:

            quantity = int(price_information.ask_size/2)




        order = self.ib.generate_order(price=price, quantity=quantity, action=BUY)
        self.place_order_ib(contract=c, order=order)

    def ib_sell(self, ticker, asset_type, quantity, price):

        c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)

        price_information = self.ib.get_market_data(contract=c, data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE, BID_SIZE, ASK_SIZE], live_data=False)
        time.sleep(1)

        if quantity > price_information.bid_size:
            quantity = int(price_information.bid_size/2)

        order = self.ib.generate_order(price=price, quantity=quantity, action=SELL)
        self.place_order_ib(contract=c, order=order)

    def close_position_ib(self, ticker, asset_type, price, quantity, position):

        if position == IN_LONG:

            order = self.ib.generate_order(price=price,quantity=quantity, action=SELL)
            c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)
            self.place_order_ib(contract=c, order=order)

        elif position == IN_SHORT:
            order = self.ib.generate_order(price=price, quantity=quantity, action=BUY)
            c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)
            self.place_order_ib(contract=c, order=order)

