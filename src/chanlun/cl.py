from abc import ABCMeta, abstractmethod
from chanlun.cl_interface import ICL, Config, Kline, CLKline, FX, BI, XD, ZS, LINE
from typing import List, Union, Tuple
import datetime
import pandas as pd
from chanlun.get_src_klines import get_src_klines, convert_src_klines
from chanlun.get_cl_klines import get_cl_lines
from chanlun.get_fx import FX_PROCESS
from chanlun.get_bi import BI_Process
from chanlun.get_xd import XD_Process

# 修正类名，按照 Python 命名规范，类名应该使用大写字母开头
class CL(ICL):
    # 实现 ICL 中的所有抽象方法
    def __init__(self, code, frequency, cl_config):
        from chanlun.exchange.exchange_tdx import ExchangeTDX
        self.code = code
        self.frequency = frequency
        self.cl_config = cl_config
        self.src_klines = []
        self.cl_klines = []
        self.idx = {}
        self.fxs = []
        self.bis = []
        self.xds = []
        self.zsds = []
        self.qsds = []
        self.bi_zss = []
        self.xd_zss = []
        self.zsd_zss = []
        self.qsd_zss = []

    def process_klines(self, klines: pd.DataFrame):
        self.src_klines = convert_src_klines(klines)
        self.cl_klines = get_cl_lines(self.src_klines)
        fx_proc = FX_PROCESS()
        self.fxs = fx_proc.find_fenxing(self.cl_klines)
        bi_process = BI_Process()
        self.bis = bi_process.handle(self.fxs)
        xd_process = XD_Process()
        self.xds = xd_process.handle(self.bis)
        self.zsds = []
        self.qsds = []
        self.zsds = []
        self.bi_zss = []
        self.xd_zss = []
        self.zsd_zss = []
        self.qsd_zss = []


    def get_code(self):
        return self.code

    def get_frequency(self):
        return self.frequency

    def get_cl_config(self):
        return self.cl_config

    def get_src_klines(self) -> List[Kline]:
        return self.src_klines

    def get_cl_klines(self) -> List[CLKline]:
        return self.cl_klines

    def get_klines(self) -> List[CLKline]:
        #ToDo 增加返回cl_klines逻辑
        return pd.DataFrame(self.src_klines).values.tolist()

    def get_idx(self) -> dict:
        return None

    def get_fx(self) -> FX:
        return self.fxs[0]

    def get_bis(self) -> List[BI]:
        return self.bis

    def get_xds(self) -> List[XD]:
        return self.xds

    def get_zsds(self) -> List[XD]:
        return self.zsds

    def get_qsds(self) -> List[XD]:
        return self.qsds

    def get_bi_zss(self, zs_type: str = None) -> List[ZS]:
        return self.bi_zss

    def get_xd_zss(self, zs_type: str = None) -> List[ZS]:
        return self.xd_zss

    def get_zsd_zss(self) -> List[ZS]:
        return self.zsd_zss

    def get_qsd_zss(self) -> List[ZS]:
        return self.qsd_zss

    def get_last_bi_zs(self) -> Union[ZS, None]:
        return None

    def get_last_xd_zs(self) -> Union[ZS, None]:
        return None

    def create_dn_zs(self, zs_type, lines, max_line_num = 999, zs_include_last_line=True):
        pass

    def beichi_pz(self, zs: ZS, now_line: LINE) -> Tuple[bool, Union[LINE, None]]:
        pass

    def beichi_qs(self, lines: List[LINE], zss: List[ZS], now_line: LINE) -> Tuple[bool, List[LINE]]:
        pass

    def zss_is_qs(self, one_zs: ZS, two: ZS) -> Tuple[str, None]:
        pass

    def get_fxs(self) -> List[FX]:
        return self.fxs


        