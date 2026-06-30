from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path to allow imports from src
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.pipeline import run_pipeline
from src.projector import DEFAULT_CONFIG


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Eightfold Candidate Data Transformer CLI"
    )
    parser.add_argument(
        "--sources",
        "-s",
        type=str,
        default="data/sources",
        help="Path to the directory containing candidate data sources",
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=None,
        help="Path to custom runtime config JSON file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Path to write the output JSON (prints to stdout if not specified)",
    )
    parser.add_argument(
        "--indent",
        "-i",
        type=int,
        default=2,
        help="Indentation for JSON output",
    )

    args = parser.parse_args()

    sources_dir = Path(args.sources)
    if not sources_dir.exists():
        print(f"Error: Sources directory '{args.sources}' does not exist.", file=sys.stderr)
        sys.exit(1)

    config = None
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Config file '{args.config}' does not exist.", file=sys.stderr)
            sys.exit(1)
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"Error parsing config JSON: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        config = DEFAULT_CONFIG

    try:
        results = run_pipeline(sources_dir, config)
    except Exception as exc:
        print(f"Pipeline execution failed: {exc}", file=sys.stderr)
        sys.exit(1)

    output_str = json.dumps(results, indent=args.indent, ensure_ascii=False)

    if args.output:
        out_path = Path(args.output)
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(output_str, encoding="utf-8")
            print(f"Successfully processed {len(results)} candidates. Output written to {args.output}")
        except Exception as exc:
            print(f"Failed to write output to file: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_str)


if __name__ == "__main__":
    main()
