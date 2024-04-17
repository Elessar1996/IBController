from flask import Flask, request
from Constants import *
from db_utils import *
# from Central import Trader
from CSMATrader import CMSATrader
from IBInterface import MainIB
from IBAlternative import IBAlternative
import sys
import pprint

##TODO: Fix the new_multiple_sma calls in this file


app = Flask(__name__)
data = ["NOTHING"]

sma_numbers = [5, 20, 30, 60, 90, 150, 180, 240, 300, 360, 420, 480, 540, 600]
cdv_numbers = sma_numbers
cvd_numbers = [5, 100, 500, 900, 1300, 1700, 2100, 2500, 2900, 3300, 3700, 4100, 4500, 4900]

QUANTITY = 100

leverage = None
stop_loss = None
use_cvd = None
use_cdv = None

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


def separate(json_d):
    cdvs = []
    cvds = []
    smas = []

    for k in json_d.keys():

        if 'cdv' in k:
            cdvs.append((k, float(json_d[k])))
        elif 'cvd' in k:
            cvds.append((k, float(json_d[k])))
        elif 'sma' in k:
            smas.append((k, float(json_d[k])))

    return cdvs, cvds, smas


def run_command(command, ticker, price, quantity, asset_type, is_shortable):
    global ib
    global traders
    if command == 'long':

        ib.ib_buy(ticker, asset_type, quantity, price)
    elif command == 'short':
        if not is_shortable:
            return
        ib.ib_sell(ticker, asset_type, quantity, price)

    elif command == 'close and go short':

        ib.close_position_ib(ticker, asset_type, price, quantity, position=IN_LONG)
        if not is_shortable:
            return
        ib.ib_sell(ticker, asset_type, quantity, price)

    elif command == 'close and go long':
        if is_shortable:
            ib.close_position_ib(ticker, asset_type, price, quantity, position=IN_SHORT)
        ib.ib_buy(ticker, asset_type, quantity, price)

    elif command == 'close long':

        ib.close_position_ib(ticker, asset_type, price, quantity, position=IN_LONG)

    elif command == 'close short':

        if not is_shortable:
            return
        ib.close_position_ib(ticker, asset_type, price, quantity, position=IN_SHORT)

    else:

        return "No Command"


def generate_command(ticker, trade_args, price):
    global traders
    global stop_loss

    if ticker in traders.keys():
        return traders[ticker].new_multiple_sma(**trade_args)
    else:
        traders[ticker] = CMSATrader(tickness=tickness, beginning=begining, ticker=ticker,
                                     stop_loss=float(stop_loss))
        return traders[ticker].new_multiple_sma(**trade_args)


def insert_data_table(ticker, tuple_of_values):
    insert_item(f'{ticker}_data_table',
                columns_list=['created_at'] + [f'sma_{i}' for i in sma_numbers] +
                             [f'cdv_{i}' for i in cdv_numbers] + [f'cvd_{i}' for i in cvd_numbers] + ['command'],
                value_tuple=tuple_of_values)


def create_data_table(ticker):
    all_tables = get_list_of_all_tables()


    if f'{ticker}_data_table'.lower() in all_tables:

        return False
    else:

        create_table(

            columns=[('created_at', 'VARCHAR', '')] + [(f'sma_{i}', 'FLOAT', '') for i in sma_numbers]
                    + [(f'cdv_{i}', 'FLOAT', '') for i in cdv_numbers]
                    + [(f'cvd_{i}', 'FLOAT', '') for i in cvd_numbers]
                    + [('command', 'VARCHAR', '')],
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

    keys_and_values = webhook_message.split(',')

    json_dict = {}
    for kv in keys_and_values:
        kv_splitted = kv.split(':')
        if kv_splitted[0] not in json_dict.keys():
            json_dict[kv_splitted[0]] = kv_splitted[1]

    cdvs, cvds, smas = separate(json_dict)

    cdvs.sort(key=lambda t: int(t[0].split('_')[1]), reverse=False)
    cvds.sort(key=lambda t: int(t[0].split('_')[1]), reverse=False)
    smas.sort(key=lambda t: int(t[0].split('_')[1]), reverse=False)

    price = float(json_dict['close'])
    is_shortable = True if json_dict.get('is_shortable') == 'true' else False
    create_data_table(json_dict['ticker'])

    list_smas = []

    for k, v in json_dict.items():
        list_smas.append((k, v))

    sma_list = [i[1] for i in smas]
    cdv_list = [i[1] for i in cdvs]
    cvd_list = [i[1] for i in cvds]

    price = float(json_dict['close'])

    trade_args = {
        'price': price,
        'list_smas': sma_list,
        'list_cvds': cvd_list if use_cvd == 'use_cvd' else None,
        'list_cdvs': cdv_list if use_cdv == 'use_cdv' else None
    }

    ib.start_getting_level_two(json_dict['ticker'], STOCK)

    command = generate_command(json_dict['ticker'], trade_args, price)

    print(f'command: {command}')

    run_command(
        command=command,
        ticker=json_dict['ticker'],
        price=price,
        quantity=QUANTITY,
        asset_type=STOCK,
        is_shortable=is_shortable
    )

    values = [json_dict['time']] + sma_list + cvd_list + cdv_list + [command]

    values_tuple = tuple(values)

    insert_data_table(json_dict['ticker'], values_tuple)

    data.append(json_dict)


    return json_dict


if __name__ == '__main__':
    print(f'Server has been started ...')
    app.config['leverage'] = sys.argv[1]
    app.config['stop_loss'] = sys.argv[2]
    app.config['use_cdv'] = sys.argv[3]
    app.config['use_cvd'] = sys.argv[4]
    leverage = app.config['leverage']
    stop_loss = app.config['stop_loss']
    use_cdv = app.config['use_cdv']
    use_cvd = app.config['use_cvd']
    app.run()
