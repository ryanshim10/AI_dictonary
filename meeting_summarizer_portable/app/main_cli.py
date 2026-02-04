import argparse
import glob
from pathlib import Path

from .pipeline import process_one


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="../config.ini", help="path to config.ini")
    ap.add_argument("--input", required=True, help="mp4 path or glob (e.g., input\\*.mp4)")
    ap.add_argument("--out", default="../out", help="output root directory")
    args = ap.parse_args()

    base_dir = str(Path(__file__).resolve().parents[1])
    cfg_path = str((Path(base_dir) / args.config).resolve()) if not Path(args.config).is_absolute() else args.config
    out_root = str((Path(base_dir) / args.out).resolve()) if not Path(args.out).is_absolute() else args.out

    files = glob.glob(args.input)
    if not files:
        raise SystemExit(f"No files matched: {args.input}")

    for f in files:
        def log(s: str):
            print(s, flush=True)
        process_one(f, base_dir=base_dir, out_root=out_root, cfg_path=cfg_path, log=log)


if __name__ == "__main__":
    main()
