from Constants import *
import time


class IBAlternative:

    def __init__(self, ib):
        self.ib = ib

        self.track_volume = {}

    def place_order_ib(self, contract, order):
        self.ib.placeOrder(orderId=self.ib.get_order_id(), contract=contract, order=order)

    def ib_buy(self, ticker, asset_type, quantity, price):

        c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)

        price_information = self.ib.get_market_data(contract=c,
                                                    data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE, ASK_SIZE, BID_SIZE],
                                                    live_data=False)
        time.sleep(1)

        if quantity > price_information.ask_size:
            quantity = int(price_information.ask_size / 2) if int(price_information.ask_size / 2) != 0 else 1

        price = price_information.ask if price_information.ask is not None else price

        order = self.ib.generate_order(price=price, quantity=quantity, action=BUY)
        self.place_order_ib(contract=c, order=order)

        self.track_volume[ticker] = quantity

        self.check_open_orders(ticker=ticker)

    def ib_sell(self, ticker, asset_type, quantity, price):

        c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)

        price_information = self.ib.get_market_data(contract=c,
                                                    data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE, BID_SIZE, ASK_SIZE],
                                                    live_data=False)
        time.sleep(1)

        if quantity > price_information.bid_size/2:
            quantity = int(price_information.bid_size / 2) if int(price_information.bid_size / 2) != 0 else 1

        price = price_information.bid if price_information.bid is not None else price
        order = self.ib.generate_order(price=price, quantity=quantity, action=SELL)
        self.place_order_ib(contract=c, order=order)

        self.track_volume[ticker] = quantity

    def close_position_ib(self, ticker, asset_type, price, quantity, position):

        if position == IN_LONG:

            quantity = self.track_volume[ticker]

            c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)
            price_information = self.ib.get_market_data(contract=c,
                                                        data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE, BID_SIZE,
                                                                    ASK_SIZE], live_data=False)
            price = price_information.bid if price_information.bid is not None else price

            order = self.ib.generate_order(price=price, quantity=quantity, action=SELL)
            self.place_order_ib(contract=c, order=order)

        elif position == IN_SHORT:
            quantity = self.track_volume[ticker]
            c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)
            price_information = self.ib.get_market_data(contract=c,
                                                        data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE, BID_SIZE,
                                                                    ASK_SIZE], live_data=False)
            price = price_information.ask if price_information.ask is not None else price

            order = self.ib.generate_order(price=price, quantity=quantity, action=BUY)
            self.place_order_ib(contract=c, order=order)

    def check_open_orders(self, ticker):

        open_orders = self.ib.get_open_orders()
        print(f"open orders call from IBAlternative: {open_orders}")
        if ticker in open_orders.keys() and open_orders[ticker].status == 'PreSubmitted':
            print(f'ticker: {ticker} exists in open order lists')



if __name__ == '__main__':
    from IBInterface import MainIB
    import time

    ib = MainIB(0)
    time.sleep(1)

    ib_al = IBAlternative(ib=ib)

    ib_al.ib_buy(ticker='AAPL', ticker_type='stock', quantity=1, price=120)









