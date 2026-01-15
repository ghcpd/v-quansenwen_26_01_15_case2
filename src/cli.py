import argparse
import json

from .api import run_workflow


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a DriftFlow workflow")
    parser.add_argument("--config", default="./config.json", help="Path to JSON config")
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()

    result = run_workflow(args.config)

    if args.print_json:
        print(json.dumps(result, indent=2))
        return

    for item in result["results"]:
        if item.get("ok"):
            print(f"OK {item['name']}: {item['output']}")
        else:
            print(f"FAIL {item['name']}: {item.get('error')}")


if __name__ == "__main__":
    main()
