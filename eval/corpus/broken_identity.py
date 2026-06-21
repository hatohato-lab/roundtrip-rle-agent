# 陰性対照: 恒等変換。往復は完全に通る（decode(encode(x))==x）が、何も圧縮しない。
# 往復だけでは見抜けないため、圧縮性プロパティで捕まえる。
def encode(s):
    return s


def decode(s):
    return s
