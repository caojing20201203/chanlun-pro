from chanlun.cl_interface import Kline
from typing import List
from datetime import datetime
import pandas as pd
from chanlun import fun


def get_src_klines(code: str, frequency, start_datetime: datetime) -> List[Kline]:
    from chanlun.exchange.exchange_tdx import ExchangeTDX
    ret_klines = []
    ex = ExchangeTDX()
    tdx_klines = ex.klines(code, frequency, start_datetime)
    src_klines = convert_src_klines(tdx_klines)
    return src_klines

def convert_src_klines(tdx_klines):
    ret_klines = []
    for num in range(0, len(tdx_klines)):
        kline = tdx_klines.iloc[num].copy()
        src_kline = Kline(num, kline['date'], kline['high'], kline['low'], kline['open'], kline['close'], kline['volume'])
        ret_klines.append(src_kline)
    data = [vars(kline) for kline in ret_klines]
    df = pd.DataFrame(data)
    return df


if __name__ == '__main__':
    src_klines = get_src_klines('SH.601698', 'd', None )
    #dates = src_klines['date'].map(fun.datetime_to_int).tolist()
    dates = src_klines['date']
    print(dates)