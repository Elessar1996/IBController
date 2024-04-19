from Constants import *
import time
import threading
import random


##TODO: Make it buy with the price with highest volume

class IBAlternative:

    def __init__(self, ib):
        self.ib = ib

        self.track_volume = {}

        self.id_ticker = {}

        self.all_ids = []

    def make_req_id(self, ticker):

        req_id = random.randint(1, 1000)
        while req_id in self.all_ids:
            req_id = random.randint(1, 1000)
        else:

            self.id_ticker[req_id] = ticker
            self.all_ids.append(req_id)

        return req_id

    def start_getting_level_two(self, ticker, ticker_type):

        if ticker in self.id_ticker.values():
            return
        req_id = self.make_req_id(ticker)

        t = threading.Thread(target=self.ib.get_level_two, args=(ticker, ticker_type, req_id))

        t.start()

    def get_req_id(self, ticker):

        return {v: k for k, v in self.id_ticker.items()}[ticker]

    def get_bid_price(self, ticker):

        req_id = self.get_req_id(ticker)

        data_items = self.ib.level_two[req_id][-10:]

        bid_items = [i for i in data_items if i.side == 1]

        if len(bid_items) == 0:
            return None

        return sorted(bid_items, key=lambda t: t.position)[-1].price

    def get_ask_price(self, ticker):

        req_id = self.get_req_id(ticker)

        data_items = self.ib.level_two[req_id][-10:]

        ask_items = [i for i in data_items if i.side == 0]

        if len(ask_items) == 0:
            return None

        return sorted(ask_items, key=lambda t: t.position)[-1].price

    def place_order_ib(self, contract, order):
        self.ib.placeOrder(orderId=self.ib.get_order_id(), contract=contract, order=order)

    def ib_buy(self, ticker, asset_type, quantity, price):

        p = price

        c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)

        price_information = self.ib.get_market_data(contract=c,
                                                    data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE, ASK_SIZE, BID_SIZE],
                                                    live_data=False)
        time.sleep(1)

        if quantity > price_information.ask_size:
            quantity = int(price_information.ask_size / 2) if int(price_information.ask_size / 2) != 0 else 1

        # price = price_information.ask if price_information.ask is not None else price
        price = self.get_ask_price(ticker)

        if price is None:
            price = price_information.ask if price_information.ask is not None else p

        order = self.ib.generate_order(price=price, quantity=quantity, action=BUY)
        self.place_order_ib(contract=c, order=order)
        self.track_volume[ticker] = quantity
        self.check_open_orders(ticker=ticker)

    def ib_sell(self, ticker, asset_type, quantity, price):

        p = price

        c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)

        price_information = self.ib.get_market_data(contract=c,
                                                    data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE, BID_SIZE, ASK_SIZE],
                                                    live_data=False)
        time.sleep(1)

        if quantity > price_information.bid_size / 2:
            quantity = int(price_information.bid_size / 2) if int(price_information.bid_size / 2) != 0 else 1

        # price = price_information.bid if price_information.bid is not None else price
        price = self.get_bid_price(ticker)

        if price is None:
            price = price_information.bid if price_information.bid is not None else p

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
        time.sleep(2)
        if ticker in open_orders.keys() and open_orders[ticker]['status'] == 'PreSubmitted':
            return True
        else:
            return False


if __name__ == '__main__':
    from IBInterface import MainIB
    import time

    ib = MainIB(0)
    time.sleep(1)

    ib_al = IBAlternative(ib=ib)
    ib_al.start_getting_level_two('INAB', ticker_type=STOCK)
    for i in range(100):
        time.sleep(0.1)
        print(ib_al.ib.level_two)
    # ib_al.ib_buy(ticker='INAB', asset_type='stock', quantity=1000000, price=120)
