"""Command-line interface for assistant_core."""

import argparse
import json
import logging
import re
import sys
import time

from pydantic import ValidationError

from assistant_core.config import Settings, load_settings
from assistant_core.errors import AssistantError, ConfigError, DataError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message, Response
from assistant_core.responder import StubLLMResponder, TemplateResponder
from assistant_core.service import AssistantService


def parse_session_id(text: str) -> str:
    """Accept a bounded opaque identifier, keeping arbitrary text out of metadata."""
    value = text.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value):
        raise argparse.ArgumentTypeError("session ID must be 1-64 ASCII letters/digits, with optional _ or -")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="assistant_core",
        description="Smart academic assistant command-line interface.",
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Query to ask the assistant. If omitted, starts interactive mode.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the response formatted as JSON instead of plain text.",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="List the titles of the loaded handbook rules and exit.",
    )
    parser.add_argument(
        "--show-sources",
        action="store_true",
        help="Include source IDs and titles in plain-text responses.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=None,
        help="Override the log level for this run (DEBUG, INFO, WARNING, ERROR).",
    )
    parser.add_argument(
        "--session-id",
        type=parse_session_id,
        default="local",
        help="Opaque session identifier for request logs (1-64 letters/digits, _ or -).",
    )
    parser.add_argument(
        "--credit-rate",
        type=int,
        default=None,
        help="Override the tuition credit rate (VND) for this run.",
    )
    parser.add_argument(
        "--fail-provider",
        action="store_true",
        help="Simulate an upstream provider failure to exercise fallback behavior.",
    )
    return parser


def format_output(response: Response, as_json: bool, show_sources: bool = False) -> str:
    if as_json:
        return json.dumps(
            {
                "answer": response.answer,
                "intent": response.intent.value,
                "sources": [s.model_dump() for s in response.sources],
                "degraded": response.degraded,
            },
            ensure_ascii=False,
            indent=2,
        )
    if show_sources and response.sources:
        citations = "\n".join(f"- {source.id}: {source.title}" for source in response.sources)
        return f"{response.answer}\nSources:\n{citations}"
    return response.answer


def process_message(
    service: AssistantService,
    text: str,
    logger: logging.Logger,
    as_json: bool,
    session_id: str = "local",
    show_sources: bool = False,
) -> None:
    start_time = time.perf_counter()
    msg = Message(text=text, session_id=session_id)
    response = service.handle(msg)
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    logger.info(
        "handled",
        extra={
            "intent": response.intent.value,
            "latency_ms": elapsed_ms,
            "session": msg.session_id,
            "degraded": response.degraded,
        },
    )
    sys.stdout.write(format_output(response, as_json, show_sources) + "\n")
    sys.stdout.flush()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.json and args.show_sources:
        parser.error("--show-sources is for plain text; --json already includes sources")
    if args.list_rules and args.query:
        parser.error("--list-rules cannot be combined with a query")

    try:
        settings = load_settings()
        overrides = {}
        if args.log_level is not None:
            overrides["log_level"] = args.log_level
        if args.credit_rate is not None:
            overrides["credit_rate_vnd"] = args.credit_rate
        if overrides:
            settings = Settings.model_validate({**settings.model_dump(), **overrides})

        logger = setup_logging(level=settings.log_level)

        offices_path = settings.data_dir / "offices.csv"
        handbook_path = settings.data_dir / "handbook.json"

        offices = OfficeDirectory.from_csv(offices_path)
        handbook = Handbook.from_json(handbook_path)

        if settings.llm_provider == "stub":
            responder = StubLLMResponder(fail=args.fail_provider)
        else:
            responder = TemplateResponder()

        service = AssistantService(
            settings=settings,
            offices=offices,
            handbook=handbook,
            responder=responder,
        )
    except (ConfigError, DataError, AssistantError, ValidationError, OSError) as exc:
        sys.stderr.write(f"Startup error: {exc}\n")
        return 1

    if args.list_rules:
        sys.stdout.write(format_output(service.list_rules(), args.json, args.show_sources) + "\n")
        return 0

    if args.query:
        query_text = " ".join(args.query).strip()
        if not query_text:
            sys.stderr.write("Error: Query cannot be empty.\n")
            return 1
        try:
            process_message(
                service,
                query_text,
                logger,
                as_json=args.json,
                session_id=args.session_id,
                show_sources=args.show_sources,
            )
            return 0
        except (AssistantError, ValidationError, ValueError) as exc:
            sys.stderr.write(f"Runtime error: {exc}\n")
            return 1

    # Interactive mode
    sys.stdout.write("Assistant ready. Type 'quit' to exit.\n")
    sys.stdout.flush()
    while True:
        try:
            sys.stdout.write("> ")
            sys.stdout.flush()
            line = sys.stdin.readline()
            if not line:  # EOF
                break
            text = line.strip()
            if not text:
                continue
            if text.lower() == "quit":
                break
            process_message(
                service,
                text,
                logger,
                as_json=args.json,
                session_id=args.session_id,
                show_sources=args.show_sources,
            )
        except KeyboardInterrupt:
            break
        except (AssistantError, ValidationError, ValueError) as exc:
            sys.stderr.write(f"Error: {exc}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
