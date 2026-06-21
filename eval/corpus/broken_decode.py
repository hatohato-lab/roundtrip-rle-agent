# 陰性対照: decode が個数を 1 桁しか読まないバグ。encode は正しいが、10 個以上の連続で破綻する。
def encode(s):
    out = []
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(s[i] + str(j - i))
        i = j
    return "".join(out)


def decode(s):
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        out.append(ch * int(s[i + 1]))  # バグ: 個数を 1 桁固定で読む
        i += 2
    return "".join(out)
