import csv
import pickle
import decimal  # 이것은 시간이 오래 걸리기 때문에 주문이 들어기지 않는 경우에만 사용하는 것이 좋다(전송 수량 찾을 때 굳)

# ck
import datetime
# import pytictoc
import sys

sys.setrecursionlimit(1000000)  # 재귀함수 제한 늘리기
import pandas as pd
import numpy as np
import pip
import sys
import requests
import json
# api json 파싱 python 업비트
import jwt  # PyJWT
import uuid
import requests
from urllib.parse import urlencode
import pyupbit  # 업비트#버젼 0.2.8 # '0.2.33'

print(pyupbit.Upbit)
import ccxt  # 바이낸스

print(ccxt)

import pprint
import time
import math

import binance  # !pip install binance-connector # 버젼 '1.0.16'
import os
import hashlib
from binance.client import Client  # python-binance
########선물거래를 위해#######
from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *
from binance_f.model.constant import *
from IPython.display import display, clear_output
from binance.spot import Spot  # !pip install binance-connector

##############################소수점 정리....##############################################

##@@@ 이 두개도 합치기


###########업비트에서 환율 조회


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def upbit_get_usd_krw():
    try:
        url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
        exchange = requests.get(url, headers=headers).json()
        return exchange[0]['basePrice']
    except:
        pass


# https://docs.upbit.com/docs/market-info-trade-price-detail
################################원화 마켄 주문 최소 주문 가격 단위###########################
def UP_Minimum_Order_cash_Size(up_pre):  ##@@여기 전부 가격을 넣는 형식으로 바꿈.
    #     up_pre = pyupbit.get_current_price("KRW-" + symbol)  # 해당코인 가격조회
    # print(up_pre,"원화 최소 주문 가격 단위 조회")
    if (2000000 <= up_pre):
        return 1000
    if (1000000 <= up_pre < 2000000):
        return 500
    if (500000 <= up_pre < 1000000):
        return 100
    if (100000 <= up_pre < 500000):
        return 50
    if (10000 <= up_pre < 100000):
        return 10
    if (1000 <= up_pre < 10000):
        return 5
    if (100 <= up_pre < 1000):
        return 1
    if (10 <= up_pre < 100):
        return 0.1
    if (0 <= up_pre < 10):
        return 0.01


#########################################전송가능 심볼명#########################################
######심볼명 예외처리로 중복제거를 위해######
def removeAllOccur(l, i):
    try:
        while True: l.remove(i)
    except ValueError:
        pass


#########################################
def bin_fu_setting(send_to_bin_optimal_symbol, future_leverage):
    try:
        result = request_client.change_margin_type(symbol=send_to_bin_optimal_symbol + "USDT", marginType=FuturesMarginType.ISOLATED)
    #         PrintBasic.print_obj(result)
    except:  # print("마진타입 변화 불필요")
        pass

    try:
        result = request_client.change_initial_leverage(symbol=send_to_bin_optimal_symbol + "USDT", leverage=future_leverage)
    #         PrintBasic.print_obj(result) # 레버리지 변화 (자본에 따라 기본 10배)
    except:
        pass


#     PrintBasic.print_obj(result)

def up_spot_ask_bid_info(sym_name):
    # 업비트 매수, 매도 호가창 한번에 조회
    up_sym_names = ["KRW-" + sym_name[i] for i in range(len(sym_name))]
    up_spot_ask_bid = pyupbit.get_orderbook(ticker=up_sym_names)
    return up_sym_names, up_spot_ask_bid


def up_ask_info(up_sym_names, up_spot_ask_bid):  # 업비트 매수 호가창
    up_ask_price = []
    up_ask_size = []
    up_ask_price_append = up_ask_price.append
    up_ask_size_append = up_ask_size.append
    for i in range(len(up_sym_names)):
        up_ask_price_append(float(next((item for item in up_spot_ask_bid if item['market'] == up_sym_names[i]), None)['orderbook_units'][0]['ask_price']))
        up_ask_size_append(float(next((item for item in up_spot_ask_bid if item['market'] == up_sym_names[i]), None)['orderbook_units'][0]['ask_size']))
    #         print(up_ask_price[i],up_ask_size[i],up_sym_names[i])
    return up_ask_price, up_ask_size


def up_bid_info(up_sym_names, up_spot_ask_bid):  # 업비트 매도 호가창
    up_bid_price = []
    up_bid_size = []
    up_bid_price_append = up_bid_price.append
    up_bid_size_append = up_bid_size.append
    for i in range(len(up_sym_names)):
        up_bid_price_append(float(next((item for item in up_spot_ask_bid if item['market'] == up_sym_names[i]), None)['orderbook_units'][0]['bid_price']))
        up_bid_size_append(float(next((item for item in up_spot_ask_bid if item['market'] == up_sym_names[i]), None)['orderbook_units'][0]['bid_size']))
    #         print(up_bid_price[i],up_bid_size[i],up_sym_names[i])
    return up_bid_price, up_bid_size


# up_sym_names, up_spot_ask_bid = up_spot_ask_bid_info(sym_name)
# up_ask_price, up_ask_size = up_ask_info(up_sym_names,up_spot_ask_bid)
# up_bid_price, up_bid_size= up_bid_info(up_sym_names,up_spot_ask_bid)
def bin_spot_ask_bid_info(sym_name):  # 바이낸스 현물 호가창 한번에 조회
    bin_sym_names = [sym_name[i] + "USDT" for i in range(len(sym_name))]
    bin_spot_ask_bid = client_spot.book_ticker()
    return bin_sym_names, bin_spot_ask_bid


def bin_ask_info(bin_sym_names, bin_spot_ask_bid):  # 바이낸스 현물 호가창 조회로 매수 호가창 가져옴
    bin_spot_ask_price = []
    bin_spot_ask_size = []
    bin_spot_ask_price_append = bin_spot_ask_price.append
    bin_spot_ask_size_append = bin_spot_ask_size.append
    for i in range(len(bin_sym_names)):
        bin_spot_ask_price_append(float(next((item for item in bin_spot_ask_bid if item['symbol'] == bin_sym_names[i]), None)['askPrice']))
        bin_spot_ask_size_append(float(next((item for item in bin_spot_ask_bid if item['symbol'] == bin_sym_names[i]), None)['askQty']))
    #         print(bin_spot_ask_price[i],bin_spot_ask_size[i],bin_sym_names[i])
    return bin_spot_ask_price, bin_spot_ask_size


def bin_bid_info(bin_sym_names, bin_spot_ask_bid):  # 바이낸스 현물 호가창 조회로 매도 호가창 가져옴
    bin_spot_bid_price = []
    bin_spot_bid_size = []
    bin_spot_bid_price_append = bin_spot_bid_price.append
    bin_spot_bid_size_append = bin_spot_bid_size.append

    for i in range(len(bin_sym_names)):
        bin_spot_bid_price_append(float(next((item for item in bin_spot_ask_bid if item['symbol'] == bin_sym_names[i]), None)['bidPrice']))
        bin_spot_bid_size_append(float(next((item for item in bin_spot_ask_bid if item['symbol'] == bin_sym_names[i]), None)['bidQty']))
    #         print(bin_spot_bid_price[i],bin_spot_bid_size[i],bin_sym_names[i])
    return bin_spot_bid_price, bin_spot_bid_size


# bin_sym_names, bin_spot_ask_bid = bin_spot_ask_bid_info(sym_name)
# bin_spot_ask_price,bin_spot_ask_size = bin_ask_info(bin_sym_names,bin_spot_ask_bid)
# bin_spot_bid_price,bin_spot_bid_size = bin_bid_info(bin_sym_names,bin_spot_ask_bid)

def bin_fu_ask_bid_info(sym_name):
    bin_sym_names = [sym_name[i] + "USDT" for i in range(len(sym_name))]
    bin_fu_ask_bid = client.futures_orderbook_ticker()

    return bin_sym_names, bin_fu_ask_bid


def bin_fu_ask_info(bin_sym_names, bin_fu_ask_bid):
    bin_fu_ask_price = []
    bin_fu_ask_size = []
    bin_fu_ask_price_append = bin_fu_ask_price.append
    bin_fu_ask_size_append = bin_fu_ask_size.append
    for i in range(len(bin_sym_names)):
        bin_fu_ask_price_append(float(next((item for item in bin_fu_ask_bid if item['symbol'] == bin_sym_names[i]), None)['askPrice']))
        bin_fu_ask_size_append(float(next((item for item in bin_fu_ask_bid if item['symbol'] == bin_sym_names[i]), None)['askQty']))
    #         print(bin_fu_ask_price[i],bin_fu_ask_size[i],bin_sym_names[i])
    return bin_fu_ask_price, bin_fu_ask_size


def bin_fu_bid_info(bin_sym_names, bin_fu_ask_bid):
    bin_fu_bid_price = []
    bin_fu_bid_size = []
    bin_fu_bid_price_append = bin_fu_bid_price.append
    bin_fu_bid_size_append = bin_fu_bid_size.append

    for i in range(len(bin_sym_names)):
        bin_fu_bid_price_append(float(next((item for item in bin_fu_ask_bid if item['symbol'] == bin_sym_names[i]), None)['bidPrice']))
        bin_fu_bid_size_append(float(next((item for item in bin_fu_ask_bid if item['symbol'] == bin_sym_names[i]), None)['bidQty']))
    #         print(bin_fu_bid_price[i],bin_fu_bid_size[i],bin_sym_names[i])
    return bin_fu_bid_price, bin_fu_bid_size


# bin_sym_names,bin_fu_ask_bid = bin_fu_ask_bid_info(sym_name)
# bin_fu_ask_price,bin_fu_ask_size = bin_fu_ask_info(sym_name,bin_fu_ask_bid)
# bin_fu_bid_price,bin_fu_bid_size = bin_fu_bid_info(sym_name,bin_fu_ask_bid)

def find_max_per(second_using_asset, sym_name, bin_spot_ask_price, bin_withdrawfee):
    max_per = []
    max_per_append = max_per.append
    for i in range(len(sym_name)):
        max_per_append(bin_spot_ask_price[i] * bin_withdrawfee[i] / ((second_using_asset / Usdt) / 2))

    return max_per[max_per.index(max(max_per))]


def Adjusting_second_using_asset(second_using_asset, up_market_fee, bin_spot_market_fee, bin_future_market_fee, per, adjust_leverage):
    # 레버리지를 비율 조정.. 이 부분 맞나?
    #     if (adjust_leverage == 1):
    #         pass
    #     else:
    #         adjust_leverage = adjust_leverage - 1

    a = (1 - bin_future_market_fee) * adjust_leverage  # 바
    b = (1 - bin_spot_market_fee) * (1 - up_market_fee) * (1 - per)  # *(1-0.0004)#@ 0.0004는 추가 보정치 #업

    c = a / (a + b)  # 업
    d = b / (a + b)  # 바

    bin_spot_Usdt_Send_to_up = second_using_asset * c
    bin_fu_Usdt_asset = second_using_asset * d

    return bin_spot_Usdt_Send_to_up, bin_fu_Usdt_asset


# def Adjusting_first_using_asset(sym_name,up_bid_price,up_withdrawfee,up_asset,binance_asset,up_market_fee,bin_spot_market_fee,bin_future_market_fee):
#     max_per = []
#     for i in range(len(sym_name)):
#         max_per.append(up_bid_price[i]* up_withdrawfee[i])
#     max_val= max_per[max_per.index(max(max_per))]

#     a = (1- up_market_fee) * (1-(max_val/up_asset)) *(1- bin_spot_market_fee)
#     b = (1- bin_future_market_fee)

#     c = (a / (a + b)) * (up_asset + binance_asset)
#     d = (b / (a + b)) * (up_asset + binance_asset)
# #     print(c,d)
#     return c,d #바낸자본 업비트 자본

def up_to_bin_canwithdrow_fee(sym_name):
    server_url = 'https://api.upbit.com'
    query = {'currency': sym_name, }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {'access_key': access_key, 'nonce': str(uuid.uuid4()), 'query_hash': query_hash,
               'query_hash_alg': 'SHA512', }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/withdraws/chance", params=query, headers=headers)
    # 해당 코인 전송수수료(해당코인 시가 * 전송 수수료)
    symbol_fee = float(res.json()['currency']['withdraw_fee'])
    #         print(symbol_fee)
    #     upbit_withdraw_fee = float(res.json()['currency']['withdraw_fee']) * up_pre
    #         print(upbit_withdraw_fee,"업비트 보낼 시 심볼 전송 가격")

    bin_sym_send_state = res.json()['withdraw_limit']['can_withdraw']  # 출금지원가능여부

    if (bin_sym_send_state == True):
        pass
    else:
        print(sym_name, "해당코인 업비트에서 바이낸스로 출금 불가상태")

    return symbol_fee, bin_sym_send_state


def up_deposit_address(sym_name):
    server_url = 'https://api.upbit.com'
    ############추가 ... 입출금 상태는 주소로 받아야댐..
    try:
        query = {'currency': sym_name, }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {'access_key': access_key,
                   'nonce': str(uuid.uuid4()),
                   'query_hash': query_hash,
                   'query_hash_alg': 'SHA512', }

        jwt_token = jwt.encode(payload, secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.post(server_url + "/v1/deposits/generate_coin_address", params=query, headers=headers)
        up_add = res.json()['deposit_address']
        bin_sym_send_state_2 = True
        up_seadd = res.json()['secondary_address']

        return up_add, bin_sym_send_state_2, up_seadd
    # print(up_add, up_seadd)

    except KeyError:
        up_add = "해당코인 바이낸스에서 업비트 입금 불가상태"
        up_seadd = "해당코인 바이낸스에서 업비트 입금 불가상태"
        bin_sym_send_state_2 = False
        print(sym_name, "해당코인 바이낸스에서 업비트 입금 불가상태")
        return up_add, bin_sym_send_state_2, up_seadd


def up_deposit_address_2(sym_name):
    #### 업비트 해당코인 입금 주소 생성요청
    try:
        query = {'currency': sym_name, }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512', }

        jwt_token = jwt.encode(payload, secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.post(server_url + "/v1/deposits/generate_coin_address", params=query,
                            headers=headers)
        up_add = res.json()['deposit_address']
        up_sym_send_state = True
        up_seadd = res.json()['secondary_address']
        # print(up_add, up_seadd)
        return up_add, up_sym_send_state, up_seadd

    except KeyError:
        up_add = "해당코인 바이낸스에서 업비트 입금 불가상태"
        up_seadd = "해당코인 바이낸스에서 업비트 입금 불가상태"
        up_sym_send_state = False
        print(sym_name, "해당코인 바이낸스에서 업비트 입금 불가상태")
        return up_add, up_sym_send_state, up_seadd


def up_bin_withdraw_fee(sym_name, all_coin_info):
    # 심볼명,달러 등은 전부 수수료를 저장해두고 나중에 갱신.
    up_withdrawfee = []
    bin_withdrawfee = []
    up_withdrawfee_append = up_withdrawfee.append
    bin_withdrawfee_append = bin_withdrawfee.append
    #     all_coin_info = client_spot.coin_info()
    for i in range(len(sym_name)):
        aa = next((item for item in all_coin_info if item['coin'] == sym_name[i]), None)['networkList']
        bin_withdrawfee_append(float(next((item for item in aa if item['network'] == sym_name[i]), None)['withdrawFee']))
        symbol_fee, bin_sym_send_state = up_to_bin_canwithdrow_fee(sym_name[i])
        up_withdrawfee_append(symbol_fee)
        time.sleep(0.4)
    return up_withdrawfee, bin_withdrawfee


def bin_withdraw_fee(all_coin_info, sym_name):
    aa = next((item for item in all_coin_info if item['coin'] == sym_name), None)['networkList']
    bin_withdrawfee = (float(next((item for item in aa if item['network'] == sym_name), None)['withdrawFee']))
    return bin_withdrawfee


def sym_intersection():
    ######바이낸스 달러 선물가능 심볼명#####
    bin_fu_sym = client.futures_symbol_ticker()
    for i in range(len(bin_fu_sym)):
        if (bin_fu_sym[i]['symbol'][-4:] == 'USDT'):
            bin_fu_sym[i] = bin_fu_sym[i]['symbol'][:-4]
        else:
            bin_fu_sym[i] = 'remove'
    removeAllOccur(bin_fu_sym, 'remove')
    ########################################
    #####바이낸스 달러 현물가능 코인 심볼명#USDT만 찾기 #####
    bin_sym = client.get_symbol_ticker()

    for i in range(len(bin_sym)):
        if (bin_sym[i]['symbol'][-4:] == 'USDT'):
            bin_sym[i] = bin_sym[i]['symbol'][:-4]
        else:
            bin_sym[i] = 'remove'
    removeAllOccur(bin_sym, 'remove')
    ########################################################
    ######업비트 코인 심볼명########
    up_sym = pyupbit.get_tickers(fiat="KRW")
    for i in range(len(up_sym)):
        # tickers[i].replace('KRW-','')
        up_sym[i] = up_sym[i][4:]
    #################################
    ######심볼명 교집합#####
    # sym_name = list(set(bin_sym) & set(up_sym))  # @
    sym_name = list(set(bin_fu_sym) & set(bin_sym) & set(up_sym))
    print(len(sym_name), len(sym_name))  # 선물없이 업비트만해선..
    return sym_name


def bin_coin_withdrow_fee(all_coin_info, sym_name):
    try:
        aa = next((item for item in all_coin_info if item['coin'] == sym_name), None)['networkList']
        withdrawfee = float(next((item for item in aa if item['network'] == sym_name), None)['withdrawFee'])
        return withdrawfee
    except:
        withdrawfee = "None_network"
        return withdrawfee
        pass


def bin_coin_withdrow_deopsit_Enable(all_coin_info, sym_name):
    try:  # 자기자신의 네트워크를 가지고, 현재 바이낸스의 입출금 가능상태를 가져옴
        aa = next((item for item in all_coin_info if item['coin'] == sym_name), None)['networkList']
        bb = next((item for item in aa if item['network'] == sym_name), None)
        depositEnable, withdrawEnable = bb['depositEnable'], bb['withdrawEnable']
    except:
        depositEnable, withdrawEnable = False, False

    return depositEnable, withdrawEnable


def del_bin_disable_withdrow_deopsit(all_coin_info, sym_name):
    delet_list = []
    delet_list_append = delet_list.append
    for i in range(len(sym_name)):  # 바이낸스에서 입금 가능 , 전송 불가능
        depositEnable, withdrawEnable = bin_coin_withdrow_deopsit_Enable(all_coin_info, sym_name[i])
        #         print(sym_name[i],depositEnable,withdrawEnable)
        if (depositEnable == False or withdrawEnable == False):
            delet_list_append(sym_name[i])
    name = list(set(sym_name) - set(delet_list))
    return name


def delet_None_network(all_coin_info, sym_name):
    delet_list = []
    delet_list_append = delet_list.append
    for i in range(len(sym_name)):  # 바이낸스에서 전송
        withdrawfee = bin_coin_withdrow_fee(all_coin_info, sym_name[i])
        #         print(sym_name[i],withdrawfee)
        if (withdrawfee == "None_network"):
            delet_list_append(sym_name[i])
    name = list(set(sym_name) - set(delet_list))
    return name


def regester_by_upbit_withdrow_addres(sym_name):
    for i in range(len(sym_name)):
        #         print(sym_name[i])
        try:
            bin_address = client_spot.deposit_address(sym_name[i])['address']
            bin_Memo = client_spot.deposit_address(sym_name[i])['tag']
            time.sleep(0.1)
            print(sym_name[i])
            print('bin_address', bin_address)
            print('bin_Memo', bin_Memo)
        except:
            print(sym_name[i], "바이낸스 지갑이 닫혔을 수도 있음")


# def Adjusting_second_using_asset(second_using_asset,up_market_fee,bin_spot_market_fee,bin_future_market_fee):
#     a = (1- bin_future_market_fee) #바
#     b = (1- bin_spot_market_fee) * (1- up_market_fee) #업

#     c = a / (a+b) #업
#     d = b / (a+b) #바

#     bin_spot_Usdt_Send_to_up = second_using_asset * c
#     bin_fu_Usdt_asset = second_using_asset * d
#     return bin_spot_Usdt_Send_to_up , bin_fu_Usdt_asset

def Bin_Minimum_Spot_Order_Size(sym_name):
    Bin_Spot_Minimum_Order_Size = []
    Bin_Spot_Minimum_Order_Size_append = Bin_Spot_Minimum_Order_Size.append
    aa = client.get_exchange_info()

    for i in range(len(sym_name)):
        bb = next((item for item in aa['symbols'] if item['symbol'] == sym_name[i] + 'USDT'), None)
        Bin_Spot_Minimum_Order_Size_append(float(next((item for item in bb['filters'] if item['filterType'] == 'LOT_SIZE'), None)['minQty']))
    #     print(Bin_Spot_Minimum_Order_Size)
    return Bin_Spot_Minimum_Order_Size


# def Bin_Minimum_FU_Order_Size(sym_name):
#     Bin_Fu_Minimum_Order_Size = []
#     Bin_Fu_Minimum_Order_Size_append = Bin_Fu_Minimum_Order_Size.append
#     aa = client.futures_exchange_info()

#     for i in range(len(sym_name)):
#         bb = next((item for item in aa['symbols'] if item['symbol'] == sym_name[i] + 'USDT'), None)
#         Bin_Fu_Minimum_Order_Size_append(float(next((item for item in bb['filters'] if item['filterType'] == 'PERCENT_PRICE'), None)['multiplierDecimal']))
#     #     print(Bin_Fu_Minimum_Order_Size)
#     return Bin_Fu_Minimum_Order_Size

def Bin_Minimum_FU_Order_Size(sym_name):
    Bin_Fu_Minimum_Order_Size = []
    Bin_Fu_Minimum_Order_Size_append = Bin_Fu_Minimum_Order_Size.append
    aa = client.futures_exchange_info()

    for i in range(len(sym_name)):
        bb = next((item for item in aa['symbols'] if item['symbol'] == sym_name[i] + 'USDT'), None)
        Bin_Fu_Minimum_Order_Size_append(float(next((item for item in bb['filters'] if item['filterType'] == 'MARKET_LOT_SIZE'), None)['minQty']))
    #     print(Bin_Fu_Minimum_Order_Size)
    return Bin_Fu_Minimum_Order_Size


def Bin_Minimum_Withdraw_Size(symbol, all_coin_info):  # 바이낸스 최소전송가능량
    aa = next((item for item in all_coin_info if item['coin'] == symbol), None)['networkList']
    minWithdrawAmount = float(next((item for item in aa if item['network'] == symbol), None)['withdrawIntegerMultiple'])
    return minWithdrawAmount


def del_bin_disable_deopsit(all_coin_info, sym_name):  # 바이낸스 입금 불가능 코인 삭제
    delet_list = []
    delet_list_append = delet_list.append
    for i in range(len(sym_name)):
        depositEnable, withdrawEnable = bin_coin_withdrow_deopsit_Enable(all_coin_info, sym_name[i])
        #         print(sym_name[i],depositEnable,withdrawEnable)
        if (depositEnable == False):
            delet_list_append(sym_name[i])
    name = list(set(sym_name) - set(delet_list))
    return name


def del_bin_disable_withdraw(all_coin_info, sym_name):  # 바이낸스 출금 불가능 심볼 삭제
    delet_list = []
    delet_list_append = delet_list.append
    for i in range(len(sym_name)):
        depositEnable, withdrawEnable = bin_coin_withdrow_deopsit_Enable(all_coin_info, sym_name[i])
        #         print(sym_name[i],depositEnable,withdrawEnable)
        if (withdrawEnable == False):
            delet_list_append(sym_name[i])
    name = list(set(sym_name) - set(delet_list))
    return name


def del_up_disable_deopsit(sym_name):  # 업비트 입금 불가능 코인 삭제
    server_url = 'https://api.upbit.com'
    delet_list = []
    for i in range(len(sym_name)):

        query = {'currency': sym_name[i], }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {'access_key': access_key, 'nonce': str(uuid.uuid4()), 'query_hash': query_hash, 'query_hash_alg': 'SHA512', }

        jwt_token = jwt.encode(payload, secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(server_url + "/v1/withdraws/chance", params=query, headers=headers)
        up_sym_whthdraw_state = res.json()['currency']['wallet_support']

        if 'deposit' in up_sym_whthdraw_state:
            pass
        else:
            delet_list.append(sym_name[i])
            print(sym_name[i], "해당코인 업비트에서 바이낸스로 입금 불가상태")

        time.sleep(0.4)
    name = list(set(sym_name) - set(delet_list))
    return name


def del_up_disable_whthdraw(sym_name):  # 업비트 출금 불가능 코인 삭제
    server_url = 'https://api.upbit.com'
    delet_list = []
    for i in range(len(sym_name)):

        query = {'currency': sym_name[i], }
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {'access_key': access_key, 'nonce': str(uuid.uuid4()), 'query_hash': query_hash, 'query_hash_alg': 'SHA512', }

        jwt_token = jwt.encode(payload, secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.get(server_url + "/v1/withdraws/chance", params=query, headers=headers)
        up_sym_whthdraw_state = res.json()['currency']['wallet_support']

        if 'withdraw' in up_sym_whthdraw_state:
            pass
        else:
            delet_list.append(sym_name[i])
            print(sym_name[i], "해당코인 업비트에서 바이낸스로 출금 불가상태")

        time.sleep(0.4)
    name = list(set(sym_name) - set(delet_list))
    return name


#####업비트 => 바이낸스 전송가능정보와 코인 수수료 가져오는코드#########################
def Up_Minimum_Withdraw_Size(sym_name):  # 업비트 최소전송가능량
    server_url = 'https://api.upbit.com'
    query = {'currency': sym_name, }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {'access_key': access_key, 'nonce': str(uuid.uuid4()), 'query_hash': query_hash,
               'query_hash_alg': 'SHA512', }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/withdraws/chance", params=query, headers=headers)

    return float(res.json()['withdraw_limit']['fixed'])  # 이부분 틀려있었음


#     return (0.1)**float(res.json()['withdraw_limit']['fixed'])
#         print(bin_sym_send_state,sym_name[i],"출금지원가능여부")


def up_bin_withdraw_Size(sym_name, all_coin_info):  # 바이낸스 최소전송가능량
    up_Min_Withdraw_Size = []
    bin_Min_Withdraw_Size = []
    up_Min_Withdraw_Size_append = up_Min_Withdraw_Size.append
    bin_Min_Withdraw_Size_append = bin_Min_Withdraw_Size.append
    for i in range(len(sym_name)):  # 잘되나 확인 중 나중에 지우기
        up_Min_Withdraw_Size_append(Up_Minimum_Withdraw_Size(sym_name[i]))
        bin_Min_Withdraw_Size_append(Bin_Minimum_Withdraw_Size(sym_name[i], all_coin_info))
        time.sleep(0.4)
    return up_Min_Withdraw_Size, bin_Min_Withdraw_Size


def remove_sym_name_1(all_coin_info, sym_name, Usdt, up_asset, per, ban_list, up_market_fee):  # 심볼명 리스트, 달러 환율, 자본대비 최소 퍼센테이지

    up_withdrawfee, bin_withdrawfee = up_bin_withdraw_fee(sym_name, all_coin_info)  # 업비트 전송 수수료 , 바이낸스 전송 수수료
    up_Min_Withdraw_Size, bin_Min_Withdraw_Size = up_bin_withdraw_Size(sym_name, all_coin_info)  # 업비트, 바이낸스 전송최소 가능량
    # Bin_Fu_Minimum_Order_Size = Bin_Minimum_FU_Order_Size(sym_name)  # 바이낸스 선물 최소 주문 가능량
    # Bin_Spot_Minimum_Order_Size = Bin_Minimum_Spot_Order_Size(sym_name)  # 바이낸스 현물 최소 주문가능량
    # 자본대비 수수료 , 잡다한 코인들 제외

    up_sym_names, up_spot_ask_bid = up_spot_ask_bid_info(sym_name)
    up_ask_price, up_ask_size = up_ask_info(up_sym_names, up_spot_ask_bid)  # 업비트 매수 호가창 4
    # up_bid_price, up_bid_size = up_bid_info(up_sym_names, up_spot_ask_bid)  # 업비트 매도 호가창 1

    #     bin_sym_names, bin_spot_ask_bid = bin_spot_ask_bid_info(sym_name)
    #     bin_spot_ask_price, bin_spot_ask_size = bin_ask_info(bin_sym_names, bin_spot_ask_bid)  # 바-현 매수 호가창 2
    #     bin_spot_bid_price, bin_spot_bid_size = bin_bid_info(bin_sym_names, bin_spot_ask_bid)  # 바-현 매도 호가창 3

    # up_to_bin_pre_rate = []
    # bin_to_up_pre_rate = []
    # up_withdrawfee_by_asset = []
    # bin_withdrawfee_by_asset = []

    for i in range(len(sym_name)):

        up_can_order_amout = up_asset * (1 - up_market_fee)  # *0.005이미함
        up_can_order_amout = up_can_order_amout + (up_withdrawfee[i] * up_ask_price[i])  ##완벽한 헷징을 위해 업비트 전송료만큼 추가..#@@이부분..계산
        Decimal_rounding = UP_Minimum_Order_cash_Size(up_ask_price[i])
        up_can_order_amout = (up_can_order_amout // Decimal_rounding) * Decimal_rounding

        can_send_Decimal = up_Min_Withdraw_Size[i]  # 전송가능 최소량@@이게 잇어야 계산 가능
        if (can_send_Decimal == 0):  # 전송 수수료가 0 인경우 나눌 수가 없음
            pass
        else:
            Decimal_rounding, Decimal_rounding_dig = (0.1) ** int(can_send_Decimal + 1), int(can_send_Decimal)  # 소수점 라운딩
            up_can_order_amout = (up_can_order_amout // Decimal_rounding) * Decimal_rounding
            up_can_order_amout = round(up_can_order_amout, Decimal_rounding_dig)

        if (((up_ask_price[i] * up_withdrawfee[i]) / up_can_order_amout) < per):  # 구매가능 정보로 해서 더 깔끔(소수점 절단)
            pass
        else:
            print((up_ask_price[i] * up_withdrawfee[i]) / up_can_order_amout, sym_name[i], "자본대비 수수료가 큰 코인")
            print(up_ask_price[i] * up_withdrawfee[i])
            sym_name[i] = 'remove'

        ###@@@ BNB코인 배제 이 부분 로직으로 대체 가능
        if ((sym_name[i] in ban_list) == True):
            sym_name[i] = 'remove'

    removeAllOccur(sym_name, 'remove')
    print(sym_name, len(sym_name))
    return sym_name


def remove_sym_name_2(all_coin_info, sym_name, Usdt, binance_asset, per, ban_list, bin_spot_market_fee):  # 심볼명 리스트, 달러 환율, 자본대비 최소 퍼센테이지

    up_withdrawfee, bin_withdrawfee = up_bin_withdraw_fee(sym_name, all_coin_info)  # 업비트 전송 수수료 , 바이낸스 전송 수수료
    up_Min_Withdraw_Size, bin_Min_Withdraw_Size = up_bin_withdraw_Size(sym_name, all_coin_info)  # 업비트, 바이낸스 전송최소 가능량
    # Bin_Fu_Minimum_Order_Size = Bin_Minimum_FU_Order_Size(sym_name)  # 바이낸스 선물 최소 주문 가능량
    Bin_Spot_Minimum_Order_Size = Bin_Minimum_Spot_Order_Size(sym_name)  # 바이낸스 현물 최소 주문가능량
    # 자본대비 수수료 , 잡다한 코인들 제외

    # up_sym_names, up_spot_ask_bid = up_spot_ask_bid_info(sym_name)
    # up_ask_price, up_ask_size = up_ask_info(up_sym_names, up_spot_ask_bid)  # 업비트 매수 호가창 4
    # up_bid_price, up_bid_size = up_bid_info(up_sym_names, up_spot_ask_bid)  # 업비트 매도 호가창 1

    bin_sym_names, bin_spot_ask_bid = bin_spot_ask_bid_info(sym_name)
    bin_spot_ask_price, bin_spot_ask_size = bin_ask_info(bin_sym_names, bin_spot_ask_bid)  # 바-현 매수 호가창 2
    # bin_spot_bid_price, bin_spot_bid_size = bin_bid_info(bin_sym_names, bin_spot_ask_bid)  # 바-현 매도 호가창 3

    for i in range(len(sym_name)):

        bin_spot_Usdt_Send = binance_asset - binance_asset * bin_spot_market_fee  # 바이낸스 현물 시장가 수수료
        send_to_up_quantity = (bin_spot_Usdt_Send / bin_spot_ask_price[i])  # 바이낸스 업비트로 보낼 달러 / 티커 가격 = 수량
        send_to_up_quantity = send_to_up_quantity + bin_withdrawfee[i]
        # 전송가능 최소량과 주문가능 최소량으로 잘 자름.
        Decimal_rounding = bin_Min_Withdraw_Size[i]
        if (Decimal_rounding == 0):  # 전송 수수료가 0 인경우 나눌 수가 없음
            pass
        else:
            send_to_up_quantity = (send_to_up_quantity // Decimal_rounding) * Decimal_rounding

        Decimal_rounding = Bin_Spot_Minimum_Order_Size[i]
        bin_spot_to_up_can_order_amount = (send_to_up_quantity // Decimal_rounding) * Decimal_rounding
        bin_spot_to_up_can_order_amount = round(bin_spot_to_up_can_order_amount, 6)
        print(sym_name[i], bin_spot_to_up_can_order_amount, (bin_spot_ask_price[i] * bin_withdrawfee[i]) / (binance_asset), bin_spot_ask_price[i])

        if (((bin_spot_ask_price[i] * bin_withdrawfee[i]) / (binance_asset)) < per):  # 구매가능 정보로 해서 더 깔끔(소수점 절단)
            #             print((up_bid_price[i] * up_withdrawfee[i]) / up_can_order_amout, sym_name[i])
            pass

        else:
            print((bin_spot_ask_price[i] * bin_withdrawfee[i]) / (binance_asset), "자본대비 수수료가 큰 코인")
            print(bin_spot_ask_price[i] * bin_withdrawfee[i])
            sym_name[i] = 'remove'

        ###@@@ BNB코인 배제 이 부분 로직으로 대체 가능
        if ((sym_name[i] in ban_list) == True):
            sym_name[i] = 'remove'

    removeAllOccur(sym_name, 'remove')
    print(sym_name, len(sym_name))
    return sym_name


# 업비트 매수 평단가
def up_avg_buy_price(sym_name):
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()), }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/accounts", headers=headers)
    aa = float(next((item for item in res.json() if item['currency'] == sym_name), None)['avg_buy_price'])
    bb = float(next((item for item in res.json() if item['currency'] == sym_name), None)["balance"])
    return aa, bb


# def bin_fu_avg_buy_price(sym_name):
#     aa = float(next((item for item in client.futures_account()['positions'] if item['symbol'] == sym_name + 'USDT'), None)['entryPrice'])
#     bb = -(float(next((item for item in client.futures_account()['positions'] if item['symbol'] == sym_name + 'USDT'), None)["positionAmt"]))
#     return aa, bb
# @@ 밑에게 더 낫 지 않나 왜 안대
def bin_fu_avg_buy_price(sym_name, bin_fu_position_info):
    aa = float(next((item for item in bin_fu_position_info['positions'] if item['symbol'] == sym_name + 'USDT'), None)['entryPrice'])
    bb = -(float(next((item for item in bin_fu_position_info['positions'] if item['symbol'] == sym_name + 'USDT'), None)["positionAmt"]))
    return aa, bb


def up_withdrow_request(send_to_bin_optimal_simbol, point_of_Withdrow_UP_amount_1, bin_address, bin_Memo):
    # @ 2.코인 출금 요청#########################
    # point_of_Withdrow_UP_amount_1 조심 가져오든지 해야함
    query = {
        'currency': send_to_bin_optimal_simbol,
        'amount': point_of_Withdrow_UP_amount_1,
        'address': bin_address,
        'secondary_address': bin_Memo,
        'transaction_type': 'default'  # default가 일반출금
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512', }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/withdraws/coin", params=query, headers=headers)

    #     print(res.json())
    #     send_amount = res.json()['amount']
    #     send_amount = float(send_amount)
    #     print(send_amount)
    return res.json()


# 업비트 입금주소 요청
def up_deposit_address_request(send_to_up_optimal_simbol):
    query = {'currency': send_to_up_optimal_simbol, }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {'access_key': access_key,
               'nonce': str(uuid.uuid4()),
               'query_hash': query_hash,
               'query_hash_alg': 'SHA512', }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/deposits/generate_coin_address", params=query,
                        headers=headers)
    up_add = res.json()['deposit_address']
    up_seadd = res.json()['secondary_address']
    return up_add, up_seadd


def Up_Minimum_Withdraw_Size_digit(sym_name):  # 자릿수
    server_url = 'https://api.upbit.com'
    query = {'currency': sym_name, }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {'access_key': access_key, 'nonce': str(uuid.uuid4()), 'query_hash': query_hash,
               'query_hash_alg': 'SHA512', }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/withdraws/chance", params=query, headers=headers)

    return float(res.json()['withdraw_limit']['fixed'])  # 이부분 틀려있었음


# api 키는 바이낸스와 unbit apikey에 저장해둔다
# api 키 값 로드
with open('apikeys.pickle', 'rb') as fr:
    apikeys = pickle.load(fr)

# 암호키 가져옴.
request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)  # 선물 거래
# request_client_D = RequestClient_D(api_key=g_api_key, secret_key=g_secret_key) # coin_m 선물거래
server_url = 'https://api.upbit.com'
Usdt = upbit_get_usd_krw()
# Usdt = 1170
print("Usdt =", Usdt)

# 업비트 잔고 조회 및 해당 코인 가격에 맞는 가격 도출 기능
access_key = apikeys['up_access_key']
secret_key = apikeys['up_secret_key']
upbit = pyupbit.Upbit(access_key, secret_key)

# 바이낸스 잔고조회
binance = ccxt.binance({
    'apiKey': g_api_key,
    'secret': g_secret_key})

binance_fu = ccxt.binance({
    'apiKey': g_api_key,
    'secret': g_secret_key,
    'options': {'defaultType': 'future'}})

client_spot = Spot(key=g_api_key
                   , secret=g_secret_key)

client = Client(api_key=g_api_key,
                api_secret=g_secret_key)


def cheak_about_regester_by_upbit():
    with open('regester_by_upbit.pickle', 'rb') as fr:
        regester_by_upbit = pickle.load(fr)
        past_sym_name = regester_by_upbit["past_sym_name"]

    sym_name = sym_intersection()

    New_sym_bols = list(set(sym_name) - set(regester_by_upbit['past_sym_name']))

    if (len(set(sym_name) - set(regester_by_upbit['past_sym_name'])) != 0):
        print("==================================warning==================================")
        print("새로운 심볼들 !!!!(업비트 출금주소 등록할것!)", list(set(sym_name) - set(regester_by_upbit['past_sym_name'])))
        print("==================================warning==================================")

        print("새로운 출금 주소를 등록하시고 진행하시겠습니까 ? (Y/N)")
        print("Y입력 시 업비트에 출금 주소 입력하고 진행")
        print("N입력 시 새로 추가된 심볼은 사용하지 않고 진행함.")
        input_command = input()

        if (input_command == "Y"):
            import warnings
            warnings.warn("새로운 심볼들 !!!!(업비트 출금주소 등록할것!)", DeprecationWarning)
            sys.exit()  ## 강제로 파이썬 종료

        elif (input_command == "N"):
            User_data['ban_list'] = User_data['ban_list'] + New_sym_bols
        #             return User_data

        else:
            print("input 입력 오류")
            sys.exit()  ## 강제로 파이썬 종료


def cheak_about_regester_by_bin():
    with open('regester_by_binance.pickle', 'rb') as fr:
        regester_by_binance = pickle.load(fr)
        past_sym_name = regester_by_binance["past_sym_name"]

    sym_name = sym_intersection()

    New_sym_bols = list(set(sym_name) - set(regester_by_binance['past_sym_name']))

    if (len(set(sym_name) - set(regester_by_binance['past_sym_name'])) != 0):
        print("==================================warning==================================")
        print("새로운 심볼들 !!!!(업비트 출금주소 등록할것!)", list(set(sym_name) - set(regester_by_binance['past_sym_name'])))
        print("==================================warning==================================")

        print("새로운 출금 주소를 등록하시고 진행하시겠습니까 ? (Y/N)")
        print("Y입력 시 업비트에 출금 주소 입력하고 진행")
        print("N입력 시 새로 추가된 심볼은 사용하지 않고 진행함.")
        input_command = input()

        if (input_command == "Y"):
            import warnings
            warnings.warn("새로운 심볼들 !!!!(업비트 출금주소 등록할것!)", DeprecationWarning)
            sys.exit()  ## 강제로 파이썬 종료

        elif (input_command == "N"):
            User_data['ban_list'] = User_data['ban_list'] + New_sym_bols
        #             return User_data

        else:
            print("input 입력 오류")
            sys.exit()  ## 강제로 파이썬 종료


def Save_ALL_DATA():
    ## 펑션을 종료시키고 싶을 경우 해당 로직 실행
    # save data 파이썬 딕셔너리 자료형 데이터 저장.
    with open('Free_Risk_Arbitrage_asset_division.pickle', 'wb') as fw:
        pickle.dump(asset_division, fw)

    with open('Free_Risk_Arbitrage_User_data.pickle', 'wb') as fw:
        pickle.dump(User_data, fw)

    for i in range(len(asset_division)):
        print(i, asset_division[i]['up_asset'], asset_division[i]['State'])
    print("====================asset_division============================")
    print(asset_division)
    print("=======================User_data==============================")
    print(User_data)


def set_premium_asset_division():  # 입력은 %로
    print("%단위로 입력할것 (김프가 그대로)")

    print("역프~약김프 최대 수치(프로그램 실행 시), 추천 => 1")
    a_1_1 = float(input())  # a_1_1 = 2.5
    print("최소 차익 볼 김프, 추천 => 1.5 ")
    a_2_1 = float(input())  # a_2_2 = 1
    print("조정하고 싶은 레버리지 비율 기본 10배")
    adjust_leverage = float(input())

    print("역프~약김프 최대 수치(프로그램 실행 시 )", a_1_1, "%")
    print("최소 차익 볼 김프", ((1 + a_2_1 / 100) / (1 - a_1_1 / 100) - 1) * 100, "%")

    a_1_1 = a_1_1 / 100
    a_2_1 = a_2_1 / 100
    for i in range(len(asset_division)):
        asset_division[i]['want_premium_step_1_1'] = a_1_1
        asset_division[i]['want_premium_step_2_1'] = a_2_1
        asset_division[i]['adjust_leverage'] = adjust_leverage

    return asset_division


def check_logic(asset_division):
    # 검산용
    sum_1 = 0
    sum_2 = 0
    for i in range(len(asset_division)):
        sum_1 = sum_1 + asset_division[i]["up_asset"]
        sum_2 = sum_2 + asset_division[i]["binance_asset"] * asset_division[i]['Usdt_first'] * asset_division[i]["future_leverage"]
    print("업비트 = ", sum_1, "바이낸스 = ", sum_2)
    if (sum_1 - 1 < sum_2 < sum_1 + 1):  # 파이썬이 아주 작은 수를 남겨서
        print("사용중인 자본 맞음")
    else:
        import warnings
        warnings.warn("업비트와 바이낸스자본이 맞지 않은 확인 바람.", DeprecationWarning)
        sys.exit()  ## 강제로 파이썬 종료

    State_All = [asset_division[w]["State"] for w in range(len(asset_division))]
    for i in range(len(asset_division)):
        if (asset_division[i]["future_leverage"] >= 20) & ((len(set(State_All) & {'None', 'send_bin_to_up'}) == 0)):
            import warnings
            warnings.warn("처음 자본 전송일시 다른파일 사용(레버리지 20 배 이상에 포지션이 없음.)", DeprecationWarning)
            sys.exit()  ## 강제로 파이썬 종료


def up_avg_buy_price_info():  # @@ 나중에 이 부분 다 바꾸기 => upbit.get_balances() 로 변환 하면 됨
    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()), }

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/accounts", headers=headers)
    return res.json()


def first_asset_division(div_unit):
    try:  # load data 파이썬 딕셔너리 자료형 데이터 로드
        with open('Free_Risk_Arbitrage_asset_division.pickle', 'rb') as fr:
            asset_division = pickle.load(fr)

        with open('Free_Risk_Arbitrage_User_data.pickle', 'rb') as fr:
            User_data = pickle.load(fr)
            qwer = User_data["qwer"]

            sum_1 = 0
            sum_2 = 0
            for i in range(len(asset_division)):
                sum_1 = sum_1 + asset_division[i]["up_asset"]
                sum_2 = sum_2 + asset_division[i]["binance_asset"] * asset_division[i]["Usdt_first"] * asset_division[i]["future_leverage"]

        # 아직 운용 중인 자본이 있다면 로직을 사용하지 않고 그대로 배출..
        All_States = [asset_division[i]["State"] for i in range(len(asset_division))]  # 모든 States를 가져옮
        if (len(set(All_States) & {'step_1_1', 'send_up_to_bin', 'send_up_to_bin_Completion', 'step_1_2', 'Capital_distribution', 'step_2_1', 'send_bin_to_up', 'send_bin_to_up_Completion', 'step_2_2', 'final_fun'}) != 0):  # 교집합이 0일 경우(모든상태가 저기에 포함되지 않을경우)
            print("한 싸이클이 아직 끝나지 않음.")
            return asset_division, User_data
        else:
            # 옵션 1 오류를 내서 종료 => 이 경우 새로운 엑셀 파일 생성 및 새로운 자본배분
            # 옵션 1 선택. 100 만원 이상 자본 운용 안되게 하기 위함.
            sys.exit()
            # 옵션 2 오류가 아닌 이전 데이터 사용 => 이 경우 그냥 옛날에 나뉜대로 사용 새로운 자본배분 x
    #             return asset_division, User_data

    except:

        sum_1 = 0
        sum_2 = 0
        asset_division = {}
        now = datetime.datetime.now()
        qwer = str(now.year) + "_" + str(now.month) + "_" + str(now.day)
        columns_name = ['sicle',
                        'k',
                        'up_asset',
                        'binance_asset',
                        'Using_asset',
                        'step_1_1_up_krw_asset',
                        'step_1_1_bin_fu_usdt_asset',
                        'rest_step_1_1_up_krw_asset',
                        'rest_step_1_1_bin_fu_usdt_asset',
                        'x1',
                        'y1',
                        'Usdt_1',
                        'sym_name_a',
                        'future_leverage',
                        'point_of_buy_UP_ticker_1',
                        'point_of_buy_UP_amount_1',
                        'point_of_buy_bin_fu_ticker_1',
                        'point_of_buy_bin_fu_amount_1',
                        'second_using_asset',
                        'step_1_2_bin_spot_usdt_asset',
                        'step_1_2_bin_fu_usdt_asset',
                        'x2',
                        'y2',
                        'Usdt_2',
                        '업=>바 손해액 ((x2 + y2)*Usdt_2) - ((x1+y1)*Usdt_1)',
                        'sym_name_b',
                        'step_2_1_bin_spot_usdt_asset',
                        'step_2_1_bin_fu_usdt_asset',
                        'rest_step_2_1_bin_spot_usdt_asset',
                        'rest_step_2_1_bin_fu_usdt_asset',
                        'x3',
                        'y3',
                        'Usdt_3',
                        'point_of_buy_bin_spot_ticker_2',
                        'point_of_buy_bin_spot_amount_2',
                        'point_of_buy_bin_fu_ticker_2',
                        'point_of_buy_bin_fu_amount_2',
                        'step_2_2_up_krw_asset',
                        'step_2_2_bin_fu_usdt_asset',
                        'x4',
                        'y4',
                        'Usdt_4',
                        'total_before',
                        'total_after',
                        'date',
                        'want_premium_step_1_1',
                        'want_premium_step_2_1'
                        ]
        # csv파일로 적기 # newline 설정을 안하면 한줄마다 공백있는 줄이 생긴다.
        with open(qwer + 'Free_Risk_Trading_data.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns_name)

    # Using_up_asset의 경우를 제한다.
    Sum_Using_Up_asset = 0
    Sum_Using_Bin_asset = 0
    for i in range(len(asset_division)):  # @@ 이렇게 하는 경우 한번 나뉘면 환율이 바뀌어도 소용없이 계속 나뉜상태,..=>포지션 진입 아닌 경우는 지우는/..?
        if (asset_division[i]['State'] == 'None_position'):
            Sum_Using_Up_asset = Sum_Using_Up_asset + asset_division[i]["up_asset"]
            Sum_Using_Bin_asset = Sum_Using_Bin_asset + asset_division[i]["binance_asset"]

    num = len(asset_division)

    sicle = 0
    save_state = {}  # 사전형태
    save_state[sicle] = []

    first_up_asset = upbit.get_balance("KRW")
    up_asset = first_up_asset - first_up_asset * 0.0005  # 계좌 현금 확인
    up_asset = up_asset - up_asset * 0.0005  # 수수료 보정치(슬리피지)

    first_bin_fu_ass = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])
    #     first_bin_fu_ass = 133 #@@ 삭제 할것
    #     first_bin_fu_ass = up_asset/Usdt / 5 #@@ 삭제 할것
    bin_fu_ass = first_bin_fu_ass - first_bin_fu_ass * 0.0004
    binance_asset = bin_fu_ass * Usdt

    # @ 수수료들 가져오기 ex)client.get_trade_fee() # https://www.binance.com/en/fee/trading <= 수수료 주소
    up_market_fee = float(upbit.get_chance("KRW-ETC")["maker_bid_fee"])  # 업비트 코인 현물 시장가 #taker,maker 동일해서 그런지 이것만 존재. @ # 다른 (코인)정보로 받아도 됨
    bin_fees = binance_fu.fees
    bin_spot_market_fee = bin_fees["trading"]['taker']  # 바이낸스 현물 시장가 수수료 #taker는 시장가   # maker 0.1% taker 0.1% # 0.001
    bin_future_market_fee = bin_fees["future"]["trading"]["taker"]  # 바이낸스 선물 시장가 수수료 #taker는 시장가
    bin_Coin_M_future_market_fee = bin_fees["delivery"]["trading"]["taker"]  # 바이낸스 선물 coin-m 시장가 수수료 #taker는 시장가

    asset_for_div_UP = up_asset - Sum_Using_Up_asset
    asset_for_div_bin = (bin_fu_ass - Sum_Using_Bin_asset)
    asset_for_div_bin = asset_for_div_bin * Usdt

    if (asset_for_div_UP > asset_for_div_bin):  # 업비트 자본이 큰 경우
        future_leverage_first = math.ceil(asset_for_div_UP / asset_for_div_bin)
    else:  # 바이낸스 자본이 더 큰경우 # 바이낸스 자본비율이
        future_leverage_first = 1  # 그냥 1해도 됨

    if (asset_for_div_UP > asset_for_div_bin):  # 업비트 자본이 큰 경우
        Decimal_rounding = 0.0000000000001
        future_leverage_by_order_set = ((asset_for_div_UP / asset_for_div_bin) // Decimal_rounding) * Decimal_rounding
    #     future_leverage_by_order_set = (asset_for_div_UP / asset_for_div_bin)

    else:  # 바이낸스 자본이 더 큰경우 # 바이낸스 자본비율이
        future_leverage_by_order_set = 1  # 그냥 1해도 됨

    # asset_for_div_bin = asset_for_div_bin * future_leverage_by_order_set

    #     if (15 < future_leverage_by_order_set) or (first_up_asset < 50000) or (first_bin_fu_ass < 130):
    #         import warnings
    #         print(future_leverage_by_order_set, first_bin_fu_ass)
    #         warnings.warn("바이낸스 자본 or 배율이 이상함", DeprecationWarning)
    #         sys.exit()  ## 강제로 파이썬 종료

    if (future_leverage_first >= 2):
        #     if (future_leverage_first >= 2 and (future_leverage_first < 10)): # @@ option
        while True:
            if ((asset_for_div_UP >= div_unit) and (asset_for_div_bin * future_leverage_by_order_set >= div_unit)):

                asset_division[num] = {'State': "None_position"}
                asset_division[num]['up_asset'] = div_unit
                asset_division[num]['binance_asset'] = (div_unit / future_leverage_by_order_set) / Usdt

                asset_for_div_UP = asset_for_div_UP - div_unit
                asset_for_div_bin = asset_for_div_bin - div_unit / future_leverage_by_order_set
                future_leverage = future_leverage_by_order_set

                asset_division[num]['future_leverage'] = future_leverage
                asset_division[num]['Usdt_first'] = Usdt  # 자본 나눌 때 달러가치
                asset_division[num]['save_state'] = save_state
                asset_division[num]["qwer"] = qwer
                asset_division[num]["div_unit"] = div_unit
                asset_division[num]['want_premium_step_1_1'] = 0.01
                asset_division[num]['want_premium_step_2_1'] = 0.0125
                asset_division[num]['adjust_leverage'] = 10

                num = num + 1

            elif ((asset_for_div_UP <= div_unit / 10) or (asset_for_div_bin <= div_unit / 10) or (asset_for_div_bin < 50000) or (asset_for_div_UP < 50000)):  # --이하는 투자하지않음(최소주문가능량 고려)
                print("option1", "업비트 남은자본:", asset_for_div_UP, "바이낸스 남은자본:", asset_for_div_bin, "자본배율이 10(숫자만 바꾸면 됨) 배 이상 차이남")
                #             asset_division[num] = {'up_asset' : asset_for_div_UP,"binance_asset" : asset_for_div_bin,"future_leverage":1}
                break
            else:
                asset_division[num] = {'State': "None_position"}

                if (asset_for_div_UP > asset_for_div_bin):  # 업비트 자본이 큰 경우
                    Decimal_rounding = 0.0000000000001
                    future_leverage_by_order_set = ((asset_for_div_UP / asset_for_div_bin) // Decimal_rounding) * Decimal_rounding

                asset_division[num]['up_asset'] = asset_for_div_UP
                asset_division[num]['binance_asset'] = asset_for_div_bin / Usdt

                asset_for_div_UP = asset_for_div_UP - asset_for_div_UP
                asset_for_div_bin = asset_for_div_bin - asset_for_div_bin
                future_leverage = future_leverage_by_order_set

                asset_division[num]['future_leverage'] = future_leverage
                asset_division[num]['Usdt_first'] = Usdt  # 자본 나눌 때 달러가치
                asset_division[num]['save_state'] = save_state
                asset_division[num]["qwer"] = qwer
                asset_division[num]["div_unit"] = div_unit
                asset_division[num]['want_premium_step_1_1'] = 0.01
                asset_division[num]['want_premium_step_2_1'] = 0.0125
                asset_division[num]['adjust_leverage'] = 10

    else:  # 2배 차이 안날시
        while True:
            if ((asset_for_div_UP >= div_unit) and (asset_for_div_bin >= div_unit)):
                asset_division[num] = {'State': "None_position"}
                asset_division[num]['up_asset'] = div_unit
                asset_division[num]['binance_asset'] = (div_unit / future_leverage_first) / Usdt

                asset_for_div_UP = asset_for_div_UP - div_unit
                asset_for_div_bin = asset_for_div_bin - div_unit

                future_leverage = 1

                asset_division[num]['future_leverage'] = future_leverage
                asset_division[num]['Usdt_first'] = Usdt  # 자본 나눌 때 달러가치
                asset_division[num]['save_state'] = save_state
                asset_division[num]["qwer"] = qwer
                asset_division[num]["div_unit"] = div_unit
                asset_division[num]['want_premium_step_1_1'] = 0.01
                asset_division[num]['want_premium_step_2_1'] = 0.0125
                asset_division[num]['adjust_leverage'] = 10

                num = num + 1

            # @@ 레버리지가 너무 크면 안좋을 거 같음 => 나누는 단위에 따라서 최소값 제한함
            elif ((asset_for_div_UP <= div_unit / 5) or (asset_for_div_bin <= div_unit / 5)):  # --이하는 투자하지않음(최소주문가능량 고려)
                print("option2", "업비트 남은자본:", asset_for_div_UP, "바이낸스 남은자본:", asset_for_div_bin)
                break

            else:
                asset_division[num] = {'State': "None_position"}

                if (asset_for_div_UP > asset_for_div_bin):  # 업비트 자본이 큰 경우
                    future_leverage = math.floor(asset_for_div_UP / asset_for_div_bin)
                else:  # 바이낸스 자본이 더 큰경우 # 바이낸스 자본비율이
                    future_leverage = 1  # 그냥 1해도 됨

                if (future_leverage != 1):  # @ 바이낸스 자본과 업비트 자본의 비율이 2배 이상이 될 경우.

                    if (asset_for_div_UP < asset_for_div_bin):  # 바이낸스 자본이 더 큰 경우 @@주로 김프니까(역프는..)이 경우는 그냥 업비트 자본 따라가는게 맞겠지..?
                        asset_Up = asset_for_div_UP  # 변수명이 바뀌어서
                        asset_bin = asset_for_div_UP

                    elif (asset_for_div_bin <= asset_for_div_UP):  # 김프의 경우 2배차이가 나기 시작하면
                        asset_bin = asset_for_div_bin
                        asset_Up = asset_for_div_bin * future_leverage  # @이렇게 하면 업비트 자본이 남고 바이낸스는 전부 쓴다.

                elif (asset_for_div_UP < asset_for_div_bin):  # 작은 자본의 가격을 따라간다.
                    asset_bin = asset_for_div_UP
                    asset_Up = asset_bin
                elif (asset_for_div_bin <= asset_for_div_UP):
                    asset_Up = asset_for_div_bin
                    asset_bin = asset_Up

                asset_division[num]['up_asset'] = asset_Up
                asset_division[num]['binance_asset'] = asset_bin / Usdt

                asset_for_div_UP = asset_for_div_UP - asset_Up
                asset_for_div_bin = asset_for_div_bin - asset_bin

                asset_division[num]['future_leverage'] = future_leverage
                asset_division[num]['Usdt_first'] = Usdt
                asset_division[num]['save_state'] = save_state
                asset_division[num]["qwer"] = qwer
                asset_division[num]["div_unit"] = div_unit
                asset_division[num]['want_premium_step_1_1'] = 0.01
                asset_division[num]['want_premium_step_2_1'] = 0.0125
                asset_division[num]['adjust_leverage'] = 10

    #################################################################################
    # if (future_leverage_first >= 2): # @@ 이 부분 다시 돌리면 이상해짐..
    #
    #     for i in range(len(asset_division)):
    #         sum_1 = sum_1 + asset_division[i]["up_asset"]
    #         sum_2 = sum_2 + asset_division[i]["binance_asset"]
    #     print("업비트 = ", sum_1, "바이낸스 = ", sum_2 * Usdt)
    #
    #     if ((up_asset - sum_1) - 1 < asset_for_div_UP < (up_asset - sum_1) + 1) and ((asset_for_div_bin / Usdt - 1) < bin_fu_ass - sum_2 < (asset_for_div_bin / Usdt + 1)):
    #         print("사용중인 자본 맞음")
    #     else:
    #         import warnings
    #         warnings.warn("업비트와 바이낸스자본이 맞지 않은 확인 바람.", DeprecationWarning)
    #         sys.exit()  ## 강제로 파이썬 종료
    #################################################################################

    check_logic(asset_division)  # 로직 체크

    # @@ 1시간 이상 걸리는것들 찾아서 추가해 제거하기
    # 분단위 전송 심볼들
    ban_list = ["WAVES", 'OMG', 'XMR', 'MANA', 'BCHA', 'BCH', 'AE', 'SAND', 'USDT', 'BSV', 'BTG', 'SRM', 'CHZ', 'SC', 'ANKR', 'STORJ', 'BCD', 'RVN', 'XTZ', 'NEO', 'ONT', 'ZEC', 'SXP', 'ICX', 'CVC', 'ETH', 'BCN', 'ZRX', 'QTUM', 'KNC', 'LSK', 'ETC', 'ADA', 'ENJ', 'LTC', 'BAT', 'DCR', 'BTC', 'LINK']
    # 내가 직접 지정한 심볼들
    # ban_list = ['CHZ', 'ETH', 'ANKR', 'LINK', 'BAT', 'SXP', 'ETC', 'OMG', 'MANA', 'ZRX', 'ENJ', 'STORJ', 'KNC', 'SRM', 'SRM', 'SAND', 'CVC', 'NEO', 'BCH', 'SC', 'QTUM']
    # 분단위가 아닌 심볼들
    # ban_list = ['ADA','AE','ANKR','BAT','BCD','BCH','BCHA','BCN','BSV','BTC','BTG','BTT','CHZ','CVC','DASH','DCR','DGB','DOGE','ENJ','ETC','ETH','ICX','IOTA','KNC','LINK','LSK','LTC','MANA','NEO','OMG','ONT','QTUM','RVN','SAND','SC','SRM','STORJ','SXP','TRX','XMR','XTZ','ZEC','ZRX']
    # 50분 내외로 전송되는 심볼들
    # ban_list = ['ANKR', 'BAT', 'BCD', 'BCH', 'BCHA', 'BSV', 'BTC', 'BTG', 'CHZ', 'CVC', 'DCR', 'ENJ', 'ETC', 'ETH', 'KNC', 'LINK', 'LTC', 'MANA', 'NEO', 'OMG', 'QTUM', 'RVN', 'SAND', 'SC', 'SRM', 'STORJ', 'SXP', 'XMR', 'ZEC', 'ZRX']

    User_data = {}
    #     User_data["asset_division"] = asset_division
    User_data['ban_list'] = ban_list
    User_data["up_market_fee"] = up_market_fee  # 0.05%
    User_data["bin_spot_market_fee"] = bin_spot_market_fee  # maker 0.1% taker 0.1%
    User_data["bin_future_market_fee"] = bin_future_market_fee  # maker 0.02% taker 0.04%
    User_data["bin_Coin_M_future_market_fee"] = bin_Coin_M_future_market_fee  # maker 0.01% taker 0.05%

    User_data["qwer"] = qwer

    return asset_division, User_data

##@ 0.기본셋팅
Usdt = upbit_get_usd_krw()
print('Usdt', Usdt)

balance = binance.fetch_balance()  # free:보유중인 코인, used:거래진행중인 코인 total:전체코인
print("총 자본", upbit.get_balance("KRW") + float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['walletBalance']) * Usdt + balance['USDT']['free'] * Usdt)

# 업비트 현물계좌 원화(현금) 확인
# first_up_asset = 1000000# $$@@ 가정한부분 나중에 바꾸기
# first_up_asset = upbit.get_balance("KRW")
# up_asset = first_up_asset - first_up_asset * 0.0005 # @ up_market_fee # 계좌 현금 확인
# up_asset = up_asset - up_asset * 0.0005 # @ up_market_fee # 수수료 보정치(슬리피지)
# print(up_asset, "업비드 자본(수수료 제외)")
up_asset_cheak = upbit.get_balance("KRW")
print(up_asset_cheak, "업비드 자본")

# 바이낸스 선물계좌 달러 확인
# bin_fu_ass = 350# $$@@가정하고 계산하는 부분 나중에 바꾸기.
fu_asset_cheak =float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])
print(fu_asset_cheak, "바이낸스 선물계좌 달러 잔고 확인:") #bin_fu_ass

# first_bin_fu_ass = bin_fu_ass
# bin_fu_ass = bin_fu_ass - bin_fu_ass * 0.0004 # @ bin_future_market_fee
# binance_asset = bin_fu_ass * Usdt
# print(binance_asset, "원 바이낸스 자본(조정 전)")

#@@@ 벤리스트 마지막에 처리하기. 일단 복잡하니까.=> 새로추가된 심볼명들 !!제하기
# ban_list = ['CHZ', 'ETH', 'ANKR', 'LINK', 'BAT', 'SXP', 'ETC', 'OMG', 'MANA', 'ZRX', 'ENJ', 'STORJ', 'KNC', 'SRM', 'SRM', 'SAND', 'CVC', 'NEO', 'BCH', 'SC', 'QTUM']

def cheak_about_regester_by_upbit():
    with open('regester_by_upbit.pickle', 'rb') as fr:
        regester_by_upbit = pickle.load(fr)
        past_sym_name = regester_by_upbit["past_sym_name"]

    sym_name = sym_intersection()

    New_sym_bols = list(set(sym_name) - set(regester_by_upbit['past_sym_name']))

    if (len(set(sym_name) - set(regester_by_upbit['past_sym_name'])) != 0):
        print("==================================warning==================================")
        print("새로운 심볼들 !!!!(업비트 출금주소 등록할것!)", list(set(sym_name) - set(regester_by_upbit['past_sym_name'])))
        print("==================================warning==================================")

        print("새로운 출금 주소를 등록하시고 진행하시겠습니까 ? (Y/N)")
        print("Y입력 시 업비트에 출금 주소 입력하고 진행")
        print("N입력 시 새로 추가된 심볼은 사용하지 않고 진행함.")
        input_command = input()

        if (input_command == "Y"):
            import warnings
            warnings.warn("새로운 심볼들 !!!!(업비트 출금주소 등록할것!)", DeprecationWarning)
            sys.exit()  ## 강제로 파이썬 종료

        elif (input_command == "N"):
            User_data['ban_list'] = User_data['ban_list'] + New_sym_bols
        #             return User_data

        else:
            print("input 입력 오류")
            sys.exit()  ## 강제로 파이썬 종료


import telegram  # pip install python-telegram-bot
import requests


def Telegramchat(text):  # @ 조기정
    telegram_token = '5106829469:AAGc-XqcK67mDADEuJERXFXgazI68dcO_x0'
    telegram_chat_id = '5257112430'
    bot = telegram.Bot(token=telegram_token)

    url = 'https://api.telegram.org/bot' + telegram_token + '/sendMessage?chat_id=' + telegram_chat_id + '&text=' + text
    return requests.get(url)
# send_text = "봇 종료"
# response = Telegramchat(send_text)
# response = Telegramchat(str("응애응애응애")+str(a)+str(2))

# fu_D_setting() # coin_M레버리지 세팅 @@여기서 오래걸림
asset_division, User_data = first_asset_division(500000)  # div_unit = 2000000 #자본을 나눌 단위 (krw) #@@ input()을 추가?

cheak_about_regester_by_upbit()  # 별말 없으면 그냥 진행
# cheak_about_regester_by_bin()

check_logic(asset_division)

asset_division = set_premium_asset_division() # %수치 변화. #@@ 여기도 레버리지에 따라 최소 차익 볼 김프 수치 조정하기

# @@업비트 자본이 11배 이상 큰 경우 .. 아 ㅅㅂ 이게 아니라.. 그냥 100 만원이상 못보내는건데.. 어칼까.
State_All = [asset_division[w]["State"] for w in range(len(asset_division))]
if up_asset_cheak > (fu_asset_cheak * 11 * Usdt) and (len(set(State_All) & {'None_position'}) == 1):  # 11배 차이가 안나고, 중복이 없다면
    print("바이낸스가 너무 소액만 남았고 업비트 자본만 너무 큰 경우 처음이라고 인식")
    print("업비트에서 적정금액 바이낸스로 전송해야 함.=> 새로운 로직 추가")

elif (len(set(State_All) & {'None_position'}) == 1):
    print("모든 상태가 없을때 다시 자본을 분배함.")
else:
    print("그대로 계속 실행하면 됨.")


def step_1_1_sym_name(up_asset, future_leverage, ban_list, up_market_fee):
    # 업비트에서 출금가능 바이낸스에서 입금가능 #업 => 바
    sym_name = sym_intersection()  # 업비트 현물 , 바이낸스 현물 , 바이낸스 선물의 교집합을 가진 심볼명만 가져옴
    Usdt = upbit_get_usd_krw()  # 업비트에서 1달러당 환율 가져옴
    all_coin_info = client_spot.coin_info()  # 코인 정보를 전부 한번만 가져와서 저장함
    sym_name = delet_None_network(all_coin_info, sym_name)  # 코인 스스로 전송 불가능 한 코인은 제외(바이낸스 체인 ,bnb만 전송가능한코인)

    # @@ 전송속도 1분 이상거르기
    # ban_list = ['CHZ', 'ETH', 'ANKR', 'LINK', 'BAT', 'SXP', 'ETC', 'OMG', 'MANA', 'ZRX', 'ENJ', 'STORJ', 'KNC', 'SRM', 'SRM', 'SAND', 'CVC', 'NEO', 'BCH', 'SC', 'QTUM']
    sym_name = list(set(sym_name) - set(ban_list))
    sym_name = del_bin_disable_withdrow_deopsit(all_coin_info, sym_name)  # 바이낸스 입출금 불가능 심볼 삭제
    sym_name = del_up_disable_deopsit(sym_name)  # 업비트 입금 불가능 심볼 삭제 # @@ 아예 여기서 심볼명 다 정의해..?
    sym_name = del_up_disable_whthdraw(sym_name)  # 업비트 출금 불가능 심볼 삭제

    # 시간 줄이기 위함, 각 자본마다 심볼명 저장해두고 그것중에서 선택 => 전송수수료가 싸진 코인은 나중에서야 알수있는 단점이 있음
    sym_name = remove_sym_name_1(all_coin_info, sym_name, Usdt, up_asset / future_leverage, 0.003, ban_list, up_market_fee)

    future_leverage_ceil = math.ceil(future_leverage)

    for i in range(len(sym_name)):
        bin_fu_setting(sym_name[i], future_leverage_ceil)

    ##
    aa = client.futures_account()
    del_list = []
    del_list_append = del_list.append
    for i in range(len(sym_name)):
        if (future_leverage_ceil > int(next((item for item in aa['positions'] if item['symbol'] == sym_name[i] + 'USDT'), None)['leverage'])):
            #         print(int(next((item for item in aa['positions'] if item['symbol'] == sym_name[i] + 'USDT'), None)['leverage']))
            #         print(sym_name[i])
            del_list_append(sym_name[i])

    sym_name = list(set(sym_name) - set(del_list))
    ##

    # aa = client.futures_account()
    # for i in range(len(sym_name)):
    #     if (future_leverage_ceil > int(next((item for item in aa['positions'] if item['symbol'] == sym_name[i] + 'USDT'), None)['leverage'])):
    #         print('레버리지변환 오류 프로그램 실행 멈추고 확인 바람')
    #         sys.exit()  ## 강제로 파이썬 종료

    #     statuses = ('심볼명',sym_name) # 더러워 보여서 추가한 코드..

    #     if (len(statuses) != 0):
    #         clear_output(wait=True)
    #         display(statuses)

    return sym_name, future_leverage_ceil


def step_1_1(sym_name, up_asset, binance_asset, up_market_fee, bin_spot_market_fee, bin_future_market_fee, want_premium_step_1_1, ban_list, adjust_leverage, before_future_leverage_ceil, div_unit):
    before_step_1_1_up_krw_asset = upbit.get_balance("KRW")
    before_step_1_1_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])

    Usdt = upbit_get_usd_krw()  # 그래서 잘 안변하는 달러는 여기서 갱신
    binance_asset = binance_asset * Usdt  # 환율 변동 떄문에 바이낸스에서 쓸 자본은 달러로 저장해야함..

    if (up_asset > binance_asset):  # 업비트 자본이 큰 경우
        future_leverage = up_asset / binance_asset
    else:  # 바이낸스 자본이 더 큰경우 # 바이낸스 자본비율이
        future_leverage = 1

    if (future_leverage != 1):  # @ 바이낸스 자본과 업비트 자본의 비율이 2배 이상이 될 경우.
        if (up_asset < binance_asset):  # 바이낸스 자본이 더 큰 경우 @@주로 김프니까(역프는..)이 경우는 그냥 업비트 자본 따라가는게 맞겠지..?
            binance_asset = up_asset
        elif (binance_asset <= up_asset):  # 김프의 경우 2배차이가 나기 시작하면
            binance_asset = binance_asset  # * future_leverage
            up_asset = binance_asset * future_leverage  # 이렇게 함으로 써 같은 비율..?
    elif (up_asset < binance_asset):  # 작은 자본의 가격을 따라간다.(레버리지 1일때)
        binance_asset = up_asset
    elif (binance_asset <= up_asset):
        up_asset = binance_asset

    Using_asset = up_asset + binance_asset  # 더 적은 것으로 맞춰진 자본들.

    all_coin_info = client_spot.coin_info()  # 코인 정보를 전부 한번만 가져와서 저장함
    # # 아래 두개는 입출금 불가 상태에서 끼는 김프를 대비
    #
    # sym_name = del_bin_disable_withdrow_deopsit(all_coin_info, sym_name)  # 바이낸스 입출금 불가능 심볼 삭제
    #
    # # sym_name = del_bin_disable_withdraw(all_coin_info, sym_name)  # 바이낸스 출금 불가능 심볼 삭제
    # sym_name = del_up_disable_deopsit(sym_name)  # 업비트 입금 불가능 심볼 삭제
    # # sym_name = del_bin_disable_deopsit(all_coin_info, sym_name)  # 바이낸스 입금 불가능 코인 삭제
    # sym_name = del_up_disable_whthdraw(sym_name)  # 업비트 출금 불가능 심볼 삭제
    #
    # ##!!!!!처음 사용자는 아래코드 주석처리 없이 실행하고 여기서 주소 가져다가 써야함!!!!!!
    # # regester_by_upbit_withdrow_addres(sym_name)#업비트 오류방지 !! 필요
    #
    # # @@위에서 정의하면 없어도댐
    # sym_name = remove_sym_name_1(all_coin_info, sym_name, Usdt, up_asset / future_leverage, 0.003, ban_list, up_market_fee)  # 내 자본 대비 전송수수료(0.005)가 큰 코인 심볼명 삭제

    future_leverage_ceil = math.ceil(future_leverage)
    if (before_future_leverage_ceil < future_leverage_ceil):
        for i in range(len(sym_name)):
            bin_fu_setting(sym_name[i], future_leverage_ceil)
    else:
        pass

    # 함수 정의해도 될듯 업비트 사전 평단가, 수량 가져옴
    up_previous_ticker_list = []
    up_previous_ticker_list_append = up_previous_ticker_list.append
    up_previous_amount_list = []
    up_previous_amount_list_append = up_previous_amount_list.append

    up_avg_buy_price_info_all = up_avg_buy_price_info() #웹소켓 이용 내 정보 요청이다.

    for i in range(len(sym_name)):
        try:
            up_previous_ticker = float(next((item for item in up_avg_buy_price_info_all if item['currency'] == sym_name[i]), None)['avg_buy_price'])
            up_previous_amount = float(next((item for item in up_avg_buy_price_info_all if item['currency'] == sym_name[i]), None)["balance"])
        except:
            up_previous_ticker = 0
            up_previous_amount = 0
        up_previous_ticker_list_append(up_previous_ticker)
        up_previous_amount_list_append(up_previous_amount)

    time.sleep(0.4)

    bin_fu_previous_ticker_list = []
    bin_fu_previous_ticker_list_append = bin_fu_previous_ticker_list.append
    bin_fu_previous_amount_list = []
    bin_fu_previous_amount_list_append = bin_fu_previous_amount_list.append

    bin_fu_position_info = client.futures_account()  # 포지션 정보 가져옴
    for i in range(len(sym_name)):
        try:
            bin_fu_previous_ticker, bin_fu_previous_amount = bin_fu_avg_buy_price(sym_name[i], bin_fu_position_info)
            # time.sleep(0.3)
        except:
            bin_fu_previous_ticker = 0
            bin_fu_previous_amount = 0
        bin_fu_previous_ticker_list_append(bin_fu_previous_ticker)
        bin_fu_previous_amount_list_append(bin_fu_previous_amount)

    up_withdrawfee, bin_withdrawfee = up_bin_withdraw_fee(sym_name, all_coin_info)  # 업비트 전송 수수료 , 바이낸스 전송 수수료
    up_Min_Withdraw_Size, bin_Min_Withdraw_Size = up_bin_withdraw_Size(sym_name, all_coin_info)  # 업비트, 바이낸스 전송최소 가능량
    Bin_Fu_Minimum_Order_Size = Bin_Minimum_FU_Order_Size(sym_name)  # 바이낸스 현물 최소 주문 가능량
    Bin_Spot_Minimum_Order_Size = Bin_Minimum_Spot_Order_Size(sym_name)  # 바이낸스 선물 최소 주문가능량

    up_to_bin_pre_rate = []
    up_to_bin_pre_rate_append = up_to_bin_pre_rate.append
    bin_to_up_pre_rate = []
    bin_to_up_pre_rate_append = bin_to_up_pre_rate.append
    up_withdrawfee_by_asset = []
    up_withdrawfee_by_asset_append = up_withdrawfee_by_asset.append
    bin_withdrawfee_by_asset = []
    bin_withdrawfee_by_asset_append = bin_withdrawfee_by_asset.append

    # 호가창 정보 가져옴
    up_sym_names, up_spot_ask_bid = up_spot_ask_bid_info(sym_name)
    up_ask_price, up_ask_size = up_ask_info(up_sym_names, up_spot_ask_bid)  # 업비트 매수 호가창 1
    up_bid_price, up_bid_size = up_bid_info(up_sym_names, up_spot_ask_bid)  # 업비트 매도 호가창 4

    bin_sym_names, bin_spot_ask_bid = bin_spot_ask_bid_info(sym_name)
    bin_spot_ask_price, bin_spot_ask_size = bin_ask_info(bin_sym_names, bin_spot_ask_bid)  # 바-현 매수 호가창 3
    bin_spot_bid_price, bin_spot_bid_size = bin_bid_info(bin_sym_names, bin_spot_ask_bid)  # 바-현 매도 호가창 2

    bin_sym_names, bin_fu_ask_bid = bin_fu_ask_bid_info(sym_name)
    bin_fu_ask_price, bin_fu_ask_size = bin_fu_ask_info(bin_sym_names, bin_fu_ask_bid)  # 바-선 매수 호가창 2 4
    bin_fu_bid_price, bin_fu_bid_size = bin_fu_bid_info(bin_sym_names, bin_fu_ask_bid)  # 바-선 매도 호가창 1 3

    for i in range(len(sym_name)):
        #     up_to_bin_pre_rate.append(up_bid_price[i]/(bin_spot_ask_price[i]*Usdt)) # 역프 or 바낸 전송시 예상 손수익 %
        #     bin_to_up_pre_rate.append((bin_spot_bid_price[i]*Usdt)/up_ask_price[i]) # 김프 or 업비트 전송시 예상 손수익 %

        # 프리미엄들(역프,김프)
        up_to_bin_pre_rate_append((bin_spot_bid_price[i] * Usdt) / up_ask_price[i])  # 역프 or 바낸 전송시 예상 손수익 %(김프시 손해)
        bin_to_up_pre_rate_append(up_bid_price[i] / (bin_spot_ask_price[i] * Usdt))  # 김프 or 업비트 전송시 예상 손수익 %(김프시 수익)

        # 자본대비 수수료 오직 비율로만 따짐.
        up_withdrawfee_by_asset_append(up_to_bin_pre_rate[i] - ((up_ask_price[i] * up_withdrawfee[i]) / up_asset))  # 내 자본 대비 전송수수료를 포함하여 가장 좋은 최적의 값 서칭
        bin_withdrawfee_by_asset_append(bin_to_up_pre_rate[i] - ((bin_spot_ask_price[i] * bin_withdrawfee[i]) / (up_asset)))  # 바이낸스 선물에서 매수 할거니 매도호가창조회

    # 나중에 a는 변수명 최적_to_bin으로 바꾸기?b도
    # (업 => 바)전송시 최적 코인 인덱스 번호(a) , (바 => 업)전송 시 최적 코인 인덕스 번호(b)
    a = up_withdrawfee_by_asset.index(max(up_withdrawfee_by_asset))  # 리스트에서 가장 큰 값 뽑음(업 => 바 가장 큰 값 인덱스) @@맞지? 현재 김프역프 왔다리 갓다리 하니까
    b = bin_withdrawfee_by_asset.index(max(bin_withdrawfee_by_asset))  # 리스트에서 가장 큰 값 뽑음(바 => 업 가장 큰 값 인덱스)
    # 여기서 김프또한 손해 보는 비율로 가져온것이기 떄문에 이전 코드와는 좀 다름.

    # 인덱스번호 ab,역프 심볼명, 김프 심볼명, 김프%, 역프 %,

    # 시드의 움직임

    # 1.업비트 주문 가능량########이 부분은 빨라야 해서 함수 정의 안함######################## option1
    # up_can_order_amout = up_asset * (1 - up_market_fee)  # *0.005이미함
    # up_can_order_amout = up_can_order_amout + (up_withdrawfee[a] * up_ask_price[a])  ##완벽한 헷징을 위해 업비트 전송료만큼 추가..#@@이부분..계산

    # # option @@ 정확한 수량을 사용하기 위해선 아래의 로직 필요함 (업비트에 전송 안남기기)
    # up_can_order_amout = ((up_can_order_amout/ up_ask_price[a]) // Bin_Spot_Minimum_Order_Size[a])* Bin_Spot_Minimum_Order_Size[a] * up_ask_price[a]

    # up_withdrow_fee_Max = (((up_withdrawfee[a] * up_ask_price[a]) // Decimal_rounding) + 1) * Decimal_rounding  # 주문전에 더해줄 업비트 수량 #업비트는 주문을 원화로 들어가니 올림해버림.

    # Decimal_rounding = UP_Minimum_Order_cash_Size(up_ask_price[a])
    # up_can_order_amout = (up_can_order_amout // Decimal_rounding) * Decimal_rounding

    # can_send_Decimal = up_Min_Withdraw_Size[a]  # 전송가능 최소량 @@ 여기에 바이낸스 현물.. 디미컬 라운딩 할까..? => 업비트는 원화로 주문해서 더 정교한 수식이 핋요
    # if (can_send_Decimal == 0):  # 전송 수수료가 0 인경우 나눌 수가 없음
    #     pass
    # else:
    #     Decimal_rounding, Decimal_rounding_dig = (0.1)**int(can_send_Decimal + 1) , int(can_send_Decimal)# 소수점 라운딩
    #     up_can_order_amout = (up_can_order_amout // Decimal_rounding) * Decimal_rounding
    #     up_can_order_amout = round(up_can_order_amout , Decimal_rounding_dig)
    # 전송수수료 만큼 더 주문함.
    ################################################################################## option2

    up_can_order_amout = up_asset * (1 - up_market_fee)  # *0.005이미함
    up_can_order_amout = (((up_can_order_amout / up_ask_price[a])) // Bin_Spot_Minimum_Order_Size[a]) * Bin_Spot_Minimum_Order_Size[a] * up_ask_price[a]  ##완벽한 헷징을 위해 업비트 전송료만큼 추가..#@@이부분..계산

    Decimal_rounding = UP_Minimum_Order_cash_Size(up_ask_price[a])
    up_can_order_amout = (up_can_order_amout // Decimal_rounding) * Decimal_rounding

    up_withdrow_fee_Max = (((up_withdrawfee[a] * up_ask_price[a]) // Decimal_rounding) + 1) * Decimal_rounding  # 주문전에 더해줄 업비트 수량 #업비트는 주문을 원화로 들어가니 올림해버림.

    can_send_Decimal = up_Min_Withdraw_Size[a]  # 전송가능 최소량 @@ 여기에 바이낸스 현물.. 디미컬 라운딩 할까..? => 업비트는 원화로 주문해서 더 정교한 수식이 핋요
    if (can_send_Decimal == 0):  # 전송 수수료가 0 인경우 나눌 수가 없음
        pass
    else:
        Decimal_rounding, Decimal_rounding_dig = (0.1) ** int(can_send_Decimal + 1), int(can_send_Decimal)  # 소수점 라운딩
        up_can_order_amout = (up_can_order_amout // Decimal_rounding) * Decimal_rounding
        up_can_order_amout = round(up_can_order_amout, Decimal_rounding_dig)

    ##################################################################################

    # 1.바이낸스 공매도 주문가능량 ####이 부분은 빨라야 해서 함수 정의 안함##################### option1
    # if (future_leverage != 1):  # 자본조정이 필요하다면
    #     binance_asset_1 = up_can_order_amout - (up_withdrawfee[a] * up_ask_price[a])
    # #     binance_asset_1 = binance_asset * future_leverage  # @@ 이게 맞나 정녕??
    # #     if((1-((bin_spot_bid_price[a]*Usdt)/up_ask_price[a])) <= 0):#역프 상태라면 # 이렇게 하면 좀더 가능성 있을지도 역프는 금방 빠지니까.
    # #         binance_asset_1 = binance_asset * future_leverage
    # #     else:
    # #         binance_asset_1 = up_can_order_amout - (up_withdrawfee[a] * up_ask_price[a])

    # elif ((1 - ((bin_spot_ask_price[a] * Usdt) / up_ask_price[a])) <= 0):  #레버리지는 1 이 아니고 역프 상태라면
    #     binance_asset_1 = binance_asset # 레버리지가 1이 아니라면
    # else:
    #     binance_asset_1 = up_can_order_amout - (up_withdrawfee[a] * up_ask_price[a])  # 바이낸스에서는 전송 수수료 만큼 덜 주문#@@이부분 바꿔야함
    # @ 극히 드문 가능성으로, 달러가치가 변해서 여기서 오류가 날 가능성도 있음
    # asset_symbol_quantity = ((binance_asset_1 / Usdt) / bin_fu_bid_price[a]) * (1 - bin_future_market_fee * future_leverage)  # 바이낸스 시장가 수수료#@@이부분 맞나.. 수수료

    # 주문가능 최소량 소수점 라운딩
    # Decimal_rounding, Decimal_rounding_dig = Bin_Fu_Minimum_Order_Size[a] + 1, 5 # 소수점 라운딩
    # bin_can_order_asset_symbol_quantity = (asset_symbol_quantity // Decimal_rounding) * Decimal_rounding
    # bin_can_order_asset_symbol_quantity = round(bin_can_order_asset_symbol_quantity , Decimal_rounding_dig)
    ################################################################################# option2
    ## **이 경우가 안되면 전송 시 조금 수익권에서 파는 수치 조정 필요함 => 주문된 수량을 보고 얼마나 사용되었는지 파악하기 !
    ## @@ 만약 업비트 주문양이 잘 안맞는 경우 해당 로직으로 아예 업비트와 같은 양 사용하게 함(정확히)
    # (참고용) up_can_order_amout / up_ask_price[a] 와 bin_can_order_asset_symbol_quantity가 같아야함 #@@ 사실은 해당 로직을 사용해야 함.
    asset_symbol_quantity = up_can_order_amout / up_ask_price[a]

    Decimal_rounding, Decimal_rounding_dig = Bin_Fu_Minimum_Order_Size[a] + 1, 5  # 소수점 라운딩 # 4는.. 기본수치랄까
    bin_can_order_asset_symbol_quantity = (asset_symbol_quantity // Decimal_rounding) * Decimal_rounding
    bin_can_order_asset_symbol_quantity = round(bin_can_order_asset_symbol_quantity, Decimal_rounding_dig)
    #################################################################################

    up_can_order_amout = round(up_can_order_amout + up_withdrow_fee_Max, 8)  # 주문전에 더해줄 업비트 수량

    # 1. 업비트에서 매수 ask
    #     x1 = up_asset * (1 - up_market_fee) - (up_ask_price[a] * up_withdrawfee[a])
    # x1 = up_can_order_amout - (up_ask_price[a] * up_withdrawfee[a])  # * 코인 현재가 #예상평단가 up_ask_price[a]
    x1 = up_can_order_amout - up_withdrow_fee_Max  # * 코인 현재가 #예상평단가 up_ask_price[a]
    # 1. 바이낸스 선물에서 공매도 bid
    #     y1 = binance_asset * (1 - bin_future_market_fee * future_leverage) / future_leverage
    y1 = bin_can_order_asset_symbol_quantity * bin_fu_bid_price[a] * Usdt / future_leverage  # 예상 평단가 bin_fu_bid_price[a]

    # 2. 바이낸스 현물에서 매도 bid #예상수익 역프 : up_to_bin_pre_rate
    x2 = x1 * ((bin_spot_bid_price[a] * Usdt) / up_ask_price[a]) * (1 - bin_spot_market_fee)  # 예상 평단가 bin_spot_ask_price[a]
    #     x2 = up_can_order_amout * ((bin_spot_ask_price[a]*Usdt)/up_bid_price[a]) * (1 - bin_spot_market_fee) #예상 평단가 bin_spot_ask_price[a]

    # 2.바이낸스 선물에서 공매수 ask
    y2 = y1 * (1 + (1 - bin_fu_ask_price[a] / bin_fu_bid_price[a]) * future_leverage) * (1 - bin_future_market_fee * future_leverage)  # 예상 평단가 bin_fu_bid_price[a]
    #     y2 = (bin_can_order_asset_symbol_quantity*bin_fu_bid_price[a]*Usdt) * (bin_fu_ask_price[a]/bin_fu_bid_price[a]) * (1 - bin_future_market_fee) #예상 평단가 bin_fu_bid_price[a] (팔가격)
    # bin_fu_bid_price[b]/bin_fu_ask_price[a]

    second_using_asset = x2 + y2

    if (((1 - (x2 / (x1 + up_ask_price[a] * up_withdrawfee[a])) < want_premium_step_1_1) and (1 - up_to_bin_pre_rate[a] < want_premium_step_1_1) and (1 - (second_using_asset / Using_asset) < want_premium_step_1_1)) or (Using_asset < second_using_asset)):
        # if (((will_Realize_Arbitrage_rate >= (1 + 0.005 / future_leverage)) and (1 - (x2 / (x1 + up_ask_price[a] * up_withdrawfee[a])) < want_premium_step_1_1) and (1 - up_to_bin_pre_rate[a] < want_premium_step_1_1) and (1 - (second_using_asset / Using_asset) < want_premium_step_1_1)) or (Using_asset < second_using_asset)):
        # print("트루")
        if (up_ask_size[a] * 0.5 > (up_can_order_amout // up_ask_price[a]) and (up_can_order_amout < up_asset) and (bin_can_order_asset_symbol_quantity * bin_fu_bid_price[a] < binance_asset / Usdt * future_leverage) and (
                bin_can_order_asset_symbol_quantity * bin_fu_bid_price[a] < binance_asset / Usdt * future_leverage_ceil)):
            #     if (up_bid_size[a] * 0.5 > (up_can_order_amout // up_bid_price[a]) and (up_can_order_amout < up_asset) and (bin_can_order_asset_symbol_quantity * bin_fu_bid_price[a] < binance_asset / Usdt * future_leverage_ceil)): #정확한 숫자만큼 들어가지 않을 시 사용할 비율
            # print("주문요청")
            try:
                # 바이낸스주문신청                    # 심볼            #sell 이면 숏 buy면 롱
                # 바이낸스 선물 시장가 숏 # @@ 이슈 진정 전까진 이걸로

                result = request_client.post_order(symbol=sym_name[a] + "USDT", side=OrderSide.SELL,
                                                   ordertype=OrderType.MARKET,  # 시장가 거래
                                                   quantity=bin_can_order_asset_symbol_quantity)  # quantity수량.#Orderside sell 이면 판매
                PrintBasic.print_obj(result)



            except:
                result = binance_fu.create_market_sell_order(symbol=sym_name[a] + "/USDT", amount=bin_can_order_asset_symbol_quantity, )
                pprint.pprint(result)  # 시장가 주문 오류 시 지정가 주문으로 들어감 이부분 위험함

            ret = upbit.buy_market_order("KRW-" + sym_name[a], up_can_order_amout)  # 있는현금만큼 구매#갯수로 구매가능하면..
            pprint.pprint(ret)  # 구매주문확인
            # # 지정가 주문
            #                 ret = upbit.buy_limit_order("KRW-" + sym_name[a], up_ask_price[a], up_can_order_amout / up_ask_price[a])  # 지정가 주문은 또 갯수로 받음
            # # 지정가 거래
            #                 result = request_client.post_order(symbol=sym_name[a] + "USDT", side=OrderSide.SELL,
            #                                                    ordertype=OrderType.LIMIT,
            #                                                    quantity=bin_can_order_asset_symbol_quantity,
            #                                                    timeInForce="GTC",
            #                                                    price=bin_fu_bid_price[a])
            #
            # PrintBasic.print_obj(result)
            # pprint.pprint(ret)  # 구매주문확인
            # # 주문이 전부 끝날 때 까지 대기.
            # while True:  # @@ 이부분 애매한게 주문수량이 소수점으로 조금더  들어감
            #     # @@ 사실 지정가는 안긁히면 매우 위험한 방법.. 예를들어 바이낸스는 모두 긁히고 업비트는 하나도 안긁힐 경우 큰일난다.
            #     try:
            #         cheak_amount_1 = float(next((item for item in upbit.get_balances() if item['currency'] == sym_name[a]), None)['balance'])
            #         cheak_amount_2 = ((up_can_order_amout / up_ask_price[a]) // 0.00000001) * 0.00000001
            #         cheak_amount_3 = float(next((item for item in client.futures_account()['positions'] if item['symbol'] == sym_name[a] + "USDT"), None)['positionAmt'])
            #         cheak_amount_4 = bin_can_order_asset_symbol_quantity
            #
            #         statuses = ("업비트 : 주문완료량 / 주문량", cheak_amount_1, "/", cheak_amount_2,
            #                     "바이낸스 : 주문완료량 / 주문량", cheak_amount_3, "/", cheak_amount_4,
            #                     "현재시각", time.ctime(time.time())
            #                     )
            #
            #         if ((cheak_amount_1 >= cheak_amount_2) and (cheak_amount_3 == cheak_amount_4)):
            #             print("모든 수량 포지션 진입")
            #             break
            #
            #     except TypeError:
            #         statuses = ("업비트 주문량 아직 0개", "현재시각", time.ctime(time.time()))
            #
            #     if (len(statuses) != 0):
            #         clear_output(wait=True)
            #         display(statuses)
            #
            #     time.sleep(3)

            # pass

            # tt.toc()
            time.sleep(3)
            # 업비트 매수 평단가  , 수량
            point_of_buy_UP_ticker_1, point_of_buy_UP_amount_1 = up_avg_buy_price(sym_name[a])
            # 바이낸스 매수 평단가 , 수량
            bin_fu_position_info = client.futures_account()
            point_of_buy_bin_fu_ticker_1, point_of_buy_bin_fu_amount_1 = bin_fu_avg_buy_price(sym_name[a], bin_fu_position_info)

            # ##가상으로 할 경우
            # point_of_buy_UP_ticker_1, point_of_buy_UP_amount_1 = up_ask_price[a], up_can_order_amout/up_ask_price[a]
            # point_of_buy_bin_fu_ticker_1, point_of_buy_bin_fu_amount_1 = bin_fu_bid_price[a], bin_can_order_asset_symbol_quantity

            if (up_previous_ticker_list[a] != 0):  # 이전에 구매한 코인이 아니라면(평단가는0 이 아님)
                up_previous_ticker, up_previous_amount = up_previous_ticker_list[a], up_previous_amount_list[a]  # 이전 평단가,수량
                now_ticker, now_amount = up_avg_buy_price(sym_name[a])  # 이후 평단가,수량
                #     now_ticker, now_amount = up_ask_price[a], up_can_order_amout/up_ask_price[a] # 이후 평단가,수량 ##가상으로 할 경우

                # (기존 평단가 * 기존 개수) + (point_of_buy_UP_ticker_1  * point_of_buy_UP_amount_1)/(모든 개수) = 바뀐평단가
                point_of_buy_UP_amount_1 = now_amount - up_previous_amount
                point_of_buy_UP_ticker_1 = (now_ticker * (up_previous_amount + point_of_buy_UP_amount_1) - (up_previous_amount * up_previous_ticker)) / point_of_buy_UP_amount_1

            if (bin_fu_previous_ticker_list[a] != 0):  # 이전에 구매한 코인이 아니라면(평단가는0 이 아님)
                bin_fu_previous_ticker, bin_fu_previous_amount = bin_fu_previous_ticker_list[a], bin_fu_previous_amount_list[a]  # 이전 평단가,수량
                bin_fu_now_ticker, bin_fu_now_amount = bin_fu_avg_buy_price(sym_name[a], bin_fu_position_info)  # 이후 평단가,수량
                #     bin_fu_now_ticker, bin_fu_now_amount =  bin_fu_bid_price[a], bin_can_order_asset_symbol_quantity  # 이후 평단가,수량 ##가상으로 할 경우

                # (기존 평단가 * 기존 개수) + (point_of_buy_bin_spot_ticker_2  * point_of_buy_bin_spot_amount_2)/(모든 개수) = 바뀐평단가
                point_of_buy_bin_fu_amount_1 = bin_fu_now_amount - bin_fu_previous_amount
                point_of_buy_bin_fu_ticker_1 = ((bin_fu_now_ticker * bin_fu_now_amount) - (bin_fu_previous_amount * bin_fu_previous_ticker)) / point_of_buy_bin_fu_amount_1

            # x1 = point_of_buy_UP_ticker_1 * (point_of_buy_UP_amount_1 - up_withdrawfee[a])  # 업비트 자본 사용량 # up_can_order_amout == point_of_buy_UP_amount_1
            x1 = point_of_buy_UP_ticker_1 * point_of_buy_UP_amount_1 - up_withdrow_fee_Max  # 업비트 자본 사용량 # up_can_order_amout == point_of_buy_UP_amount_1
            y1 = point_of_buy_bin_fu_amount_1 * point_of_buy_bin_fu_ticker_1 * Usdt / future_leverage  # bin_can_order_asset_symbol_quantity == point_of_buy_bin_fu_amount_1
            # print(x1, y1)

            # 2. 바이낸스 현물에서 매도 #예상수익 역프 : up_to_bin_pre_rate
            # expect_x2 = x1 * ((bin_spot_ask_price[a]*Usdt)/up_bid_price[a]) * (1 - bin_spot_market_fee) #예상 평단가 bin_spot_ask_price[a]
            expect_x2 = x1 * ((bin_spot_bid_price[a] * Usdt) / point_of_buy_UP_ticker_1) * (1 - bin_spot_market_fee)  # 예상 평단가 bin_spot_ask_price[a]
            # 2.바이낸스 선물에서 공매수
            expect_y2 = y1 * (1 + (1 - bin_fu_ask_price[a] / point_of_buy_bin_fu_ticker_1) * future_leverage) * (1 - bin_future_market_fee * future_leverage)  # 예상 평단가 bin_fu_bid_price[a]
            # print(expect_x2 ,expect_y2)

            ##### 잔고조회로 남는 코인자본 전송 같이 시킴
            can_send_amount = upbit.get_balance(sym_name[a])
            if (0 < ((can_send_amount - point_of_buy_UP_amount_1) * point_of_buy_UP_ticker_1) < (div_unit / 15)):
                point_of_buy_UP_amount_1 = can_send_amount  # can_send_amount 가 자기자신이 된다 (남은 자본 보냄)
            else:
                pass
            ##### 전송 간가능수량도출
            point_of_Withdrow_UP_amount_1 = point_of_buy_UP_amount_1 - up_withdrawfee[a]

            can_withdrow_Decimal = up_Min_Withdraw_Size[a]  # 전송가능 최소량 @@ 여기에 바이낸스 현물.. 디미컬 라운딩 할까..? => 업비트는 원화로 주문해서 더 정교한 수식이 핋요
            if (can_withdrow_Decimal == 0):  # 전송 수수료가 0 인경우 나눌 수가 없음
                pass
            else:
                Decimal_rounding, Decimal_rounding_dig = (0.1) ** int(can_withdrow_Decimal + 1), int(can_withdrow_Decimal)  # 소수점 라운딩
                # point_of_Withdrow_UP_amount_1 = float("{:0.0{}f}".format(point_of_Withdrow_UP_amount_1, Decimal_rounding_dig)) #@@ 자꾸 오류생기면 해당 식으로 변환
                point_of_Withdrow_UP_amount_1 = (point_of_Withdrow_UP_amount_1 // Decimal_rounding) * Decimal_rounding
                point_of_Withdrow_UP_amount_1 = round(point_of_Withdrow_UP_amount_1, Decimal_rounding_dig)
            #####

            # 바이낸스 주소 가져옴
            bin_address = client_spot.deposit_address(sym_name[a])['address']
            bin_Memo = client_spot.deposit_address(sym_name[a])['tag']

            print("주문신청 완료")
            time.sleep(0.4)

            ## 가상으로 해볼 경우
            # after_step_1_1_up_krw_asset = before_step_1_1_up_krw_asset - up_can_order_amout
            # after_step_1_1_bin_fu_usdt_asset = before_step_1_1_bin_fu_usdt_asset - bin_can_order_asset_symbol_quantity/future_leverage * bin_fu_bid_price[a]
            after_step_1_1_up_krw_asset = upbit.get_balance("KRW")
            after_step_1_1_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])

            step_1_1_up_krw_asset = before_step_1_1_up_krw_asset - after_step_1_1_up_krw_asset
            step_1_1_bin_fu_usdt_asset = before_step_1_1_bin_fu_usdt_asset - after_step_1_1_bin_fu_usdt_asset  # == point_of_buy_bin_fu_amount_1* point_of_buy_bin_fu_ticker_1 / future_leverage_ceil + point_of_buy_bin_fu_amount_1 * point_of_buy_bin_fu_ticker_1 * bin_future_market_fee

            rest_step_1_1_up_krw_asset = up_asset - step_1_1_up_krw_asset
            rest_step_1_1_bin_fu_usdt_asset = binance_asset / Usdt - step_1_1_bin_fu_usdt_asset

            Measure_Usdt = 1

            return 'step_1_1', sym_name[a], point_of_buy_UP_ticker_1, point_of_buy_UP_amount_1, point_of_buy_bin_fu_ticker_1, point_of_buy_bin_fu_amount_1, expect_x2, expect_y2, point_of_Withdrow_UP_amount_1, bin_address, bin_Memo, future_leverage, Bin_Spot_Minimum_Order_Size[a], x1, y1, Usdt, Using_asset, step_1_1_up_krw_asset, step_1_1_bin_fu_usdt_asset, rest_step_1_1_up_krw_asset, rest_step_1_1_bin_fu_usdt_asset, up_withdrawfee[a], up_withdrawfee_by_asset[a], (x2 / (x1 + up_ask_price[a] * up_withdrawfee[a])), ((Measure_Usdt / bin_spot_bid_price[a]) * up_ask_price[a]) / Measure_Usdt, up_Min_Withdraw_Size[a]

    else:

        # 원화가로 환산됨 # @@ 여기서 실현할 차익 계산 부분은 없어도 된다. (will_Realize_Arbitrage_rate) 까지
        per = find_max_per(second_using_asset, sym_name, bin_spot_ask_price, bin_withdrawfee)
        bin_spot_usdt, bin_fu_Usdt = Adjusting_second_using_asset(second_using_asset, up_market_fee, bin_spot_market_fee, bin_future_market_fee, per, adjust_leverage)
        # 다른 step에선 adjust_leverage 가 아닌 future_leverage가 맞을것.
        # 3.바이낸스 현물 구매 ask #예상수익 김프 : up_to_bin_pre_rate
        x3 = bin_spot_usdt * (1 - bin_spot_market_fee) - (bin_spot_ask_price[b] * bin_withdrawfee[b] * Usdt)  # * 코인 현재가 #예상 평단가 bin_spot_bid_price[b]

        # 3.바이낸스 선물 공매도 bid
        y3 = bin_fu_Usdt * (1 - bin_future_market_fee * adjust_leverage)  # 예상 평단가 bin_fu_bid_price[b] * future_leverage

        # @@이동후

        # step_2_1 에서 @@ adjust_leverage => future_leverage 로 바꾸기
        # 4.업비트 현물에서 매도 bid
        x4 = x3 * (up_bid_price[b] / (bin_spot_ask_price[b] * Usdt)) * (1 - up_market_fee)  # 여기는 어디서 수익볼지가 애매함 #예상 평단가 up_ask_price[b]

        # 4.바이낸스 선물에서 공매수 ask
        y4 = y3 * (1 + (1 - bin_fu_ask_price[b] / bin_fu_bid_price[b]) * adjust_leverage) * (1 - bin_future_market_fee * adjust_leverage)  # 예상 평단가 bin_fu_bid_price[b]
        # bin_fu_bid_price[b]/bin_fu_ask_price[a]

        # 얻을수 있을것으로 보이는 차익,손익(%)
        will_Realize_Arbitrage = (x4 + y4) - (up_asset + binance_asset)
        will_Realize_Arbitrage_rate = (x4 + y4) / (up_asset + binance_asset)

        Measure_Usdt = 1

        statuses = ('x1', x1, 'y1', y1,
                    'x2', x2, 'y2', y2,
                    'x3', x3, 'y3', y3,
                    'x4', x4, 'y4', y4,
                    "처음 사용중인 자본", Using_asset, "전송 후 사용중일 자본", second_using_asset,
                    "첫번째 예상 손수익율", (x2 + y2) / (binance_asset + up_asset),
                    "첫번째 예상 손수익", (x2 + y2) - (binance_asset + up_asset),
                    "두번째 예상 손수익율", (x4 + y4) / (up_asset + binance_asset),
                    "두번째 예상 손수익", (x4 + y4) - (up_asset + binance_asset),
                    "달러가치", Usdt,
                    "바이낸스 실제 쓰일 자본", bin_can_order_asset_symbol_quantity * bin_fu_bid_price[a] * Usdt,
                    "업비트 실제 쓰일 자본", up_can_order_amout - (up_ask_price[a] * up_withdrawfee[a]),
                    "내가 원하는 프리미엄가", want_premium_step_1_1,
                    "전송 시 자본 비율", (x2 / (x1 + up_ask_price[a] * up_withdrawfee[a])),  # (second_using_asset / Using_asset)
                    "현재 최적김프", (1 - up_to_bin_pre_rate[a]) * 100,
                    "평균김프(%)", (1 - (sum(up_to_bin_pre_rate) / len(up_to_bin_pre_rate))) * 100,
                    "해당로직이 통과 시 통과 (want_premium_step_1_1)", (1 - (second_using_asset / Using_asset)),
                    "김프포함 달러가치 (step_1_1)", ((Measure_Usdt / bin_spot_bid_price[a]) * up_ask_price[a]) / Measure_Usdt
                    )
        if (len(statuses) != 0):
            clear_output(wait=True)
            display(statuses)

    Measure_Usdt = 1

    return 'None_position', sym_name[a], 'point_of_buy_UP_ticker_1', 'point_of_buy_UP_amount_1', 'point_of_buy_bin_fu_ticker_1', 'point_of_buy_bin_fu_amount_1', 'expect_x2', 'expect_y2', 'point_of_Withdrow_UP_amount_1', 'bin_address', 'bin_Memo', future_leverage, Bin_Spot_Minimum_Order_Size[a], x1, y1, Usdt, Using_asset, 'step_1_1_up_krw_asset', 'step_1_1_bin_fu_usdt_asset', 'rest_step_1_1_up_krw_asset', 'rest_step_1_1_bin_fu_usdt_asset', up_withdrawfee[a], up_withdrawfee_by_asset[a], (x2 / (x1 + up_ask_price[a] * up_withdrawfee[a])), ((Measure_Usdt / bin_spot_bid_price[a]) * up_ask_price[a]) / Measure_Usdt, up_Min_Withdraw_Size[a]


def send_up_to_bin(send_to_bin_optimal_simbol, point_of_Withdrow_UP_amount_1, bin_address, bin_Memo):  # 업비트에서 바이낸스 전송주문 요청
    send_state_1 = [""]
    try:
        send_state_1 = up_withdrow_request(send_to_bin_optimal_simbol, point_of_Withdrow_UP_amount_1, bin_address, bin_Memo)  # 전송주문 요청
        ########################### 최초 1회 전송시 100 만원 제한 때문에 추가됨 ###############
        try:
            send_amount = float(send_state_1['amount'])
        except KeyError:  # @@ 여기가 만약 수량 오류가 된다면 key에러 말고 다른것.
            print(send_state_1["error"])
            print("업비트에서 바이낸스 전송 시 과거 100 만원 이상 입출금 기록이 없는 주소일 경우 수동으로 등록해야 합니다.")
            print("심볼명, 바이낸스 주소, 바이낸스 메모, 보낼 수량", send_to_bin_optimal_simbol, bin_address, bin_Memo, point_of_Withdrow_UP_amount_1)
            print("전송을 수동으로 완료하였으면 Y 를 입력할 것")
            cheak = str(input())
            if cheak == "Y":
                pass
            else:
                import warnings
                warnings.warn("전송 부분 오류", send_state_1)
                print(20)
                sys.exit()  ## 강제로 파이썬 종료 => 오류 반환
        #####################################################################################
        balance = binance.fetch_balance()  # 바이낸스 잔고 확인 (전송완료 확인때문에)#@@하지만 동시에 전송된다면..?
        return "send_up_to_bin", balance[send_to_bin_optimal_simbol]['free']

    except:  # 전송주문 실패
        statuses = ("업비트 => 바이낸스 전송주문 실패", send_state_1)
        if (len(statuses) != 0):
            clear_output(wait=True)
            display(statuses)
        return "step_1_1", "보내기 전 바이낸스잔고"


def send_up_to_bin_2(send_to_bin_optimal_simbol, point_of_Withdrow_UP_amount_1, bin_address, bin_Memo):  # 업비트에서 바이낸스 전송주문 요청
    send_state_1 = [""]

    can_withdrow_Decimal = 8

    Decimal_rounding, Decimal_rounding_dig = (0.1) ** int(can_withdrow_Decimal + 1), int(can_withdrow_Decimal)  # 소수점 라운딩
    point_of_Withdrow_UP_amount_1 = (point_of_Withdrow_UP_amount_1 // Decimal_rounding) * Decimal_rounding
    point_of_Withdrow_UP_amount_1 = round(point_of_Withdrow_UP_amount_1, Decimal_rounding_dig)

    try:
        send_state_1 = up_withdrow_request(send_to_bin_optimal_simbol, point_of_Withdrow_UP_amount_1, bin_address, bin_Memo)  # 전송주문 요청

        balance = binance.fetch_balance()  # 바이낸스 잔고 확인 (전송완료 확인때문에)#@@하지만 동시에 전송된다면..?
        return "send_up_to_bin", balance[send_to_bin_optimal_simbol]['free'], point_of_Withdrow_UP_amount_1

    except:  # 전송주문 실패
        statuses = ("업비트 => 바이낸스 전송주문 실패", send_state_1)
        if (len(statuses) != 0):
            clear_output(wait=True)
            display(statuses)
        return "step_1_1", "보내기 전 바이낸스잔고", point_of_Withdrow_UP_amount_1


def send_up_to_bin_3(send_to_bin_optimal_simbol, point_of_Withdrow_UP_amount_1, bin_address, bin_Memo, Bin_Spot_Minimum_Order_Size_a):  # 업비트에서 바이낸스 전송주문 요청
    send_state_1 = [""]
    Decimal_rounding = Bin_Spot_Minimum_Order_Size_a
    point_of_Withdrow_UP_amount_1 = (point_of_Withdrow_UP_amount_1 // Decimal_rounding) * Decimal_rounding
    try:
        send_state_1 = up_withdrow_request(send_to_bin_optimal_simbol, point_of_Withdrow_UP_amount_1, bin_address, bin_Memo)  # 전송주문 요청

        balance = binance.fetch_balance()  # 바이낸스 잔고 확인 (전송완료 확인때문에)#@@하지만 동시에 전송된다면..?
        return "send_up_to_bin", balance[send_to_bin_optimal_simbol]['free'], point_of_Withdrow_UP_amount_1

    except:  # 전송주문 실패
        statuses = ("업비트 => 바이낸스 전송주문 실패", send_state_1)
        if (len(statuses) != 0):
            clear_output(wait=True)
            display(statuses)
        return "step_1_1", "보내기 전 바이낸스잔고", point_of_Withdrow_UP_amount_1


# @@ 잔고 수량 확인하는 부분 평단가 고려 해야함.
# bin_fu_bid_price[a] 이거처럼 인덱스 가지는거 다변경해야함.
def send_up_to_bin_Completion(send_to_bin_optimal_simbol, before_send_to_bin_balace, point_of_Withdrow_UP_amount_1, point_of_buy_bin_fu_amount_1, Bin_Spot_Minimum_Order_Size_a):  # 업비트에서 바이낸스 전송완료?

    balance = binance.fetch_balance()

    # quotePrecision = 8
    # aa = before_send_to_bin_balace + point_of_Withdrow_UP_amount_1
    # Decimal_rounding, Decimal_rounding_dig = (0.1)**int(quotePrecision) , int(quotePrecision)# 소수점 라운딩
    # aa = (aa // Decimal_rounding) * Decimal_rounding
    # aa = round(aa , Decimal_rounding_dig - 1)

    quotePrecision = 8  ## @@ 옵션
    aa = before_send_to_bin_balace + point_of_Withdrow_UP_amount_1
    Decimal_rounding = Bin_Spot_Minimum_Order_Size_a
    aa = (aa // Decimal_rounding) * Decimal_rounding
    aa = round(aa, quotePrecision - 1)

    if (balance[send_to_bin_optimal_simbol]['free'] >= aa):
        return "send_up_to_bin_Completion", 0
    # before_send_to_bin_balace는 보내기 전 바이낸스 잔고

    bin_sym_names, bin_fu_ask_bid = bin_fu_ask_bid_info([send_to_bin_optimal_simbol])
    bin_fu_ask_price, bin_fu_ask_size = bin_fu_ask_info(bin_sym_names, bin_fu_ask_bid)  # 바-선 매수 호가창 1 3

    aa = client.futures_account()  # @@ 곂쳤을 수도 있으니 내 계좌 정보 불러와서 계산
    # next((item for item in aa['positions'] if item['symbol'] == send_to_bin_optimal_simbol + 'USDT'), None)
    future_leverage_ceil = int(next((item for item in aa['positions'] if item['symbol'] == send_to_bin_optimal_simbol + 'USDT'), None)['leverage'])
    point_of_buy_bin_fu_ticker_1 = float(next((item for item in aa['positions'] if item['symbol'] == send_to_bin_optimal_simbol + 'USDT'), None)['entryPrice'])

    if ((1 + (1 - bin_fu_ask_price[0] / point_of_buy_bin_fu_ticker_1) * future_leverage_ceil) < 0.2):  # 이 때 청산. 80% 위기 (-는 청산 1이상은 수익)
        before_send_up_to_bin_Completion_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])

        print(1 + (1 - bin_fu_ask_price[0] / point_of_buy_bin_fu_ticker_1) * future_leverage_ceil)
        try:
            result = request_client.post_order(symbol=send_to_bin_optimal_simbol + "USDT", side=OrderSide.BUY, ordertype=OrderType.MARKET, quantity=point_of_buy_bin_fu_amount_1)  # quantity수량.#Orderside sell 이면 판매
            PrintBasic.print_obj(result)
            #             state = ["warning"]
            time.sleep(2)
            after_send_up_to_bin_Completion_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])
            send_up_to_bin_Completion_bin_fu_usdt_asset = before_send_up_to_bin_Completion_bin_fu_usdt_asset - after_send_up_to_bin_Completion_bin_fu_usdt_asset  # == point_of_buy_bin_fu_amount_1* point_of_buy_bin_fu_ticker_1 / future_leverage_ceil + point_of_buy_bin_fu_amount_1 * point_of_buy_bin_fu_ticker_1 * bin_future_market_fee

            response = Telegramchat(
                "send_up_to_bin_Completion 청산 80% 위기 강제 종료" + str(send_up_to_bin_Completion_bin_fu_usdt_asset) + str(send_to_bin_optimal_simbol) + str(before_send_to_bin_balace) + str(point_of_Withdrow_UP_amount_1) + str(point_of_buy_bin_fu_amount_1) + str(Bin_Spot_Minimum_Order_Size_a))

            return "청산 80% 위기 포지션 강제 종료", send_up_to_bin_Completion_bin_fu_usdt_asset
        except:
            # 바이낸스 선물 시장가 롱 # @@ 이슈 진정 전까진 이걸로
            result = binance_fu.create_market_buy_order(symbol=send_to_bin_optimal_simbol + "/USDT", amount=point_of_buy_bin_fu_amount_1, )
            pprint.pprint(result)
            time.sleep(2)
            after_send_up_to_bin_Completion_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])
            send_up_to_bin_Completion_bin_fu_usdt_asset = before_send_up_to_bin_Completion_bin_fu_usdt_asset - after_send_up_to_bin_Completion_bin_fu_usdt_asset  # == point_of_buy_bin_fu_amount_1* point_of_buy_bin_fu_ticker_1 / future_leverage_ceil + point_of_buy_bin_fu_amount_1 * point_of_buy_bin_fu_ticker_1 * bin_future_market_fee

            response = Telegramchat(
                "send_up_to_bin_Completion 청산 80% 위기 강제 종료" + str(send_up_to_bin_Completion_bin_fu_usdt_asset) + str(send_to_bin_optimal_simbol) + str(before_send_to_bin_balace) + str(point_of_Withdrow_UP_amount_1) + str(point_of_buy_bin_fu_amount_1) + str(Bin_Spot_Minimum_Order_Size_a))

            return "청산 80% 위기 포지션 강제 종료", send_up_to_bin_Completion_bin_fu_usdt_asset

    #     time.sleep(0.4)  # @ 이거 없어도 됨.. 나중에 api 다시 생각
    statuses = ("업비트 => 바이낸스",
                send_to_bin_optimal_simbol,
                "전송 중", balance[send_to_bin_optimal_simbol]['free'],
                "현재시각", time.ctime(time.time()))

    if (len(statuses) != 0):
        clear_output(wait=True)
        display(statuses)
    return "send_up_to_bin", 0

# before_send_up_to_bin_Completion_fu_usdt = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])
# after_send_up_to_bin_Completion_fu_usdt = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])
# send_up_to_bin_Completion_fu_usdt = before_send_up_to_bin_Completion_fu_usdt - after_send_up_to_bin_Completion_fu_usdt


# before_send_up_to_bin_Completion_spot_usdt = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
# after_send_up_to_bin_Completion_spot_usdt = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
# send_up_to_bin_Completion_spot_usdt = before_send_up_to_bin_Completion_spot_usdt - after_send_up_to_bin_Completion_spot_usdt


############################################################################################################################################
def step_1_2(binance_asset, up_asset, sym_name, point_of_Withdrow_UP_amount_1, point_of_buy_UP_ticker_1, point_of_buy_bin_fu_ticker_1, future_leverage, Bin_Spot_Minimum_Order_Size_a, point_of_buy_bin_fu_amount_1, x1, y1, expect_x2, expect_y2, div_unit, bin_spot_market_fee, bin_future_market_fee,
             Usdt_1_1):
    # 헷징 종료 전 바이낸스 현물, 선물 지갑 달러잔고 확인
    before_step_1_2_bin_spot_usdt_asset = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
    before_step_1_2_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])
    Usdt = upbit_get_usd_krw()

    time.sleep(5)  # @@여기 정밀 조정

    balance = binance.fetch_balance()  # 이거지우기
    if (0 < (balance[sym_name]['free'] - point_of_Withdrow_UP_amount_1) * point_of_buy_UP_ticker_1 < (div_unit / 15)):
        Decimal_rounding = Bin_Spot_Minimum_Order_Size_a  # 주문가능 최소량
        order_amount_bin_spot = (balance[sym_name]['free'] // Decimal_rounding) * Decimal_rounding
    else:
        Decimal_rounding = Bin_Spot_Minimum_Order_Size_a  # 주문가능 최소량
        order_amount_bin_spot = (point_of_Withdrow_UP_amount_1 // Decimal_rounding) * Decimal_rounding
    #####

    bin_sym_names, bin_spot_ask_bid = bin_spot_ask_bid_info([sym_name])
    # bin_spot_ask_price, bin_spot_ask_size = bin_ask_info(bin_sym_names, bin_spot_ask_bid)  # 바-현 매수 호가창 2
    bin_spot_bid_price, bin_spot_bid_size = bin_bid_info(bin_sym_names, bin_spot_ask_bid)  # 바-현 매도 호가창 3

    bin_sym_names, bin_fu_ask_bid = bin_fu_ask_bid_info([sym_name])
    bin_fu_ask_price, bin_fu_ask_size = bin_fu_ask_info(bin_sym_names, bin_fu_ask_bid)  # 바-선 매수 호가창 1 3
    # bin_fu_bid_price, bin_fu_bid_size = bin_fu_bid_info(bin_sym_names, bin_fu_ask_bid)  # 바-선 매도 호가창 2 4

    # 2. 바이낸스 현물에서 매도 #예상수익 역프 : up_to_bin_pre_rate
    # x2 = order_amount_bin_spot * bin_spot_bid_price[0] * (1 - bin_spot_market_fee) * Usdt # @@ 이것으로 계간해야 더 정확?
    x2 = x1 * ((bin_spot_bid_price[0] * Usdt) / point_of_buy_UP_ticker_1) * (1 - bin_spot_market_fee)
    # 2.바이낸스 선물에서 공매수
    y2 = y1 * (1 + (1 - bin_fu_ask_price[0] / point_of_buy_bin_fu_ticker_1) * future_leverage) * (1 - bin_future_market_fee * future_leverage)  # 예상 평단가 bin_fu_bid_price[a]
    #     y2 = y1 * (bin_fu_bid_price[0] / point_of_buy_bin_fu_ticker_1) * (1 - bin_future_market_fee * future_leverage) / future_leverage  # 예상 평단가 bin_fu_bid_price[a]

    # 예상손해보다 크면 판매 하지 않고 대기함 #역프일시(전송후 바로 수익이 나면)바로 판매함 @@ 호가창 단위비교 로직 나중에 추가하기
    # 이 아래 if문에 전송시 예상 수익 비교 해서 수익이 크면 가는 코드 ? or 에상 손해가 1%이하면 그냥 파는 코드.. 음
    # option 1 ((x2 + y2)/(expect_x2 + expect_y2) > 1.001) or ((x2 + y2)/(expect_x2 + expect_y2) > 1.003)
    #     if((expect_x2 + expect_y2) <= (x2 + y2) or ((x1 + y1) <= (x2 + y2))):#@ 여기에 수익 좀더 보는 코드 추가..? ((x2 + y2)/(expect_x2 + expect_y2) > 1.003)
    if ((((expect_x2 + expect_y2) <= (x2 + y2) or ((x1 + y1) <= (x2 + y2))) and ((x2 + y2) / (expect_x2 + expect_y2) >= 1.00001)) or (0 < (x2 + y2) - (x1 + y1))):
        #         print("매도주문 하는 코드 넣기")

        # 2.바이낸스 & 업비트 포지션 종료
        # 잔고만큼 판매 주문 전송
        order = binance.create_market_sell_order(sym_name + '/USDT', order_amount_bin_spot)

        # 숏포지선 종료#주문신청 과 반대 포지션을 잡아서 포지션 종료.
        # 바이낸스 선물 시장가 롱(숏 종료) # @@ 이슈 진정 전까진 이걸로
        result = binance_fu.create_market_buy_order(symbol=sym_name + "/USDT", amount=point_of_buy_bin_fu_amount_1, )
        pprint.pprint(result)
        # result = request_client.post_order(symbol=sym_name + "USDT", side=OrderSide.BUY, ordertype=OrderType.MARKET,quantity=point_of_buy_bin_fu_amount_1)  # quantity수량.#Orderside sell 이면 판매
        print(order)
        # PrintBasic.print_obj(result)

        print("예상 손(익)해와의 차이", (x2 + y2) - (expect_x2 + expect_y2))
        print("역프인 경우(양수)", ((x2 + y2) - (x1 + y1)))
        print("실제 손해", (x2 + y2) - (binance_asset + up_asset))
        print("손해율", 1 - (y2 + x2) / (binance_asset + up_asset))

        # save_state[sicle].append(bin_spot_ask_price[0])
        # save_state[sicle].append(bin_fu_bid_price[0])
        # save_state[sicle].append(binance_asset + up_asset - (x2 + y2))
        # save_state[sicle].append(sym_name)

        time.sleep(3)

        # 헷징 종료 후 바이낸스 현물, 선물 지갑 달러잔고 확인
        after_step_1_2_bin_spot_usdt_asset = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
        after_step_1_2_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])

        step_1_2_bin_spot_usdt_asset = after_step_1_2_bin_spot_usdt_asset - before_step_1_2_bin_spot_usdt_asset
        step_1_2_bin_fu_usdt_asset = after_step_1_2_bin_fu_usdt_asset - before_step_1_2_bin_fu_usdt_asset

        # 혹시모를 위험 대비 , 이전에 있던 달러와 조회가 이상할 경우,x1,y1,x2,y2비교 까지해서 팔 때 볼 손해 어느정도 예측 후 보정치 10%
        if ((step_1_2_bin_spot_usdt_asset + step_1_2_bin_fu_usdt_asset) * 1.1 >= (y2 + x2)):
            print("다 팔았는데 이상한 상태 or 한쪽에서 수익이 20% 이상 난 상태, 10 %이상 손해본 상태?")
            return "다 팔았는데 이상한 상태 or 한쪽에서 수익이 20% 이상 난 상태, 10 %이상 손해본 상태?", step_1_2_bin_spot_usdt_asset, step_1_2_bin_fu_usdt_asset, after_step_1_2_bin_spot_usdt_asset, after_step_1_2_bin_fu_usdt_asset, before_step_1_2_bin_spot_usdt_asset, before_step_1_2_bin_fu_usdt_asset, x2, y2, Usdt

        return "step_1_2", step_1_2_bin_spot_usdt_asset, step_1_2_bin_fu_usdt_asset, after_step_1_2_bin_spot_usdt_asset, after_step_1_2_bin_fu_usdt_asset, before_step_1_2_bin_spot_usdt_asset, before_step_1_2_bin_fu_usdt_asset, x2, y2, Usdt

    # @@청산관련 .. 이 부분 좋게 바꿀만한 방법이 있을까?
    aa = client.futures_account()
    future_leverage_ceil = int(next((item for item in aa['positions'] if item['symbol'] == sym_name + 'USDT'), None)['leverage'])
    point_of_buy_bin_fu_ticker = float(next((item for item in aa['positions'] if item['symbol'] == sym_name + 'USDT'), None)['entryPrice'])

    if ((1 + (1 - bin_fu_ask_price[0] / point_of_buy_bin_fu_ticker) * future_leverage_ceil) < 0.2):  # 이 때 청산. 80% 위기 (-는 청산 1이상은 수익)

        order = binance.create_market_sell_order(sym_name + '/USDT', order_amount_bin_spot)

        result = binance_fu.create_market_buy_order(symbol=sym_name + "/USDT", amount=point_of_buy_bin_fu_amount_1, )
        pprint.pprint(result)

        # result = request_client.post_order(symbol=sym_name + "USDT", side=OrderSide.BUY, ordertype=OrderType.MARKET, quantity=point_of_buy_bin_fu_amount_1)  # quantity수량.#Orderside sell 이면 판매
        # PrintBasic.print_obj(result)
        print(order)
        print(1 + (1 - bin_fu_ask_price[0] / point_of_buy_bin_fu_ticker) * future_leverage_ceil)
        print("청산에 가까워짐 포지션 해제 하는 코드")

        time.sleep(3)

        # 헷징 종료 후 바이낸스 현물, 선물 지갑 달러잔고 확인
        after_step_1_2_bin_spot_usdt_asset = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
        after_step_1_2_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])

        step_1_2_bin_spot_usdt_asset = after_step_1_2_bin_spot_usdt_asset - before_step_1_2_bin_spot_usdt_asset
        step_1_2_bin_fu_usdt_asset = after_step_1_2_bin_fu_usdt_asset - before_step_1_2_bin_fu_usdt_asset

        # save_state[sicle].append(bin_spot_ask_price[0])
        # save_state[sicle].append(bin_fu_bid_price[0])
        # save_state[sicle].append(binance_asset + up_asset - (x2 + y2))
        # save_state[sicle].append(sym_name)

        # 혹시모를 위험 대비 , 이전에 있던 달러와 조회가 이상할 경우,x1,y1,x2,y2비교 까지해서 팔 때 볼 손해 어느정도 예측 후 보정치 10%
        if ((step_1_2_bin_spot_usdt_asset + step_1_2_bin_fu_usdt_asset) * 1.1 >= (y2 + x2)):
            print("다 팔았는데 이상한 상태 or 한쪽에서 수익이 20% 이상 난 상태, 10 %이상 손해본 상태?")
            return "다 팔았는데 이상한 상태 or 한쪽에서 수익이 20% 이상 난 상태, 10 %이상 손해본 상태?", step_1_2_bin_spot_usdt_asset, step_1_2_bin_fu_usdt_asset, after_step_1_2_bin_spot_usdt_asset, after_step_1_2_bin_fu_usdt_asset, before_step_1_2_bin_spot_usdt_asset, before_step_1_2_bin_fu_usdt_asset, x2, y2, Usdt

        return "step_1_2_청산에 가까워짐 포지션 해제 하는 코드", step_1_2_bin_spot_usdt_asset, step_1_2_bin_fu_usdt_asset, after_step_1_2_bin_spot_usdt_asset, after_step_1_2_bin_fu_usdt_asset, before_step_1_2_bin_spot_usdt_asset, before_step_1_2_bin_fu_usdt_asset, x2, y2, Usdt

    else:

        # 팔시점 아직 안나옴
        statuses = ("현 달러 가치", Usdt,
                    "step_1_1달러", Usdt_1_1,
                    "손익 비율(보정치 [1.001])", (x2 + y2) / (expect_x2 + expect_y2),
                    "예상 손해(익)와의 차이", (x2 + y2) - (expect_x2 + expect_y2),
                    "역프인 경우(양수)", ((x2 + y2) - (x1 + y1)),
                    "예상 금액(step_1_1에서 매도시) ", (expect_y2 + expect_x2) - (binance_asset + up_asset),
                    "실제 금액(매도시)", (x2 + y2) - (binance_asset + up_asset),  # @ 엄밀히는 틀림
                    "손해율", 1 - (y2 + x2) / (binance_asset + up_asset)  # @ 엄밀히는 틀림
                    #  expect_x2 + expect_y2, (x2 + y2),
                    # (x1 + y1), (x2 + y2),
                    # (x2 + y2) / (expect_x2 + expect_y2), 1.0003
                    )
        if (len(statuses) != 0):
            clear_output(wait=True)
            display(statuses)

        # save_state[sicle].append(bin_spot_ask_price[0])
        # save_state[sicle].append(bin_fu_bid_price[0])
        # save_state[sicle].append(binance_asset + up_asset - (x2 + y2))
        # save_state[sicle].append(sym_name)
    return "send_up_to_bin_Completion", 'step_1_2_bin_spot_usdt_asset', 'step_1_2_bin_fu_usdt_asset', 'after_step_1_2_bin_spot_usdt_asset', 'after_step_1_2_bin_fu_usdt_asset', 'before_step_1_2_bin_spot_usdt_asset', 'before_step_1_2_bin_fu_usdt_asset', 'x2', 'y2', 'Usdt_1_2'


def Capital_distribution(sym_name,step_1_2_bin_spot_usdt_asset,step_1_2_bin_fu_usdt_asset, before_step_1_2_bin_spot_usdt_asset, before_step_1_2_bin_fu_usdt_asset, bin_spot_market_fee, rest_step_1_1_bin_fu_usdt_asset, adjust_leverage, ban_list , up_market_fee, bin_future_market_fee):
    time.sleep(1)
    # @@ 아래 두개 before~~ 를 사용할 경우엔 Capital_distribution 에서 함수 두개를 덜 받아도 되지먼 api 호출 수는 2개 더 많게 됨
    before_Capital_distribution_bin_spot_usdt_asset = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
    before_Capital_distribution_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])

#     time.sleep(0.4)
    time.sleep(1)
    Usdt = upbit_get_usd_krw()
    ####단위들이 원화로 환산되어있음.
    # step_1_2_bin_spot_usdt_asset = step_1_2_bin_spot_usdt_asset #* Usdt
    # step_1_2_bin_fu_usdt_asset = step_1_2_bin_fu_usdt_asset #* Usdt

    second_using_asset = (step_1_2_bin_spot_usdt_asset + step_1_2_bin_fu_usdt_asset + rest_step_1_1_bin_fu_usdt_asset) * Usdt

    ##심볼명들 다시 거름#####################################

    sym_name = sym_intersection()  # 업비트 현물 , 바이낸스 현물 , 바이낸스 선물의 교집합을 가진 심볼명만 가져옴
    Usdt = upbit_get_usd_krw()  # 업비트에서 1달러당 환율 가져옴
    all_coin_info = client_spot.coin_info()  # 코인 정보를 전부 한번만 가져와서 저장함
    sym_name = delet_None_network(all_coin_info, sym_name)  # 코인 스스로 전송 불가능 한 코인은 제외(바이낸스 체인 ,bnb만 전송가능한코인)

    sym_name = list(set(sym_name) - set(ban_list))

    sym_name = del_bin_disable_withdraw(all_coin_info, sym_name)  # 바이낸스 출금 불가능 심볼 삭제
    sym_name = del_up_disable_deopsit(sym_name)  # 업비트 입금 불가능 심볼 삭제
    sym_name = del_bin_disable_deopsit(all_coin_info, sym_name)  # 바이낸스 입금 불가능 코인 삭제
    sym_name = del_up_disable_whthdraw(sym_name)  # 업비트 출금 불가능 심볼 삭제

    time.sleep(1)

    # @@여기서 바이낸스 자본은 원화??  ## step_1_2_bin_spot_usdt_asset or second_using_asset
    sym_name = remove_sym_name_2(all_coin_info, sym_name, Usdt, step_1_2_bin_spot_usdt_asset, 0.003/adjust_leverage, ban_list ,bin_spot_market_fee)  # 내 자본 대비 전송수수료(0.005)가 큰 코인 심볼명 삭제
    print("자본대비 쓸 수 있는 심볼 갯수", len(sym_name))

    up_withdrawfee, bin_withdrawfee = up_bin_withdraw_fee(sym_name, all_coin_info)  # 업비트 전송 수수료 , 바이낸스 전송 수수료
    # up_Min_Withdraw_Size, bin_Min_Withdraw_Size = up_bin_withdraw_Size(sym_name, all_coin_info)  # 업비트, 바이낸스 전송최소 가능량
    # Bin_Fu_Minimum_Order_Size = Bin_Minimum_FU_Order_Size(sym_name)  # 바이낸스 선물 최소 주문 가능량
    # Bin_Spot_Minimum_Order_Size = Bin_Minimum_Spot_Order_Size(sym_name)  # 바이낸스 현물 최소 주문가능량

    ##########전송후 값어치 변화가 아마도 비슷할거니까 수수료 만큼 현물에 더 비중을 두는 코드.###############################################
    # up_to_bin_pre_rate = []
    # up_to_bin_pre_rate_append = up_to_bin_pre_rate.append
    bin_to_up_pre_rate = []
    bin_to_up_pre_rate_append = bin_to_up_pre_rate.append
    # up_withdrawfee_by_asset = []
    # up_withdrawfee_by_asset_append = up_withdrawfee_by_asset.append
    bin_withdrawfee_by_asset = []
    bin_withdrawfee_by_asset_append = bin_withdrawfee_by_asset.append

    # 호가창 정보 가져옴
    up_sym_names, up_spot_ask_bid = up_spot_ask_bid_info(sym_name)
    # up_ask_price, up_ask_size = up_ask_info(up_sym_names, up_spot_ask_bid)  # 업비트 매수 호가창 1
    up_bid_price, up_bid_size = up_bid_info(up_sym_names, up_spot_ask_bid)  # 업비트 매도 호가창 4

    bin_sym_names, bin_spot_ask_bid = bin_spot_ask_bid_info(sym_name)
    bin_spot_ask_price, bin_spot_ask_size = bin_ask_info(bin_sym_names, bin_spot_ask_bid)  # 바-현 매수 호가창 3
    # bin_spot_bid_price, bin_spot_bid_size = bin_bid_info(bin_sym_names, bin_spot_ask_bid)  # 바-현 매도 호가창 2

    # bin_sym_names, bin_fu_ask_bid = bin_fu_ask_bid_info(sym_name)
    # bin_fu_ask_price, bin_fu_ask_size = bin_fu_ask_info(bin_sym_names, bin_fu_ask_bid)  # 바-선 매수 호가창 2 4
    # bin_fu_bid_price, bin_fu_bid_size = bin_fu_bid_info(bin_sym_names, bin_fu_ask_bid)  # 바-선 매도 호가창 1 3

    for i in range(len(sym_name)):
        #     up_to_bin_pre_rate.append(up_bid_price[i]/(bin_spot_ask_price[i]*Usdt)) # 역프 or 바낸 전송시 예상 손수익 %
        #     bin_to_up_pre_rate.append((bin_spot_bid_price[i]*Usdt)/up_ask_price[i]) # 김프 or 업비트 전송시 예상 손수익 %

        # 프리미엄들(역프,김프)
        #     up_to_bin_pre_rate_append((bin_spot_bid_price[i] * Usdt) / up_ask_price[i])  # 역프 or 바낸 전송시 예상 손수익 %(김프시 손해)
        bin_to_up_pre_rate_append(up_bid_price[i] / (bin_spot_ask_price[i] * Usdt))  # 김프 or 업비트 전송시 예상 손수익 %(김프시 수익)

        # 자본대비 수수료 오직 비율로만 따짐.
        #     up_withdrawfee_by_asset_append(up_to_bin_pre_rate[i] - ((up_ask_price[i] * up_withdrawfee[i]) / up_asset))  # 내 자본 대비 전송수수료를 포함하여 가장 좋은 최적의 값 서칭
        bin_withdrawfee_by_asset_append(bin_to_up_pre_rate[i] - ((bin_spot_ask_price[i] * bin_withdrawfee[i]) / step_1_2_bin_spot_usdt_asset))  # 바이낸스 선물에서 매수 할거니 매도호가창조회
    # 나중에 a는 변수명 최적_to_bin으로 바꾸기?b도
    # (업 => 바)전송시 최적 코인 인덱스 번호(a) , (바 => 업)전송 시 최적 코인 인덕스 번호(b)
    # a = up_withdrawfee_by_asset.index(max(up_withdrawfee_by_asset))  # 리스트에서 가장 큰 값 뽑음(업 => 바 가장 큰 값 인덱스) @@맞지? 현재 김프역프 왔다리 갓다리 하니까
    b = bin_withdrawfee_by_asset.index(max(bin_withdrawfee_by_asset))  # 리스트에서 가장 큰 값 뽑음(바 => 업 가장 큰 값 인덱스)
    # 여기서 김프또한 손해 보는 비율로 가져온것이기 떄문에 이전 코드와는 좀 다름.

    ###################################################################################################

    per = find_max_per(second_using_asset, sym_name, bin_spot_ask_price, bin_withdrawfee)
    bin_spot_usdt, bin_fu_Usdt = Adjusting_second_using_asset(second_using_asset, up_market_fee, bin_spot_market_fee, bin_future_market_fee, per, adjust_leverage)
    # future_leverage = 1

    bin_spot_usdt = bin_spot_usdt / Usdt
    bin_fu_Usdt = bin_fu_Usdt / Usdt

    # print(bin_spot_usdt, bin_fu_Usdt)

    ###################################################################################################
    # Decimal_rounding = 0.00000001  # (바이낸스 현물,선물 지갑끼리 이동 가능 최소량)
    # @ option 잘 안될 경우 아래 위에 주석처리 후 식 사용##########
    can_send_Decimal = 8
    Decimal_rounding, Decimal_rounding_dig = (0.1) ** int(can_send_Decimal + 1), int(can_send_Decimal)  # 소수점 라운딩
    #
    bin_spot_usdt = (bin_spot_usdt // Decimal_rounding) * Decimal_rounding
    bin_fu_Usdt = (bin_fu_Usdt // Decimal_rounding) * Decimal_rounding
    #
    need_spot_Usdt = (((before_Capital_distribution_bin_spot_usdt_asset - step_1_2_bin_spot_usdt_asset) + bin_spot_usdt) // Decimal_rounding) * Decimal_rounding
    need_fu_Usdt = (((before_Capital_distribution_bin_fu_usdt_asset - (step_1_2_bin_fu_usdt_asset + rest_step_1_1_bin_fu_usdt_asset)) + bin_fu_Usdt) // Decimal_rounding) * Decimal_rounding
    # need_fu_Usdt = ((((before_Capital_distribution_bin_fu_usdt_asset - step_1_2_bin_fu_usdt_asset + rest_step_1_1_bin_fu_usdt_asset)) + bin_fu_Usdt) // Decimal_rounding) * Decimal_rounding

    # @ option 잘 안될 경우 아래 위에 주석처리 후 식 사용##########

    bin_spot_usdt = round((bin_spot_usdt // Decimal_rounding) * Decimal_rounding, Decimal_rounding_dig)
    # can_send_Decimal = 8
    # Decimal_rounding, Decimal_rounding_dig = (0.1) ** int(can_send_Decimal), int(can_send_Decimal)  # 소수점 라운딩
    bin_fu_Usdt = round((bin_fu_Usdt // Decimal_rounding) * Decimal_rounding, Decimal_rounding_dig)
    # can_send_Decimal = 8
    # Decimal_rounding, Decimal_rounding_dig = (0.1) ** int(can_send_Decimal), int(can_send_Decimal)  # 소수점 라운딩
    need_spot_Usdt = round((need_spot_Usdt // Decimal_rounding) * Decimal_rounding, Decimal_rounding_dig)
    # can_send_Decimal = 8
    # Decimal_rounding, Decimal_rounding_dig = (0.1) ** int(can_send_Decimal), int(can_send_Decimal)  # 소수점 라운딩
    need_fu_Usdt = round((need_fu_Usdt // Decimal_rounding) * Decimal_rounding, Decimal_rounding_dig)

    ###################################################################################################
    # 지갑 달러잔고 => 선물지갑으로 전부 보낸후 원래있던 달러만큼 + 추가로 쓸 자본(바=>업)만큼만 현물로 보냄
    while True:  # 서버 응답 오류때문에 만듦
        bin_cash_ass_Usdt = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
        print(bin_cash_ass_Usdt, "현물지갑 달러 잔고 확인")
        # 현재 달러 계좌조회로 바꾸는 로직은쓰지 않았음.@@@@
        time.sleep(4) # @@ 이부분이 문젠가? => 달러 전송이 조금 느림..;
        try:
            ret = client.futures_account_transfer(asset="USDT", amount=bin_cash_ass_Usdt, type=1, )  # 타입1:바현=>바선
        except:
            pass
        time.sleep(4)
        try:
            ret = client.futures_account_transfer(asset="USDT", amount=need_spot_Usdt, type=2, )  # 타입2:바선=>바현
        except:
            pass
        time.sleep(4)
        bin_fu_ass = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])
        print(bin_fu_ass, "선물지갑 달러 잔고 확인")
        time.sleep(4)
        bin_cash_ass_Usdt = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
        print(bin_cash_ass_Usdt, "현물지갑 달러 잔고 확인")

        if (bin_cash_ass_Usdt >= need_spot_Usdt and bin_fu_ass >= need_fu_Usdt):
            return 'Capital_distribution', bin_spot_usdt, bin_fu_Usdt, second_using_asset
        else:
            print("자본분배 중 바이낸스 서버 문제")

        if (need_spot_Usdt < 0):
            print("바이낸스 현물자본 오류")

        time.sleep(3)


def step_2_1_sym_name(Second_Use_Bin_Spot_Usdt, Second_Use_Bin_Fu_Usdt, ban_list, bin_spot_market_fee):
    sym_name = sym_intersection()
    Usdt = upbit_get_usd_krw()
    all_coin_info = client_spot.coin_info()

    sym_name = delet_None_network(all_coin_info, sym_name)  # 코인 스스로 전송 불가능 한 코인은 제외(바이낸스 체인 ,bnb만 전송가능한코인)
    sym_name = list(set(sym_name) - set(ban_list))
    sym_name = del_bin_disable_withdraw(all_coin_info, sym_name)  # 바이낸스 출금 불가능 심볼 삭제
    sym_name = del_up_disable_deopsit(sym_name)  # 업비트 입금 불가능 심볼 삭제

    sym_name = remove_sym_name_2(all_coin_info, sym_name, Usdt, Second_Use_Bin_Spot_Usdt, 0.003, ban_list, bin_spot_market_fee)  # 내 자본 대비 전송수수료(0.005)가 큰 코인 심볼명 삭제
    print("자본대비 쓸 수 있는 심볼 갯수", len(sym_name))

    future_leverage = Second_Use_Bin_Spot_Usdt / Second_Use_Bin_Fu_Usdt
    future_leverage_ceil = math.ceil(future_leverage)

    for i in range(len(sym_name)):
        bin_fu_setting(sym_name[i], future_leverage_ceil)

    ##
    aa = client.futures_account()
    del_list = []
    del_list_append = del_list.append
    for i in range(len(sym_name)):
        if (future_leverage_ceil > int(next((item for item in aa['positions'] if item['symbol'] == sym_name[i] + 'USDT'), None)['leverage'])):
            #         print(int(next((item for item in aa['positions'] if item['symbol'] == sym_name[i] + 'USDT'), None)['leverage']))
            #         print(sym_name[i])
            del_list_append(sym_name[i])

    sym_name = list(set(sym_name) - set(del_list))
    ##

    # aa = client.futures_account()
    # for i in range(len(sym_name)):
    #     if (future_leverage_ceil > int(next((item for item in aa['positions'] if item['symbol'] == sym_name[i] + 'USDT'), None)['leverage'])):
    #         print('레버리지변환 오류 프로그램 실행 멈추고 확인 바람')
    #         sys.exit()  ## 강제로 파이썬 종료

    return sym_name, future_leverage, future_leverage_ceil

def step_2_1(sym_name, Second_Use_Bin_Spot_Usdt, Second_Use_Bin_Fu_Usdt, x1, y1, x2, y2, second_using_asset, Usdt_1_1, before_future_leverage_ceil , bin_spot_market_fee, bin_future_market_fee, up_market_fee, div_unit,want_premium_step_1_1, want_premium_step_2_1, step_1_1_up_krw_asset, step_1_1_bin_fu_usdt_asset, rest_step_1_1_bin_fu_usdt_asset):  # 바 => 업 보낼 코인 서칭 및 헷징(콘탱코)

    before_step_2_1_bin_spot_usdt_asset = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
    before_step_2_1_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])

    can_profit_preium = ((1 + want_premium_step_2_1 / 100) / (1 - want_premium_step_1_1 / 100) - 1) * 100
    Using_asset = step_1_1_up_krw_asset + (step_1_1_bin_fu_usdt_asset + rest_step_1_1_bin_fu_usdt_asset) * Usdt_1_1

    if (Second_Use_Bin_Spot_Usdt > Second_Use_Bin_Fu_Usdt):  # 업비트 자본이 큰 경우
        future_leverage = Second_Use_Bin_Spot_Usdt / Second_Use_Bin_Fu_Usdt
    else:  # 바이낸스 자본이 더 큰경우 # 바이낸스 자본비율이
        print('자본배율이상함')
        sys.exit()

    # if (future_leverage != 1):  # @ 바이낸스 자본과 업비트 자본의 비율이 2배 이상이 될 경우.
    #     if (Second_Use_Bin_Spot_Usdt < Second_Use_Bin_Fu_Usdt):  # 바이낸스 자본이 더 큰 경우 @@주로 김프니까(역프는..)이 경우는 그냥 업비트 자본 따라가는게 맞겠지..?
    #         Second_Use_Bin_Fu_Usdt = Second_Use_Bin_Spot_Usdt
    #     elif (Second_Use_Bin_Fu_Usdt <= Second_Use_Bin_Spot_Usdt):  # 김프의 경우 2배차이가 나기 시작하면
    #         Second_Use_Bin_Fu_Usdt = Second_Use_Bin_Fu_Usdt  # * future_leverage
    #         Second_Use_Bin_Spot_Usdt = Second_Use_Bin_Fu_Usdt * future_leverage  # 이렇게 함으로 써 같은 비율..?
    # elif (Second_Use_Bin_Spot_Usdt < Second_Use_Bin_Fu_Usdt):  # 작은 자본의 가격을 따라간다.(레버리지 1일때)
    #     Second_Use_Bin_Fu_Usdt = Second_Use_Bin_Spot_Usdt
    # elif (Second_Use_Bin_Fu_Usdt <= Second_Use_Bin_Spot_Usdt):
    #     Second_Use_Bin_Spot_Usdt = Second_Use_Bin_Fu_Usdt

    Second_Using_asset = Second_Use_Bin_Spot_Usdt + Second_Use_Bin_Fu_Usdt

    future_leverage_ceil = math.ceil(future_leverage)
    if (before_future_leverage_ceil < future_leverage_ceil):
        for i in range(len(sym_name)):
            bin_fu_setting(sym_name[i], future_leverage_ceil)
    else:
        pass

    bin_fu_previous_ticker_list = []
    bin_fu_previous_ticker_list_append = bin_fu_previous_ticker_list.append
    bin_fu_previous_amount_list = []
    bin_fu_previous_amount_list_append = bin_fu_previous_amount_list.append

    bin_fu_position_info = client.futures_account()  # 포지션 정보 가져옴
    for i in range(len(sym_name)):
        try:
            bin_fu_previous_ticker, bin_fu_previous_amount = bin_fu_avg_buy_price(sym_name[i], bin_fu_position_info)

        except:
            bin_fu_previous_ticker = 0
            bin_fu_previous_amount = 0
        bin_fu_previous_ticker_list_append(bin_fu_previous_ticker)
        bin_fu_previous_amount_list_append(bin_fu_previous_amount)

    time.sleep(0.4)
    # time.sleep(5)

    # bin_spot_usdt = Second_Use_Bin_Spot_Usdt
    # bin_fu_usdt = Second_Use_Bin_Fu_Usdt
    Usdt = upbit_get_usd_krw()
    all_coin_info = client_spot.coin_info()

    up_withdrawfee, bin_withdrawfee = up_bin_withdraw_fee(sym_name, all_coin_info)  # 업비트 전송 수수료 , 바이낸스 전송 수수료
    up_Min_Withdraw_Size, bin_Min_Withdraw_Size = up_bin_withdraw_Size(sym_name, all_coin_info)  # 업비트, 바이낸스 전송최소 가능량
    Bin_Fu_Minimum_Order_Size = Bin_Minimum_FU_Order_Size(sym_name)  # 바이낸스 선물 최소 주문 가능량
    Bin_Spot_Minimum_Order_Size = Bin_Minimum_Spot_Order_Size(sym_name)  # 바이낸스 현물 최소 주문가능량

    # up_to_bin_pre_rate = []
    # up_to_bin_pre_rate_append = up_to_bin_pre_rate.append
    bin_to_up_pre_rate = []
    bin_to_up_pre_rate_append = bin_to_up_pre_rate.append
    # up_withdrawfee_by_asset = []
    # up_withdrawfee_by_asset_append = up_withdrawfee_by_asset.append
    bin_withdrawfee_by_asset = []
    bin_withdrawfee_by_asset_append = bin_withdrawfee_by_asset.append

    # 호가창 정보 가져옴
    up_sym_names, up_spot_ask_bid = up_spot_ask_bid_info(sym_name)
    # up_ask_price, up_ask_size = up_ask_info(up_sym_names, up_spot_ask_bid)  # 업비트 매수 호가창 1
    up_bid_price, up_bid_size = up_bid_info(up_sym_names, up_spot_ask_bid)  # 업비트 매도 호가창 4

    bin_sym_names, bin_spot_ask_bid = bin_spot_ask_bid_info(sym_name)
    bin_spot_ask_price, bin_spot_ask_size = bin_ask_info(bin_sym_names, bin_spot_ask_bid)  # 바-현 매수 호가창 3
    # bin_spot_bid_price, bin_spot_bid_size = bin_bid_info(bin_sym_names, bin_spot_ask_bid)  # 바-현 매도 호가창 2

    bin_sym_names, bin_fu_ask_bid = bin_fu_ask_bid_info(sym_name)
    bin_fu_ask_price, bin_fu_ask_size = bin_fu_ask_info(bin_sym_names, bin_fu_ask_bid)  # 바-선 매수 호가창 2 4
    bin_fu_bid_price, bin_fu_bid_size = bin_fu_bid_info(bin_sym_names, bin_fu_ask_bid)  # 바-선 매도 호가창 1 3

    for i in range(len(sym_name)):
        #     up_to_bin_pre_rate.append(up_bid_price[i]/(bin_spot_ask_price[i]*Usdt)) # 역프 or 바낸 전송시 예상 손수익 %
        #     bin_to_up_pre_rate.append((bin_spot_bid_price[i]*Usdt)/up_ask_price[i]) # 김프 or 업비트 전송시 예상 손수익 %

        # 프리미엄들(역프,김프)
        #     up_to_bin_pre_rate_append((bin_spot_bid_price[i] * Usdt) / up_ask_price[i])  # 역프 or 바낸 전송시 예상 손수익 %(김프시 손해)
        bin_to_up_pre_rate_append(up_bid_price[i] / (bin_spot_ask_price[i] * Usdt))  # 김프 or 업비트 전송시 예상 손수익 %(김프시 수익)

        # 자본대비 수수료 오직 비율로만 따짐.
        #     up_withdrawfee_by_asset_append(up_to_bin_pre_rate[i] - ((up_ask_price[i] * up_withdrawfee[i]) / up_asset))  # 내 자본 대비 전송수수료를 포함하여 가장 좋은 최적의 값 서칭
        bin_withdrawfee_by_asset_append(bin_to_up_pre_rate[i] - ((bin_spot_ask_price[i] * bin_withdrawfee[i]) / Second_Use_Bin_Spot_Usdt))  # 바이낸스 선물에서 매수 할거니 매도호가창조회

    # 나중에 a는 변수명 최적_to_bin으로 바꾸기?b도
    # (업 => 바)전송시 최적 코인 인덱스 번호(a) , (바 => 업)전송 시 최적 코인 인덕스 번호(b)
    # a = up_withdrawfee_by_asset.index(max(up_withdrawfee_by_asset))  # 리스트에서 가장 큰 값 뽑음(업 => 바 가장 큰 값 인덱스) @@맞지? 현재 김프역프 왔다리 갓다리 하니까
    b = bin_withdrawfee_by_asset.index(max(bin_withdrawfee_by_asset))  # 리스트에서 가장 큰 값 뽑음(바 => 업 가장 큰 값 인덱스)
    # 여기서 김프또한 손해 보는 비율로 가져온것이기 떄문에 이전 코드와는 좀 다름.

    # 3. 바이낸스 현물 구매주문######################################################################################
#     bin_spot_Usdt_Send = Second_Use_Bin_Spot_Usdt * (1 - (0.003 + bin_spot_market_fee)) # 바이낸스 현물 시장가 수수료 #@@ option
    bin_spot_Usdt_Send = Second_Use_Bin_Spot_Usdt * (1 - bin_spot_market_fee) # 바이낸스 현물 시장가 수수료 # @@ option
    send_to_up_quantity = bin_spot_Usdt_Send / bin_spot_ask_price[b]  # 바이낸스 업비트로 보낼 달러 / 티커 가격 = 수량


    Decimal_rounding = Bin_Spot_Minimum_Order_Size[b]
    bin_spot_to_up_can_order_amount = (send_to_up_quantity // Decimal_rounding) * Decimal_rounding
    # bin_spot_to_up_can_order_amount = round(bin_spot_to_up_can_order_amount, 8) # @@ 안될경우 주석처리 풀어보기

    if (Decimal_rounding == bin_withdrawfee[b]): # 속도가 느릴 것 같으면.. 밑에 else 쓰자
        bin_withdrow_fee_Max = Decimal_rounding
    else: # 몫 + 1로 비슷하게 따라가게 함!
        bin_withdrow_fee_Max = ((bin_withdrawfee[b] // Decimal_rounding) + 1) * Decimal_rounding

    ###############################################################################################################

    # 3. 바이낸스 선물 주문############################################################################################

    # asset_symbol_quantity = Second_Use_Bin_Fu_Usdt  / bin_fu_bid_price[b]
    # asset_symbol_quantity = asset_symbol_quantity * (1 - bin_future_market_fee * future_leverage)* future_leverage

    # Decimal_rounding, Decimal_rounding_dig = Bin_Fu_Minimum_Order_Size[b] + 1, 8
    # bin_fu_can_order_send_to_up_optimal_symbol_quantity = (asset_symbol_quantity // Decimal_rounding) * Decimal_rounding
    # bin_fu_can_order_send_to_up_optimal_symbol_quantity = round(bin_fu_can_order_send_to_up_optimal_symbol_quantity, Decimal_rounding_dig)
    ################################################################################################################

    Decimal_rounding, Decimal_rounding_dig = Bin_Fu_Minimum_Order_Size[b] + 1, 8
    bin_fu_can_order_send_to_up_optimal_symbol_quantity = (bin_spot_to_up_can_order_amount // Decimal_rounding) * Decimal_rounding
    bin_fu_can_order_send_to_up_optimal_symbol_quantity = round(bin_fu_can_order_send_to_up_optimal_symbol_quantity, Decimal_rounding_dig)
    ################################################################################################################

    bin_spot_to_up_can_order_amount = round(bin_spot_to_up_can_order_amount + bin_withdrow_fee_Max, 8)

    # 다른 step에선 adjust_leverage 가 아닌 future_leverage가 맞을것.

    # 3.바이낸스 현물 구매 ask #예상수익 김프 : up_to_bin_pre_rate #업비트 전송 금액
    x3 = (bin_spot_to_up_can_order_amount - bin_withdrow_fee_Max) * bin_spot_ask_price[b] * Usdt #* (1 - bin_spot_market_fee)

    # 3.바이낸스 선물 공매도 bid #바이낸스 포지션 금액
    y3 = (bin_fu_can_order_send_to_up_optimal_symbol_quantity * bin_fu_bid_price[b] / future_leverage) * Usdt

    # 4.업비트 현물에서 매도 bid
    # = ((bin_spot_to_up_can_order_amount - bin_withdrow_fee_Max) * up_bid_price[b] * (1 - up_market_fee))
    x4 = x3 * (up_bid_price[b] / (bin_spot_ask_price[b] * Usdt)) * (1 - up_market_fee)

    # 4.바이낸스 선물에서 공매수 ask
    #(point_of_buy_bin_fu_ticker_2 * point_of_buy_bin_fu_amount_2 * (1 + (1 - bin_fu_ask_price[0] / point_of_buy_bin_fu_ticker_2) * future_leverage) * (1 - bin_future_market_fee * future_leverage))/future_leverage*Usdt
    y4 = y3 * (1 + (1 - bin_fu_ask_price[b] / bin_fu_bid_price[b]) * future_leverage) * (1 - bin_future_market_fee * future_leverage)  # 예상 평단가 bin_fu_bid_price[b]

    if ((((x4 + y4) / Using_asset - 1) > want_premium_step_2_1) and ((x4 + y4) > Using_asset) and (bin_withdrawfee_by_asset[b] - 1 > can_profit_preium) and (x4 / (bin_spot_to_up_can_order_amount * bin_spot_ask_price[b] * Usdt) - 1 > can_profit_preium) and ((x4 + y4) / (Second_Using_asset * Usdt) - 1 >  want_premium_step_2_1)) or (((x4 + y4) / Using_asset - 1) > 0.025):
        # @@ 정확히 보려면 수수료까지..
        # if(bin_spot_to_up_can_order_amount * bin_spot_ask_price[b] < Second_Use_Bin_Spot_Usdt): ## @@ 나중에 잘되면 이거 주석 풀어도 될듯
        if(bin_spot_to_up_can_order_amount * bin_spot_ask_price[b] < Second_Use_Bin_Spot_Usdt) and (bin_fu_can_order_send_to_up_optimal_symbol_quantity * bin_fu_bid_price[b] < Second_Use_Bin_Fu_Usdt * future_leverage_ceil):


            try:

                result = request_client.post_order(symbol=sym_name[b] + "USDT", side=OrderSide.SELL,
                                                   ordertype=OrderType.MARKET,
                                                   quantity=bin_fu_can_order_send_to_up_optimal_symbol_quantity)  # quantity수량.#Orderside sell 이면 판매
                PrintBasic.print_obj(result)


            except:
                #         3.바이낸스 선물 주문
                #         주문신청                             # 심볼            #sell 이면 숏 buy면 롱     # 시장가 거래         # 몇개 살것인지 (여기를 더 고민 ,잔고 또는 자본에 맞춰서 구매하게 만들어야함)
                # 바이낸스 선물 시장가 숏 # @@ 이슈 진정 전까진 이걸로
                result = binance_fu.create_market_sell_order(symbol=sym_name[b] + "/USDT", amount=bin_fu_can_order_send_to_up_optimal_symbol_quantity, )
                pprint.pprint(result)

            #         3. 바이낸스 현물 주문
            order = binance.create_market_buy_order(sym_name[b] + '/USDT', bin_spot_to_up_can_order_amount)
            print(order)

                # # 지정가 주문
                # order = binance.create_limit_buy_order(symbol=sym_name[b] + "/USDT",
                #                                        amount=bin_spot_to_up_can_order_amount,
                #                                        price=bin_spot_ask_price[b])
                # # 지정가 거래
                # result = request_client.post_order(symbol=sym_name[b] + "USDT", side=OrderSide.SELL,
                #                                    ordertype=OrderType.LIMIT,
                #                                    quantity=bin_fu_can_order_send_to_up_optimal_symbol_quantity,
                #                                    timeInForce="GTC",
                #                                    price=bin_fu_bid_price[b])
                # pprint.pprint(order)
                # PrintBasic.print_obj(result)
                # # 주문이 전부 끝날 때 까지 대기.
                # while True:  # @@ 이부분 애매한게 주문수량이 소수점으로 조금더  들어감
                #     # @@ 사실 지정가는 안긁히면 매우 위험한 방법.. 예를들어 바이낸스는 모두 긁히고 업비트는 하나도 안긁힐 경우 큰일난다.
                #
                #     balance = binance.fetch_balance()
                #
                #     cheak_amount_1 = balance[sym_name[b]]["free"]
                #     cheak_amount_2 = bin_spot_to_up_can_order_amount
                #     cheak_amount_3 = float(next((item for item in client.futures_account()['positions'] if
                #                                  item['symbol'] == sym_name[b] + "USDT"), None)['positionAmt'])
                #     cheak_amount_4 = bin_fu_can_order_send_to_up_optimal_symbol_quantity
                #
                #     statuses = ("바-현 : 주문완료량 / 주문량", cheak_amount_1, "/", cheak_amount_2,
                #                 "바-선 : 주문완료량 / 주문량", cheak_amount_3, "/", cheak_amount_4,
                #                 "현재시각", time.ctime(time.time())
                #                 )
                #
                #     if ((cheak_amount_1 >= cheak_amount_2) and (cheak_amount_3 == cheak_amount_4)):
                #         print("모든 수량 포지션 진입")
                #
                #     if (len(statuses) != 0):
                #         clear_output(wait=True)
                #         display(statuses)
                #
                #     time.sleep(6)
                # pass
            time.sleep(1)
            # 가상의 경우
            # point_of_buy_bin_spot_ticker_2 = bin_spot_ask_price[b]
            # point_of_buy_bin_spot_amount_2 = bin_spot_to_up_can_order_amount
            # point_of_buy_bin_fu_ticker_2 = bin_fu_bid_price[b]
            # point_of_buy_bin_fu_amount_2 = bin_fu_can_order_send_to_up_optimal_symbol_quantity

            try:  # 시장가 주문의 경우
                point_of_buy_bin_spot_ticker_2 = order["average"]
                point_of_buy_bin_spot_amount_2 = order["amount"] - order['fee']['cost']
            except:  # 지정가 주문의 경우
                point_of_buy_bin_spot_ticker_2 = bin_spot_ask_price[b]  # 이부분 bin_spot_bid_price이게 맞을거
                point_of_buy_bin_spot_amount_2 = bin_spot_to_up_can_order_amount

            bin_fu_position_info = client.futures_account()
            point_of_buy_bin_fu_ticker_2, point_of_buy_bin_fu_amount_2 = bin_fu_avg_buy_price(sym_name[b], bin_fu_position_info)

            if (bin_fu_previous_ticker_list[b] != 0):  # 이전에 구매한 코인이 아니라면(평단가는0 이 아님)
                bin_fu_previous_ticker, bin_fu_previous_amount = bin_fu_previous_ticker_list[b], bin_fu_previous_amount_list[b]  # 이전 평단가,수량
                bin_fu_now_ticker, bin_fu_now_amount = bin_fu_avg_buy_price(sym_name[b], bin_fu_position_info)  # 이후 평단가,수량
                # (기존 평단가 * 기존 개수) + (point_of_buy_bin_spot_ticker_2  * point_of_buy_bin_spot_amount_2)/(모든 개수) = 바뀐평단가
                point_of_buy_bin_fu_amount_2 = bin_fu_now_amount - bin_fu_previous_amount
                point_of_buy_bin_fu_ticker_2 = ((bin_fu_now_ticker * bin_fu_now_amount) - (bin_fu_previous_amount * bin_fu_previous_ticker)) / (point_of_buy_bin_fu_amount_2)

            print("바-현 해당 심볼 평단가", point_of_buy_bin_spot_ticker_2)
            print("바-현 해당 심볼 개수", point_of_buy_bin_spot_amount_2)

            print("바-선 코인 심볼 평단가", point_of_buy_bin_fu_ticker_2)
            print("바-선 코인 심볼 개수", point_of_buy_bin_fu_amount_2)

            print("3. 바-현 자본 사용량", point_of_buy_bin_spot_amount_2 * point_of_buy_bin_spot_ticker_2 * Usdt)
            print("3. 바-선 자본 사용량", point_of_buy_bin_fu_ticker_2 * point_of_buy_bin_fu_amount_2 * Usdt)

            # 3.바이낸스 현물 구매 ask #예상수익 김프 : up_to_bin_pre_rate #업비트 전송 금액
            x3 = (point_of_buy_bin_spot_amount_2 - bin_withdrow_fee_Max) * point_of_buy_bin_spot_ticker_2 * Usdt  # * (1 - bin_spot_market_fee)

            # 3.바이낸스 선물 공매도 bid #바이낸스 포지션 금액
            y3 = (point_of_buy_bin_fu_amount_2 * point_of_buy_bin_fu_ticker_2 / future_leverage) * Usdt

            # 4.업비트 현물에서 매도 bid
            # = ((bin_spot_to_up_can_order_amount - bin_withdrow_fee_Max) * up_bid_price[b] * (1 - up_market_fee))
            expect_x4 = x3 * (up_bid_price[b] / (point_of_buy_bin_spot_ticker_2 * Usdt)) * (1 - up_market_fee)

            # 4.바이낸스 선물에서 공매수 ask
            # (point_of_buy_bin_fu_ticker_2 * point_of_buy_bin_fu_amount_2 * (1 + (1 - bin_fu_ask_price[0] / point_of_buy_bin_fu_ticker_2) * future_leverage) * (1 - bin_future_market_fee * future_leverage))/future_leverage*Usdt
            expect_y4 = y3 * (1 + (1 - bin_fu_ask_price[b] / point_of_buy_bin_fu_ticker_2) * future_leverage) * (1 - bin_future_market_fee * future_leverage)  # 예상 평단가 bin_fu_bid_price[b]

            print("예상 x4, y4", (expect_y4, expect_x4))
            # print("예상 수익(수수료,전송최소량 다해서)", (expect_y4 + expect_x4) - (binance_asset + up_asset))
            # print("예상 수익율(수수료,전송최소량 다해서)", (expect_y4 + expect_x4) / (binance_asset + up_asset))

            time.sleep(3)

            ### 전송 주소 요청 코드
            # 업비트 입금주소 요청
            up_add, up_seadd = up_deposit_address_request(sym_name[b])

            ##### 잔고조회로 남는 코인자본 전송 같이 시킴
            can_send_amount = float(next((item for item in binance.fetch_balance()['info']['balances'] if item['asset'] == sym_name[b]), None)['free'])

            # 가상으로 돌릴 시
            # can_send_amount = can_send_amount + point_of_buy_bin_spot_amount_2
            if (0 < ((can_send_amount - point_of_buy_bin_spot_amount_2) * point_of_buy_bin_spot_ticker_2 * Usdt) < (div_unit / 15)):
                pass  # can_send_amount 가 자기자신이 된다 (남은 자본 보냄)
            else:
                can_send_amount = point_of_buy_bin_spot_amount_2  # can_send_amount 가 정확히 구매한양이 된다 point_of_buy_bin_spot_amount_2
            #####

            #####전송수수료를 제외한 양과 포함한 양 도출
            real_send_amount = can_send_amount - bin_withdrawfee[b]  # 구매한 수량과 전송수수료를 포함하지 않은 양으로 확인
            Decimal_rounding = bin_Min_Withdraw_Size[b]
            if (Decimal_rounding == 0):  # 전송 수수료가 0 인경우 나눌 수가 없음
                pass
            else:
                real_send_amount = (real_send_amount // Decimal_rounding) * Decimal_rounding
            real_send_amount = round(real_send_amount, 8)
            # point_of_Withdrow_UP_amount_2 = float(decimal.Decimal(str(real_send_amount)) + decimal.Decimal(str(bin_withdrawfee[b]))) # 구매한 수량과 전송수수료를 포함한 양을 전송요청
            point_of_Withdrow_UP_amount_2 = round(real_send_amount + bin_withdrawfee[b], 8)

            ### 업비트 처럼 따라해봄 하지만 무쓸모일듯
            ##### 잔고조회로 남는 코인자본 전송 같이 시킴
            # if (0 < ((can_send_amount - point_of_buy_bin_spot_amount_2) * point_of_buy_bin_spot_ticker_2 * Usdt) < (div_unit / 15)):
            #     point_of_buy_bin_spot_amount_2 = can_send_amount# can_send_amount 가 자기자신이 된다 (남은 자본 보냄)
            # else:
            #     pass # can_send_amount 가 정확히 구매한양이 된다 point_of_buy_bin_spot_amount_2
            # #####

            # #####전송수수료를 제외한 양과 포함한 양 도출
            # point_of_Withdrow_UP_amount_2 = point_of_buy_bin_spot_amount_2 - up_withdrawfee[b]

            # Decimal_rounding = bin_Min_Withdraw_Size[b]

            # if (Decimal_rounding == 0):  # 전송 수수료가 0 인경우 나눌 수가 없음
            #     pass
            # else:
            #     point_of_Withdrow_UP_amount_2 = (point_of_Withdrow_UP_amount_2 // Decimal_rounding) * Decimal_rounding
            # point_of_Withdrow_UP_amount_2 = round(point_of_Withdrow_UP_amount_2, 8)
            # point_of_Withdrow_UP_amount_2 = point_of_Withdrow_UP_amount_2 + bin_withdrawfee[b]

            time.sleep(3)

            # 가상의 경우
            # after_step_2_1_bin_spot_usdt_asset = point_of_buy_bin_spot_ticker_2 * point_of_buy_bin_spot_amount_2
            # after_step_2_1_bin_fu_usdt_asset = point_of_buy_bin_fu_ticker_2 * point_of_buy_bin_fu_amount_2
            # 진짜의 경우
            after_step_2_1_bin_spot_usdt_asset = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
            after_step_2_1_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])

            step_2_1_bin_spot_usdt_asset = before_step_2_1_bin_spot_usdt_asset - after_step_2_1_bin_spot_usdt_asset
            step_2_1_bin_fu_usdt_asset = before_step_2_1_bin_fu_usdt_asset - after_step_2_1_bin_fu_usdt_asset
            # step_2_1_bin_spot_usdt_asset = float(decimal.Decimal(str(before_step_2_1_bin_spot_usdt_asset)) - decimal.Decimal(str(after_step_2_1_bin_spot_usdt_asset))) # 구매한 수량과 전송수수료를 포함한 양을 전송요청
            # step_2_1_bin_fu_usdt_asset = float(decimal.Decimal(str(before_step_2_1_bin_fu_usdt_asset)) - decimal.Decimal(str(after_step_2_1_bin_fu_usdt_asset))) # 구매한 수량과 전송수수료를 포함한 양을 전송요청

            rest_step_2_1_bin_spot_usdt_asset = Second_Use_Bin_Spot_Usdt - step_2_1_bin_spot_usdt_asset
            rest_step_2_1_bin_fu_usdt_asset = Second_Use_Bin_Fu_Usdt - step_2_1_bin_fu_usdt_asset
            # rest_step_2_1_bin_spot_usdt_asset = float(decimal.Decimal(str(Second_Use_Bin_Spot_Usdt)) - decimal.Decimal(str(step_2_1_bin_spot_usdt_asset))) # 구매한 수량과 전송수수료를 포함한 양을 전송요청
            # rest_step_2_1_bin_fu_usdt_asset = float(decimal.Decimal(str(Second_Use_Bin_Fu_Usdt)) - decimal.Decimal(str(step_2_1_bin_fu_usdt_asset))) # 구매한 수량과 전송수수료를 포함한 양을 전송요청

            print("두 숫자가 음수이면 내가 초기 지정한 사용량을 초과한 것 코드 재확인 필요(첫 번째는 ㄱㅊ)", rest_step_2_1_bin_spot_usdt_asset, rest_step_2_1_bin_fu_usdt_asset)  # @@bin_spot_Usdt_Send = Second_Use_Bin_Spot_Usdt * (1 - (0.005 + bin_spot_market_fee))  #@ option 위에서 이 부분 사용해야 할지도

            if (rest_step_2_1_bin_spot_usdt_asset > 0):  # 사용하고 현물지갑에서 선물지갑 남은 달러 전송요청# dust = rest_step_2_1_bin_spot_usdt_asset
                try:
                    Decimal_rounding = 0.00000001
                    rest_step_2_1_bin_spot_usdt_asset = (rest_step_2_1_bin_spot_usdt_asset // Decimal_rounding) * Decimal_rounding
                    ret = client.futures_account_transfer(asset="USDT", amount=rest_step_2_1_bin_spot_usdt_asset, type=1, )  # 타입1:바현=>바선
                    print(ret)
                except:
                    quotePrecision = 8
                    rest_step_2_1_bin_spot_usdt_asset = float("{:0.0{}f}".format(rest_step_2_1_bin_spot_usdt_asset, quotePrecision))
                    ret = client.futures_account_transfer(asset="USDT", amount=rest_step_2_1_bin_spot_usdt_asset, type=1, )  # 타입1:바현=>바선
                    print(ret)

            elif (rest_step_2_1_bin_spot_usdt_asset < 0):  # 음수의 경우 바이낸스 선물 지갑에서 현물 기잡으로 이동한다
                try:
                    Decimal_rounding = 0.00000001
                    rest_step_2_1_bin_spot_usdt_asset_minus = - rest_step_2_1_bin_spot_usdt_asset
                    rest_step_2_1_bin_spot_usdt_asset_minus = (rest_step_2_1_bin_spot_usdt_asset_minus // Decimal_rounding) * Decimal_rounding
                    ret = client.futures_account_transfer(asset="USDT", amount=rest_step_2_1_bin_spot_usdt_asset_minus, type=2, )  # 타입2:바선=>바현
                    rest_step_2_1_bin_spot_usdt_asset = - rest_step_2_1_bin_spot_usdt_asset_minus
                    print(ret)
                except:
                    quotePrecision = 8
                    rest_step_2_1_bin_spot_usdt_asset_minus = - rest_step_2_1_bin_spot_usdt_asset
                    rest_step_2_1_bin_spot_usdt_asset_minus = float("{:0.0{}f}".format(rest_step_2_1_bin_spot_usdt_asset_minus, quotePrecision))
                    ret = client.futures_account_transfer(asset="USDT", amount=rest_step_2_1_bin_spot_usdt_asset_minus, type=2, )  # 타입2:바선=>바현
                    rest_step_2_1_bin_spot_usdt_asset = - rest_step_2_1_bin_spot_usdt_asset_minus
                    print(ret)

            else:  # rest_step_2_1_bin_spot_usdt_asset = 0
                pass
            rest_step_2_1_bin_fu_usdt_asset = float("{:0.0{}f}".format(rest_step_2_1_bin_fu_usdt_asset, 8))
            print("바이낸스 남은 자본 (나중에 업비트에서 팔고 나서 추가로 사용할 자본(더해주면됨)", rest_step_2_1_bin_spot_usdt_asset + rest_step_2_1_bin_fu_usdt_asset)

            return 'step_2_1', sym_name[b], point_of_buy_bin_spot_ticker_2, point_of_buy_bin_spot_amount_2, point_of_buy_bin_fu_ticker_2, point_of_buy_bin_fu_amount_2, expect_x4, expect_y4, point_of_Withdrow_UP_amount_2, real_send_amount, up_add, up_seadd, Bin_Spot_Minimum_Order_Size[b], Bin_Fu_Minimum_Order_Size[b], x3, y3 , Usdt, second_using_asset, bin_Min_Withdraw_Size[b], bin_withdrawfee[b], step_2_1_bin_spot_usdt_asset, step_2_1_bin_fu_usdt_asset, rest_step_2_1_bin_spot_usdt_asset, rest_step_2_1_bin_fu_usdt_asset, future_leverage

    else:
        # 김프포함 1달러 당 환율 #step_2_1

        Measure_Usdt = 1
        # 바이낸스 현물 주문자본 (업비트 전송)
        # a1 = bin_spot_to_up_can_order_amount * bin_spot_ask_price[b]  # - bin_withdrow_fee_Max) # * Usdt
        # a2 = bin_spot_to_up_can_order_amount * bin_spot_ask_price[b] * bin_spot_market_fee
        # #바이낸스 현물 주문자본 (업비트 전송) or
        a1 = real_order_amount = bin_spot_to_up_can_order_amount / (bin_spot_ask_price[b] * (1 - bin_spot_market_fee)) #실제로 전송 시 주문해야 할 양 # - bin_withdrow_fee_Max) # * Usdt
        a2 = bin_spot_to_up_can_order_amount * bin_spot_ask_price[b] * (1 - bin_spot_market_fee) #수수료
        # 바이낸스 선물 주문자본
        b1 = (bin_fu_can_order_send_to_up_optimal_symbol_quantity * bin_fu_bid_price[b]) / future_leverage  # * Usdt
        b2 = (bin_fu_can_order_send_to_up_optimal_symbol_quantity * bin_fu_bid_price[b]) * bin_future_market_fee * future_leverage_ceil  # * future_leverage_ceil ? or future_leverage

        bin_spot_real_order_Usdt = a1 + a2
        bin_fu_real_order_Usdt = b1 + b2

        statuses = (
                    'x1', x1, 'y1', y1,
                    'x2', x2, 'y2', y2,
                    'x3', x3, 'y3', y3,
                    'x4', x4, 'y4', y4,
                    "처음 사용중인 자본", Using_asset, "전송 후 사용중일 자본", x3 + y4,

                    "첫번째 예상 손수익율", (x2 + y2) / (Using_asset),
                    "첫번째 예상 손수익", (x2 + y2) - (Using_asset),
                    "두번째 예상 손수익율", (x4 + y4) / (Using_asset),
                    "두번째 예상 손수익", (x4 + y4) - (Using_asset),

                    "달러가치", Usdt,
                    "김프포함 달러가치", ((Measure_Usdt / bin_spot_ask_price[b]) * up_bid_price[b]) / (Measure_Usdt),

                    "바이낸스 선물 실제 쓰일 자본", bin_fu_real_order_Usdt * Usdt,
                    "바이낸스 현물 실제 쓰일 자본", bin_spot_real_order_Usdt * Usdt,

                    "내가 원하는 프리미엄가", want_premium_step_2_1,
                    "내가 원하는 프리미엄가", can_profit_preium,

                    "전송 시 자본 비율", (x3 + y3) / ((Second_Use_Bin_Spot_Usdt + Second_Use_Bin_Fu_Usdt) * Usdt),  # (second_using_asset / Using_asset)

                    "현재 자본대비 최적김프", (bin_to_up_pre_rate[b] - 1) * 100,
                    "평균김프(%)", (1-(sum(bin_to_up_pre_rate) / len(bin_to_up_pre_rate))) * 100,
                    "해당로직이 통과 시 통과 (can_profit_preium)", x4 / (bin_spot_to_up_can_order_amount * bin_spot_ask_price[b] * Usdt) - 1,

                    (((x4 + y4) / Using_asset - 1), want_premium_step_2_1),  # 처음 사용 자본보다 수익율이 좋아야 함 (모든 수익 고려됨) #
                    ((x4 + y4), Using_asset),  # 초기 사용자본 대비 예측 수익율이 무조건 커야 함 달러가치 하락에 있어서 고려됨
                    (bin_withdrawfee_by_asset[b] - 1, can_profit_preium),  # 수수료 포함 총 주문 수량이 수익 을 볼 수 있는 퍼센트 이상
                    (x4 / (bin_spot_to_up_can_order_amount * bin_spot_ask_price[b] * Usdt) - 1, can_profit_preium),  # 달러 가치 상승 뿐 아니라 김프가 어느정도 끼어야 로직 들어감 # @@ 해당로직은 없앨까..?
                    ((x4 + y4) / (Second_Using_asset * Usdt) - 1, want_premium_step_2_1),  # 수익율 5퍼이상 예측 될 경우
                    (((x4 + y4) / Using_asset - 1), 0.05),
                    bin_spot_to_up_can_order_amount * bin_spot_ask_price[b], Second_Use_Bin_Spot_Usdt
                    )
        if (len(statuses) != 0):
            clear_output(wait=True)
            display(statuses)

    return 'Capital_distribution', 'sym_name[b]', 'point_of_buy_bin_spot_ticker_2', 'point_of_buy_bin_spot_amount_2', 'point_of_buy_bin_fu_ticker_2', 'point_of_buy_bin_fu_amount_2', 'expect_x4', 'expect_y4', 'point_of_Withdrow_UP_amount_2', 'real_send_amount', 'up_add', 'up_seadd', 'Bin_Spot_Minimum_Order_Size[b]', 'Bin_Fu_Minimum_Order_Size[b]', 'x3', 'y3', 'Usdt_2_1', second_using_asset, 'bin_Min_Withdraw_Size[b]', 'bin_withdrawfee[b]', 'step_2_1_bin_spot_usdt_asset', 'step_2_1_bin_fu_usdt_asset', 'rest_step_2_1_bin_spot_usdt_asset', 'rest_step_2_1_bin_fu_usdt_asset', future_leverage


def send_bin_to_up(send_to_up_optimal_simbol, up_add, up_seadd, real_send_amount, point_of_Withdrow_UP_amount_2):  # 바이낸스에서 업비트 전송주문 요청

    send_state_2 = [send_to_up_optimal_simbol, up_add, up_seadd, real_send_amount, point_of_Withdrow_UP_amount_2, "전송실패"]
    # 바 => 업 전송, 오류날 경우를 대비

    try:
        if (send_to_up_optimal_simbol == 'BHC'):  # BCH코인은 주소가 좀 이상하게 나옴, 그리고 태그도 없어야 전송이 됨.
            up_add = up_add[12:]
            res = client_spot.withdraw(coin=send_to_up_optimal_simbol, amount=point_of_Withdrow_UP_amount_2, address=up_add, addressTag=up_seadd)
            # addressTag=up_seadd)

            send_state_2 = res
            print(res)
            return 'send_bin_to_up', upbit.get_balance(send_to_up_optimal_simbol)
            # 성공시 send_bin_to_up

        if (up_seadd == None):

            res = client_spot.withdraw(coin=send_to_up_optimal_simbol, amount=point_of_Withdrow_UP_amount_2, address=up_add, )
            # 두번째 주소가 없는경우 그 양식에 맞게 전송주문을 제출 하여야 함.
            # addressTag=up_seadd)

            send_state_2 = res
            print(res)
            return 'send_bin_to_up', upbit.get_balance(send_to_up_optimal_simbol)
            # 성공시 send_bin_to_up

        else:
            # 바이낸스 코인 전송

            res = client_spot.withdraw(coin=send_to_up_optimal_simbol, amount=point_of_Withdrow_UP_amount_2, address=up_add, addressTag=up_seadd)
            send_state_2 = res
            print(res)
            return 'send_bin_to_up', upbit.get_balance(send_to_up_optimal_simbol)
            # 성공시 send_bin_to_up

    except:

        statuses = (send_state_2)

        if (len(statuses) != 0):
            clear_output(wait=True)
            display(statuses)
        return 'step_2_1', "보내기 전 업비트 잔고"

def send_bin_to_up_Completion(send_to_up_optimal_simbol, real_send_amount, bin_Min_Withdraw_Size_b, bin_fu_can_order_send_to_up_optimal_symbol_quantity, before_send_to_up_balace):  # 바이낸스에서 업비트 전송완료

    up_simbol_balance = upbit.get_balance("KRW-" + send_to_up_optimal_simbol)

    quotePrecision = 8  ## @@ 옵션

    aa = before_send_to_up_balace + real_send_amount  # 전송량 + 업비트 이전에있던 심볼 수량
    Decimal_rounding = bin_Min_Withdraw_Size_b
    aa = (aa // Decimal_rounding) * Decimal_rounding
    aa = round(aa, quotePrecision)

    if (up_simbol_balance >= aa):
        print("업비트", send_to_up_optimal_simbol, "전송 완료", up_simbol_balance)
        return 'send_bin_to_up_Completion'

    #########################################
    bin_sym_names, bin_fu_ask_bid = bin_fu_ask_bid_info([send_to_up_optimal_simbol])
    bin_fu_ask_price, bin_fu_ask_size = bin_fu_ask_info(bin_sym_names, bin_fu_ask_bid)  # 바-선 매수 호가창 2 4
    # bin_fu_bid_price, bin_fu_bid_size = bin_fu_bid_info(bin_sym_names, bin_fu_ask_bid)  # 바-선 매도 호가창 1 3

    aa = client.futures_account()  # @@ 곂쳤을 수도 있으니 내 계좌 정보 불러와서 계산
    # next((item for item in aa['positions'] if item['symbol'] == send_to_bin_optimal_simbol + 'USDT'), None)
    future_leverage_ceil = int(next((item for item in aa['positions'] if item['symbol'] == send_to_up_optimal_simbol + 'USDT'), None)['leverage'])
    point_of_buy_bin_fu_ticker_2 = float(next((item for item in aa['positions'] if item['symbol'] == send_to_up_optimal_simbol + 'USDT'), None)['entryPrice'])

    # 계좌 잔고 확인 option
    print(1 + (1 - bin_fu_ask_price[0] / point_of_buy_bin_fu_ticker_2) * future_leverage_ceil)
    if ((1 + (1 - bin_fu_ask_price[0] / point_of_buy_bin_fu_ticker_2) * future_leverage_ceil) < 0.2):  # 이 때 청산. 80% 위기 (-는 청산 1이상은 수익)
        try:
            result = request_client.post_order(symbol=send_to_up_optimal_simbol + "USDT", side=OrderSide.BUY, ordertype=OrderType.MARKET, quantity=bin_fu_can_order_send_to_up_optimal_symbol_quantity)  # quantity수량.#Orderside sell 이면 판매
            PrintBasic.print_obj(result)
            #         state = ["warning"]
            return "청산 80% 위기 포지션 강제 종료_3"
        except:
            pass

    statuses = ("바이낸스 => 업비트", send_to_up_optimal_simbol, "전송 중", up_simbol_balance,
                "현재시각", time.ctime(time.time()))

    if (len(statuses) != 0):
        clear_output(wait=True)
        display(statuses)

    time.sleep(5)

    return 'send_bin_to_up'


# before_send_bin_to_up_Completion_fu_usdt = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])
# after_send_bin_to_up_Completion_fu_usdt = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])
# send_bin_to_up_Completion_fu_usd = before_send_up_to_bin_Completion_fu_usdt - after_send_up_to_bin_Completion_fu_usdt


# before_send_bin_to_up_Completion_up_krw = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
# after_send_bin_to_up_Completion_up_krw = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
# send_bin_to_up_Completion_up_krw = before_send_up_to_bin_Completion_spot_usdt - after_send_up_to_bin_Completion_spot_usdt

def step_2_2(x3, y3, point_of_buy_bin_spot_ticker_2, point_of_buy_bin_fu_ticker_2, expect_x4, expect_y4, sym_name_b, real_send_amount, point_of_buy_bin_fu_amount_2, up_market_fee, bin_future_market_fee, future_leverage, Usdt_1_1, step_1_1_up_krw_asset, step_1_1_bin_fu_usdt_asset,
             rest_step_1_1_bin_fu_usdt_asset, div_unit, want_premium_step_2_1):  # 전송완료 후 예상 손해보다 덜 보는 상태에서 매도
    before_step_2_2_up_krw_asset = upbit.get_balance("KRW")
    before_step_2_2_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])

    # can_profit_preium = ((1 + want_premium_step_2_1 / 100) / (1 - want_premium_step_1_1 / 100) - 1) * 100
    Using_asset = step_1_1_up_krw_asset + (step_1_1_bin_fu_usdt_asset + rest_step_1_1_bin_fu_usdt_asset) * Usdt_1_1
    Usdt = upbit_get_usd_krw()

    ##### @@ 남는자본 + div_unit / 5 보다 작은 잔고가 존재할 시 찌꺼기로 생각하고 포함해서 계산
    rest_sym = upbit.get_balance("KRW-" + sym_name_b)  # (upbit.get_balance("KRW-" + sym_name_b) 이부분 업비트 요청 1번으로 바꾸기 위해 변수명 생성
    if (0 < (rest_sym - real_send_amount) * point_of_buy_bin_spot_ticker_2 * Usdt < (div_unit / 15)):  # 0< 인 이유는 다른 자본 사용 시 혹시모를 경우 대비(마지막에 찌꺼기 처럼 남은 자본)
        # if (0 < (rest_sym - real_send_amount) * up_bid_price[0] < (div_unit / 15)):  # 0< 인 이유는 다른 자본 사용 시 혹시모를 경우 대비(마지막에 찌꺼기 처럼 남은 자본)
        # @@주문가능 최소량
        quotePrecision = 8
        Decimal_rounding, Decimal_rounding_dig = (0.1) ** int(quotePrecision), int(quotePrecision)  # 소수점 라운딩
        rest_sym = (rest_sym // Decimal_rounding) * Decimal_rounding
        real_send_amount = round(rest_sym, Decimal_rounding_dig)
    else:
        pass
    #####

    # 전송 후
    up_sym_names, up_spot_ask_bid = up_spot_ask_bid_info([sym_name_b])
    up_bid_price, up_bid_size = up_bid_info(up_sym_names, up_spot_ask_bid)  # 업비트 매도 호가창 4

    bin_sym_names, bin_fu_ask_bid = bin_fu_ask_bid_info([sym_name_b])
    bin_fu_ask_price, bin_fu_ask_size = bin_fu_ask_info(bin_sym_names, bin_fu_ask_bid)  # 바-선 매수 호가창 2 4

    # 4.업비트 현물에서 매도 bid
    # = ((bin_spot_to_up_can_order_amount - bin_withdrow_fee_Max) * up_bid_price[b] * (1 - up_market_fee))
    # x4 = real_send_amount * up_bid_price[0] * (1 - up_market_fee) # @@ 이것으로 계산해야 더 정확?
    x4 = x3 * (up_bid_price[0] / (point_of_buy_bin_spot_ticker_2 * Usdt)) * (1 - up_market_fee)

    # 4.바이낸스 선물에서 공매수 ask
    # (point_of_buy_bin_fu_ticker_2 * point_of_buy_bin_fu_amount_2 * (1 + (1 - bin_fu_ask_price[0] / point_of_buy_bin_fu_ticker_2) * future_leverage) * (1 - bin_future_market_fee * future_leverage))/future_leverage*Usdt
    y4 = y3 * (1 + (1 - bin_fu_ask_price[0] / point_of_buy_bin_fu_ticker_2) * future_leverage) * (1 - bin_future_market_fee * future_leverage)  # 예상 평단가 bin_fu_bid_price[b]

    if (((expect_x4 + expect_y4) <= (x4 + y4) or ((x3 + y3) <= (x4 + y4))) and ((x4 + y4) / (expect_x4 + expect_y4) >= 1.00001)) or (Using_asset * (1 + want_premium_step_2_1) < (x4 + y4)) or (Using_asset * (1 + 0.03) < (x4 + y4)):  # 3% 이상 수익이면 그냥 팔기
        # print("주문신청")
        if ((real_send_amount < up_bid_size[0] * 0.5)):
            res = upbit.sell_market_order("KRW-" + sym_name_b, real_send_amount)
            try:
                # 주문신청                             # 심볼            #sell 이면 숏 buy면 롱     # 시장가 거래         # 몇개 살것인지 (여기를 더 고민 ,잔고 또는 자본에 맞춰서 구매하게 만들어야함)
                result = request_client.post_order(symbol=sym_name_b + "USDT", side=OrderSide.BUY, ordertype=OrderType.MARKET, quantity=point_of_buy_bin_fu_amount_2)  # quantity수량.#Orderside sell 이면 판매
                PrintBasic.print_obj(result)
            except:
                result = binance_fu.create_market_buy_order(symbol=sym_name_b + "/USDT", amount=point_of_buy_bin_fu_amount_2, )
                pprint.pprint(result)
            pprint.pprint(res)

            after_step_2_2_up_krw_asset = upbit.get_balance("KRW")
            after_step_2_2_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])
            step_2_2_up_krw_asset = after_step_2_2_up_krw_asset - before_step_2_2_up_krw_asset
            step_2_2_bin_fu_usdt_asset = after_step_2_2_bin_fu_usdt_asset - before_step_2_2_bin_fu_usdt_asset

            return 'step_2_2', step_2_2_up_krw_asset, step_2_2_bin_fu_usdt_asset, x4, y4, Usdt

    aa = client.futures_account()
    future_leverage_ceil = int(next((item for item in aa['positions'] if item['symbol'] == sym_name_b + 'USDT'), None)['leverage'])
    point_of_buy_bin_fu_ticker_2 = float(next((item for item in aa['positions'] if item['symbol'] == sym_name_b + 'USDT'), None)['entryPrice'])

    if ((1 + (1 - bin_fu_ask_price[0] / point_of_buy_bin_fu_ticker_2) * future_leverage_ceil) < 0.2):  # 이 때 청산. 80% 위기 (-는 청산 1이상은 수익)

        res = upbit.sell_market_order("KRW-" + sym_name_b, real_send_amount)
        try:
            # 주문신청                             # 심볼            #sell 이면 숏 buy면 롱     # 시장가 거래         # 몇개 살것인지 (여기를 더 고민 ,잔고 또는 자본에 맞춰서 구매하게 만들어야함)
            result = request_client.post_order(symbol=sym_name_b + "USDT", side=OrderSide.BUY, ordertype=OrderType.MARKET, quantity=point_of_buy_bin_fu_amount_2)  # quantity수량.#Orderside sell 이면 판매
            PrintBasic.print_obj(result)
        except:
            result = binance_fu.create_market_buy_order(symbol=sym_name_b + "/USDT", amount=point_of_buy_bin_fu_amount_2, )
            pprint.pprint(result)
        pprint.pprint(res)

        time.sleep(3)  # 매수or매도 이후 바로 값 잘 못불러옴

        after_step_2_2_up_krw_asset = upbit.get_balance("KRW")
        after_step_2_2_bin_fu_usdt_asset = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['availableBalance'])
        step_2_2_up_krw_asset = after_step_2_2_up_krw_asset - before_step_2_2_up_krw_asset
        step_2_2_bin_fu_usdt_asset = after_step_2_2_bin_fu_usdt_asset - before_step_2_2_bin_fu_usdt_asset

        return "청산 80% 위기 포지션 강제 종료_step_2_2", step_2_2_up_krw_asset, step_2_2_bin_fu_usdt_asset, x4, y4, Usdt

    else:

        # 팔시점 아직 안나옴
        statuses = ("예상 수익과의 차이", (x4 + y4) - (expect_x4 + expect_y4),
                    #                     "확인차 추가한 코드",binance_asset + up_asset ,Using_asset,
                    #                     "예상 수익 ", (expect_y4 + expect_x4) - (Using_asset),
                    ##@@뭔가 이상하다 Using_asset , binance_asset + up_asset이 다르다
                    "예상했던 수익 ", (expect_y4 + expect_x4) - (Using_asset),
                    "실제 수익", (x4 + y4) - (Using_asset),
                    "수익율", (x4 + y4) / (Using_asset),
                    "(거래후)업비트 예상자본", x4,
                    "(거래후)바이낸스 예상자본", y4
                    )
        if (len(statuses) != 0):
            clear_output(wait=True)
            display(statuses)
    time.sleep(1)

    # 바이낸스 현물가 , 바이낸스 선물가 , 실제 전송 후 손해 ,최적이였던 전송코인

    return "send_bin_to_up_Completion", 'step_2_2_up_krw_asset', 'step_2_2_bin_fu_usdt_asset', x4, y4, Usdt


def final_fun(qwer, k, save_state, sicle, up_asset, binance_asset, Using_asset, x1, y1, Usdt_1_1, sym_name_a, future_leverage, point_of_buy_UP_ticker_1, point_of_buy_UP_amount_1, point_of_buy_bin_fu_ticker_1, point_of_buy_bin_fu_amount_1, second_using_asset, x2, y2, Usdt_1_2, sym_name_b, x3, y3,
              Usdt_2_1, point_of_buy_bin_spot_ticker_2, point_of_buy_bin_spot_amount_2, point_of_buy_bin_fu_ticker_2, point_of_buy_bin_fu_amount_2, x4, y4, Usdt_2_2, step_2_2_up_krw_asset, step_2_2_bin_fu_usdt_asset, step_1_1_up_krw_asset, step_1_1_bin_fu_usdt_asset, rest_step_1_1_up_krw_asset,
              rest_step_1_1_bin_fu_usdt_asset, step_1_2_bin_spot_usdt_asset, step_1_2_bin_fu_usdt_asset, step_2_1_bin_spot_usdt_asset, step_2_1_bin_fu_usdt_asset, rest_step_2_1_bin_spot_usdt_asset, rest_step_2_1_bin_fu_usdt_asset, want_premium_step_1_1, want_premium_step_2_1):
    now = datetime.datetime.now()
    date = str(now.year) + "Y_" + str(now.month) + "M_" + str(now.day) + "D_" + str(now.hour) + "h_" + str(now.minute) + "m_" + str(now.second) + "s"
    total_before = up_asset + binance_asset * Usdt_1_1

    # @@ total_after=> step_1_1에서 남는돈 , step_2_1에서 남는돈 합해야 정확함
    total_after = step_2_2_up_krw_asset + rest_step_1_1_up_krw_asset + (step_2_2_bin_fu_usdt_asset + rest_step_2_1_bin_spot_usdt_asset + rest_step_2_1_bin_fu_usdt_asset) * Usdt_2_2

    # x2=step_1_2_bin_spot_usdt_asset,y2=step_1_2_bin_fu_usdt_asset,x4=step_2_2_up_krw_asset,y4=step_2_2_bin_fu_usdt_asset
    save_state[sicle] = [sicle,
                         k,
                         up_asset,
                         binance_asset,
                         Using_asset,
                         step_1_1_up_krw_asset,
                         step_1_1_bin_fu_usdt_asset,
                         rest_step_1_1_up_krw_asset,
                         rest_step_1_1_bin_fu_usdt_asset,
                         x1,
                         y1,
                         Usdt_1_1,
                         sym_name_a,
                         future_leverage,
                         point_of_buy_UP_ticker_1,
                         point_of_buy_UP_amount_1,
                         point_of_buy_bin_fu_ticker_1,
                         point_of_buy_bin_fu_amount_1,
                         second_using_asset,
                         step_1_2_bin_spot_usdt_asset,
                         step_1_2_bin_fu_usdt_asset,
                         x2,
                         y2,
                         Usdt_1_2,
                         ((x2 + y2) * Usdt_1_2) - ((x1 + y1) * Usdt_1_1),
                         sym_name_b,
                         step_2_1_bin_spot_usdt_asset,
                         step_2_1_bin_fu_usdt_asset,
                         rest_step_2_1_bin_spot_usdt_asset,
                         rest_step_2_1_bin_fu_usdt_asset,
                         x3,
                         y3,
                         Usdt_2_1,
                         point_of_buy_bin_spot_ticker_2,
                         point_of_buy_bin_spot_amount_2,
                         point_of_buy_bin_fu_ticker_2,
                         point_of_buy_bin_fu_amount_2,
                         step_2_2_up_krw_asset,
                         step_2_2_bin_fu_usdt_asset,
                         x4,
                         y4,
                         Usdt_2_2,
                         total_before,
                         total_after,
                         date,
                         want_premium_step_1_1,
                         want_premium_step_2_1
                         ]

    # csv파일로 적기 # newline 설정을 안하면 한줄마다 공백있는 줄이 생긴다.
    with open(qwer + 'Free_Risk_Trading_data.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(save_state[sicle])

    sicle = sicle + 1
    save_state[sicle] = []

    # @@ total_after=> step_1_1에서 남는돈 , step_2_1에서 남는돈 합해야 정확함
    up_asset = step_2_2_up_krw_asset + rest_step_1_1_up_krw_asset
    binance_asset = step_2_2_bin_fu_usdt_asset + rest_step_2_1_bin_spot_usdt_asset + rest_step_2_1_bin_fu_usdt_asset

    future_leverage = up_asset / (binance_asset * Usdt)

    return 'None_position', save_state, up_asset, binance_asset, future_leverage

# ============ 주요 전체 코드
while True: # 전체 코드
    # asset_division = set_premium_asset_division() # %수치 변화. #@@ 여기도 레버리지에 따라 최소 차익 볼 김프 수치 조정하기
    while True:
        for i in range(len(asset_division)):
            if (asset_division[i]["State"] == 'None_position'):  # 업 => 바 보낼 코인 서칭 및 헷징(백워데이션)
                asset_division[i]['sym_name'], asset_division[i]['step_1_1_sym_name_future_leverage_ceil'] = step_1_1_sym_name(asset_division[i]['up_asset'], asset_division[i]['future_leverage'], User_data['ban_list'], User_data['up_market_fee'])
                asset_division[i]['State'], asset_division[i]['sym_name[a]'], asset_division[i]['point_of_buy_UP_ticker_1'], asset_division[i]['point_of_buy_UP_amount_1'], asset_division[i]['point_of_buy_bin_fu_ticker_1'], asset_division[i]['point_of_buy_bin_fu_amount_1'], asset_division[i]['expect_x2'], asset_division[i]['expect_y2'], asset_division[i]['point_of_Withdrow_UP_amount_1'], asset_division[i]['bin_address'], asset_division[i]['bin_Memo'], asset_division[i]['future_leverage'], asset_division[i]['Bin_Spot_Minimum_Order_Size_a'], asset_division[i]['x1'] , asset_division[i]['y1'], asset_division[i]['Usdt_1_1'], asset_division[i]['Using_asset'], asset_division[i]['step_1_1_up_krw_asset'], asset_division[i]['step_1_1_bin_fu_usdt_asset'], asset_division[i]['rest_step_1_1_up_krw_asset'], asset_division[i]['rest_step_1_1_bin_fu_usdt_asset'], asset_division[i]['up_withdrawfee[a]'], asset_division[i]['up_withdrawfee_by_asset[a]'], asset_division[i]['step_1_1_premium'] = step_1_1(asset_division[i]['sym_name'], asset_division[i]['up_asset'], asset_division[i]['binance_asset'], User_data['up_market_fee'], User_data['bin_spot_market_fee'], User_data['bin_future_market_fee'], asset_division[i]['want_premium_step_1_1'] , User_data['ban_list'] , asset_division[i]['adjust_leverage'], asset_division[i]['step_1_1_sym_name_future_leverage_ceil'], asset_division[i]['div_unit'])

        State_All = [asset_division[w]["State"] for w in range(len(asset_division))]  # 중복이 없어야 종료 됨.
        if (len(set(State_All) & {'None_position'}) == 0):  # 그 전 단계 이름들만 있으면 됨
            del(State_All)  # 메모리 아끼기
            break

        # 전송한 심볻들(sending_sym)중에 같은 심볼명이 없다면 => 전송 중 도착해버리는 경우고려(평단가 도출이 어려움ex1번 보내고 2번 보내는데 1번 도착해서 2번이 도착한줄 알면)
        for i in range(len(asset_division)):
            # @@ 곂치는 심볼이 있으면 같이 전송하는 구조로 만들기
            sending_sym = []
            for j in range(len(asset_division)):
                if (asset_division[j]["State"] == 'send_up_to_bin'):  # 전송중인 코인명 가져옴
                    sending_sym.append(asset_division[j]['sym_name[a]'])

            if (asset_division[i]["State"] == 'step_1_1'):
                if ((asset_division[i]['sym_name[a]'] in sending_sym) == False):  # 전송중인 심볼이 두개가 곂치지 않게 함.(곂치는 경우 pass)
                    asset_division[i]["State"], asset_division[i]["보내기 전 바이낸스잔고"] = send_up_to_bin(asset_division[i]["sym_name[a]"], asset_division[i]['point_of_Withdrow_UP_amount_1'], asset_division[i]['bin_address'], asset_division[i]['bin_Memo'])  # 업비트에서 바이낸스 전송주문 요청

                    if (asset_division[i]["State"] == 'step_1_1'):
                        asset_division[i]["State"], asset_division[i]["보내기 전 바이낸스잔고"], asset_division[i]['point_of_Withdrow_UP_amount_1'] = send_up_to_bin_2(asset_division[i]["sym_name[a]"], asset_division[i]['point_of_Withdrow_UP_amount_1'], asset_division[i]['bin_address'], asset_division[i]['bin_Memo'])  # 업비트에서 바이낸스 전송주문 요청
                        if (asset_division[i]["State"] == 'step_1_1'):
                            asset_division[i]["State"], asset_division[i]["보내기 전 바이낸스잔고"], asset_division[i]['point_of_Withdrow_UP_amount_1'] = send_up_to_bin_3(asset_division[i]["sym_name[a]"], asset_division[i]['point_of_Withdrow_UP_amount_1'], asset_division[i]['bin_address'], asset_division[i]['bin_Memo'], asset_division[i]['Bin_Spot_Minimum_Order_Size_a'])  # 업비트에서 바이낸스 전송주문 요청
                else:
                    pass

    while True:
        for i in range(len(asset_division)):
            if (asset_division[i]["State"] == 'send_up_to_bin'):
                asset_division[i]["State"] = send_up_to_bin_Completion(asset_division[i]["sym_name[a]"], asset_division[i]["보내기 전 바이낸스잔고"], asset_division[i]["point_of_Withdrow_UP_amount_1"], asset_division[i]['point_of_buy_bin_fu_amount_1'], asset_division[i]['Bin_Spot_Minimum_Order_Size_a'])
                time.sleep(5)

        State_All = [asset_division[w]["State"] for w in range(len(asset_division))]  # 중복이 없어야 종료 됨.
        if (len(set(State_All) & {'send_up_to_bin'}) == 0):  # 그 전 단계 이름들만 있으면 됨
            del (State_All)  # 메모리 아끼기
            break

    # for i in range(len(asset_division)):
    #     if (asset_division[i]["State"] == 'send_up_to_bin'):
    #         asset_division[i]["State"] = send_up_to_bin_Completion(asset_division[i]["sym_name[a]"],asset_division[i]["보내기 전 바이낸스잔고"] ,asset_division[i]["point_of_Withdrow_UP_amount_1"],asset_division[i]['point_of_buy_bin_fu_amount_1'],asset_division[i]['Bin_Spot_Minimum_Order_Size_a'])
    #         time.sleep(5)


        ## 이 부분들 리턴값을 받을 수 있게 함수로 만들어야함.. 전송완료를 확인 한 이후에 사용되고 있는 달러를 도출해내야함.
        ############################# @@ 나중에 고치기 !!####################################################################################
        for i in range(len(asset_division)):
            if (asset_division[i]["State"] == '청산 80% 위기 포지션 강제 종료'):

                balance = binance.fetch_balance()

                Bin_Spot_Minimum_Order_Size_a = asset_division[i]['Bin_Spot_Minimum_Order_Size_a'] #@@옵션션
                point_of_Withdrow_UP_amount_1 = asset_division[i]["point_of_Withdrow_UP_amount_1"]
                before_send_to_bin_balace = asset_division[i]["보내기 전 바이낸스잔고"]

                quotePrecision = 8  ## @@ 옵션
                aa = before_send_to_bin_balace + point_of_Withdrow_UP_amount_1
                Decimal_rounding = Bin_Spot_Minimum_Order_Size_a
                aa = (aa // Decimal_rounding) * Decimal_rounding
                aa = round(aa, quotePrecision)

                # quotePrecision = 8
                # aa = before_send_to_bin_balace + point_of_Withdrow_UP_amount_1
                # Decimal_rounding, Decimal_rounding_dig = (0.1) ** int(quotePrecision), int(quotePrecision)  # 소수점 라운딩
                # aa = (aa // Decimal_rounding) * Decimal_rounding
                # aa = round(aa, Decimal_rounding_dig - 1)

                if (balance[asset_division[i]['sym_name[a]']]['free'] >= aa):
                    asset_division[i]["State"] = "청산 80% 위기 포지션 강제 종료_1"  # 전송완료 확인

            # 전송중에 급상승으로 포지션 강제 종료위기
            if (asset_division[i]["State"] == "청산 80% 위기 포지션 강제 종료_1"):  # 현물도 파는 코드
                try:
                    #@@@이 부분 리턴값을 가지고 있어야 계속 돌수가 있음
                    order = binance.create_market_sell_order(asset_division[i]['sym_name[a]'] + '/USDT', asset_division[i]['point_of_Withdrow_UP_amount_1'])  # @@ 이부분
                    print("청산 80% 위기 포지션 강제 종료")
                    asset_division[i]["State"] = "청산 80% 위기 포지션 강제 종료_2"
                except:
                    pass
        ############################################################################################################################################

    while True:
        for i in range(len(asset_division)):
            if (asset_division[i]["State"] == 'send_up_to_bin_Completion'):
                asset_division[i]['State'], asset_division[i]['step_1_2_bin_spot_usdt_asset'], asset_division[i]['step_1_2_bin_fu_usdt_asset'], asset_division[i]['after_step_1_2_bin_spot_usdt_asset'], asset_division[i]['after_step_1_2_bin_fu_usdt_asset'], asset_division[i]['before_step_1_2_bin_spot_usdt_asset'], asset_division[i]['before_step_1_2_bin_fu_usdt_asset'], asset_division[i]['x2'], asset_division[i]['y2'], asset_division[i]['Usdt_1_2'] = step_1_2(asset_division[i]['binance_asset'], asset_division[i]['up_asset'],asset_division[i]['sym_name[a]'], asset_division[i]['point_of_Withdrow_UP_amount_1'],asset_division[i]['point_of_buy_UP_ticker_1'], asset_division[i]['point_of_buy_bin_fu_ticker_1'],asset_division[i]['future_leverage'], asset_division[i]['Bin_Spot_Minimum_Order_Size_a'],asset_division[i]['point_of_buy_bin_fu_amount_1'], asset_division[i]['x1'],asset_division[i]['y1'], asset_division[i]['expect_x2'], asset_division[i]['expect_y2'],asset_division[i]['div_unit'], User_data['bin_spot_market_fee'],User_data['bin_future_market_fee'], asset_division[i]['Usdt_1_1'])

            if (asset_division[i]["State"] == 'step_1_2'):
                asset_division[i]['State'], asset_division[i]['Second_Use_Bin_Spot_Usdt'], asset_division[i]['Second_Use_Bin_Fu_Usdt'], asset_division[i]['second_using_asset'] = Capital_distribution(asset_division[i]['sym_name'], asset_division[i]['step_1_2_bin_spot_usdt_asset'],asset_division[i]['step_1_2_bin_fu_usdt_asset'],asset_division[i]['before_step_1_2_bin_spot_usdt_asset'],asset_division[i]['before_step_1_2_bin_fu_usdt_asset'], User_data['bin_spot_market_fee'],asset_division[i]['rest_step_1_1_bin_fu_usdt_asset'], asset_division[i]["adjust_leverage"],User_data['ban_list'], User_data['up_market_fee'], User_data["bin_future_market_fee"])

        State_All = [asset_division[w]["State"] for w in range(len(asset_division))]  # 중복이 없어야 종료 됨.
        if (len(set(State_All) & {'send_up_to_bin_Completion', 'step_1_2'}) == 0):
            del (State_All)  # 메모리 아끼기
            break

    Save_ALL_DATA()

    while True:
        for i in range(len(asset_division)):
            if (asset_division[i]["State"] == 'Capital_distribution'):#자본 배분이 끝난 상태 이후에 업비트에서 수익이 날지 서칭
                asset_division[i]['sym_name'], asset_division[i]['future_leverage'], asset_division[i]['step_2_1_future_leverage_ceil'] = step_2_1_sym_name(asset_division[i]['Second_Use_Bin_Spot_Usdt'],asset_division[i]['Second_Use_Bin_Fu_Usdt'], User_data['ban_list'], User_data['bin_spot_market_fee'])
                asset_division[i]['State'], asset_division[i]['sym_name[b]'], asset_division[i]['point_of_buy_bin_spot_ticker_2'], asset_division[i]['point_of_buy_bin_spot_amount_2'], asset_division[i]['point_of_buy_bin_fu_ticker_2'], asset_division[i]['point_of_buy_bin_fu_amount_2'], asset_division[i]['expect_x4'], asset_division[i]['expect_y4'], asset_division[i]['point_of_Withdrow_UP_amount_2'], asset_division[i]['real_send_amount'], asset_division[i]['up_add'], asset_division[i]['up_seadd'], asset_division[i]['Bin_Spot_Minimum_Order_Size[b]'], asset_division[i]['Bin_Fu_Minimum_Order_Size[b]'], asset_division[i]['x3'], asset_division[i]['y3'], asset_division[i]['Usdt_2_1'], asset_division[i]['second_using_asset'], asset_division[i]['bin_Min_Withdraw_Size[b]'], asset_division[i]['bin_withdrawfee[b]'], asset_division[i]['step_2_1_bin_spot_usdt_asset'], asset_division[i]['step_2_1_bin_fu_usdt_asset'], asset_division[i]['rest_step_2_1_bin_spot_usdt_asset'], asset_division[i]['rest_step_2_1_bin_fu_usdt_asset'], asset_division[i]['future_leverage'] = step_2_1(asset_division[i]['sym_name'], asset_division[i]['Second_Use_Bin_Spot_Usdt'], asset_division[i]['Second_Use_Bin_Fu_Usdt'], asset_division[i]['x1'], asset_division[i]['y1'], asset_division[i]['x2'], asset_division[i]['y2'], asset_division[i]['second_using_asset'], asset_division[i]['Usdt_1_1'], asset_division[i]['step_2_1_future_leverage_ceil'], User_data['bin_spot_market_fee'], User_data['bin_future_market_fee'], User_data['up_market_fee'], asset_division[i]['div_unit'],asset_division[i]['want_premium_step_1_1'], asset_division[i]['want_premium_step_2_1'], asset_division[i]['step_1_1_up_krw_asset'], asset_division[i]['step_1_1_bin_fu_usdt_asset'], asset_division[i]['rest_step_1_1_bin_fu_usdt_asset'])

        State_All = [asset_division[w]["State"] for w in range(len(asset_division))]  # 중복이 없어야 종료 됨.
        # 여긴 전송 중 중인것도 고려..... @@ 아래 로직 좀 바꾸기 ex : {'Capital_distribution', 'send_bin_to_up' }
        if (len(set(State_All) & {'Capital_distribution', 'send_bin_to_up'}) == 0):  # 그 전 단계 이름들만 있으면 됨
            del (State_All)  # 메모리 아끼기
            break

        for i in range(len(asset_division)):
            if (asset_division[i]["State"] == 'send_bin_to_up'):
                asset_division[i]["State"] = send_bin_to_up_Completion(asset_division[i]["sym_name[b]"], asset_division[i]["real_send_amount"], asset_division[i]["bin_Min_Withdraw_Size[b]"], asset_division[i]["point_of_buy_bin_fu_amount_2"], asset_division[i]["보내기 전 업비트 잔고"])
                time.sleep(3)

            if (asset_division[i]["State"] == '청산 80% 위기 포지션 강제 종료_3'):
                # asset_division[i]["보내기 전 업비트 잔고"] = before_send_to_up_balace
                if (upbit.get_balance("KRW-" + asset_division[i]["sym_name[b]"]) >= asset_division[i]["보내기 전 업비트 잔고"] + asset_division[i]['real_send_amount']):
                    asset_division[i]["State"] = "청산 80% 위기 포지션 강제 종료_4"  # 전송완료 확인

            if (asset_division[i]["State"] == "청산 80% 위기 포지션 강제 종료_4"):  # 바이낸스 청산위기 포지션 종료 후 업비트에 도착하면 바로 파는 코드
                try:
                    ret = upbit.sell_market_order("KRW-" + asset_division[i]["sym_name[b]"], asset_division[i]['real_send_amount'])  # 있는현금만큼 구매#갯수로 구매가능하면..?
                    print(ret)
                    print("청산 80% 위기 포지션 강제 종료_send_bin_to_up_Completion")
                except:
                    pass

        for i in range(len(asset_division)):
            sending_sym_2 = []
            for j in range(len(asset_division)):
                if (asset_division[j]["State"] == 'send_bin_to_up'):  # 전송중인 코인명 가져옴
                    sending_sym_2.append(asset_division[j]['sym_name[b]'])

            if (asset_division[i]["State"] == 'step_2_1'):
                if ((asset_division[i]['sym_name[b]'] in sending_sym_2) == False):  # 전송중인 심볼이 두개가 곂치지 않게 함.(곂치는 경우 pass)
                    asset_division[i]['State'], asset_division[i]['보내기 전 업비트 잔고'] = send_bin_to_up(asset_division[i]['sym_name[b]'], asset_division[i]['up_add'], asset_division[i]['up_seadd'], asset_division[i]['real_send_amount'], asset_division[i]['point_of_Withdrow_UP_amount_2'])
                else:
                    pass

        for i in range(len(asset_division)):
            if (asset_division[i]["State"] == 'send_bin_to_up'):
                asset_division[i]["State"] = send_bin_to_up_Completion(asset_division[i]["sym_name[b]"], asset_division[i]["real_send_amount"], asset_division[i]["bin_Min_Withdraw_Size[b]"], asset_division[i]["point_of_buy_bin_fu_amount_2"], asset_division[i]["보내기 전 업비트 잔고"])
                time.sleep(3)

            if (asset_division[i]["State"] == '청산 80% 위기 포지션 강제 종료_3'):
                # asset_division[i]["보내기 전 업비트 잔고"] = before_send_to_up_balace
                if (upbit.get_balance("KRW-" + asset_division[i]["sym_name[b]"]) >= asset_division[i]["보내기 전 업비트 잔고"] + asset_division[i]['real_send_amount']):
                    asset_division[i]["State"] = "청산 80% 위기 포지션 강제 종료_4"  # 전송완료 확인

            if (asset_division[i]["State"] == "청산 80% 위기 포지션 강제 종료_4"):  # 바이낸스 청산위기 포지션 종료 후 업비트에 도착하면 바로 파는 코드
                try:
                    ret = upbit.sell_market_order("KRW-" + asset_division[i]["sym_name[b]"], asset_division[i]['real_send_amount'])  # 있는현금만큼 구매#갯수로 구매가능하면..?
                    print(ret)
                    print("청산 80% 위기 포지션 강제 종료_send_bin_to_up_Completion")
                except:
                    pass

    while True:
        for i in range(len(asset_division)):
            if (asset_division[i]["State"] == 'send_bin_to_up_Completion'):
                asset_division[i]['State'], asset_division[i]['step_2_2_up_krw_asset'], asset_division[i]['step_2_2_bin_fu_usdt_asset'], asset_division[i]['x4'], asset_division[i]['y4'], asset_division[i]['Usdt_2_2'] = step_2_2(asset_division[i]['x3'], asset_division[i]['y3'], asset_division[i]['point_of_buy_bin_spot_ticker_2'], asset_division[i]['point_of_buy_bin_fu_ticker_2'], asset_division[i]['expect_x4'], asset_division[i]['expect_y4'], asset_division[i]['sym_name[b]'], asset_division[i]['real_send_amount'], asset_division[i]['point_of_buy_bin_fu_amount_2'], User_data['up_market_fee'], User_data['bin_future_market_fee'], asset_division[i]['future_leverage'], asset_division[i]['Usdt_1_1'], asset_division[i]['step_1_1_up_krw_asset'], asset_division[i]['step_1_1_bin_fu_usdt_asset'], asset_division[i]['rest_step_1_1_bin_fu_usdt_asset'], asset_division[i]['div_unit'], asset_division[i]['want_premium_step_2_1'])

        State_All = [asset_division[w]["State"] for w in range(len(asset_division))]  # 중복이 없어야 종료 됨.
        if (len(set(State_All) & {'send_bin_to_up_Completion'}) == 0):  # 그 전 단계 이름들만 있으면 됨
            del (State_All)  # 메모리 아끼기
            break


    while True:
        for i in range(len(asset_division)):
            if (asset_division[i]["State"] == 'step_2_2'):  # 데이터 엑셀 저장
                asset_division[i]['State'], asset_division[i]['save_state'], asset_division[i]['up_asset'], asset_division[i]['binance_asset'], asset_division[i]['future_leverage'] = final_fun(asset_division[i]['qwer'], i, asset_division[i]['save_state'], len(asset_division[i]['save_state']) - 1,asset_division[i]['up_asset'], asset_division[i]['binance_asset'], asset_division[i]['Using_asset'],asset_division[i]['x1'], asset_division[i]['y1'], asset_division[i]['Usdt_1_1'],asset_division[i]['sym_name[a]'], asset_division[i]['future_leverage'],asset_division[i]['point_of_buy_UP_ticker_1'], asset_division[i]['point_of_buy_UP_amount_1'],asset_division[i]['point_of_buy_bin_fu_ticker_1'], asset_division[i]['point_of_buy_bin_fu_amount_1'],asset_division[i]['second_using_asset'], asset_division[i]['x2'], asset_division[i]['y2'],asset_division[i]['Usdt_1_2'], asset_division[i]['sym_name[b]'], asset_division[i]['x3'],asset_division[i]['y3'], asset_division[i]['Usdt_2_1'], asset_division[i]['point_of_buy_bin_spot_ticker_2'],asset_division[i]['point_of_buy_bin_spot_amount_2'], asset_division[i]['point_of_buy_bin_fu_ticker_2'],asset_division[i]['point_of_buy_bin_fu_amount_2'], asset_division[i]['x4'], asset_division[i]['y4'],asset_division[i]['Usdt_2_2'], asset_division[i]['step_2_2_up_krw_asset'],asset_division[i]['step_2_2_bin_fu_usdt_asset'], asset_division[i]['step_1_1_up_krw_asset'],asset_division[i]['step_1_1_bin_fu_usdt_asset'], asset_division[i]['rest_step_1_1_up_krw_asset'],asset_division[i]['rest_step_1_1_bin_fu_usdt_asset'], asset_division[i]['step_1_2_bin_spot_usdt_asset'],asset_division[i]['step_1_2_bin_fu_usdt_asset'], asset_division[i]['step_2_1_bin_spot_usdt_asset'],asset_division[i]['step_2_1_bin_fu_usdt_asset'], asset_division[i]['rest_step_2_1_bin_spot_usdt_asset'],asset_division[i]['rest_step_2_1_bin_fu_usdt_asset'], asset_division[i]['want_premium_step_1_1'],asset_division[i]['want_premium_step_2_1'])
                # 다시 사용할 데이터 빼고 전부 삭제
                asset_division_keys = list(asset_division[i].keys())
                asset_division_keys = list(set(asset_division_keys) - {'State', 'save_state', 'up_asset', 'binance_asset', 'adjust_leverage', 'qwer', 'div_unit', 'up_market_fee', 'bin_spot_market_fee', 'bin_Coin_M_future_market_fee', 'want_premium_step_1_1', 'want_premium_step_2_2','future_leverage'})  # @@ 옵션 (option) 여기에 없애면 안될 변수들 저장.
                print(i, "final_fun")
                for j in range(len(asset_division_keys)):
                    asset_division[i][asset_division_keys[j]] = asset_division_keys[j]

        State_All = [asset_division[w]["State"] for w in range(len(asset_division))]  # 중복이 없어야 종료 됨.
        if (len(set(State_All) & {'step_2_2'}) == 0):  # 그 전 단계 이름들만 있으면 됨
            del (State_All)  # 메모리 아끼기
            break