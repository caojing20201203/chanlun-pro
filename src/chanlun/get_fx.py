from pandas import DataFrame 
import pandas as pd
from enum import Enum
from chanlun.cl_interface import FX, CLKline, Kline, FxStatus
from datetime import datetime
from chanlun.get_src_klines import get_src_klines
from chanlun.get_cl_klines import get_cl_lines

class FenXingProcessStatus(Enum):
    LEFT = '左边K线'
    MIDDLE = '中间K线'
    RIGHT = '右边K线'
    FREE = '自由K线'
    NEXT_LEFT = '下一个左边K线'
    NEXT_MIDDLE = '下一个中间K线'
    

class FX_PROCESS:
    def __init__(self):
        self.left = None
        self.middle = None
        self.right = None
        self.free = None
        self.next_left = None
        self.next_middle = None
        self.status = FenXingProcessStatus.LEFT
        self.fx_lists = []

    def find_fenxing(self, in_df:DataFrame):
        df = in_df.copy()
        fx_klines = []
        for index, row in df.iterrows():
            fx_status, middle = self.find_gd_high_low(row)
            if fx_status:
                fx_klines.append(df.loc[index])
                if fx_status == FxStatus.TOP:
                    fx = FX(FxStatus.TOP, middle, fx_klines, middle.h, middle.k_index, False)
                    self.fx_lists.append(fx)
                elif fx_status == FxStatus.BOTTOM:
                    fx = FX(FxStatus.BOTTOM, middle, fx_klines, middle.l, middle.k_index, False)
                    self.fx_lists.append(fx)
                elif fx_status == FxStatus.VERIFY_TOP:
                    if self.fx_lists[-1].type == FxStatus.TOP and self.fx_lists[-1].k.date == middle.date:
                        self.fx_lists.pop()
                    fx = FX(FxStatus.VERIFY_TOP, middle, fx_klines, middle.h, middle.k_index, True)
                    self.fx_lists.append(fx)
                    fx_klines = []
                elif fx_status == FxStatus.VERIFY_BOTTOM:
                    if self.fx_lists[-1].type == FxStatus.BOTTOM and self.fx_lists[-1].k.date == middle.date:
                        self.fx_lists.pop()
                    fx = FX(FxStatus.VERIFY_BOTTOM, middle, fx_klines, middle.l, middle.k_index, True)
                    self.fx_lists.append(fx) 
                    fx_klines = []
                elif fx_status == FxStatus.FAILURE_TOP or fx_status == FxStatus.FAILURE_BOTTOM:
                    self.fx_lists.pop()
            else:
                fx_klines.append(df.loc[index])
        return self.fx_lists
                
    def find_gd_high_low(self, k:CLKline):
        date_str = k.date.strftime('%Y-%m-%d %H:%M:%S')
        high = k.h
        low = k.l
        index_no = k.k_index
        if self.status == FenXingProcessStatus.NEXT_MIDDLE:
            before_last_fx, last_fx = self.get_before_last_fx()
            if last_fx.type == FxStatus.TOP:
                if high > last_fx.val:
                    ret_k = self.middle
                    self.left = self.next_left
                    self.middle = k
                    self.status = FenXingProcessStatus.RIGHT
                    return FxStatus.FAILURE_TOP, ret_k
                elif low < self.next_left.l:
                    ret_k = self.middle
                    self.left = self.next_left
                    self.middle = k
                    self.status = FenXingProcessStatus.RIGHT
                    return FxStatus.VERIFY_TOP, ret_k
            elif last_fx.type == FxStatus.BOTTOM:
                if low < last_fx.val:
                    ret_k = self.middle
                    self.left = self.next_left
                    self.middle = k
                    self.status = FenXingProcessStatus.RIGHT
                    return FxStatus.FAILURE_BOTTOM, ret_k
                elif high > self.next_left.h:
                    ret_k = self.middle
                    self.left = self.next_left
                    self.middle = k
                    self.status = FenXingProcessStatus.RIGHT
                    return FxStatus.VERIFY_BOTTOM, ret_k
                
        elif self.status == FenXingProcessStatus.NEXT_LEFT:
            before_last_fx, last_fx = self.get_before_last_fx()
            if last_fx.type == FxStatus.TOP:
                if high > last_fx.val:
                    ret_k = self.middle
                    self.left = self.free
                    self.middle = k
                    self.status = FenXingProcessStatus.RIGHT
                    return FxStatus.FAILURE_TOP, ret_k
                elif low < self.free.l:
                    self.next_left = k
                    self.status = FenXingProcessStatus.NEXT_MIDDLE
            elif last_fx.type == FxStatus.BOTTOM:
                if low < last_fx.val:
                    ret_k = self.middle
                    self.left = self.free
                    self.middle = k
                    self.status = FenXingProcessStatus.RIGHT
                    return FxStatus.FAILURE_BOTTOM, ret_k
                elif high > self.free.h:
                    self.next_left = k
                    self.status = FenXingProcessStatus.NEXT_MIDDLE

        elif self.status == FenXingProcessStatus.FREE:
            before_last_fx, last_fx = self.get_before_last_fx()
            if last_fx.type == FxStatus.TOP and high > last_fx.val:
                ret_k = self.middle
                self.left = self.right
                self.middle = k
                self.status = FenXingProcessStatus.RIGHT
                return FxStatus.FAILURE_TOP, self.right
            elif last_fx.type == FxStatus.BOTTOM and low < last_fx.val:
                ret_k = self.middle
                self.left = self.right
                self.middle = k
                self.status = FenXingProcessStatus.RIGHT
                return FxStatus.FAILURE_BOTTOM, self.right
            else:
                self.free = k
                self.status = FenXingProcessStatus.NEXT_LEFT

        elif self.status == FenXingProcessStatus.RIGHT:
            if self.middle.h > self.left.h:
                if high > self.middle.h:
                    #向上
                    self.left = self.middle
                    self.middle = k
                else:
                    #顶分型
                    self.right = k
                    before_last_fx, last_fx = self.get_before_last_fx()
                    if last_fx is None:
                        self.status = FenXingProcessStatus.FREE
                        return FxStatus.TOP, self.middle
                    elif last_fx.type == FxStatus.VERIFY_BOTTOM and low < last_fx.val:
                        ret_k = self.middle
                        self.left = self.middle
                        self.middle = k
                        self.status = FenXingProcessStatus.RIGHT
                        return FxStatus.TOP, ret_k
                    elif last_fx.type == FxStatus.BOTTOM and low < last_fx.val:
                        ret_k = self.middle
                        self.left = self.middle
                        self.middle = self.right
                        self.status = FenXingProcessStatus.RIGHT
                        return FxStatus.TOP, ret_k
                    else:
                        self.status = FenXingProcessStatus.FREE
                        return FxStatus.TOP, self.middle

            elif self.middle.l < self.left.l:
                if low < self.middle.l:
                    #向下
                    self.left = self.middle
                    self.middle = k
                else:
                    #底分型
                    self.right = k
                    before_last_fx, last_fx = self.get_before_last_fx()
                    if last_fx is None:
                        self.status = FenXingProcessStatus.FREE
                        return FxStatus.BOTTOM, self.middle
                    elif last_fx.type == FxStatus.VERIFY_TOP and high > last_fx.val:
                        ret_k = self.middle
                        self.left = self.middle
                        self.middle = k
                        self.status = FenXingProcessStatus.RIGHT
                        return FxStatus.BOTTOM, ret_k
                    elif last_fx.type == FxStatus.TOP and high > last_fx.val:
                        ret_k = self.middle
                        self.left = self.middle
                        self.middle = self.right
                        self.status = FenXingProcessStatus.RIGHT
                        return FxStatus.BOTTOM, ret_k
                    else:
                        self.status = FenXingProcessStatus.FREE
                        return FxStatus.BOTTOM, self.middle
                
        elif self.status == FenXingProcessStatus.MIDDLE:
            self.middle = k
            self.status = FenXingProcessStatus.RIGHT

        elif self.status == FenXingProcessStatus.LEFT:
            self.left = k
            self.status = FenXingProcessStatus.MIDDLE
        return None, None
    
    def get_before_last_fx(self):
        if len(self.fx_lists) >= 2:
            return self.fx_lists[-2], self.fx_lists[-1]
        elif len(self.fx_lists) == 1:
            return None, self.fx_lists[-1]
        else:
            return None, None

    
if __name__ == '__main__':
    src_klines = get_src_klines('SH.601698', 'd', None )
    # 假设 src_klines 是 pandas DataFrame 格式
    cl_klines = get_cl_lines(src_klines)
    fx_proc = FX_PROCESS()
    fx_list = fx_proc.find_fenxing(cl_klines)
    for fx in fx_list:
        print(fx.type, fx.k.date, fx.val, fx.index)