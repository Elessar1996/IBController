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

        self.orderId_ticker = {}

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
            return None, None

        # selected_item = bid_items[-1]
        selected_item = sorted(bid_items, key=lambda t: t.price)[0]
        # selected_item = sorted(bid_items, key=lambda t: t.position)[-1]
        print(f'bid price for the ticker={ticker} has been picked up from level 2: {selected_item}')
        return selected_item.price, selected_item.size

    def get_ask_price(self, ticker):

        req_id = self.get_req_id(ticker)

        data_items = self.ib.level_two[req_id][-10:]

        ask_items = [i for i in data_items if i.side == 0]

        if len(ask_items) == 0:
            return None, None
        # selected_item = ask_items[-1]
        # selected_item = sorted(ask_items, key=lambda t: t.position)[-1]
        selected_item = sorted(ask_items, key=lambda t: t.price)[-1]
        print(f'ask price for the ticker={ticker} has been picked up from level 2: {selected_item}')
        return selected_item.price, selected_item.size

    def place_order_ib(self, contract, order):
        self.ib.placeOrder(orderId=self.ib.get_order_id(), contract=contract, order=order)

    def simple_buy(self, ticker, asset_type, quantity, price):
        c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)
        order = self.ib.generate_order(price=price, quantity=quantity, action=BUY)

        self.place_order_ib(contract=c, order=order)

    def ib_buy(self, ticker, asset_type, quantity, price):

        p = price

        q = quantity

        c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)

        price_information = self.ib.get_market_data(contract=c,
                                                    data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE, ASK_SIZE, BID_SIZE],
                                                    live_data=False)
        time.sleep(1)

        if q > price_information.ask_size:
            q = int(price_information.ask_size / 2) if int(price_information.ask_size / 2) != 0 else 1

        # price = price_information.ask if price_information.ask is not None else price
        price, quantity = self.get_ask_price(ticker)

        if quantity is not None:
            quantity = int(0.5 * float(quantity)) if int(0.5 * float(quantity)) != 0 else 1

        if price is None:
            price = price_information.ask if price_information.ask is not None else p
        if quantity is None:
            quantity = q
        order = self.ib.generate_order(price=price, quantity=quantity, action=BUY)

        # print('order id is:', order.id)
        self.place_order_ib(contract=c, order=order)
        self.orderId_ticker[self.ib.next_valid_order_id] = (c, order)

        self.track_volume[ticker] = quantity

        return quantity, self.ib.next_valid_order_id
        # self.check_open_orders(ticker=ticker)

    def ib_sell(self, ticker, asset_type, quantity, price):

        p = price

        q = quantity

        c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)

        price_information = self.ib.get_market_data(contract=c,
                                                    data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE, BID_SIZE, ASK_SIZE],
                                                    live_data=False)
        time.sleep(1)

        if q > price_information.bid_size / 2:
            q = int(price_information.bid_size / 2) if int(price_information.bid_size / 2) != 0 else 1

        # price = price_information.bid if price_information.bid is not None else price
        price, quantity = self.get_bid_price(ticker)

        if quantity is not None:
            quantity = int(0.5 * float(quantity)) if int(0.5 * float(quantity)) != 0 else 1

        if price is None:
            price = price_information.bid if price_information.bid is not None else p

        if quantity is None:
            quantity = q

        order = self.ib.generate_order(price=price, quantity=quantity, action=SELL)
        self.place_order_ib(contract=c, order=order)

        self.orderId_ticker[self.ib.next_valid_order_id] = (c, order)

        self.track_volume[ticker] = quantity

        return quantity, self.ib.next_valid_order_id

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

            self.orderId_ticker[self.ib.next_valid_order_id] = (c, order)

        elif position == IN_SHORT:
            quantity = self.track_volume[ticker]
            c = self.ib.make_contract(ticker=ticker.upper(), ticker_type=asset_type)
            price_information = self.ib.get_market_data(contract=c,
                                                        data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE, BID_SIZE,
                                                                    ASK_SIZE], live_data=False)
            price = price_information.ask if price_information.ask is not None else price

            order = self.ib.generate_order(price=price, quantity=quantity, action=BUY)
            self.place_order_ib(contract=c, order=order)

            self.orderId_ticker[self.ib.next_valid_order_id] = (c, order)

    def check_order(self, order_id):

        open_orders = self.ib.get_open_orders()
        time.sleep(2)

        the_order = open_orders[order_id]

        if the_order.remaining == 0:
            return True
        else:
            return False

    def handle_unfulfilled(self, order_id):

        self.cancel_order(order_id)

    def cancel_order(self, order_id):

        self.ib.cancelOrder(order_id, '')

    # def check_open_orders(self, ticker):
    #
    #     open_orders = self.ib.get_open_orders()
    #     time.sleep(2)
    #     if ticker in open_orders.keys() and open_orders[ticker]['status'] == 'PreSubmitted':
    #         return True
    #     else:
    #         return False


if __name__ == '__main__':
    from IBInterface import MainIB
    import time

    ib = MainIB(0)
    time.sleep(1)

    ib_al = IBAlternative(ib=ib)
    ib_al.simple_buy(ticker='AAPL', asset_type='stock', quantity=100, price=120)
    # open_orders = ib_al.ib.get_open_orders()
    # time.sleep(2)
    # print(open_orders)
    if ib_al.check_order(ib_al.ib.next_valid_order_id):
        print(f'order is fully fulfilled')
    else:
        print(f'Nah')
    # ib_al.ib.cancelOrder(ib_al.ib.next_valid_order_id)

    # ib_al.start_getting_level_two('INAB', ticker_type=STOCK)
    # for i in range(100):
    #     time.sleep(0.1)
    #     print(ib_al.ib.level_two)
