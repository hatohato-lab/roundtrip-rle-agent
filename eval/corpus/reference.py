# 正例: ランレングス符号化 (RLE)。同じ文字の連続を「文字＋個数」に畳む。
# 例: "aaabb" -> "a3b2"。decode はその逆。入力は英小文字を想定。
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
        j = i + 1
        while j < len(s) and s[j].isdigit():
            j += 1
        out.append(ch * int(s[i + 1:j]))
        i = j
    return "".join(out)
