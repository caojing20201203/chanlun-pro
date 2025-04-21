from chanlun.cl import cl

if __name__ == '__main__':
    code = '000001.SZ'
    frequency = '1m'
    src_klines = cl.CL(code, frequency, None)
    print(src_klines)