#binance.fees로 수수료 가져올수 있다!!

##해야할것 4번 (최적안 찾기)시간줄이기
# 자본 나누는거 깔끔하게 생각하기.. 이익의 얼마
# 서버 URL이랑 test 입력하기
# 패키지 따로 저장하기
# 선물가격 정보 티커를 못 가져 오고 있음
# @자본을 입력 vs 자본 자동화 거래
# if문 시간 줄이기
#_Usdt가 붙지 않는 이상 원화 기준
#50만원으로 바이낸스에서 엄청난 거래량이 들어오면서 역프이고 전송불가 상태이면 사고 30%이득보면 파는로직..?
# for 문안에 if 문으로 만약 실현가능 수익이 높으면 바로 break=>서칭하는동안 둘다 가능..
#@김프가 상황에 따라서 -1~-2까지가 최소값이 되는경우가 있음 이 경우를 대비해야함,
#@ 내 자본 대비 코인 수수료가 1% 미만인 코인들만 서칭하는 로직 추가해보기.
# 추가할 로직:
# 1. 수익율 계산해서 어디다가 적기
# 2.오를 가능성이 없는 코인은 재전송 하는것.=>while과 Try로 쓰기
# 3.if문 데이터 프레임 형식으로 만들면 더 빠르려나..
# 4. 전송가능 코인만큼만 구매하고, 자본 분배 (첫 번쨰)
# 5. 사용가능 자본만 ..어떻게 하기.
#  김프가 8%이상 끼면 해외자본 한국으로 보내는 로직 추가 그리고 김프가 2%미만이면 해외로 다시 한국 자본 보내는 로직.
######
#@코인 전송 수수료(자본대비)를 0.5%로 바꿀까?
# 1.거래수수료를 생각한 조금더 자세한 계산
# 2.호가창을 확인한 좀더 정확한 계산
# 3.찾는 속도를 개선한 좀 더 빠른 써칭
# 4.100,1000만원일때의 수익율
# 5.정확히 살수있는개수만큼만 사고 나머지 계산제외해야함
######
#ck
import sys
sys.setrecursionlimit(1000000)#재귀함수 제한 늘리기
import pandas as pd
import numpy as np
import pip
import pyupbit  # 업비트#버젼1.1.7
print(pyupbit.Upbit)
import ccxt  # 바이낸스
print(ccxt)
import pprint
import time
import math
import sys
import requests
import json
# api json 파싱 python 업비트
import jwt  # PyJWT
import uuid
import requests
from urllib.parse import urlencode
from binance.client import Client
##@ 0.기본셋팅
sicle = 0
import binance
import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests
from binance.client import Client
########선물거래를 위해#######
from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *
from binance_f.model.constant import *

# 암호키 가져옴.
request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)
server_url = 'https://api.upbit.com'
##############################소수점 정리....##############################################
def Bin_Minimum_FU_Order_Size(symbol):
    aa =next((item for item in client.futures_exchange_info()['symbols']if item['symbol']==symbol+'USDT'),None)
    Bin_Minimum_Order_Size = float(next((item for item in aa['filters'] if item['filterType']=='MARKET_LOT_SIZE'),None)['minQty'])
    return Bin_Minimum_Order_Size

def Bin_Minimum_Order_Size(symbol):
    aa =next((item for item in client.get_exchange_info()['symbols']if item['symbol']==symbol+'USDT'),None)
    Bin_Minimum_Order_Size = float(next((item for item in aa['filters'] if item['filterType']=='LOT_SIZE'),None)['minQty'])
    return Bin_Minimum_Order_Size

###########업비트에서 환율 조회.
def upbit_get_usd_krw():
    url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    exchange = requests.get(url, headers=headers).json()
    return exchange[0]['basePrice']

def Bin_Minimum_Withdraw_Size(symbol):
    aa = client.get_asset_details()['assetDetail'][symbol]['minWithdrawAmount']
    return aa

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
Usdt = upbit_get_usd_krw()
print("Usdt =", Usdt)


# https://docs.upbit.com/docs/market-info-trade-price-detail
################################원화 마켄 주문 최소 주문 가격 단위###########################
def UP_Minimum_Order_cash_Size(symbol):
    up_pre = pyupbit.get_current_price("KRW-" + symbol)  # 해당코인 가격조회
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

###########################################################################################


# 업비트 잔고 조회 및 해당 코인 가격에 맞는 가격 도출 기능
access_key = "PrB8rZnXbvsGpCjhPC79PmbZZV10bMY2Tt59Ms3V"
secret_key = "JuHCBPzvJF9V5JX0lXUwPIgbCe9yxLDKfYTC7YtL"
upbit = pyupbit.Upbit(access_key, secret_key)

# 바이낸스 잔고조회
binance = ccxt.binance({
    'apiKey': 'SE4VoeIa2ObXkxooN2NcYJhv0FYBgffmbsn9ODtqXtteY9gs2eX8L1adyYAyC8Im',
    'secret': '1MPys7009oUtxGO5BjLB9quBtsBK5Dk54ooVIRLARpTLTy2x0IxFZqcIewNvmMCn'})

client = Client(api_key='SE4VoeIa2ObXkxooN2NcYJhv0FYBgffmbsn9ODtqXtteY9gs2eX8L1adyYAyC8Im',
                api_secret='1MPys7009oUtxGO5BjLB9quBtsBK5Dk54ooVIRLARpTLTy2x0IxFZqcIewNvmMCn')

#########################################전송가능 심볼명#########################################
######심볼명 예외처리로 중복제거를 위해######
def removeAllOccur(l, i):
    try:
        while True: l.remove(i)
    except ValueError:
        pass
#########################################

while True:
###################################################################################################################기본정보############################################
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
    ###############################################################################################

    #####사용가능 비용(@업비트 수수료 0.05%)############################################
    # 달러환율(업비트기준)
    Usdt = upbit_get_usd_krw()
    print(Usdt)
    balance = binance.fetch_balance()  # free:보유중인 코인, used:거래진행중인 코인 total:전체코인
    print("총 자본", upbit.get_balance("KRW") + float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['walletBalance']) * Usdt + balance['USDT']['free'] * Usdt)
    # 업비트 현물계좌 원화(현금) 확인
    up_asset = upbit.get_balance("KRW")  # 계좌 현금 확인
    print(up_asset)

    # ##@@@@업비트 자본 50 만원은 내 생각대로 투자하기
    # up_asset = up_asset - 500000

    # @또는 주석처리하고 원하는 자본 원화로 입력
    ##@@@개시증거금이 아니라 시장가 수수료 0.05%일경우계산 # 업비트 유동자본 수수료 뺸 가격만큼만 매수가능 (자본 맞추기전 그냥 빼고 시작.)
    up_asset = up_asset - up_asset * 0.0005 #아직 전송수수료 계산 안됨.
    print(up_asset, "업비트 유동 자본(조정 수수료만제거)")
    #
    # @@@@@@ ###업비트 자본이 1100 만원 이상이면 1100만원으로 고정
    # if (up_asset >11000000):
    #     up_asset = 11000000

    # 바이낸스 선물계좌 달러 확인
    bin_fu_ass = float(
        next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['walletBalance'])
    print("바이낸스 선물계좌 달러 잔고 확인:", bin_fu_ass)

    ######자본자동화################################################
    ##@@@ -0.01은 바이낸스 개시증거금(공식이 생각보다 복잡한데 10배율이면 보통0.01 달러면 됨 하지만 자본이 커지면..? 다시 생가해보자)
    ##@@@개시증거금은 레버리지 올릴시 계산 필요 북마크 참조
    ##https://www.google.com/search?q=%EA%B2%A9%EB%A6%AC%EA%B0%9C%EC%8B%9C%EC%A6%9D%EA%B1%B0%EA%B8%88&oq=%EA%B2%A9%EB%A6%AC%EA%B0%9C%EC%8B%9C%EC%A6%9D%EA%B1%B0%EA%B8%88&aqs=chrome..69i57j0i512l6j69i65.4378j1j7&sourceid=chrome&ie=UTF-8
    ###시장가 수수료 0.04%일경우계산
    bin_fu_ass = bin_fu_ass - bin_fu_ass * 0.0004
    binance_asset = bin_fu_ass * Usdt
    # binance_asset = (bin_fu_ass - 0.016) * Usdt  # 바이낸스 자본 원화(현금)#10%일시 시장가 수수료로 뺴버림


    print(binance_asset, "원 바이낸스 자본(조정 전)")
    ##############1배율 일시.###########################################
    if (up_asset < binance_asset):  # 작은 자본의 가격을 따라간다.
        binance_asset = up_asset
    if (binance_asset <= up_asset):
        up_asset = binance_asset

    ##레버리지도 입력
    future_leverage = math.floor(up_asset / binance_asset)
    # if (future_leverage >= 10):
    #     future_leverage = 10
    # if (future_leverage < 1):
    #     print("업비트 자본부족")
    #     sys.exit()
    # print(future_leverage, "자본에 맞춘 레버리지 배율")
    # up_asset = binance_asset * future_leverage
    # binance_asset = up_asset / future_leverage
    ###################################################
    # accumulate_fee = 0.05 * 2 + 0.08 * 2 + 0.04 * 4 * future_leverage  # @ 예상되는 누적수수료.

    print(binance_asset, "바이낸스 자본(조정 후)", up_asset, "업비트 자본(조정 후)")
    Using_asset = binance_asset + up_asset  # @ 쓰고 있는 총자본
    print("쓰고 있는 총 자본", Using_asset)
    ##########################################################################
    # 업비트=>바이낸스 전송코인#차익이 클 때
    # 자본대비 전송수수료, 역프를 계산하여 최대 이익을 낼 수 있는 코인 선정
    # per = 0.8  # 최저값과 최고값의 순차익

    time.sleep(5)
###################################################################################################################기본 정보############################################
#자본 대비 쓸 수 있는 심볼명만 추출(시작)##################################################################################################################################
#def로 정의 가능한가?
    print(binance_asset, "바이낸스 자본(조정 후)", up_asset, "업비트 자본(조정 후)")
    while True:
        for i in range(len(sym_name)):

            up_pre = pyupbit.get_current_price('KRW-' + sym_name[i])
            bin_ticker = ccxt.binance().fetch_ticker(sym_name[i] + '/USDT')['close']
            bin_fu_ticker = float(
                next((item for item in client.futures_ticker() if item['symbol'] == sym_name[i] + 'USDT'), None)[
                    'lastPrice'])
            bin_pre = bin_fu_ticker * Usdt


            #####업비트 => 바이낸스 전송가능정보와 코인 수수료 가져오는코드#########################

            server_url = 'https://api.upbit.com'
            query = {'currency': sym_name[i], }
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
            upbit_withdraw_fee = float(res.json()['currency']['withdraw_fee']) * up_pre
            #         print(symbol_send_fee,"업비트 보낼 시 심볼 전송 가격")

            bin_sym_send_state = res.json()['withdraw_limit']['can_withdraw']  # 출금지원가능여부

            if (bin_sym_send_state == True):
                pass
            else:
                print(sym_name[i], "해당코인 업비트에서 바이낸스로 출금 불가상태")
            #         print(bin_sym_send_state,sym_name[i],"출금지원가능여부")
            ########################################################################
            # 업비트 계좌 현금 확인
            up_can_order_amout = up_asset
            Decimal_rounding = UP_Minimum_Order_cash_Size(sym_name[i])
            up_can_order_amout = (up_can_order_amout // Decimal_rounding) * Decimal_rounding

            up_can_order_amout = up_can_order_amout + symbol_fee##여기서 오류 날 수도 있음 딱 맞아 떨어지면
            can_send_Decimal = float(res.json()['withdraw_limit']['minimum'])  # 전송가능 최소량@@이게 잇어야 계산 가능
            up_can_order_amout = (up_can_order_amout // can_send_Decimal) * can_send_Decimal

            binance_asset = up_can_order_amout  # @마진증거금도 없이 계산하긴함
            # print(sym_name[i],up_can_order_amout)
            # print('binance_asset', binance_asset, 'up_asset', up_can_order_amout, '288줄')
            ###################################################################
            ############추가 ... 입출금 상태는 주소로 받아야댐..
            try:
                query = {'currency': sym_name[i], }
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
            # print(up_add, up_seadd)

            except KeyError:
                bin_sym_send_state_2 = False
                print(sym_name[i], "해당코인 입금 불가상태")

            # @@##############################################################################

            bin_ticker = ccxt.binance().fetch_ticker(sym_name[i] + '/USDT')['close']
            binance_withdraw_fee = client.get_asset_details()['assetDetail'][sym_name[i]][
                                       'withdrawFee'] * bin_ticker * Usdt

            #### 업비트 해당코인 입금 주소 생성요청
            try:
                query = {'currency': sym_name[i], }
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

            except KeyError:
                up_sym_send_state = False
                print(sym_name[i], "해당코인 바이낸스에서 업비트 입금 불가상태")
            #######자본대비 코인전송 수수료 (뺄것)#코인별 프리미엄

            up_sym_send_state_2 = client.get_deposit_address(asset=sym_name[i])['success']

            if ((bin_sym_send_state == True) and ((upbit_withdraw_fee / up_can_order_amout) < 0.01) and (
                    bin_sym_send_state_2 == True)) and (up_sym_send_state_2 == True):
                print("이름", sym_name[i])
            #             bin_address = client.get_deposit_address(asset=sym_name[i])['address']
            #             bin_Memo = client.get_deposit_address(asset=sym_name[i])['addressTag']
            #             print('bin_address',bin_address)
            #             print('bin_Memo',bin_Memo)
            #             print("__________________________________23523___________________________")
            else:
                sym_name[i] = 'remove'

            if ((up_sym_send_state == True) and (binance_withdraw_fee / binance_asset) < 0.01):
                print("이름", sym_name[i])
            #             bin_address = client.get_deposit_address(asset=sym_name[i])['address']
            #             bin_Memo = client.get_deposit_address(asset=sym_name[i])['addressTag']
            #             print('bin_address',bin_address)
            #             print('bin_Memo',bin_Memo)
            #             print("______________________________asdasd_______________________________")
            else:
                sym_name[i] = 'remove'
            ###@@@ BNB코인 배제
            if (sym_name[i] == 'CHZ' or sym_name[i] == 'ETH' or sym_name[i] == 'ANKR ' or sym_name[i] == 'LINK' or sym_name[i] == 'BAT'or sym_name[i] == 'SXP' or sym_name[i] == 'ETC'):
                sym_name[i] = 'remove'
            ###@@@ 이더리움 코인 배제
            if (sym_name[i] == 'OMG' or sym_name[i] == 'MANA' or sym_name[i] == 'ZRX ' or sym_name[i] == 'ENJ' or sym_name[i] == 'STORJ' or sym_name[i] == 'KNC' or sym_name[i] == 'SRM' or sym_name[i] == 'SAND' or sym_name[i] == 'CVC'):
                sym_name[i] = 'remove'
            if (sym_name[i] == 'NEO' or sym_name[i] == 'BCH' or sym_name[i] == 'SC' or sym_name[i] == 'QTUM'):##@@이거 나중에 지우기.BCH는 전송시간이 오래걸리고 NEO는 소수점이 극혐임.(코인은 비싼대 소수점 이 )#SC코인은 전송시간 너무김 퀀텀도 전송시간 너무 김
                sym_name[i] = 'remove'

        removeAllOccur(sym_name, 'remove')
        print(sym_name, len(sym_name))
        time.sleep(10)
        break
#자본 대비 쓸 수 있는 심볼명만 추출(끝)####################################################################################################################################
    while True:
        min_rate = 100
        min_rate_name = 0
        send_to_bin_optimal_symbol = 0

        max_rate = -100
        max_rate_name = 0
        send_to_up_optimal_symbol = 0

        Arbitrage = 0  # 차익
        will_Realize_Arbitrage = 0
        Usdt = upbit_get_usd_krw()

        for i in range(len(sym_name)):

            # 현재가 조회#업비트
            up_pre = pyupbit.get_current_price('KRW-' + sym_name[i])  # 업비트 현재가 조회#리플이든 비트코인이든
            # print ("업비트가격",up_pre)

            # 현재가 조회#바이낸스
            bin_ticker = ccxt.binance().fetch_ticker(sym_name[i] + '/USDT')['close']

            # 바이낸스 해당코인 선물 현재가
            bin_fu_ticker = float(next((item for item in client.futures_ticker()if item['symbol']==sym_name[i]+'USDT'),None)['lastPrice'])
            # print(bin_fu_ticker)

            # print(bin_ticker)#최근거래@@bin_tiker를 bin_futiker로?
            bin_pre = bin_fu_ticker * Usdt
            # bin_pre = bin_ticker * Usdt

            #####업비트 => 바이낸스 전송가능정보와 코인 수수료 가져오는코드#########################

            server_url = 'https://api.upbit.com'
            query = {'currency': sym_name[i], }
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
            upbit_withdraw_fee = float(res.json()['currency']['withdraw_fee']) * up_pre
            #         print(upbit_withdraw_fee,"업비트 보낼 시 심볼 전송 가격")

            bin_sym_send_state = res.json()['withdraw_limit']['can_withdraw']  # 출금지원가능여부

            if (bin_sym_send_state == True):
                pass
            else:
                print(sym_name[i], "해당코인 업비트에서 바이낸스로 출금 불가상태")
            #         print(bin_sym_send_state,sym_name[i],"출금지원가능여부")
            ########################################################################
            # 업비트 계좌 현금 확인&소수점6자리까지 자르기
            up_can_order_amout = up_asset
            Decimal_rounding = UP_Minimum_Order_cash_Size(sym_name[i])
            # print(Decimal_rounding)
            up_can_order_amout = (up_can_order_amout // Decimal_rounding) * Decimal_rounding
            # print(up_can_order_amout)

            up_can_order_amout = up_can_order_amout + symbol_fee##여기서 오류 날 수도 있음 딱 맞아 떨어지면
            can_send_Decimal = float(res.json()['withdraw_limit']['minimum'])  # 전송가능 최소량@@이게 잇어야 계산 가능
            up_can_order_amout = (up_can_order_amout // can_send_Decimal) * can_send_Decimal

            binance_asset = up_can_order_amout  # @마진증거금도 없이 계산하긴함
            # print('binance_asset',binance_asset,'up_asset',up_asset,'288줄')
            ###################################################################
            ############추가 ... 입출금 상태는 주소로 받아야댐..
            try:
                query = {'currency': sym_name[i],}
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
            # print(up_add, up_seadd)

            except KeyError:
                bin_sym_send_state_2 = False
                print(sym_name[i], "해당코인 입금 불가상태")

            # @@##############################################################################

            bin_ticker = ccxt.binance().fetch_ticker(sym_name[i] + '/USDT')['close']
            binance_withdraw_fee = client.get_asset_details()['assetDetail'][sym_name[i]]['withdrawFee'] * bin_ticker * Usdt

            # 김치프리이미엄이고  ## 전송시간도 가져오면 좋을듯

            #### 업비트 해당코인 입금 주소 생성요청
            try:
                query = {'currency': sym_name[i],}
                query_string = urlencode(query).encode()

                m = hashlib.sha512()
                m.update(query_string)
                query_hash = m.hexdigest()

                payload = {
                    'access_key': access_key,
                    'nonce': str(uuid.uuid4()),
                    'query_hash': query_hash,
                    'query_hash_alg': 'SHA512',}

                jwt_token = jwt.encode(payload, secret_key)
                authorize_token = 'Bearer {}'.format(jwt_token)
                headers = {"Authorization": authorize_token}

                res = requests.post(server_url + "/v1/deposits/generate_coin_address", params=query,
                                    headers=headers)
                up_add = res.json()['deposit_address']
                up_sym_send_state = True
                up_seadd = res.json()['secondary_address']
            # print(up_add, up_seadd)

            except KeyError:
                up_sym_send_state = False
                print(sym_name[i], "해당코인 바이낸스에서 업비트 입금 불가상태")
            ###바이낸스 입금 불가상태인 경우가 있음.

            up_sym_send_state_2 = client.get_deposit_address(asset=sym_name[i])['success']

            #######자본대비 코인전송 수수료 (뺄것)#코인별 프리미엄
            new_rate = ((up_pre / bin_pre) - 1) * 100
            new_bin_fee_by_asset_rate = (upbit_withdraw_fee / up_can_order_amout) * 100
            new_up_fee_by_asset_rate = (binance_withdraw_fee / binance_asset) * 100

            # print( 'sym_name[i]',sym_name[i],'new_bin_fee_by_asset_rate',new_bin_fee_by_asset_rate,'new_up_fee_by_asset_rate',new_up_fee_by_asset_rate)

            if (i == 0):
                to_bin_fee_by_asset_rate = new_bin_fee_by_asset_rate
                to_up_fee_by_asset_rate = new_up_fee_by_asset_rate

            # 김프+내자본대비 전송수수료가 가장 적은 것
            # print(new_rate,min_rate, new_bin_fee_by_asset_rate, bin_sym_send_state, upbit_withdraw_fee / up_can_order_amout, sym_name[i], up_can_order_amout, upbit_withdraw_fee, new_rate + new_bin_fee_by_asset_rate)
            if (new_rate + new_bin_fee_by_asset_rate < min_rate + to_bin_fee_by_asset_rate) and (bin_sym_send_state == True) and ((upbit_withdraw_fee / up_can_order_amout) < 0.01) and (bin_sym_send_state_2 == True) and (up_sym_send_state_2 == True):
                # @심볼 전송료
                to_bin_fee_by_asset_rate = new_bin_fee_by_asset_rate
                min_upbit_withdraw_fee = upbit_withdraw_fee
                min_rate = new_rate
                min_rate_name = sym_name[i]
                print('min_rate_name', min_rate_name, 'min_rate', min_rate ,'to_bin_fee_by_asset_rate + min_rate',to_bin_fee_by_asset_rate+min_rate)

            # 김프가 가장 크고 + 내 자본대배 수수료가 가장 적은것
            # print(new_rate, max_rate, new_up_fee_by_asset_rate, up_sym_send_state,binance_withdraw_fee / binance_asset, sym_name[i], binance_asset ,max_rate - new_up_fee_by_asset_rate)
            if (new_rate - new_up_fee_by_asset_rate > max_rate - to_up_fee_by_asset_rate) and (up_sym_send_state == True) and ((binance_withdraw_fee / binance_asset) < 0.01) and (up_sym_send_state_2 == True):
                to_up_fee_by_asset_rate = new_up_fee_by_asset_rate
                max_binance_withdraw_fee = binance_withdraw_fee
                max_rate = new_rate
                max_rate_name = sym_name[i]
                print('max_rate_name', max_rate_name, 'max_rate', max_rate, 'max_rate - to_up_fee_by_asset_rate',max_rate - to_up_fee_by_asset_rate)
            #@@@@@@@@@@@@@@@@@
            # if (-min_rate-to_bin_fee_by_asset_rate<-1):#-1 보다 작으면 빠르게 나가서 전송 하기.
            #     gogo = True
            #     break
########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################
                ##@@@@@@@@@출금불가상태이고 역프가 많이낀 코인 찾으면 50만원 가지고 배팅 ㄱㄱ
            if ((((up_pre / bin_pre) - 1) * 100) < -(4) and bin_sym_send_state_2 == False):  # 2%더 있을 시 작동하도록 함.
                # @좁아지면 파는코딩
                # up_can_order_amout = 500000  # @ 50만원으로할지 고민해볼것.

                ret = upbit.buy_market_order("KRW-" + sym_name[i], up_can_order_amout)  # 업비트자본만큼구매
                print(ret)

                buy_time_ticker = pyupbit.get_current_price("KRW-" + sym_name[i])  # 업비트 현재가 조회

                # 주문 신청
                while True:
                    # 환율도 가져오기
                    up_pre = pyupbit.get_current_price("KRW-"+sym_name[i])  # 업비트 현재가 조회
                    bin_ticker = ccxt.binance().fetch_ticker(sym_name[i]+'/USDT')['close']  # 바이낸스 현재가 조회
                    bin_fu_ticker = float(next((item for item in client.futures_ticker() if item['symbol'] == sym_name[i] + 'USDT'),None)['lastPrice'])

                    bin_pre = bin_ticker * Usdt  # 해외거래소 환율 환산
                    Usdt = upbit_get_usd_krw()  # 환율정보 수신

                    print((((up_pre / bin_pre) - 1) * 100), "매도대기")

                    income_rate = buy_time_ticker/up_pre

                    ##@수익구간일떄 판매하는 코드로 바꾸기
                    if (-0.5 < (((up_pre / bin_pre) - 1) * 100) < 1 or (income_rate > 1.3) ):  # +,- 1%이내에 있을시, 30%이상의 수익이면 판매

                        balance = upbit.get_balance("KRW-" + sym_name[i])  # 계좌의 코인 수량 확인
                        print(balance)

                        resp = upbit.sell_market_order("KRW-" + sym_name[i], balance)  # 코인 수량만큼판매
                        pprint.pprint(resp)

                        break
                    time.sleep(1)
                    # 구매시 가격보다 1%이상 떨어지면 멈추는 기능 추가.go to?

                ##@@@@@@@@@입금(출금) 가능 상태이고 역프가 줄어들면 파는 로직
########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################

        # 리플 이더리움 스텔라 루멘 등은 그냥 빠르게 보내기 ###############
        #         if ((-1 < ((up_pre / bin_pre) - 1) * 100) and (sym_name[i] == "XRP", "XLM","ETH") and (up_sym_send_state == True)):# and ((binance_withdraw_fee / send_to_up_amont) < 0.01)):
        # #             max_rate_name = sym_name[i]
        # #             print(max_rate_name,'send_to_up_optimal_symbol')
        # #             break
        ##@@@@출금불가상태이고 역프가 많이낀 코인 찾으면 50만원 가지고 배팅 ㄱㄱ
        ##@@@@@입금(출금) 가능 상태이고 역프가 줄어들면 파는 로직


        #####서칭시간이 길어서 다시 재조회############
        print('min_rate_name', min_rate_name, 'min_rate', min_rate, "min_rate_name", min_rate_name,'min_rate + new_up_fee_by_asset_rate',min_rate + to_bin_fee_by_asset_rate)
        print('max_rate_name', max_rate_name, 'max_rate', max_rate, "max_rate_name", max_rate_name,'max_rate - new_up_fee_by_asset_rate',max_rate - to_up_fee_by_asset_rate)
        print()
        ##########
        up_pre = pyupbit.get_current_price('KRW-' + min_rate_name)  # 업비트 현재가 조회#리플이든 비트코인이든
        # 현재가 조회#바이낸스
        # bin_ticker = ccxt.binance().fetch_ticker(min_rate_name + '/USDT')['close']

        # @바이낸스 해당코인 선물 현재가
        bin_fu_ticker = float(next((item for item in client.futures_ticker() if item['symbol'] == min_rate_name + 'USDT'), None)['lastPrice'])
        # print(bin_fu_ticker)

        # print(bin_ticker)#최근거래@@bin_tiker를 bin_futiker로?
        bin_pre = bin_fu_ticker * Usdt
        # bin_pre = bin_ticker * Usdt
        min_rate = ((up_pre / bin_pre) - 1) * 100
        ###########
        up_pre = pyupbit.get_current_price('KRW-' + max_rate_name)  # 업비트 현재가 조회#리플이든 비트코인이든
        # 현재가 조회#바이낸스
        # bin_ticker = ccxt.binance().fetch_ticker(max_rate_name + '/USDT')['close']

        # @바이낸스 해당코인 선물 현재가
        bin_fu_ticker = float(next((item for item in client.futures_ticker() if item['symbol'] == max_rate_name + 'USDT'), None)['lastPrice'])
        # print(bin_fu_ticker)

        # print(bin_ticker)#최근거래@@bin_tiker를 bin_futiker로?
        #     bin_pre = bin_ticker * Usdt
        bin_pre = bin_fu_ticker * Usdt
        max_rate = ((up_pre / bin_pre) - 1) * 100
        print('max_rate', max_rate, 'min_rate', min_rate)
        ############################################################################################
        # new_bin_fee_by_asset_rate = (symbol_send_fee / up_can_order_amout) * 100
        # new_up_fee_by_asset_rate = (binance_withdraw_fee / binance_asset) * 100
        # 현재까지 실현되는 누적손익(%)

        will_Realize_Arbitrage = ((100-min_rate - to_bin_fee_by_asset_rate-0.2)/100) * ((100 + max_rate - to_up_fee_by_asset_rate)/100)

        # 헷징 시 아마도 얻을 차익
        Arbitrage = up_can_order_amout * ((100-min_rate - to_bin_fee_by_asset_rate-0.2)/100) * ((100 + max_rate - to_up_fee_by_asset_rate)/100)
        print("638줄 지우기",100-min_rate-to_bin_fee_by_asset_rate,100 + max_rate - to_up_fee_by_asset_rate)
        print('will_Arbitrage', Arbitrage, 'will_Realize_Arbitrage',will_Realize_Arbitrage)
        if (((Arbitrage > up_can_order_amout) and (will_Realize_Arbitrage > 1.011)) or (will_Realize_Arbitrage < 0)): #or gogo == True):##@@@@이부분 0 으로 고치면 김프일때 헷징하고 전송하게 됨.#역프끼고 전송료가 ㄱㅊ은 코인은 그대로 전송#(1-will_Realize_Arbitrage > accumulate_fee * (10 **-2)))
            # if (Arbitrage > per):#@
            # 실현되는 누적이익(%)

            send_to_bin_optimal_symbol = min_rate_name
            send_to_up_optimal_symbol = max_rate_name
            print('send_to_bin_optimal_symbol =', send_to_bin_optimal_symbol, 'Arbitrage=', Arbitrage,
                  'Realizing_Arbitrage=', will_Realize_Arbitrage, 'min_rate=', min_rate)
            print('send_to_up_optimal_symbol =', send_to_up_optimal_symbol, 'Arbitrage=', Arbitrage, 'will_Realize_Arbitrage=',
                  will_Realize_Arbitrage, 'max_rate', max_rate)
            break
        time.sleep(1)

    try:
        result = request_client.change_margin_type(symbol=send_to_bin_optimal_symbol + "USDT",
                                                   marginType=FuturesMarginType.ISOLATED)
        PrintBasic.print_obj(result)
    except:
        print("마진타입 변화 불필요")
        pass

    # 레버리지 변화 (자본에 따라 기본 10배)
    result = request_client.change_initial_leverage(symbol=send_to_bin_optimal_symbol + "USDT", leverage=future_leverage)
    PrintBasic.print_obj(result)

    print('binance_asset', binance_asset)
    #for문에서 해당코인 가격으로 계속 바뀌니까 옵티멀 값으로

    up_can_order_amout = up_asset
    Decimal_rounding = UP_Minimum_Order_cash_Size(send_to_bin_optimal_symbol)
    up_can_order_amout = (up_can_order_amout // Decimal_rounding) * Decimal_rounding


    # 바이낸스 해당코인 선물 현재가
    bin_fu_ticker = float(
        next((item for item in client.futures_ticker() if item['symbol'] == send_to_bin_optimal_symbol + 'USDT'), None)[
            'lastPrice'])

    # 바이낸스 해당코인 현물 현재가#사용할거면 394줄 읽어보기
    bin_ticker = ccxt.binance().fetch_ticker(send_to_bin_optimal_symbol + '/USDT')['close']

    ###@@@@좀더 자세히 고치기 주문 전송 ! #자본대비 살수있는양##이거주문 소수점 더러운데 ㄱㅊ으려나?
    #binance_asset = up_asset / future_leverage 을 해야 쓸쑤있는 한국 자본임 하지만 10배이면 10 배만큼 주문 가능
    binance_asset = up_can_order_amout
    # asset_symbol_quantity = (binance_asset / Usdt)-1#@@@@@증거금때무네.
    # asset_symbol_quantity = asset_symbol_quantity / bin_ticker#@선물 티커 vs 현물티커
    # asset_symbol_quantity = asset_symbol_quantity / bin_fu_ticker  # @선물 티커 vs 현물티커#floor 바꿈
    # asset_symbol_quantity = math.floor(asset_symbol_quantity * (10 ** -length_(Bin_Minimum_Order_Size(send_to_bin_optimal_symbol))))  # 최소 주문 가격단위 0.01달러~0.001
    # asset_symbol_quantity = asset_symbol_quantity * (10 ** length_(Bin_Minimum_Order_Size(send_to_bin_optimal_symbol)))  # 다시가격 맞춤
    # bin_can_order_asset_symbol_quantity = round(asset_symbol_quantity, -length_(Bin_Minimum_Order_Size(send_to_bin_optimal_symbol)))
    asset_symbol_quantity = ((binance_asset / Usdt)/ bin_fu_ticker) * (1 - 0.0004 * future_leverage)  # 바이낸스 시장가 수수료#@@이부분 맞나.. 수수료

    asset_symbol_quantity = asset_symbol_quantity#@@ 필요없는부분
    Decimal_rounding = Bin_Minimum_FU_Order_Size(send_to_bin_optimal_symbol)
    bin_can_order_asset_symbol_quantity = (asset_symbol_quantity // Decimal_rounding) * Decimal_rounding

    # 주문신청                             # 심볼            #sell 이면 숏 buy면 롱     # 시장가 거래         # 몇개 살것인지 (여기를 더 고민 ,잔고 또는 자본에 맞춰서 구매하게 만들어야함)
    result = request_client.post_order(symbol=send_to_bin_optimal_symbol + "USDT", side=OrderSide.SELL,
                                       ordertype=OrderType.MARKET,
                                       quantity=bin_can_order_asset_symbol_quantity)  # quantity수량.#Orderside sell 이면 판매
    PrintBasic.print_obj(result)

    # 업비트 주문신청
    ret = upbit.buy_market_order("KRW-" + send_to_bin_optimal_symbol, up_can_order_amout)  # 있는현금만큼 구매#갯수로 구매가능하면..
    pprint.pprint(ret)  # 구매주문확인

    point_of_buy_UP_ticker_1 = pyupbit.get_current_price("KRW-" + send_to_bin_optimal_symbol)  # 업비트 현재가 조회
    point_of_buy_bin_fu_ticker_1 = float(next((item for item in client.futures_ticker() if item['symbol'] == send_to_bin_optimal_symbol + 'USDT'), None)['lastPrice'])*Usdt
    print("1. 실제 헷징된 업비트 현물구매시점 가격 ,바이낸스 선물 구매시점 가격",point_of_buy_UP_ticker_1,point_of_buy_bin_fu_ticker_1)

    ######실제 주문 가격 (자본 배분을 위해)###############################
    # 바이낸스는 갯수로 주문해야함 #업비트는 원화로 주문해야함
    print('바이낸스 실제 주문량', bin_can_order_asset_symbol_quantity, '업비트 실제 주문량', up_can_order_amout/point_of_buy_UP_ticker_1)
    bin_real_order_price = (bin_can_order_asset_symbol_quantity * bin_fu_ticker) /future_leverage
    print('바이낸스 실제 주문 가격', bin_real_order_price*Usdt , '업비트 실제 주문 가격',up_can_order_amout)

    ###################################################################

    # @2.자산전송- 바이낸스 해당코인 입금주소 받아오기#################
    # from binance.client import Client
    # client = Client(api_key='SE4VoeIa2ObXkxooN2NcYJhv0FYBgffmbsn9ODtqXtteY9gs2eX8L1adyYAyC8Im',
    #                 api_secret='1MPys7009oUtxGO5BjLB9quBtsBK5Dk54ooVIRLARpTLTy2x0IxFZqcIewNvmMCn')

    ###########################################################
    time.sleep(2)

    # 코인 몇개 전송할 것인지######################################
    server_url = 'https://api.upbit.com'

    query = {'currency': send_to_bin_optimal_symbol, }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',}

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/withdraws/chance", params=query, headers=headers)
    print(res.json())

    # 해당 코인 전송수수료(해당코인 시가 * 전송 수수료)
    symbol_fee = float(res.json()['currency']['withdraw_fee'])
    print(symbol_fee)

    time.sleep(1)

    bin_sym_send_state = res.json()['withdraw_limit']['can_withdraw']  # 출금지원가능여부
    if (bin_sym_send_state == True):
        pass
    else:
        print(send_to_bin_optimal_symbol, "WARNING 구매한 상태인데 전송 불가상태")
    ############추가 ... 입출금 상태는 주소로 받아야댐..
    try:
        query = {'currency': send_to_bin_optimal_symbol, }
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
    # print(up_add, up_seadd)

    except KeyError:
        bin_sym_send_state_2 = False
        print(send_to_bin_optimal_symbol, "해당코인 입금 불가상태")

    if (bin_sym_send_state_2 == True):
        pass
    else:
        print(bin_sym_send_state_2, "WARNING 구매한 상태인데 전송 불가상태")
    ############################################################# sym_name[i], bin_sym_send_state_2
    time.sleep(1)
    ###########################################################
    # 코인 몇개 전송할 것인지######################################

    # access_key = 'PrB8rZnXbvsGpCjhPC79PmbZZV10bMY2Tt59Ms3V'
    # secret_key = 'JuHCBPzvJF9V5JX0lXUwPIgbCe9yxLDKfYTC7YtL'
    server_url = 'https://api.upbit.com'

    query = {'currency': send_to_bin_optimal_symbol,}
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',}

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get(server_url + "/v1/withdraws/chance", params=query, headers=headers)
    print(res.json())

    can_order_symbol_amount = float(res.json()['account']['balance'])  # 주문가능금액/수량
    can_order_symbol_amount = can_order_symbol_amount - symbol_fee
    can_send_Decimal = float(res.json()['withdraw_limit']['minimum'])  # 전송가능 최소량@@이게 잇어야 계산 가능
    can_order_symbol_amount = (can_order_symbol_amount // can_send_Decimal) * can_send_Decimal

    # 파이썬이 자꾸 소수점 자리를 가지고 있어서 여러번 씀 손대지 말것.#5로 하던지 6으로 하던지.

    time.sleep(2)
    ###########################################################
    bin_address = client.get_deposit_address(asset=send_to_bin_optimal_symbol)['address']
    bin_Memo = client.get_deposit_address(asset=send_to_bin_optimal_symbol)['addressTag']
    print(bin_address, bin_Memo)
    # @ 2.코인 출금 요청#########################
    # can_order_symbol_amount를 조심 가져오든지 해야함
    query = {
        'currency': send_to_bin_optimal_symbol,
        'amount': can_order_symbol_amount,
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

    print(res.json())
    send_amount = res.json()['amount']
    send_amount = float(send_amount)
    print(send_amount)
    ###########################################################
    ## @3.바이낸스 전송완료 확인 후 숏 포지션 종료 및 전송된 코인 판매

    ####전송확인###########
    while True:
        # 바이낸스 잔고조회
        # binance = ccxt.binance({
        #     'apiKey': 'SE4VoeIa2ObXkxooN2NcYJhv0FYBgffmbsn9ODtqXtteY9gs2eX8L1adyYAyC8Im',
        #     'secret': '1MPys7009oUtxGO5BjLB9quBtsBK5Dk54ooVIRLARpTLTy2x0IxFZqcIewNvmMCn',
        # })
        #
        # ##@ 출금이 안될 경우(24시간 제한 떄문에) 될 떄까지 while 문?=>그러면(274줄)2.바이낸스 코인 요청 //부분을 이 while 문 안에 들어가게 함

        balance = binance.fetch_balance()  # free:보유중인 코인, used:거래진행중인 코인 total:전체코인
        # 계좌 잔고 확인
        bin_fu_ticker = float(next((item for item in client.futures_ticker() if item['symbol'] == send_to_bin_optimal_symbol + 'USDT'),None)['lastPrice'])
        print("바이낸스 반대포지션으로 얼마나 상승 중인지 확인(109이면 청산임)(10 배 레버리지시. 이부분 고치기).",((bin_fu_ticker/point_of_buy_bin_fu_ticker_1)*100))
        if ((bin_fu_ticker/point_of_buy_bin_fu_ticker_1)*100)>9:#만약 바이낸스 잔고가 청산위기
            result = request_client.post_order(symbol=send_to_bin_optimal_symbol + "USDT", side=OrderSide.BUY,ordertype=OrderType.MARKET,quantity=bin_can_order_asset_symbol_quantity)  # quantity수량.#Orderside sell 이면 판매
            PrintBasic.print_obj(result)

            print("바이낸스 잔고 청산위기 강제 포지션 종료.",)

        print("바이낸스", send_to_bin_optimal_symbol, "전송 중", balance[send_to_bin_optimal_symbol]['free'])
        if (balance[send_to_bin_optimal_symbol]['free'] >= send_amount):
            break
        time.sleep(10)# @@ 바이낸스 api제한 걸림
    ######################

    ##@선물 거래 기록 가져와서 자본 배분하기.
    ##전송완료
    while True:
        time.sleep(1)
        #전송 완료시 자본 비교..
        bin_ticker = ccxt.binance().fetch_ticker(send_to_bin_optimal_symbol + '/USDT')['close'] * Usdt
        # bin_pre = bin_ticker
        bin_fu_ticker = float(next((item for item in client.futures_ticker() if item['symbol'] == send_to_bin_optimal_symbol + 'USDT'),None)['lastPrice']) * Usdt
        print(bin_ticker)
        rate_1 = min_rate
        rate_2 = ((point_of_buy_UP_ticker_1 / bin_ticker) - 1) * 100
        rate_3 = ((point_of_buy_UP_ticker_1 / bin_fu_ticker) - 1) * 100

        print(rate_1, rate_2, rate_3)
        print("이게 양수가 나온만큼 이득(%)",rate_2 - rate_1,"구매시점과 같은 차익인지 확인", rate_2, 'min_rate', min_rate, 'min_rate_name', min_rate_name
              ,"업비트 살때 가격 대비 선물시장 가격")
        For_No_liquidation = ((bin_fu_ticker / point_of_buy_bin_fu_ticker_1) - 1) * 100

        if (For_No_liquidation < 5):#5%이상 올랐을 떄 가망없다고 생각하고 이전에 헷징한 가격으로 들어감..
            break

        #예상보다 더 적은 차익을 낼 수 있을 떄 (손해가 최소화) 실행 .@@맞지?
        # if (point_of_buy_UP_ticker_1 *((100-min_rate - to_bin_fee_by_asset_rate)/100) <= bin_ticker *((100-rate_2 - to_bin_fee_by_asset_rate)/100)):
        #     print("팔 시점 나옴")
        #     break
        # time.sleep(1)
        if (bin_ticker >= bin_fu_ticker): #선물보다 현물이 더 클때에 현물을 판다(손해 최소화)
            print("팔 시점 나옴")
            break


    # 잔고만큼 판매 주문 전송
    order = binance.create_market_sell_order(send_to_bin_optimal_symbol + '/USDT',balance[send_to_bin_optimal_symbol]['free'])

    print(order)

    # 숏포지선 종료#주문신청 과 반대 포지션을 잡아서 거래 청산.
    result = request_client.post_order(symbol=send_to_bin_optimal_symbol + "USDT", side=OrderSide.BUY,
                                       ordertype=OrderType.MARKET,quantity=bin_can_order_asset_symbol_quantity)  # quantity수량.#Orderside sell 이면 판매
    PrintBasic.print_obj(result)

    point_of_buy_bin_ticker_1 = ccxt.binance().fetch_ticker(send_to_bin_optimal_symbol + '/USDT')['close']*Usdt
    print("1.실제 판매된 업비트 현물 ,바이낸스 선물",point_of_buy_bin_ticker_1,point_of_buy_bin_fu_ticker_1)

    #if 문안에서 끝낫을 상황을 고려해서 재정의.
    bin_ticker = ccxt.binance().fetch_ticker(send_to_bin_optimal_symbol + '/USDT')['close'] * Usdt
    bin_pre = bin_ticker
    # rate_2 = ((point_of_buy_UP_ticker_1 / bin_pre) - 1) * 100
    #
    # Realize_Arbitrage = -min_rate + (rate_2 - rate_1) - to_bin_fee_by_asset_rate ##@@맞니?
    # Realize_Arbitrage = -Realize_Arbitrage # @@기호 정의 잘못했었음.
    Realize_Arbitrage = rate_2 + to_bin_fee_by_asset_rate

    print('실제로 지금까지(1번[업비트=>바이낸스 이동])의 차익', -Realize_Arbitrage,'min_rate',min_rate)
    time.sleep(1)

    print(min_rate, rate_2, to_bin_fee_by_asset_rate, (rate_2 - rate_1), Realize_Arbitrage)
    print('min_rate', 'rate_2', 'to_bin_fee_by_asset_rate',' (rate_2 - rate_1)', 'Realize_Arbitrage')
    time.sleep(10)#@@거래 청산 후 바이낸스 사이트에서 달러러 주기까지 시간이 조금 걸림
    ##
    while True:
        #############################################################자본 분배1########################################################################
        # 선물 계정에서 현물계정으로 옮기는 코드#실제 주문 가격 만큼 이동
        # bin_fu_ticker = float(next((item for item in client.futures_ticker() if item['symbol'] == send_to_bin_optimal_symbol + 'USDT'),None)['lastPrice'])
        # print(bin_fu_ticker,"941줄 잘 되면 이부분 지우기.")
        # bin_real_order_price = (bin_can_order_asset_symbol_quantity * bin_fu_ticker) /future_leverage#현재가 가져와서 얼마나 잃었을지 계산
        # print(bin_real_order_price)
        # bin_real_order_price = bin_real_order_price*(1-0.0008*future_leverage)#수수료 차감하여 계산 시장가 1회 거래당 0.04
        # print(bin_real_order_price)
        balance = binance.fetch_balance()
        bin_fu_ass = float(
            next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['walletBalance'])
        print(bin_fu_ass, "선물지갑 달러 잔고 확인")

        # ## @@ 이부분 그냥 선물 계좌 달러 전부 이동..
        bin_real_order_price = bin_fu_ass  # binance_asset / Usdt #안되면 bin_fu_ass
        print(bin_real_order_price, "바이낸스 자본", binance_asset, Usdt)
        bin_real_order_price = math.floor(bin_real_order_price * (10 ** 6))
        print(bin_real_order_price)
        bin_real_order_price = bin_real_order_price * (10 ** -6)
        print(bin_real_order_price)
        bin_real_order_price = round(bin_real_order_price, 6)
        print(bin_real_order_price)
        try:
            ret = client.futures_account_transfer(asset="USDT", amount=bin_real_order_price,
                                                  type=2, )  # timestamp#type 2이 USDT선물계정으로#타입 1이 달러에서 선물계정/##가끔 전송 불가 코인이 있는데 이걸 어떻게 구분할지..#문제 찾음 BNB 방식이랑 이더리움 클래식 방식 전송방법이 있음 이중에서 BNB방식으로 보내는데 어떡하지..
            print(ret)
        except:
            pass

        time.sleep(1)  # @@@@이부분 while 문으로 현물지갑 선물지갑으로 돈 다 옮겨질 때풀리도록 변환하기(필요하면 try문추가).

        # 현물지갑 달러 잔고 확인
        bin_cash_ass_Usdt = float(next((item for item in client.get_account()['balances'] if item['asset'] == 'USDT'), None)['free'])
        print(bin_cash_ass_Usdt, "현물지갑 달러 잔고 확인")
        ###### 레버러지 비율만큼 자본 분배#########
        # @자동배분 좀 더생각send_to_up_amont = bin_fu_acc * (up_can_order_amout / (up_can_order_amout + bin_fu_acc * Usdt))#ex)10/(10+1)

        order_send_to_bin_fu_ass = (1 / 2) * bin_cash_ass_Usdt

        order_send_to_bin_fu_ass = math.floor(order_send_to_bin_fu_ass * (10 ** 6))
        order_send_to_bin_fu_ass = order_send_to_bin_fu_ass * (10 ** -6)
        order_send_to_bin_fu_ass = round(order_send_to_bin_fu_ass, 6)

        # 현물 계정에서 선물계정으로 옮기는 코드
        try:
            ret = client.futures_account_transfer(asset="USDT", amount=order_send_to_bin_fu_ass,
                                                  type=1, )  # timestamp#type 2이 USDT선물계정으로
            print(ret)
        except:
            pass

        print(order_send_to_bin_fu_ass, '업비트 보낼 자본 바이낸스 헷징 할 자본')

        time.sleep(1)

        # (업비트자본/(업비트자본+해외자본))X선물계좌달러=(내가 번돈+원래자본)
        # send_to_up_amont_Usdt = (1/2)*bin_cash_ass_Usdt
        send_to_up_amont_Usdt = order_send_to_bin_fu_ass  # 남은 현물지갑 달러 잔고 확인
        # @여기서 보낼 양 하는게 맞나?
        send_to_up_amont_Usdt = math.floor(send_to_up_amont_Usdt * (10 ** 6))
        send_to_up_amont_Usdt = send_to_up_amont_Usdt * (10 ** -6)
        send_to_up_amont_Usdt = round(send_to_up_amont_Usdt, 6)

        print(send_to_up_amont_Usdt, '업비트 보낼 자본 조정 후')
        ##########################자본 환율#######################################
        Usdt = upbit_get_usd_krw()

        binance_asset = order_send_to_bin_fu_ass * Usdt  # 업비트 현물 시장가 수수료
        up_asset = send_to_up_amont_Usdt * (1 - 0.001) * Usdt  # @시장가 수수료 (0.1%)차감하고 주문가능.#바이낸스 현물 시장가 수수료
        binance_Usdt_asset = order_send_to_bin_fu_ass  ##불필요 하긴 함.

        #######@4 전송할 코인 서칭###########################################################
        # 팔떄 전송완료후 차익이 남는지 확인하고 팔게 만들기
        # 수수료도 추가해서 Realize_Arbitrage가 가능할때에 보내기
        # 이번에 찾을땐 sym_name_u_b 르로 for문 돌리고 선물에서 공매도 안쳐지면 그냥 한국에서 보내서 팔기.

        # #############################################################자본 분배2########################################################################
        # balance = binance.fetch_balance()
        # up_asset = balance['USDT']['free'] * Usdt*(1 -0.001)#업비트에서 바이낸스 현물가에 도착한 자본이니까.#바이낸스현물 시장가 수수료 #0.1%
        # print(up_asset, "원 업비트 자본(조정 전)")

        # bin_fu_ass = float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['walletBalance'])
        # binance_asset = bin_fu_ass*(1 -0.0004) * Usdt  #@ 시장가수수료 차감하고 주문가능
        # print(binance_asset, "원 바이낸스 자본(조정 전)")

        ######전송 시간이 길었으니 다시 서칭###################################################################
        print(binance_asset, "바이낸스 자본(조정 후)", up_asset, "업비트 자본(조정 후)")
        if ((binance_asset + up_asset > Using_asset * 0.85) and (binance_asset > 50000) and (up_asset > 50000)):
            print(binance_asset + up_asset, "총 쓰이고 있는 자산")
            # 처음 유동자산의 0.85(김프15%까지 생각)넘을 시 말도 안된다고 판단
            break
        else:
            print("바이낸스 자본 확인 오류(서버문제)")

    if (up_asset < binance_asset):
        binance_asset = up_asset
    if (binance_asset < up_asset):
        up_asset = binance_asset
    order_send_to_bin_fu_ass = binance_asset / Usdt
    send_to_up_amont_Usdt = up_asset / Usdt
    binance_fu_Usdt_asset = order_send_to_bin_fu_ass

    ######전송 시간이 길었으니 다시 서칭###################################################################
    print(binance_asset, "바이낸스 자본(조정 후)", up_asset, "업비트 자본(조정 후)")
    # 업비트=>바이낸스 전송코인#차익이 클 때
    # 자본대비 전송수수료, 역프를 계산하여 최대 이익을 낼 수 있는 코인 선정
    # per =0.8 # 한 싸이클 돌면 0.075*10 + 0.05 +0.04 + 0.075 * 10 = 1.64

    # 현재가 조회#업비트
    up_pre = pyupbit.get_current_price('KRW-' +send_to_up_optimal_symbol)  # 업비트 현재가 조회#리플이든 비트코인이든

    # 현재가 조회#바이낸스
    bin_ticker = ccxt.binance().fetch_ticker(send_to_up_optimal_symbol+ '/USDT')['close']
    bin_pre = bin_ticker * Usdt
    binance_withdraw_fee = client.get_asset_details()['assetDetail'][send_to_up_optimal_symbol]['withdrawFee'] * bin_ticker * Usdt

    # 김치프리이미엄이고  ## 전송시간도 가져오면 좋을듯

    #### 업비트 해당코인 입금 주소 생성요청
    try:
        query = {'currency':send_to_up_optimal_symbol,}
        query_string = urlencode(query).encode()

        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',}

        jwt_token = jwt.encode(payload, secret_key)
        authorize_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorize_token}

        res = requests.post(server_url + "/v1/deposits/generate_coin_address", params=query,
                            headers=headers)
        up_add = res.json()['deposit_address']
        up_sym_send_state = True
        up_seadd = res.json()['secondary_address']
    # print(up_add, up_seadd)

    except KeyError:
        up_sym_send_state = False
        print(send_to_up_optimal_symbol, "해당코인 바이낸스에서 업비트 입금 불가상태")

    up_pre = pyupbit.get_current_price('KRW-' + max_rate_name)  # 업비트 현재가 조회#리플이든 비트코인이든

    # 현재가 조회#바이낸스
    bin_ticker = ccxt.binance().fetch_ticker(max_rate_name + '/USDT')['close']
    bin_pre = bin_ticker * Usdt
    max_rate = ((up_pre / bin_pre) - 1) * 100
    print('max_rate',max_rate,'min_rate', min_rate)

    print('max_rate_name', max_rate_name,'min_rate_name',min_rate_name)


# Arbitrage = up_can_order_amout * ((100 - min_rate - to_bin_fee_by_asset_rate) / 100) * ((100 + max_rate - to_up_fee_by_asset_rate) / 100)
# Arbitrage =  up_can_order_amout*((100-Realize_Arbitrage)/100) * ((100 + max_rate - to_up_fee_by_asset_rate)/100)

    # 현재까지 실현되는 누적이익(%)
    # Arbitrage = max_rate - to_up_fee_by_asset_rate + Realize_Arbitrage
    Arbitrage = up_can_order_amout*((100-Realize_Arbitrage)/100) * ((100 + max_rate - to_up_fee_by_asset_rate)/100)
    # Arbitrage = up_asset * ((100 + max_rate - to_up_fee_by_asset_rate) / 100)
    print('Realize_Arbitrage',Realize_Arbitrage,'Arbitrage',Arbitrage,"1037줄")

    if (Arbitrage > up_can_order_amout and up_sym_send_state == True ):
    # 실현되는 누적이익(%)
        send_to_up_optimal_symbol = max_rate_name
        print('send_to_bin_optimal_symbol=', send_to_bin_optimal_symbol, 'Arbitrage=', Arbitrage,'Realizing_Arbitrage=', Realize_Arbitrage, 'min_rate=', min_rate)
        print('send_to_up_optimal_symbol=', send_to_up_optimal_symbol, 'Arbitrage=', Arbitrage, 'Realizing_Arbitrage=',Realize_Arbitrage, 'max_rate', max_rate)
    ################################################
    else:
        time.sleep(5)
        print("보낼 최적 코인 다시 찾습니다")
        print(binance_asset, "바이낸스 자본(조정 후)", up_asset, "업비트 자본(조정 후)")
        # 업비트=>바이낸스 전송코인#차익이 클 때
        # 자본대비 전송수수료, 역프를 계산하여 최대 이익을 낼 수 있는 코인 선정

        while True:
            print(min_rate_name, min_rate)

            max_rate = -100
            max_rate_name = 0
            send_to_up_optimal_symbol = 0

            Arbitrage = 0  # 차익
            Usdt = upbit_get_usd_krw()

            for i in range(len(sym_name)):

                # 현재가 조회#업비트
                up_pre = pyupbit.get_current_price('KRW-' + sym_name[i])  # 업비트 현재가 조회#리플이든 비트코인이든

                # 현재가 조회#바이낸스
                bin_ticker = ccxt.binance().fetch_ticker(sym_name[i] + '/USDT')['close']
                bin_pre = bin_ticker * Usdt
                binance_withdraw_fee = client.get_asset_details()['assetDetail'][sym_name[i]][
                                           'withdrawFee'] * bin_ticker * Usdt

                # 김치프리이미엄이고  ## 전송시간도 가져오면 좋을듯

                #### 업비트 해당코인 입금 주소 생성요청
                try:
                    query = {
                        'currency': sym_name[i],
                    }
                    query_string = urlencode(query).encode()

                    m = hashlib.sha512()
                    m.update(query_string)
                    query_hash = m.hexdigest()

                    payload = {
                        'access_key': access_key,
                        'nonce': str(uuid.uuid4()),
                        'query_hash': query_hash,
                        'query_hash_alg': 'SHA512',
                    }

                    jwt_token = jwt.encode(payload, secret_key)
                    authorize_token = 'Bearer {}'.format(jwt_token)
                    headers = {"Authorization": authorize_token}

                    res = requests.post(server_url + "/v1/deposits/generate_coin_address", params=query,
                                        headers=headers)
                    up_add = res.json()['deposit_address']
                    up_sym_send_state = True
                    up_seadd = res.json()['secondary_address']
                # print(up_add, up_seadd)

                except KeyError:
                    up_sym_send_state = False
                    print(sym_name[i], "해당코인 바이낸스에서 업비트 입금 불가상태")
                ################바이낸스 코인 유예인 경우도 있음
                up_sym_send_state_2 = client.get_deposit_address(asset=sym_name[i])['success']
                #######@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@자본대비 코인전송 수수료 (뺄것)#코인별 프리미엄
                new_rate = ((up_pre / bin_pre) - 1) * 100
                new_up_fee_by_asset_rate = (binance_withdraw_fee / binance_asset) * 100
                # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                if (i == 0):
                    to_up_fee_by_asset_rate = new_up_fee_by_asset_rate

                # 김프가 가장 크고 + 내 자본대배 수수료가 가장 적은것#1%이하
                # print(new_rate, max_rate, new_up_fee_by_asset_rate, up_sym_send_state, binance_withdraw_fee / binance_asset,sym_name[i], max_rate - new_up_fee_by_asset_rate, binance_asset)
                if (new_rate - new_up_fee_by_asset_rate > max_rate - to_up_fee_by_asset_rate) and (up_sym_send_state == True) and ((binance_withdraw_fee / binance_asset) < 0.01) and (up_sym_send_state_2 == True):
                    to_up_fee_by_asset_rate = new_up_fee_by_asset_rate
                    max_rate = new_rate
                    max_rate_name = sym_name[i]
                    print('max_rate_name', max_rate_name, 'max_rate', max_rate, 'max_rate - to_up_fee_by_asset_rate',max_rate - to_up_fee_by_asset_rate)

            # 리플 이더리움 스텔라 루멘 등은 그냥 빠르게 보내기 ###############
            #         if ((-1 < ((up_pre / bin_pre) - 1) * 100) and (sym_name_u_b[i] == "XRP", "XLM","ETH") and (up_sym_send_state == True)):# and ((binance_withdraw_fee / send_to_up_amont) < 0.01)):
            # #             max_rate_name = sym_name_u_b[i]
            # #             print(max_rate_name,'send_to_up_optimal_symbol')
            # #             break
            ##@@@@@@@@@출금불가상태이고 역프가 많이낀 코인 찾으면 50만원 가지고 배팅 ㄱㄱ
            ##@@@@@@@@@입금(출금) 가능 상태이고 역프가 줄어들면 파는 로직

            print('max_rate_name', max_rate_name, 'min_rate_name', min_rate_name)

            up_pre = pyupbit.get_current_price('KRW-' + max_rate_name)  # 업비트 현재가 조회#리플이든 비트코인이든
            # 현재가 조회#바이낸스
            bin_ticker = ccxt.binance().fetch_ticker(max_rate_name + '/USDT')['close']

            bin_pre = bin_ticker * Usdt
            max_rate = ((up_pre / bin_pre) - 1) * 100
            print('max_rate', max_rate, 'min_rate', min_rate)
            ############################################################################################
            # Arbitrage = up_can_order_amout * ((100 - min_rate - to_bin_fee_by_asset_rate) / 100) * ((100 + max_rate - to_up_fee_by_asset_rate) / 100)
            Arbitrage = up_can_order_amout * ((100-Realize_Arbitrage)/100) * ((100 + max_rate - to_up_fee_by_asset_rate)/100)


            # 현재까지 실현되는 누적이익(%)
            # Arbitrage = up_asset * ((100 + max_rate - to_up_fee_by_asset_rate) / 100)
            # Arbitrage = up_can_order_amout * (1 - Realize_Arbitrage) * (1 + max_rate - to_up_fee_by_asset_rate)
            print('Realize_Arbitrage', Realize_Arbitrage, 'Arbitrage', Arbitrage)

            if (Arbitrage > up_can_order_amout):
                # 실현되는 누적이익(%)

                send_to_bin_optimal_symbol = min_rate_name
                send_to_up_optimal_symbol = max_rate_name
                print('send_to_bin_optimal_symbol=', send_to_bin_optimal_symbol, 'Arbitrage=', Arbitrage,
                      'Realizing_Arbitrage=', Realize_Arbitrage, 'min_rate=', min_rate)
                print('send_to_up_optimal_symbol=', send_to_up_optimal_symbol, 'Arbitrage=',  Arbitrage, 'Realizing_Arbitrage=',
                      Realize_Arbitrage, 'max_rate', max_rate)
                break
            time.sleep(1)

    ############################################################################################################################################################################
    ###@불필요한부분들#################################################################################
    # 위에 맞는지 확인

    up_pre = pyupbit.get_current_price("KRW-" + send_to_up_optimal_symbol)  # 업비트 현재가 조회###@불필요한부분들
    bin_ticker = ccxt.binance().fetch_ticker(send_to_up_optimal_symbol + '/USDT')['close']  # 바이낸스 현재가 조회
    bin_pre = bin_ticker * Usdt  # 해외거래소 환율 환산###@불필요한부분들
    Usdt = upbit_get_usd_krw()
    binance_withdraw_fee = client.get_asset_details()['assetDetail'][send_to_up_optimal_symbol]['withdrawFee'] * bin_ticker * Usdt

    #####업비트 해당코인 입금 주소 생성요청

    ###여기서 부터 달러 기준###
    binance_asset = order_send_to_bin_fu_ass * Usdt
    up_asset = send_to_up_amont_Usdt * Usdt
    binance_Usdt_asset = binance_fu_Usdt_asset = order_send_to_bin_fu_ass
    #################################################################################################################
    print(send_to_up_optimal_symbol, ((up_pre / bin_pre) - 1) * 100)
    ########구매 주문 전송#############################################################################################

    #바이낸스 살수 있는 수량만큼 코인 구매를 위해 최소값 맞춤#######

    # bin_ticker = ccxt.binance().fetch_ticker(send_to_up_optimal_symbol+'/USDT')['close']
    #여기는 바이낸스 현물 지갑에 사는것이니 bin_tiker 가 맞음.
    # send_to_up_amount = balance['USDT']['free'] / bin_ticker###바이낸스 현물지갑 자본 조회 한것 분에 티커가격
    send_to_up_quantity = (send_to_up_amont_Usdt / bin_ticker)#바이낸스 업비트로 보낼 달러 / 티커 가격 = 수량
    # asset_symbol_quantity = asset_symbol_quantity / bin_fu_ticker  # @선물 티커 vs 현물티커#floor 바꿈

    send_to_up_quantity = send_to_up_quantity# @@ 이부분 주문 가능 최소량 대신에 전송가능 최소량으로 주문하도록함.
    Decimal_rounding = Bin_Minimum_Order_Size(send_to_up_optimal_symbol)
    send_to_up_can_buy_order_amount = (send_to_up_quantity // Decimal_rounding) * Decimal_rounding

# asset_symbol_quantity = math.floor(asset_symbol_quantity * (10 ** -unit_val((send_to_up_optimal_symbol))))  # 최소 주문 가격단위 0.01개(코인)~0.001
# asset_symbol_quantity = asset_symbol_quantity * (10 ** -unit_val(send_to_up_optimal_symbol))  # 다시가격 맞춤
# bin_fu_can_order_send_to_up_optimal_symbol_quantity = round(asset_symbol_quantity,unit_val(send_to_up_optimal_symbol))

    # Decimal_rounding = Bin_Minimum_Withdraw_Size(send_to_up_optimal_symbol)
    # send_to_up_can_buy_order_amount = (send_to_up_quantity // Decimal_rounding) * Decimal_rounding


    order = binance.create_market_buy_order(send_to_up_optimal_symbol+'/USDT', send_to_up_can_buy_order_amount)
    print(order)
    ####################################################################################################################
    #바이낸스 현물구매 시점 티커(실현차익을 보기위해)
    point_of_buy_bin_ticker_2 = ccxt.binance().fetch_ticker(send_to_up_optimal_symbol + '/USDT')['close']*Usdt

    ##############작업 중 ####TRY로 헷징

    bin_fu_ticker = float(next((item for item in client.futures_ticker()if item['symbol']==send_to_up_optimal_symbol+'USDT'),None)['lastPrice'])

    ###################################################################################################################################
    try:
        result = request_client.change_margin_type(symbol=send_to_up_optimal_symbol + "USDT",marginType=FuturesMarginType.ISOLATED)
        PrintBasic.print_obj(result)
    except:
        print("마진타입 변화 불필요")
        pass
    #선물 레버리지 변화
    result = request_client.change_initial_leverage(symbol=send_to_up_optimal_symbol + "USDT",leverage=1)#future_leverage = 10 이전에 자본을 10:1로 배분했기 떄문
    PrintBasic.print_obj(result)

    asset_symbol_quantity = binance_Usdt_asset / bin_fu_ticker  # @선물 티커 vs 현물티커#floor 바꿈
    asset_symbol_quantity = asset_symbol_quantity * (1 - 0.0004 * future_leverage)# @@ 이부분 맞나.. 수수료
    # asset_symbol_quantity = math.floor(asset_symbol_quantity * (10 ** -unit_val((send_to_up_optimal_symbol))))  # 최소 주문 가격단위 0.01개(코인)~0.001
    # asset_symbol_quantity = asset_symbol_quantity * (10 ** -unit_val(send_to_up_optimal_symbol))  # 다시가격 맞춤
    # bin_fu_can_order_send_to_up_optimal_symbol_quantity = round(asset_symbol_quantity,unit_val(send_to_up_optimal_symbol))

    Decimal_rounding = Bin_Minimum_FU_Order_Size(send_to_up_optimal_symbol)
    bin_fu_can_order_send_to_up_optimal_symbol_quantity = (asset_symbol_quantity // Decimal_rounding) * Decimal_rounding

    time.sleep(5)

    # 주문신청                             # 심볼            #sell 이면 숏 buy면 롱     # 시장가 거래         # 몇개 살것인지 (여기를 더 고민 ,잔고 또는 자본에 맞춰서 구매하게 만들어야함)
    result = request_client.post_order(symbol=send_to_up_optimal_symbol + "USDT", side=OrderSide.SELL,ordertype=OrderType.MARKET,quantity=bin_fu_can_order_send_to_up_optimal_symbol_quantity)  # quantity수량.#Orderside sell 이면 판매
    PrintBasic.print_obj(result)

    # 바이낸스 선물구매 시점 티커(실현차익을 보기위해) 저장
    point_of_buy_bin_fu_ticker_2 = float(next((item for item in client.futures_ticker() if item['symbol'] == send_to_up_optimal_symbol + 'USDT'), None)['lastPrice'])*Usdt
########업비트에 자본 전송##################################################
    time.sleep(1)
    #################################################################
    #### 업비트 해당코인 입금 주소 생성요청
    query = {'currency': send_to_up_optimal_symbol,}
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',}

    jwt_token = jwt.encode(payload, secret_key)
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post(server_url + "/v1/deposits/generate_coin_address", params=query,
                        headers=headers)
    up_add = res.json()['deposit_address']
    up_sym_send_state = True
    up_seadd = res.json()['secondary_address']
    print(up_add, up_seadd)

    bin_pre = bin_ticker * Usdt  # 해외거래소 환율 환산

    print(send_to_up_optimal_symbol, ((up_pre / bin_pre) - 1) * 100)

    time.sleep(2)

    ######################################
    while True:
        # 바이낸스 계정 조회로 업비트코인전송
        can_send_amount = float(next(
            (item for item in binance.fetch_balance()['info']['balances'] if item['asset'] == send_to_up_optimal_symbol),
            None)['free'])
        ##바이낸스 전송수수료 빼고 보낼수있는 양
        print(can_send_amount)

        if (can_send_amount > bin_fu_can_order_send_to_up_optimal_symbol_quantity * 0.9):
            break

        time.sleep(1)
        # print(can_send_amount,"업비트보낼양")

    #############################################
    # 바이낸스 계정 조회로 업비트코인전송

    Decimal_rounding = Bin_Minimum_Withdraw_Size(send_to_up_optimal_symbol)
    can_order_send_amount = (can_send_amount // Decimal_rounding) * Decimal_rounding
    can_order_send_amount = round(can_order_send_amount , 6)

    # binance_sym_withdraw_fee = client.get_asset_details()['assetDetail'][send_to_up_optimal_symbol]['withdrawFee']#할필요 없는듯 지우기
    # can_order_send_amount=can_order_send_amount-binance_sym_withdraw_fee

    if (send_to_up_optimal_symbol == 'BHC'):#BCH코인은 주소가 좀 이상하게 나옴, 그리고 태그도 없어야 전송이 됨.

        up_add = up_add[12:]

        res = client.withdraw(asset=send_to_up_optimal_symbol, amount=can_order_send_amount, address=up_add,)
                              #addressTag=up_seadd)
        print(res)
    if (up_seadd == None):
        res = client.withdraw(asset=send_to_up_optimal_symbol, amount=can_order_send_amount, address=up_add, )# 두번째 주소가 없는경우 그 양식에 맞게 전송주문을 제출 하여야 함.
        # addressTag=up_seadd)

        print(res)

    else:
        # 바이낸스 코인 전송
        res = client.withdraw(asset=send_to_up_optimal_symbol,amount=can_order_send_amount, address=up_add, addressTag=up_seadd)
        print(res)

    binance_sym_withdraw_fee = client.get_asset_details()['assetDetail'][send_to_up_optimal_symbol]['withdrawFee']##가끔 전송 불가 코인이 있는데 이걸 어떻게 구분할지..#문제 찾음 BNB 방식이랑 이더리움 클래식 방식 전송방법이 있음 이중에서 BNB방식으로 보내는데 어떡하지..
    real_send_amount = can_order_send_amount - binance_sym_withdraw_fee
    print(real_send_amount)

    to_up_fee_by_asset_rate = (binance_withdraw_fee / binance_asset) * 100

    print("2. 실제 헷징된 바이낸스 현물구매시점 가격 ,바이낸스 선물 구매시점 가격", point_of_buy_bin_ticker_2, point_of_buy_bin_fu_ticker_2)

    while True:
        up_symbol_balance = upbit.get_balance("KRW-" + send_to_up_optimal_symbol)

        print("업비트", send_to_up_optimal_symbol, "전송 중", up_symbol_balance)
        if (up_symbol_balance >= real_send_amount):
            print("업비트", send_to_up_optimal_symbol, "전송 완료", up_symbol_balance)
            break
        time.sleep(1)

####################################################################################################################

    while True:
        Usdt = upbit_get_usd_krw()

        Arbitrage = 0#0으로 초기화
        bin_fu_ticker = float(next((item for item in client.futures_ticker() if item['symbol'] == send_to_up_optimal_symbol + 'USDT'),None)['lastPrice']) *Usdt
        ##########실제 얼마나 차익났는지 확인
        point_of_buy_UP_ticker_2 = pyupbit.get_current_price("KRW-" + send_to_up_optimal_symbol)  # 업비트 현재가 조회
        # bin_ticker = ccxt.binance().fetch_ticker(send_to_up_optimal_symbol + '/USDT')['close']  # 바이낸스 현재가 조회
        bin_pre = point_of_buy_bin_ticker_2  # 해외거래소 환율 환산###
        # bin_fu_pre = point_of_buy_bin_fu_ticker * Usdt
        # fu_aritrage =up_pre/bin_fu_pre

        #@청산안당하기 위해서..맞지? (오른 금액 / 이전 금액) - 1) * 100 =
        For_No_liquidation = ((bin_fu_ticker / point_of_buy_bin_fu_ticker_2) - 1) * 100
        print('For_No_liquidation', For_No_liquidation)

        ##@@@@@@@@업비트선물로 헷징한게 어케됬는지 모름!!!!!
        max_rate = ((point_of_buy_UP_ticker_2 / bin_pre) - 1) * 100
        print( point_of_buy_UP_ticker_2,bin_pre )
        # 현재까지 실현되는 누적이익(%)
        # Realize_Arbitrage = -min_rate - to_bin_fee_by_asset

        # Arbitrage = up_can_order_amout * ((100 - min_rate - to_bin_fee_by_asset_rate) / 100) * ((100 + max_rate - to_up_fee_by_asset_rate) / 100)

        # 헷징 시 아마도 얻을 차익
        # Arbitrage = up_can_order_amout * ((100 - min_rate - to_bin_fee_by_asset_rate) / 100) * ((100 + max_rate - to_up_fee_by_asset_rate) / 100)
        Arbitrage = up_can_order_amout * ((100 - Realize_Arbitrage) / 100) * ((100 + max_rate - to_up_fee_by_asset_rate)/ 100)
        # Arbitrage = up_asset * ((100 + max_rate - to_up_fee_by_asset_rate) / 100)
        print("현재까지 실현된 누적이익",Realize_Arbitrage, '코인 판매시 얻을 이익',Arbitrage)
        # @@숏포지션 프리미엄 먹음.<=이거 얼마나 먹었는지 보면서 수익날때 팔게

        # ##################################@@@@if문 수정 @@@@@@#######################################################################
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@이부분 if문이 업비트에서 수익이 나기만을 바라고 있음. 전송중 내려간 돈도 이득인데.
        # if(Arbitrage > up_can_order_amout):#@@ 전송완료시 코인이 이득일 시 팔고 아니면 차익 계속 보여주면서 대기#0.1%의 이득일시 팔게 해둠,..
        #     #한 싸이클 돌면0.46%수수료 뭄(레퍼럴 없이) 있다면 0.42
        #
        #     # 주문가능 수량만큼 판매
        #     up_symbol_balance = upbit.get_balance("KRW-" + send_to_up_optimal_symbol)
        #     res = upbit.sell_market_order("KRW-" + send_to_up_optimal_symbol, up_symbol_balance)
        #     pprint.pprint(res)
        #
        #     # 주문신청                             # 심볼            #sell 이면 숏 buy면 롱     # 시장가 거래         # 몇개 살것인지 (여기를 더 고민 ,잔고 또는 자본에 맞춰서 구매하게 만들어야함)
        #     result = request_client.post_order(symbol=send_to_up_optimal_symbol + "USDT", side=OrderSide.BUY,ordertype=OrderType.MARKET,quantity=bin_fu_can_order_send_to_up_optimal_symbol_quantity)  # quantity수량.#Orderside sell 이면 판매
        #     PrintBasic.print_obj(result)
        #     Arbitrage = up_asset * ((100 + max_rate - to_up_fee_by_asset_rate) / 100)
        #
        #     # 실현된 차익
        #     # Realize_Arbitrage = max_rate - to_up_fee_by_asset_rate + Realize_Arbitrage - accumulate_fee#@ accumulate_fee 를 if 문에 하면 0보다 클시 적용해도 될듯.
        #     print("실현된 차익",Arbitrage,'손익?') #accumulate_fee)
        #     break
        #
        # #최소#1% 이상의 이득을 취할수 있을 시 판매#헷징을 안하면 0.84만 넘으면 됨
        # if(For_No_liquidation > 5):#5%이상일 경우 청산될 가능성이 큼! 업비트로 다시 보내고고다시 서칱하는 로직
        #
        #     #이부분 while 초반부분에 try로?
        #
        #     print("차이는 점점 벌어지지만 수익권 자리는 나오기 힘들어 보임 다시 바이낸스로 재전송 후 헷징풀고 다른 코인 다시 서칭하기.")
        #     print("전송수수료도 고려해서 다시 수익이 나는 코인 찾는 로직 추가하기")
        #
        # ##################################@@@@if문 수정 @@@@@@#######################################################################
        # 주문가능 수량만큼 판매
        up_symbol_balance = upbit.get_balance("KRW-" + send_to_up_optimal_symbol)
        res = upbit.sell_market_order("KRW-" + send_to_up_optimal_symbol, up_symbol_balance)
        pprint.pprint(res)

        # 주문신청                             # 심볼            #sell 이면 숏 buy면 롱     # 시장가 거래         # 몇개 살것인지 (여기를 더 고민 ,잔고 또는 자본에 맞춰서 구매하게 만들어야함)
        result = request_client.post_order(symbol=send_to_up_optimal_symbol + "USDT", side=OrderSide.BUY,
                                           ordertype=OrderType.MARKET,
                                           quantity=bin_fu_can_order_send_to_up_optimal_symbol_quantity)  # quantity수량.#Orderside sell 이면 판매
        PrintBasic.print_obj(result)
        Arbitrage = up_asset * ((100 + max_rate - to_up_fee_by_asset_rate) / 100)

        # 실현된 차익
        # Realize_Arbitrage = max_rate - to_up_fee_by_asset_rate + Realize_Arbitrage - accumulate_fee#@ accumulate_fee 를 if 문에 하면 0보다 클시 적용해도 될듯.
        print("실현된 차익", Arbitrage, '손익?')  # accumulate_fee)
        break

        time.sleep(1)
    sicle = sicle + 1

    print(str(sicle)+"번 돎")
    print("총 자본", upbit.get_balance("KRW") + float(next((item for item in client.futures_account()['assets'] if item['asset'] == 'USDT'), None)['walletBalance']) * Usdt)
    time.sleep(2)
    break##@@@@@나중에 지우기 한바퀴 돌면 멈추게 함.,

