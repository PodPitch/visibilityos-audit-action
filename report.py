import csv
from collections import defaultdict
from datetime import date
from itertools import pairwise
from os import environ
from pathlib import Path


CONDITIONS = ("prompt", "engine", "model", "mode", "country", "language", "location", "brand")
REQUIRED_COLUMNS = {"date", "mentioned", "linked", *CONDITIONS}
FLAGS = {"yes": True, "no": False}


def read_counts(path: Path) -> dict[str, int]:
    observations = defaultdict(dict)
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, strict=True)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)) or not REQUIRED_COLUMNS.issubset(headers):
            raise ValueError("Invalid audit headers")
        for row in reader:
            if None in row or any(row[column] is None for column in headers):
                raise ValueError("Invalid number of columns")
            if row["mentioned"] not in FLAGS or row["linked"] not in FLAGS:
                raise ValueError("Invalid flag")
            recorded_on = date.fromisoformat(row["date"])
            conditions = tuple(row[column].strip() for column in CONDITIONS)
            if any(not value for column, value in zip(CONDITIONS, conditions) if column != "location"):
                raise ValueError("Missing matching field")
            checks = observations[conditions]
            if recorded_on in checks:
                raise ValueError("Duplicate audit observation")
            is_linked = FLAGS[row["linked"]]
            checks[recorded_on] = (FLAGS[row["mentioned"]] or is_linked, is_linked)

    total = presence_changes = link_changes = 0
    for checks in observations.values():
        for earlier, later in pairwise(sorted(checks)):
            total += 1
            was_present, was_linked = checks[earlier]
            is_present, is_linked = checks[later]
            presence_changes += was_present != is_present
            link_changes += was_linked != is_linked

    return {
        "matched-comparisons": total,
        "presence-changes": presence_changes,
        "link-changes": link_changes,
    }


def main() -> None:
    workspace = Path(environ["GITHUB_WORKSPACE"]).resolve()
    requested_path = Path(environ["VISIBILITYOS_AUDIT_CSV"])
    try:
        source = (workspace / requested_path).resolve(strict=True)
        if requested_path.is_absolute() or not source.is_relative_to(workspace) or not source.is_file():
            raise ValueError("Invalid workspace path")
        counts = read_counts(source)
    except (OSError, ValueError, RuntimeError, csv.Error):
        raise SystemExit(
            "The VisibilityOS audit CSV could not be read. Check the workspace path, headers, dates and yes/no fields."
        ) from None

    with Path(environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
        for name, value in counts.items():
            output.write(f"{name}={value}\n")

    with Path(environ["GITHUB_STEP_SUMMARY"]).open("a", encoding="utf-8") as summary:
        summary.write("## VisibilityOS audit comparison\n\n")
        summary.write("| Measure | Count |\n| --- | ---: |\n")
        for name, value in counts.items():
            summary.write(f"| {name.replace('-', ' ').capitalize()} | {value} |\n")


if __name__ == "__main__":
    main()
