#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oracle.py — プロパティベース（往復 / round-trip）オラクル。

個々の出力の正解は用意せず、入力に対して常に成り立つべき**性質**で判定する。
候補 encode / decode について、ランダムな文字列を大量に作り:
  (1) 往復一致 : すべての x で decode(encode(x)) == x。
  (2) 圧縮性  : 反復文字列は encode で短くなり（恒等変換のごまかし防止）、かつ decode で元に戻る。
を確かめる。種を固定するので再現可能。

使い方:
  python oracle.py                  # reference.py（正例）を採点
  python oracle.py --candidate NAME # NAME.py を採点
  python oracle.py --selftest       # オラクル自身を検証（正例→PASS / 既知バグ→FAIL）
終了コード: PASS（または selftest 期待どおり）で 0、それ以外 1。
"""
import argparse
import importlib.util
import random
import sys
from pathlib import Path

# Windows コンソール(cp932)でも日本語・記号を出せるよう出力を UTF-8 に統一。
# Linux/Mac は元から UTF-8 なので無害。これが無いと Windows で print が落ちる。
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

EVAL = Path(__file__).resolve().parent
CORPUS = EVAL / "corpus"
N = 4000        # ランダム入力の本数
SEED = 12345    # 種固定（再現可能）
ALPHA = "abcde"  # 小さめの英字 → 長い連続（2桁の個数）が出やすい

# 圧縮性チェックの点（文字 × 長さ ＝ 計12点）。
# 1点だけだと「その入力だけ特別扱いし、他は恒等変換」する実装が PASS してしまうため、
# 複数の文字（ランダム生成の ALPHA 外である k・z も含む）× 複数の長さで確かめる。
COMPRESS_CHARS = "abkz"
COMPRESS_LENS = (10, 26, 50)

# 手で選んだ際どい入力（空・単一・2桁の連続など）＋ 英小文字26字の単文字と ALPHA 外の長い反復（境界）。
# ランダム生成は ALPHA=abcde の範囲しか出さないので、f〜z は決定的な入力で必ず往復を確かめる。
SEED_CASES = ["", "a", "aa", "ab", "aaab", "abc", "a" * 20, "aabbccdd", "abababab", "a" * 12] \
    + list("abcdefghijklmnopqrstuvwxyz") + ["k" * 26, "z" * 50]


def gen_strings(n):
    random.seed(SEED)
    cases = list(SEED_CASES)
    for _ in range(n):
        length = random.randint(0, 30)
        cases.append("".join(random.choice(ALPHA) for _ in range(length)))
    return cases


def load(path):
    spec = importlib.util.spec_from_file_location("cand_" + path.stem, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for fn in ("encode", "decode"):
        if not hasattr(m, fn):
            raise AttributeError(f"{path.name} に {fn}(s) が無い")
    return m.encode, m.decode


def evaluate(encode, decode):
    # (1) 往復一致: どんな x でも decode(encode(x)) == x
    for x in gen_strings(N):
        try:
            y = encode(x)
            z = decode(y)
        except Exception as e:
            return ("FAIL", f"例外: 入力 {x!r} → {type(e).__name__}: {e}")
        if z != x:
            return ("FAIL", f"往復不一致: x={x!r} → encode={y!r} → decode={z!r}")
    # (2) 圧縮性: 反復入力は短くなる（恒等変換のごまかしを弾く）。全点で確認する。
    #     短くなるだけでなく decode で元に戻ることも同時に確かめる。ここで使う k・z は往復検査の
    #     ランダム入力（ALPHA=abcde）には出ないため、復号を見ないと「z の復号だけ壊れた実装」を見逃す。
    checked = 0
    for ch in COMPRESS_CHARS:
        for n in COMPRESS_LENS:
            x = ch * n
            enc_big = encode(x)
            if not (isinstance(enc_big, str) and len(enc_big) < n):
                got = len(enc_big) if hasattr(enc_big, "__len__") else repr(enc_big)
                return ("FAIL", f"反復入力が圧縮されない（恒等変換の疑い）: len(encode({ch!r}*{n}))={got} ≥ {n}")
            try:
                back = decode(enc_big)
            except Exception as e:
                return ("FAIL", f"例外: 圧縮検査の復号 decode(encode({ch!r}*{n})) → {type(e).__name__}: {e}")
            if back != x:
                return ("FAIL", f"圧縮検査の復号不一致: x={ch!r}*{n} → encode={enc_big!r} → decode={back!r}")
            checked += 1
    return ("PASS", f"往復一致 {len(SEED_CASES)}+{N} 件 ＋ 反復入力 {checked} 点を圧縮し復号一致（decode(encode(x))==x）")


def grade(path):
    try:
        encode, decode = load(path)
    except Exception as e:
        return ("FAIL", f"読込失敗: {e}")
    try:
        return evaluate(encode, decode)
    except Exception as e:
        return ("FAIL", f"実行エラー: {type(e).__name__}: {e}")


def table(rows, title):
    print(f"\n### {title}")
    print("| 対象 | 判定 | 詳細 |")
    print("|---|---|---|")
    for n, v, d in rows:
        print(f"| {n} | {v} | {d} |")


def selftest():
    print("# オラクル自己検証 — プロパティベース（往復）RLE")
    rv, rd = grade(CORPUS / "reference.py")
    table([("reference", rv, rd)], "① 正しい RLE reference（PASS であるべき）")
    controls = [
        ("broken_encode.py", "個数が1ずれる → 往復不一致"),
        ("broken_decode.py", "個数を1桁しか読まない → 2桁の連続で破綻"),
        ("broken_identity.py", "encode=decode=恒等 → 往復は通るが圧縮しない"),
        ("broken_decode_z.py", "z を含む符号列だけ復号が空になる → 圧縮検査で復号を見ないと見逃す"),
    ]
    brows, caught = [], True
    for f, why in controls:
        v, d = grade(CORPUS / f)
        ok = (v == "FAIL")
        caught = caught and ok
        brows.append((f, v, ("検出OK " if ok else "検出NG ") + d))
    table(brows, "② 壊れた実装（FAIL であるべき）")
    valid = (rv == "PASS") and caught
    print(f"\n## オラクル判定: {'PASS（バグを捕まえ正例を通す＝信頼できる）' if valid else 'FAIL（オラクル自体に欠陥）'}")
    return valid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", default="reference")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    v, d = grade(CORPUS / f"{a.candidate}.py")
    table([(f"{a.candidate}.py", v, d)], "採点（プロパティ／往復）")
    sys.exit(0 if v == "PASS" else 1)


if __name__ == "__main__":
    main()
