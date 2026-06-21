# 陰性対照: encode の個数が 1 ずれるバグ（j - i - 1）。decode は正しいが往復で元に戻らない。
def encode(s):
    out = []
    i = 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(s[i] + str(j - i - 1))  # バグ: -1 が余計
        i = j
    return "".join(out)


def decode(s):
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        j = i + 1
        while j < len(s) and s[j].isdigit():
            j += 1
        out.append(ch * int(s[i + 1:j]))
        i = j
    return "".join(out)
