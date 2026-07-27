#!/usr/bin/env python3
"""
Static dependency and environment-assumption audit for the UniP workspace.

Purpose
-------
1. Scan Python files under src/ and collect imported root modules.
2. Classify imports as stdlib / local / ROS / third-party.
3. Report obvious environment-specific hardcodes.

This script is intentionally read-only:
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# ROS Python import roots currently relevant to the baseline.
# This list can be extended later without changing the audit logic.
ROS_IMPORT_ROOTS = {
    "ament_index_python",
    "builtin_interfaces",
    "control_msgs",
    "cv_bridge",
    "geometry_msgs",
    "gpd_ros_messages",
    "rclpy",
    "rosidl_runtime_py",
    "sensor_msgs",
    "std_msgs",
    "std_srvs",
    "tf2_geometry_msgs",
    "tf2_ros",
    "trajectory_msgs",
    "visualization_msgs",
    "moveit_msgs",
}


# Environment assumptions we explicitly want to eliminate or review.
HARDCODE_PATTERNS: dict[str, re.Pattern[str]] = {
    "/home/ws": re.compile(r"/home/ws\b"),
    "/opt/ros/humble": re.compile(r"/opt/ros/humble\b"),
    "python3.10": re.compile(r"python3\.10"),
    "CUDA 12.1": re.compile(r"(?:cuda(?:-toolkit)?[-_/ ]?12[-.]1|cu121)", re.IGNORECASE),
    "GPU arch 8.9": re.compile(r"(?:TORCH_CUDA_ARCH_LIST.{0,30}8\.9|\b8\.9\b)"),
    "/usr/local/lib": re.compile(r"/usr/local/lib\b"),
}


@dataclass(frozen=True)
class ImportOccurrence:
    module: str
    file: Path
    line: int


@dataclass(frozen=True)
class HardcodeOccurrence:
    label: str
    file: Path
    line: int
    text: str


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parent.parent
    default_src = default_repo_root / "src"

    parser = argparse.ArgumentParser(
        description="Audit Python dependencies and environment hardcodes in UniP."
    )
    parser.add_argument(
        "--src",
        type=Path,
        default=default_src,
        help=f"Source directory to scan (default: {default_src})",
    )
    parser.add_argument(
        "--show-occurrences",
        action="store_true",
        help="Show every file/line where each imported module occurs.",
    )
    return parser.parse_args()


def iter_python_files(src_dir: Path) -> Iterable[Path]:
    yield from sorted(
        path
        for path in src_dir.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def root_module(name: str) -> str:
    return name.split(".", 1)[0]


def collect_local_roots(src_dir: Path) -> set[str]:
    """
    Collect likely local import roots.

    We include:
    - immediate package/repository directories under src/;
    - all directories containing __init__.py;
    - top-level .py module names.
    """
    roots: set[str] = set()

    for child in src_dir.iterdir():
        if child.is_dir() and not child.name.startswith("."):
            roots.add(child.name.replace("-", "_"))
        elif child.is_file() and child.suffix == ".py":
            roots.add(child.stem)

    for init_file in src_dir.rglob("__init__.py"):
        package_dir = init_file.parent
        try:
            relative = package_dir.relative_to(src_dir)
        except ValueError:
            continue
        if relative.parts:
            roots.add(relative.parts[0].replace("-", "_"))
            roots.add(package_dir.name.replace("-", "_"))

    return roots


def collect_imports(path: Path) -> tuple[list[ImportOccurrence], list[str]]:
    occurrences: list[ImportOccurrence] = []
    errors: list[str] = []

    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return [], [f"{path}: read failed: {exc}"]
    except OSError as exc:
        return [], [f"{path}: read failed: {exc}"]

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [], [f"{path}:{exc.lineno}: syntax error: {exc.msg}"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                occurrences.append(
                    ImportOccurrence(root_module(alias.name), path, node.lineno)
                )
        elif isinstance(node, ast.ImportFrom):
            # Relative imports are local by definition and do not expose a useful
            # external root module, so skip them here.
            if node.level and node.level > 0:
                continue
            if node.module:
                occurrences.append(
                    ImportOccurrence(root_module(node.module), path, node.lineno)
                )

    return occurrences, errors


def collect_hardcodes(path: Path) -> list[HardcodeOccurrence]:
    findings: list[HardcodeOccurrence] = []

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return findings

    for line_no, line in enumerate(lines, start=1):
        for label, pattern in HARDCODE_PATTERNS.items():
            if pattern.search(line):
                findings.append(
                    HardcodeOccurrence(
                        label=label,
                        file=path,
                        line=line_no,
                        text=line.strip(),
                    )
                )
    return findings


def classify_modules(
    modules: set[str],
    local_roots: set[str],
) -> dict[str, list[str]]:
    stdlib = set(getattr(sys, "stdlib_module_names", set()))

    categories: dict[str, list[str]] = {
        "STDLIB": [],
        "LOCAL": [],
        "ROS": [],
        "THIRD-PARTY": [],
    }

    for module in sorted(modules):
        if module in stdlib:
            categories["STDLIB"].append(module)
        elif module in local_roots:
            categories["LOCAL"].append(module)
        elif module in ROS_IMPORT_ROOTS:
            categories["ROS"].append(module)
        else:
            categories["THIRD-PARTY"].append(module)

    return categories


def relative(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(path)


def print_module_section(title: str, modules: list[str]) -> None:
    print(f"\n[{title}]")
    if not modules:
        print("  (none)")
        return
    for module in modules:
        print(f"  {module}")


def main() -> int:
    args = parse_args()
    src_dir = args.src.expanduser().resolve()

    if not src_dir.is_dir():
        print(f"[ERROR] Source directory does not exist: {src_dir}", file=sys.stderr)
        return 2

    repo_root = src_dir.parent
    python_files = list(iter_python_files(src_dir))

    if not python_files:
        print(f"[ERROR] No Python files found under: {src_dir}", file=sys.stderr)
        return 2

    local_roots = collect_local_roots(src_dir)

    all_occurrences: list[ImportOccurrence] = []
    parse_errors: list[str] = []
    hardcodes: list[HardcodeOccurrence] = []

    for path in python_files:
        occurrences, errors = collect_imports(path)
        all_occurrences.extend(occurrences)
        parse_errors.extend(errors)
        hardcodes.extend(collect_hardcodes(path))

    modules = {occ.module for occ in all_occurrences}
    categories = classify_modules(modules, local_roots)

    print("=" * 72)
    print("UniP Static Dependency Audit")
    print("=" * 72)
    print(f"Source root : {src_dir}")
    print(f"Python files: {len(python_files)}")
    print(f"Import roots: {len(modules)}")

    # Most useful sections first.
    print_module_section("THIRD-PARTY IMPORTS", categories["THIRD-PARTY"])
    print_module_section("ROS IMPORTS", categories["ROS"])
    print_module_section("LOCAL IMPORTS", categories["LOCAL"])
    print_module_section("STDLIB IMPORTS", categories["STDLIB"])

    print("\n[HARDCODE WARNINGS]")
    if not hardcodes:
        print("  (none)")
    else:
        for finding in hardcodes:
            location = f"{relative(finding.file, repo_root)}:{finding.line}"
            print(f"  {finding.label:<18} {location}")
            print(f"    {finding.text}")

    if args.show_occurrences:
        print("\n[IMPORT OCCURRENCES]")
        by_module: dict[str, list[ImportOccurrence]] = {}
        for occ in all_occurrences:
            by_module.setdefault(occ.module, []).append(occ)

        for module in sorted(by_module):
            print(f"  {module}")
            for occ in sorted(
                by_module[module],
                key=lambda item: (str(item.file), item.line),
            ):
                print(f"    {relative(occ.file, repo_root)}:{occ.line}")

    print("\n[PARSE WARNINGS]")
    if not parse_errors:
        print("  (none)")
    else:
        for error in parse_errors:
            print(f"  {error}")

    print("\n" + "=" * 72)
    if parse_errors:
        print("RESULT: COMPLETED WITH WARNINGS")
    else:
        print("RESULT: PASS")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
