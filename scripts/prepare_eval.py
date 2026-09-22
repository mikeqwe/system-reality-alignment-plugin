"""Export only one task's inputs to a NEW directory, without its rubric."""
import argparse
from pathlib import Path
import shutil

CASES = Path(__file__).resolve().parents[1] / "evals/cases"


def prepare(case: str, output: Path) -> Path:
    available = {p.name for p in CASES.iterdir() if p.is_dir()}
    if case not in available:
        raise ValueError(f"unknown case: {case}")
    source = CASES / case
    # Only the explicit task assets are exported; never copy rubrics or bytecode.
    inputs = [p for p in source.iterdir() if p.is_file() and p.suffix in {".md", ".py", ".json"}]
    if any(p.is_symlink() for p in inputs):
        raise ValueError("symlinked evaluation input")
    output.mkdir(parents=True, exist_ok=False)
    for path in inputs:
        shutil.copyfile(path, output / path.name)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=sorted(p.name for p in CASES.iterdir() if p.is_dir()))
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        print(prepare(args.case, args.output))
    except (OSError, ValueError) as exc:
        parser.exit(1, f"preparation failed: {exc}\n")
