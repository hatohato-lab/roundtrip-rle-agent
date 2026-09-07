# 陰性対照: decode が、符号列に 'z' を含むときだけ空文字列を返すバグ。encode は正しい。
# 往復検査のランダム入力は 'abcde' しか出さないので z を踏まず、圧縮検査で decode を見なければ PASS してしまう。
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
    if "z" in s:  # バグ: z を含む符号列を復号できない
        return ""
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
