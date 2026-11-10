from src.api.client import SportRadarAPIError
from src.api.competitions import collect_competitions
from src.api.complexes import collect_complexes
from src.api.rankings import collect_doubles_rankings


def main() -> int:
    """Run each feed independently and return a non-zero code on failure."""
    tasks = [
        ("Competitions", collect_competitions),
        ("Complexes and venues", collect_complexes),
        ("Doubles competitor rankings", collect_doubles_rankings),
    ]
    failures: list[str] = []

    print("Starting SportRadar Tennis data collection...\n")
    for name, collector in tasks:
        print(f"[{name}]")
        try:
            path = collector()
            print(f"SUCCESS: {path}\n")
        except (SportRadarAPIError, ValueError) as exc:
            failures.append(name)
            print(f"FAILED: {exc}\n")

    if failures:
        print("Collection finished with failures: " + ", ".join(failures))
        return 1

    print("All three raw JSON feeds were collected successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
