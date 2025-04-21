#参考文档：https://cyber.wtf/2025/02/12/unpacking-pyarmor-v8-scripts/
from chanlun.cl import CL
from chanlun.cl_utils import query_cl_chart_config

code = "SH.000001"
frequency = "d"
cl_config = query_cl_chart_config(code, frequency)
cl = CL(code, frequency, cl_config, start_datetime="2020-01-01")
cd = cl.CL(code, frequency, cl_config)
print(type(cd))