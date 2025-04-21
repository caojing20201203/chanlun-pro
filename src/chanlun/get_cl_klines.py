import pandas as pd
from chanlun.cl_interface import Kline, CLKline
from enum import Enum
from datetime import datetime
from chanlun.get_src_klines import get_src_klines

class Direction(Enum):
    UP = 1
    DOWN = -1
    NONE = 0

def get_cl_lines(klines):
    # 初始化方向为向上
    direction = Direction.UP
    # 取出第一根 K 线
    last_kline = klines.iloc[0].copy()
    # 初始化保留的 K 线列表
    ret_cl_klines = []
    cl_klines = []
    cl_num = 0
    # 遍历除第一根 K 线外的其他 K 线
    for i in range(1, len(klines)):
        current_kline = klines.iloc[i].copy()
        date_str = current_kline['date'].strftime('%Y-%m-%d %H:%M:%S')
        # 当前 K 线的高点和低点
        current_kline_high = current_kline['h']
        current_kline_low = current_kline['l']
        # 上一个 K 线的高点和低点
        last_kline_high = last_kline['h']
        last_kline_low = last_kline['l']
        # 情况 1：当前 K 线包含上一个 K 线
        if current_kline_high >= last_kline_high and current_kline_low <= last_kline_low:
            if direction == Direction.UP:
                current_kline['l'] = last_kline_low
            elif direction == Direction.DOWN:
                current_kline['h'] = last_kline_high
            if len(cl_klines) == 0:
                cl_klines.append(last_kline)
            last_kline = current_kline
            cl_klines.append(current_kline)
        # 情况 2：上一个 K 线包含当前 K 线
        elif last_kline_high >= current_kline_high and last_kline_low <= current_kline_low:
            if direction == Direction.UP:
                last_kline['l'] = current_kline_low
            elif direction == Direction.DOWN:
                last_kline['h'] = current_kline_high
            if len(cl_klines) == 0:
                cl_klines.append(last_kline)
            cl_klines.append(current_kline)
        # 情况 3：不包含关系
        else:
            cl = CLKline(cl_num, last_kline['date'], last_kline['h'], last_kline['l'], last_kline['o'], last_kline['c'], last_kline['a'], cl_klines, i, len(cl_klines))
            ret_cl_klines.append(cl)
            cl_klines = []
            last_kline = current_kline
            # 根据当前 K 线和上一个 K 线的高点关系更新方向
            if current_kline_high > last_kline_high:
                direction = Direction.UP
            else:
                direction = Direction.DOWN
            cl_num += 1

    # 添加最后一根 K 线
    if len(cl_klines) == 0:
        cl = CLKline(cl_num, current_kline['date'], current_kline['h'], current_kline['l'], current_kline['o'], current_kline['c'], current_kline['a'], cl_klines, i, len(cl_klines))
        ret_cl_klines.append(cl)

    data = [vars(cl) for cl in ret_cl_klines]
    # 将字典列表转换为 DataFrame
    df = pd.DataFrame(data)
    # 将保留的 K 线列表转换为 DataFrame
    return (df)

def verify_bh(cl_klines):
    last_kline = cl_klines.iloc[0].copy()
    for i in range(1, len(cl_klines)):
        cur_kline = cl_klines.iloc[i].copy()
        if cur_kline['h'] >= last_kline['h'] and cur_kline['l'] <= last_kline['l']:
            print('错误出现：', cur_kline['date'])
            return False
        elif last_kline['h'] >= cur_kline['h'] and last_kline['l'] <= cur_kline['l']:
            print('错误出现：', cur_kline['date'])
            return False
        last_kline = cur_kline
    return True

if __name__ == "__main__":
    src_klines = get_src_klines("SH.601698", "d", "2024-09-08")
    # 假设 src_klines 是 pandas DataFrame 格式
    ret_cl_klines = get_cl_lines(src_klines)
    print(ret_cl_klines)
    """
    for kline in ret_cl_klines.iterrows():
        print(kline)
    """
    verify_bh(ret_cl_klines)
