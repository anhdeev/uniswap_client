import os
import subprocess
import shutil
import time

from typing import List, Any, Optional, Callable, Union, Tuple, Dict, Generator
from contextlib import contextmanager
from dataclasses import dataclass

from web3 import Web3
from web3.types import (
    TxParams,
    Wei,
    Address,
    ChecksumAddress,
    ENS,
    Nonce,
    HexBytes,
)
from uniswap import Uniswap, InvalidToken, InsufficientBalance

# TODO: Consider dropping support for ENS altogether and instead use AnyAddress
AddressLike = Union[Address, ChecksumAddress, ENS]

@dataclass
class MyParams:
    provider: str
    eth_address: str
    eth_privkey: str

def client(ver, web3: Web3, params: MyParams):
    uniswap = Uniswap(
        params.eth_address, params.eth_privkey, web3=web3, version=ver
    )
    #uniswap._buy_test_assets()
    return uniswap

def web3(params: MyParams):
    return Web3(Web3.HTTPProvider(params.provider, request_kwargs={"timeout": 60}))

class ClientWrapper:
    ONE_WEI = 1
    ONE_SAT = 10 ** 8
    ONE_ETH = 10 ** 18 * ONE_WEI
    ONE_ETH_GWEI = 10 ** 9 * ONE_WEI
    VERSION = 2
    ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
    eth = "0x0000000000000000000000000000000000000000"
    weth = Web3.toChecksumAddress("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
    bat = Web3.toChecksumAddress("0x0D8775F648430679A709E98d2b0Cb6250d2887EF")
    dai = Web3.toChecksumAddress("0x6b175474e89094c44da98b954eedeac495271d0f")
    polk = Web3.toChecksumAddress("0xd478161c952357f05f0292b56012cd8457f1cfbf")

    def __init__(self, c_web3: web3, c_params: MyParams):
        self.uniclient = client(self.VERSION, c_web3, c_params);
        
    # ------ Exchange ------------------------------------------------------------------
    def get_fee_maker(self):
        return self.uniclient.get_fee_maker()

    def get_fee_taker(self):
        return self.uniclient.get_fee_taker()

    # ------ Market --------------------------------------------------------------------
    def get_eth_token_input_price(self, token, qty):
        return self.uniclient.get_eth_token_input_price(token, qty)
    def get_token_eth_input_price(self, token, qty):
        return self.uniclient.get_token_eth_input_price(token, qty)
 
    def trade(self, input_token: AddressLike, output_token: AddressLike, qty: Union[int, Wei], amountOutMin: int, recipent):
        r = self.uniclient.make_trade(input_token, output_token, qty, amountOutMin, recipent)
        tx = self.uniclient.w3.eth.waitForTransactionReceipt(r)
        print("txid = %s, Tx status = %s" % (r.hex(), str(tx.status)))
        print(str(tx))
        return tx.status

    def get_pair(self, token1: AddressLike, token2: AddressLike):
        r = self.uniclient.get_pair(token1, token2)

#m_params = MyParams('http://127.0.0.1:10999','0x94e3361495bD110114ac0b6e35Ed75E77E6a6cFA', '0x6f1313062db38875fb01ee52682cbf6a8420e92bfbc578c5d4fdc0a32c50266f')

#m_params = MyParams('https://mainnet.infura.io/v3/e774964c9d87435baa006b20e4e83b','0x2ea009381024cafdb0efb8eb1d1849624c74ecef', '0xd10bc8a6f7f9cfcd524737cbf4b59c2cd57ad1e0b03b0c1b7b2f981a118c953c')

m_params = MyParams('http://127.0.0.1:8547','0x2ea009381024cafdb0efb8eb1d1849624c74ecef', '0xd10bc8a6f7f9cfcd524737cbf4b59c2cd57ad1e0b03b0c1b7b2f981a118c953c')


m_web3 = web3(m_params)
m_uclient = ClientWrapper(m_web3, m_params);

#print(m_uclient.get_fee_maker())
#print(m_uclient.get_eth_token_input_price(m_uclient.bat, m_uclient.ONE_SAT))
#print(m_uclient.get_token_eth_input_price(m_uclient.bat, m_uclient.ONE_SAT))
#m_uclient.trade(m_uclient.eth, m_uclient.bat, m_web3.toWei(m_uclient.ONE_ETH/10, 'wei'), 310*m_uclient.ONE_ETH)
isSent = False
inAmount = int(m_uclient.ONE_ETH * 0.4)
outPriceMax = 2 #usd
inPrice = 1650 #usd
outAmountMin = int((inPrice/outPriceMax) * inAmount)
myrecipent = "0x92F7aF3e0575031C209A645e5b72f206B1c2c9d7"

print("My balance = " + str(m_uclient.uniclient.get_eth_balance()))
print("Min output amount accepted = " + str(outAmountMin))

while not isSent:
    try:
        outAmount = m_uclient.get_eth_token_input_price(m_uclient.bat, m_uclient.ONE_ETH)
        print("outAmount by market = " + str(outAmount))
        if(outAmount > 1):
            r = m_uclient.trade(m_uclient.eth, m_uclient.bat, m_web3.toWei(inAmount, 'wei'), outAmountMin, myrecipent)
            if(r):
                isSent = True
    except ValueError as err:
        print(str(err))
    
    time.sleep(1)




