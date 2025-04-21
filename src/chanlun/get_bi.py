from enum import Enum
from chanlun.cl_interface import FX, BI, FxStatus, BiType
from chanlun.get_src_klines import get_src_klines
from chanlun.get_cl_klines import get_cl_lines
from chanlun.get_fx import FX_PROCESS, FxStatus
 
class BI_Process:
    def __init__(self):
        self.bilist = []
        start_fx = None
        stop_fx = None
        self.no = 0
    
    def find_bi(self, fx: FX) -> BI:
        ret_bi = None
        self.date = fx.k.date.strftime('%Y-%m-%d %H:%M:%S')
        if self.start_fx.type == FxStatus.TOP:
            if fx.type == FxStatus.BOTTOM or fx.type == FxStatus.VERIFY_BOTTOM:
                ret_bi = BI(self.start_fx, fx, BiType.DOWN, self.no)
                self.start_fx = fx
                self.no += 1
            else:
                if fx.val > self.start_fx.val:
                    self._update_last_bi(fx)
        elif self.start_fx.type == FxStatus.BOTTOM:
            if fx.type == FxStatus.TOP or fx.type == FxStatus.VERIFY_TOP:
                ret_bi = BI(self.start_fx, fx, BiType.UP, self.no)
                self.start_fx = fx
                self.no += 1
            else:
                if fx.val < self.start_fx.val:
                    self._update_last_bi(fx)
        elif self.start_fx.type == FxStatus.VERIFY_TOP:
            if fx.type == FxStatus.BOTTOM:
                ret_bi = BI(self.start_fx, fx, BiType.DOWN, self.no)
                self.start_fx = fx
                self.no += 1
            elif fx.type == FxStatus.VERIFY_BOTTOM:
                ret_bi = BI(self.start_fx, fx, BiType.VERIFY_DOWN, self.no)
                self.start_fx = fx
                self.no += 1
            else:
                if fx.val < self.start_fx.val:
                    self._update_last_bi(fx)
        elif self.start_fx.type == FxStatus.VERIFY_BOTTOM:
            if fx.type == FxStatus.VERIFY_TOP:
                ret_bi = BI(self.start_fx, fx, BiType.VERIFY_UP, self.no)
                self.start_fx = fx
                self.no += 1
            elif fx.type == FxStatus.TOP:
                ret_bi = BI(self.start_fx, fx, BiType.UP, self.no)
                self.start_fx = fx
                self.no += 1
            else:
                if fx.val > self.start_fx.val:
                    self._update_last_bi(fx)
        else:
            print('未处理的GaoDiDian类型：', self.start_fx.type)
        self.last_bi = ret_bi
        return ret_bi


    def _update_last_bi(self, fx:FX):
        ret_bi = None
        if len(self.bilist) > 0:
            last_bi = self.bilist[-1]
            stop_fx = last_bi.stop_fx
            if fx.type == FxStatus.TOP and fx.val > stop_fx.val:
                ret_bi = BI(last_bi.start_fx, fx, BiType.UP, last_bi.index)
                self.bilist.pop()
                self.bilist.append(ret_bi)
                self.start_fx = fx
            elif fx.type == FxStatus.BOTTOM and fx.val < stop_fx.val:
                ret_bi = BI(last_bi.start_fx, fx, BiType.DOWN, last_bi.index)
                self.bilist.pop()
                self.bilist.append(ret_bi)
                self.start_fx = fx
            elif fx.type == FxStatus.VERIFY_TOP and fx.val > stop_fx.val:
                ret_bi = BI(last_bi.start_fx, fx, BiType.VERIFY_UP, last_bi.index)
                self.bilist.pop()
                self.bilist.append(ret_bi)
                self.start_fx = fx
            elif fx.type == FxStatus.VERIFY_BOTTOM and fx.val < stop_fx.val:
                ret_bi = BI(last_bi.start_fx, fx, BiType.VERIFY_DOWN, last_bi.index)
                self.bilist.pop()
                self.bilist.append(ret_bi)
                self.start_fx = fx
        return ret_bi
    
    def handle(self, fxlist:list[FX]):
        bilist = []
        self.start_fx = fxlist[0]
        for fx in fxlist[1:]:
            bi = self.find_bi(fx)
            if bi is not None:
                bilist.append(bi)
        return bilist

if __name__ == '__main__':
    src_klines = get_src_klines('SH.601698', 'd', None )
    cl_klines = get_cl_lines(src_klines)
    fx_proc = FX_PROCESS()
    fxlist = fx_proc.find_fenxing(cl_klines)
    bi_process = BI_Process()
    bilist = bi_process.handle(fxlist)
    for bi in bilist:
        print(bi)

    
        