#!/usr/bin/env python
"""
cleanup_logs.py  ── 清理 ./logs 目录

用法示例
--------
# 仅保留最近 10 个日志文件
python cleanup_logs.py --keep 10

# 删除 30 天前的日志，并把剩余文件 >5MB 的压缩
python cleanup_logs.py --days 30 --gzip --size 5

# 先 dry-run 看看将删除哪些
python cleanup_logs.py --days 30 --dry
"""
from __future__ import annotations
import argparse, gzip, shutil, time
from pathlib import Path
from datetime import datetime, timedelta

LOG_DIR = Path("./logs")
from pathlib import Path
THIS_FILE = Path(__file__).resolve()          # /abs/path/cleanup_logs.py
THIS_FILE_PYC = THIS_FILE.with_suffix(".pyc") # /abs/path/cleanup_logs.pyc
SKIP_SET = {THIS_FILE, THIS_FILE_PYC}
def compress_file(fp: Path):
    gz_fp = fp.with_suffix(fp.suffix + ".gz")
    with fp.open("rb") as src, gzip.open(gz_fp, "wb") as dst:
        shutil.copyfileobj(src, dst)
    fp.unlink()                          # 删除原文件
    print("gzip  ", gz_fp.name)

def main():
    ap = argparse.ArgumentParser("log cleaner")
    ap.add_argument("--keep", type=int, default=5,
                    help="保留最近 N 个日志（其余删除）")
    ap.add_argument("--days", type=int, default=None,
                    help="删除 N 天前的日志")
    ap.add_argument("--gzip", action="store_true",
                    help="把未删除但较旧/较大的文件 gzip 压缩")
    ap.add_argument("--size", type=int, default=10,
                    help="当 --gzip 时，>N MB 的文件才压缩 (默认 10MB)")
    ap.add_argument("--dry", action="store_true",
                    help="仅预览，不实际删除/压缩")
    args = ap.parse_args()

    if not LOG_DIR.exists():
        print("logs 目录不存在，退出。")
        return

    files = sorted(
        [f for f in LOG_DIR.iterdir() if f.is_file() and not f.name.endswith(".gz")],
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    to_delete: list[Path] = []
    if args.keep is not None:
        to_delete += files[args.keep:]
    if args.days is not None:
        cutoff = time.time() - args.days * 86400
        to_delete += [f for f in files if f.stat().st_mtime < cutoff]

    # 去重
    to_delete = list(dict.fromkeys(to_delete))

    # ---------- Dry-run ----------
    if args.dry:
        print("将删除：")
        for f in to_delete:
            print("  ", f.name)
        print(f"共 {len(to_delete)} 个文件。")
        return

    # ---------- 删除 ----------
    for f in to_delete:
        if f.resolve() in SKIP_SET:               # ← 判断绝对路径最稳妥
            continue
        f.unlink(missing_ok=True)
        print("delete", f.name)

    # ---------- gzip 压缩 ----------
    if args.gzip:
        threshold = args.size * 1024 * 1024
        for f in files:
            if f in to_delete or f.with_suffix(f.suffix + ".gz").exists():
                continue
            if f.stat().st_size > threshold:
                compress_file(f)

if __name__ == "__main__":
    main()
    
##定时清理：0 3 * * * /usr/bin/python ./logs/cleanup_log.py --gzip --size 5 >> ./logs/cleanup_log.py 2>&10: command not found
##python logs/cleanup_logs.py --keep 5