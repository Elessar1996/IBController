

class PositionInfo:

    def __init__(self, account, contract, position, avgCost):

        self.account = account
        self.contract = contract
        self.position = position
        self.avgCost = avgCost
        self.ticker = contract.symbol
        self.asset_type = contract.secType

    def __str__(self):

        string = f'account: {self.account} --- contract: {self.contract} --- position: {self.position} --- avgCost: {self.avgCost} --- ticker: {self.ticker} -- asset type: {self.asset_type}'

        return string


