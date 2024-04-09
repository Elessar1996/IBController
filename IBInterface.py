import time
import ibapi
import datetime
from ibapi.client import *
from ibapi.wrapper import *
from ibapi.contract import Contract
from Constants import *
from PositionInfo import PositionInfo
from PriceInformation import PriceInformation


import threading



class Wrapper(EWrapper):
    FINISHED = 'FINISHED'

    def __init__(self):
        super().__init__()

        self.contract_details = {}
        self.market_data = {}
        self.historical_data = []
        self.realtime_bars = []
        self.next_valid_order_id = None
        self.positions_pnl = {}
        self.positions = []
        self.position_end_flag = False
        self.unrealized_pnl = None
        self.current_position_id = None
        self.total_pnl = None


    def historicalData(self, reqId: int, bar: BarData):

        self.historical_data.append(bar)

    def nextValidId(self, orderId:int):
        self.next_valid_order_id = orderId

    def historicalDataEnd(self, reqId:int, start:str, end:str):

        self.historical_data.append(self.FINISHED)
        print(f'historical data request started at {start} and ended at {end}')


    def contractDetails(self, reqId: int, contractDetails: ContractDetails):

        try:
            self.contract_details[reqId].append(contractDetails)
        except KeyError:
            pass

    def contractDetailsEnd(self, reqId: int):

        try:

            self.contract_details[reqId].append(self.FINISHED)

        except KeyError:
            pass

    def pnlSingle(self, reqId: int, pos: int, dailyPnL: float, unrealizedPnL: float, realizedPnL: float, value: float):
        print(f'reqId: {reqId} --- pos: {pos}, dailyPnl: {dailyPnL} --- realizedPnl: {realizedPnL} --- unrealized pnl: {unrealizedPnL}')
        self.positions_pnl[reqId] = pos, dailyPnL, unrealizedPnL, realizedPnL, value if reqId in self.positions_pnl.keys() else None
        self.unrealized_pnl = unrealizedPnL

    def pnl(self, reqId: int, dailyPnL: float, unrealizedPnL: float, realizedPnL: float):

        self.total_pnl = unrealizedPnL

    def position(self, account:str, contract:Contract, position:float,
                 avgCost:float):
        self.positions.append(PositionInfo(account, contract, position, avgCost))

    def positionEnd(self):
        self.position_end_flag = True

    #
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float,
                  attrib: TickAttrib):

        print(f'price: {price} -- {TickTypeEnum.to_str(tickType)}')

        data_type = None
        if tickType == 0:
            data_type = BID_SIZE
        elif tickType == 1:
            data_type = BID
        elif tickType == 2:
            data_type = ASK
        elif tickType == 3:
            data_type = ASK_SIZE
        elif tickType == 6:
            data_type = HIGH
        elif tickType == 4:
            data_type = LAST_PRICE
        elif tickType == 7:
            data_type = LOW
        elif tickType == 14:
            data_type = OPEN
        elif tickType == 9:
            data_type = CLOSE
        try:
            setattr(self.market_data[reqId], data_type, price)
        except KeyError:
            pass
    def realtimeBar(self, reqId: TickerId, time:int, open_: float, high: float, low: float, close: float,
                        volume: int, wap: float, count: int):

        self.realtime_bars.append((open_, high, low, close, volume))



class Client(EClient):

    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)
        self.unique_id = 0

    def make_contract(self, ticker, ticker_type):

        if ticker_type == 'stock':

            contract = Contract()

            contract.symbol = ticker
            contract.secType = 'STK'
            contract.currency = 'USD'
            contract.exchange = 'SMART'


        elif ticker_type == 'currency':
            contract = Contract()
            contract.symbol = ticker
            contract.secType = 'CASH'
            contract.currency = 'USD'
            contract.exchange = 'IDEALPRO'

        else:
            contract = Contract()
            contract.symbol = ticker
            contract.secType = 'CRYPTO'
            contract.currency = 'USD'
            contract.exchange = 'PAXOS'

        return contract

    def get_unique_id(self)->int:

        self.unique_id += 1

        return self.unique_id

    def create_order(self, limit_price:float, quantity:float, action)-> Order:

        order = Order()
        order.action = action
        order.tif = 'GTC'
        order.eTradeOnly = False
        order.firmQuoteOnly = False
        order.orderType = 'LMT'
        order.totalQuantity = quantity
        order.lmtPrice = limit_price

        return order

    def create_market_order(self, quantity, action)-> Order:

        order = Order()
        order.action = action
        order.tif = 'GTC'
        order.eTradeOnly = False
        order.firmQuoteOnly = False
        order.orderType = 'MKT'
        order.totalQuantity = quantity

        return order

    def generate_order(self, quantity, price, action):

        this_moment = datetime.datetime.now()

        print(f'this moment: {this_moment}')

        ninethiry = this_moment.replace(hour=9, minute=30, second=0)
        print(f'nine thirty: {ninethiry}')
        fourpm = this_moment.replace(hour=16, minute=0, second=0)
        print(f'four pm: {fourpm}')

        print(f'limit order condition: {this_moment < ninethiry or this_moment > fourpm}')

        if this_moment < ninethiry or this_moment > fourpm:
            order = self.create_order(limit_price=price, quantity=quantity, action=action)
            return order
        else:
            order = self.create_market_order(quantity=quantity, action=action)
            return order



class MainIB(Wrapper, Client):

    def __init__(self, client_id):

        Wrapper.__init__(self)
        Client.__init__(self, wrapper=self)
        self.client_id = client_id
        self.reconnect()

    def main(self):

        contract = self.make_contract(ticker='EUR', ticker_type='currency')
        # order = self.create_order(limit_price=30305, action=BUY, quantity=10000)
        # self.placeOrder(orderId=self.get_order_id(),
        #                 contract=contract,
        #                 order=order)
        p = self.get_market_data(contract=contract, data_types=[BID, ASK, HIGH, LOW, OPEN, CLOSE], live_data=False)
        print(p)
        # self.get_total_pnl()
        #
        # while True:
        #     print(self.total_pnl)
        #     time.sleep(3)

        # self.get_historical_data(contract=contract)
        # self.get_realtime_bars(contract=contract, bar_size=30)

        # self.stream_market_data(contract=contract,
        #                         data_types=[ASK, BID, HIGH, CLOSE, VOLUME, OPEN, LOW],
        #                       )
        # data = self.get_market_data(contract=contract, data_types=[VOLUME])
        # print(f'volume: {data.volume}')

    def reconnect(self):

        self.connect(
            host='127.0.0.1',
            port=7497,
            clientId=self.client_id
        )

        t = threading.Thread(target=self.run).start()

        setattr(self, '_thread', t)

    def complete_contract(self, contract: Contract, timeout: int) -> list:

        req_id = self.get_unique_id()
        self.contract_details[req_id] = []

        self.reqContractDetails(req_id, contract)

        for _ in range(100 * timeout):

            time.sleep(0.01)

            if self.FINISHED in self.contract_details[req_id]:
                self.contract_details[req_id].remove(self.FINISHED)

                return [c.contract for c in self.contract_details[req_id]]
            else:
                continue
        else:
            return []

    def get_market_data(self, contract: Contract, data_types: list, live_data: bool = True,
                        timeout: int = 10) -> PriceInformation:

        req_id = self.get_unique_id()
        self.market_data[req_id] = PriceInformation(contract)
        self.reqMarketDataType(1) if live_data else self.reqMarketDataType(3)
        self.reqMarketDataType(0)
        self.reqMarketDataType(3)
        self.reqMktData(reqId=req_id, contract=contract, genericTickList="", snapshot=True, regulatorySnapshot=False,
                        mktDataOptions=[])

        for _ in range(100 * timeout):

            time.sleep(0.01)

            if None in [getattr(self.market_data[req_id], dt) for dt in data_types]:
                continue
            else:
                break

        return self.market_data.pop(req_id)

    # def stream_market_data(self, contract: Contract, data_types: list, live_data: bool = True,
    #                        timeout: int = 10) -> PriceInformation:
    #     req_id = self.get_unique_id()
    #     self.market_data[req_id] = PriceInformation(contract)
    #     self.reqMarketDataType(1)
    #     self.reqMktData(
    #         reqId=req_id,
    #         contract=contract,
    #         genericTickList='',
    #         snapshot=False,
    #         regulatorySnapshot=False,
    #         mktDataOptions=[]
    #     )
    #
    #     while True:
    #         time.sleep(1)
    #         print(self.market_data[req_id])
    #
    #     self.cancelMktData(req_id)

    def get_historical_data(self, contract: Contract, keep_updating: bool = False,
                           timeout: int = 10, whatToShow: str = 'TRADES'):
        req_id = self.get_unique_id()

        self.reqHistoricalData(reqId=req_id, contract=contract, endDateTime='',
                               durationStr='1 D', barSizeSetting='1 min', keepUpToDate=keep_updating, whatToShow=whatToShow, useRTH=True, chartOptions=[], formatDate=1)

        for _ in range(timeout*100):
            time.sleep(0.01)
            if self.FINISHED in self.historical_data:
                self.historical_data.pop()
                return self.historical_data
            else:
                continue
        else:
            return []

    def get_realtime_bars(self, contract:Contract, bar_size: int=5, whatToShow: str ='TRADES', useRTH: bool = True, timeout:int = 5):

        req_id = self.get_unique_id()

        self.reqRealTimeBars(reqId=req_id, contract=contract, barSize=bar_size, whatToShow=whatToShow, useRTH=useRTH, realTimeBarsOptions=[])
        for _ in range(100*timeout):
            time.sleep(0.01)
            if len(self.realtime_bars) > 0:
                return self.realtime_bars.pop()
            else:
                continue
        else:
            return tuple()

    def get_total_pnl(self, timeout=10):

        self.total_pnl = None
        self.reqPnL(reqId=self.get_unique_id(), account=ACCOUNT, modelCode='')
        for _ in range(100*timeout):

            time.sleep(0.01)
            if self.total_pnl is not None:
                print('total pnl:', self.total_pnl)
                break
            else:
                continue
        else:
            print('none received')


    def get_order_id(self, timeout:int=10):

        self.next_valid_order_id = None
        self.reqIds(-1)
        for _ in range(100*timeout):
            time.sleep(0.01)
            if self.next_valid_order_id is not None:
                self.current_position_id = self.next_valid_order_id
                return self.next_valid_order_id
            else:
                continue
        else:
            self.current_position_id = None
            return None

    def get_pnl(self, timeout=10):
        positions = self.get_positions()
        self.positions_pnl = {}
        contract_for_id = {}

        for position in positions:
            position: PositionInfo = position

            # if position.position == 0:
            #     continue

            req_id = self.get_unique_id()
            self.positions_pnl[req_id] = None
            self.reqPnLSingle(reqId=req_id,
                              account=position.account,
                              modelCode='',
                              conid=position.contract.conId)
            contract_for_id[req_id] = position.contract

        for _ in range(timeout*100):
            time.sleep(0.01)
            if None not in self.positions_pnl.values():
                break

        for key, pnl in self.positions_pnl.items():
            # try:
            #     self.cancelPnLSingle(key)
            # except:
            #     pass
            if pnl is not None:


                try:

                    # print(f'pnl for contract={contract_for_id[key]} is:')
                    for i in pnl:
                        pass
                        # print(i)
                except:
                    pass
        # print(f'positions pnl: {self.positions_pnl}')
        return self.positions_pnl

    def get_specific_pnl(self, contract, req_id,timeout=10):
        positions = self.get_positions()
        self.positions_pnl = {}
        contract_for_id = {}
        the_position = None
        for position in positions:
            the_position: PositionInfo = position
            # if position.contract == contract:
            #     the_position: PositionInfo = position
            #     break
        # req_id = self.get_unique_id()
        self.reqPnLSingle(
            reqId=req_id,
            modelCode='',
            account=the_position.account,
            conid=the_position.contract.conId
        )
        self.unrealized_pnl = None
        time.sleep(2)
        for _ in range(timeout*100):
            time.sleep(0.01)
            if self.unrealized_pnl is not None:
                break
            else:
                continue
        else:
            self.unrealized_pnl = 0

    def get_positions(self, timeout=10):
        self.positions = []
        self.position_end_flag = False
        self.reqPositions()

        for _ in range(timeout*100):
            time.sleep(0.01)
            if self.position_end_flag:
                break

        self.cancelPositions()

        return self.positions
    #
    # def main(self):
    #
    #     positions = self.get_positions()
    #
    #     for p in positions:
    #         print(p)






if __name__ == '__main__':
    # print(ibapi.__version__)
    ib = MainIB(11)
    time.sleep(5)
    ib.main()
