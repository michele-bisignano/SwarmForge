"""
extract_contract_doc.py

Extracts a markdown doc snippet from a griffe JSON dump for a specific class
and method subset. Used by ContractArchitect to produce context slices for
ClassCoders. Never reads or exposes source files — only parsed documentation.

Usage:
    python Tools/griffe/extract_contract_doc.py \
        --api-json docs/api/<package>.json \
        --class <ClassName> \
        --methods <method1> [<method2> ...] \
        --output docs/snippets/<ClassName>_snippet.md
"""
import argparse
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _find_class(members: dict, name: str) -> dict | None:
    """Recursively search for a class by name in a griffe member tree.

    @param members: The members dict from a griffe JSON node.
    @param name: Class name to locate.
    @return: The class dict if found, None otherwise.
    """
    for k, node in members.items():
        if k == name and node.get("kind") == "class":
            return node
        if "members" in node:
            result = _find_class(node["members"], name)
            if result is not None:
                return result
    return None


def _format_method(method_name: str, method: dict) -> str:
    """Format a single method node as a markdown documentation block.

    @param method_name: The method's name as it appears in source.
    @param method: The method dict from the griffe JSON.
    @return: Formatted markdown string including signature and docstring.
    """
    docstring: str = method.get("docstring", {}).get("value", "No docstring.")
    params: list = method.get("parameters", [])
    returns: str = (
        method.get("returns", {}).get("annotation", "None")
        if method.get("returns")
        else "None"
    )

    param_str = ", ".join(
        f"{p['name']}: {p.get('annotation', 'Any')}"
        for p in params
        if p["name"] != "self"
    )
    signature = f"{method_name}({param_str}) -> {returns}"

    return f"### `{signature}`\n```\n{docstring}\n```\n"


def extract_snippet(
    api_json_path: str,
    class_name: str,
    method_names: list[str],
    output_path: str,
) -> None:
    """Extract a markdown doc snippet for the specified class methods.

    Reads the griffe JSON dump, locates the target class, and produces a
    markdown file containing only the requested method signatures and
    docstrings. The output is the sole context artifact passed to a ClassCoder
    for dependency resolution.

    @param api_json_path: Path to the griffe JSON dump file.
    @param class_name: Name of the class to extract documentation from.
    @param method_names: List of method names to include in the snippet.
    @param output_path: Destination path for the generated markdown file.
    @raise FileNotFoundError: If the api_json_path does not exist.
    @raise KeyError: If the class or any requested method is not found in the JSON.
    """
    json_path = Path(api_json_path)
    if not json_path.exists():
        raise FileNotFoundError(f"griffe JSON not found: {api_json_path}")

    with json_path.open(encoding="utf-8") as f:
        api: dict = json.load(f)

    target_class = _find_class(api, class_name)
    if target_class is None:
        raise KeyError(f"Class '{class_name}' not found in {api_json_path}.")

    class_doc: str = target_class.get("docstring", {}).get("value", "No docstring.")

    lines: list[str] = [
        f"# Doc Snippet: {class_name}\n",
        f"**Class docstring:** {class_doc}\n",
        "## Methods\n",
    ]

    for name in method_names:
        method = target_class.get("members", {}).get(name)
        if method is None:
            raise KeyError(f"Method '{class_name}.{name}' not found in the JSON.")
        lines.append(_format_method(name, method))

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Snippet written to %s", output_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Extract a griffe doc snippet for a ClassCoder context slice."
    )
    parser.add_argument("--api-json", required=True, help="Path to the griffe JSON dump.")
    parser.add_argument("--class", dest="class_name", required=True, help="Target class name.")
    parser.add_argument("--methods", nargs="+", required=True, help="Methods to include.")
    parser.add_argument("--output", required=True, help="Output markdown path.")
    args = parser.parse_args()

    extract_snippet(args.api_json, args.class_name, args.methods, args.output)