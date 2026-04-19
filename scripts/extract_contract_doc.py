"""
extract_contract_doc.py — extracts a markdown doc snippet from a griffe JSON dump.
Produces the context slice for ClassCoders. Never touches source files.

Usage:
    python scripts/extract_contract_doc.py \
        --api-json <path> --class <ClassName> \
        --methods <method1> [<method2> ...] \
        --output <output_path>
"""
import argparse
import json
from pathlib import Path

def _find_class(members: dict, name: str) -> dict | None:
    for k, node in members.items():
        if k == name and node.get("kind") == "class":
            return node
        if "members" in node:
            result = _find_class(node["members"], name)
            if result is not None:
                return result
    return None

def extract_snippet(
    api_json_path: str,
    class_name: str,
    method_names: list[str],
    output_path: str,
) -> None:
    """Extract a markdown doc snippet for the specified class methods.

    @param api_json_path: Path to the griffe JSON dump.
    @param class_name: Target class name.
    @param method_names: Method names to include.
    @param output_path: Output markdown path.
    @raise KeyError: If the class or method is not found.
    """
    with open(api_json_path) as f:
        api: dict = json.load(f)

    target = _find_class(api.get("members", {}), class_name)
    if target is None:
        raise KeyError(f"Class '{class_name}' not found in {api_json_path}.")

    lines: list[str] = [
        f"# Doc Snippet: {class_name}\n",
        f"**Class:** {target.get('docstring', {}).get('value', 'No docstring.')}\n\n## Methods\n",
    ]
    for name in method_names:
        method = target.get("members", {}).get(name)
        if method is None:
            raise KeyError(f"Method '{class_name}.{name}' not found.")
        doc = method.get("docstring", {}).get("value", "No docstring.")
        params = method.get("parameters", [])
        ret = method.get("returns", {}).get("annotation", "None") if method.get("returns") else "None"
        sig = f"{name}({', '.join(f'{p[\"name\"]}: {p.get(\"annotation\", \"Any\")}' for p in params if p['name'] != 'self')}) -> {ret}"
        lines.append(f"### `{sig}`\n```\n{doc}\n```\n")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")

def _find_class(members: dict, name: str) -> dict | None:
    for k, node in members.items():
        if k == name and node.get("kind") == "class":
            return node
        if "members" in node:
            result = _find_class(node["members"], name)
            if result is not None:
                return result
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-json", required=True)
    parser.add_argument("--class", dest="class_name", required=True)
    parser.add_argument("--methods", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    extract_snippet(args.api_json, args.class_name, args.methods, args.output)
    print(f"Snippet → {args.output}")