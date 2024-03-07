from flask import Flask, request
from Constants import *
from db_utils import *
# from Central import Trader
from AlgorithmicTrader import AlgorithmicTrader
from IBInterface import MainIB
from IBAlternative import IBAlternative
import sys


print(f'beginning of the file')
app = Flask(__name__)
data = ["NOTHING"]

QUANTITY = 100

leverage = None
stop_loss = None

# ib = IBAlternative(
#     ib=MainIB(client_id=13)
# )
ib = None
traders = {}

begining = 5
tickness = 5

first_time = True


delete_all()
drop_all_tables()
create_db(db_name=DATABASE_NAME)


# trader = Trader(5, 5)

# QUANTITY = 100
#
# # ib = IBAlternative(
# #     ib=MainIB(client_id=13)
# # )
# ib = None
# traders = {}
#
# begining = 5
# tickness = 5
#
# first_time = True
# data = ["NOTHING"]


def run_command(command, ticker, price, quantity, asset_type):
    global ib
    global traders
    if command == 'long':

        ib.ib_buy(ticker, asset_type, quantity, price)
    elif command == 'short':
        ib.ib_sell(ticker, asset_type, quantity, price)

    elif command == 'close and go short':

        ib.close_position_ib(ticker, asset_type, price, quantity, position=IN_LONG)
        ib.ib_sell(ticker, asset_type, quantity, price)

    elif command == 'close and go long':

        ib.close_position_ib(ticker, asset_type, price, quantity, position=IN_SHORT)
        ib.ib_buy(ticker, asset_type, quantity, price)
    elif command == 'close long':

        ib.close_position_ib(ticker, asset_type, price, quantity, position=IN_LONG)

    elif command == 'close short':

        ib.close_position_ib(ticker, asset_type, price, quantity, position=IN_SHORT)

    else:

        return None

def generate_command(ticker, trade_args):
    global traders
    global stop_loss

    if ticker in traders.keys():
        return traders[ticker].multiple_sma(trade_args)
    else:
        traders[ticker] = AlgorithmicTrader(tickness=tickness, begining=begining, ticker=ticker,
                                            stop_loss=stop_loss)
        return traders[ticker].multiple_sma(trade_args)


def insert_data_table(ticker, tuple_of_values):
    insert_item(f'{ticker}_data_table',
                columns_list=['created_at',
                              'sma_5', 'sma_20', 'sma_30', 'sma_60', 'sma_90', 'sma_150',
                              'sma_180', 'sma_240', 'sma_300', 'sma_360', 'sma_420', 'sma_480',
                              'sma_540', 'sma_600', 'command'],
                value_tuple=tuple_of_values)


def create_data_table(ticker):

    all_tables = get_list_of_all_tables()

    print(all_tables)

    if f'{ticker}_data_table'.lower() in all_tables:
        print(f'Table {ticker}_data_table already exists')

        return False
    else:

        create_table(

            columns=[
                ('created_at', 'VARCHAR', ''),
                ('sma_5', 'FLOAT', ''),
                ('sma_20', 'FLOAT', ''),
                ('sma_30', 'FLOAT', ''),
                ('sma_60', 'FLOAT', ''),
                ('sma_90', 'FLOAT', ''),
                ('sma_150', 'FLOAT', ''),
                ('sma_180', 'FLOAT', ''),
                ('sma_240', 'FLOAT', ''),
                ('sma_300', 'FLOAT', ''),
                ('sma_360', 'FLOAT', ''),
                ('sma_420', 'FLOAT', ''),
                ('sma_480', 'FLOAT', ''),
                ('sma_540', 'FLOAT', ''),
                ('sma_600', 'FLOAT', ''),
                ('command', 'VARCHAR', ''),

            ],
            table_name=f'{ticker}_data_table'

        )


@app.route('/')
def dashboard():
    global data

    return dict(data)


@app.route('/webhook', methods=['POST'])
def webhook():
    global data
    global first_time
    global ib

    if first_time:
        create_db(db_name=DATABASE_NAME)
        delete_all()
        drop_all_tables()
        ib = IBAlternative(
            ib=MainIB(client_id=13)
        )


        first_time = False

    webhook_message = request.data.decode('utf-8')

    print(f'webhook message: {webhook_message}')

    keys_and_values = webhook_message.split(',')

    json_dict = {}
    for kv in keys_and_values:
        kv_splitted = kv.split(':')

        json_dict[kv_splitted[0]] = kv_splitted[1]

    price = float(json_dict['close'])
    create_data_table(json_dict['ticker'])

    list_smas = []

    for k, v in json_dict.items():
        list_smas.append((k, v))

    sorted_smas = sorted(list_smas[:-3], key=lambda t: int(t[0].split('_')[1]), reverse=False)

    trade_arg = [float(i[1]) for i in sorted_smas]
    print(f'trade args: {trade_arg}')

    command = generate_command(json_dict['ticker'], trade_arg)

    run_command(
        command=command,
        ticker=json_dict['ticker'],
        price=price,
        quantity=QUANTITY,
        asset_type=STOCK
    )

    # command = trader.multiple_sma(trade_arg)

    values = [json_dict['time']] + trade_arg + [command]

    values_tuple = tuple(values)

    insert_data_table(json_dict['ticker'], values_tuple)

    data.append(json_dict)

    return json_dict


if __name__ == '__main__':
    print(f'hi')
    app.config['leverage'] = sys.argv[1]
    app.config['stop_loss'] = sys.argv[2]
    leverage = app.config['leverage']
    stop_loss = app.config['stop_loss']
    print(leverage, stop_loss)
    app.run()



