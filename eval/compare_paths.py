"""Run the Lab 06 comparison against the team's AssistantService."""

import argparse
import json
from pathlib import Path
from statistics import median
from time import perf_counter

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.llm import StubLLM
from assistant_core.models import Intent, Message, Response
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import Hit, make_index
from assistant_core.responder import TemplateResponder
from assistant_core.service import AssistantService

ROOT = Path(__file__).resolve().parents[1]
INDEX_KIND = "bm25"
MIN_SCORE = 2.0
TOP_K = 3


class EmptyIndex:
    """Keep rule handling on the same service path with an empty corpus."""

    def search(self, query: str, k: int = 3) -> list[Hit]:
        return []


def correct(case: dict, response: Response) -> bool:
    if case.get("expect_abstain"):
        return response.path == "abstain" or response.intent is Intent.UNKNOWN
    if "expect_contains" in case:
        return case["expect_contains"] in response.answer
    return any(source.id == case["expect_source"] for source in response.sources)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true", help="Evaluate the 20 original cases only.")
    args = parser.parse_args()
    cases = [json.loads(line) for line in (ROOT / "eval/cases.jsonl").read_text(encoding="utf-8").splitlines() if line]
    if args.baseline:
        cases = cases[:20]

    settings = Settings(data_dir=ROOT / "data")
    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    chunks = load_folder(settings.data_dir / "kb")
    index = make_index(INDEX_KIND, chunks)
    stub = StubLLM()
    paths = {
        "deterministic": RagAnswerer(EmptyIndex(), None, MIN_SCORE, TOP_K),
        "retrieval": RagAnswerer(index, None, MIN_SCORE, TOP_K),
        f"llm ({stub.name})": RagAnswerer(index, stub, MIN_SCORE, TOP_K),
    }
    abstain_total = sum(case.get("expect_abstain", False) for case in cases)
    print(
        f"{len(cases)} cases, {len(chunks)} chunks, provider={stub.name}, index={INDEX_KIND}, "
        f"min_score={MIN_SCORE}, k={TOP_K}"
    )
    print(f"{'path':16} {'correct':>8} {'abstain ok':>11} {'p50 ms':>9} {'max ms':>9}  fail IDs")
    for name, rag in paths.items():
        service = AssistantService(settings, offices, handbook, TemplateResponder(), rag)
        latencies = []
        failures = []
        abstain_ok = 0
        for case in cases:
            message = Message(text=case["question"])
            start = perf_counter()
            response = service.handle(message)
            latencies.append((perf_counter() - start) * 1000)
            if correct(case, response):
                abstain_ok += case.get("expect_abstain", False)
            else:
                failures.append(case["id"])

        score = f"{len(cases) - len(failures)}/{len(cases)}"
        abstains = f"{abstain_ok}/{abstain_total}"
        print(
            f"{name:16} {score:>8} {abstains:>11} {median(latencies):9.3f} {max(latencies):9.3f}  {' '.join(failures)}"
        )


if __name__ == "__main__":
    main()
