"""Run from the repository root after installing the package."""
import json
from tess_detectability.demonstration import normalization_case

if __name__ == "__main__":
    print(json.dumps({
        "scope": "New synthetic arithmetic demonstration using the original V1 function",
        "cases": [normalization_case(depth) for depth in (0, 100, 500)],
    }, indent=2, allow_nan=False))
