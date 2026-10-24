# CL-02 proposed contracts — review pending

These are interface decisions from Week3/plan.md, not implemented runtime APIs.
Bảo owns models/errors and their PR. Owners review this document before parallel implementation.

## Shared models and errors

- Intent values: greeting, fee, office, rule, unknown.
- Message: text str, length 1–2000, reject whitespace-only; session_id str = "local".
- Source: id str, title str. Rule: id str, title str, text str.
- Response: answer str, intent Intent, sources list[Source] with Field(default_factory=list), degraded bool = False.
- Pydantic ValidationError for models; ConfigError/DataError for startup; InvalidRequest for tools;
  ProviderError for responder failure. Do not hide programming errors as unknown/fallback.

## Service and module boundaries

- AssistantService.handle(msg: Message) -> Response; constructor receives settings, offices, handbook, responder.
- Responder.explain(question: str, rule: Rule) -> str. TemplateResponder and StubLLMResponder(fail=False/True)
  share that protocol; no network/random/sleep. ProviderError causes template fallback with source retained,
  degraded=True. Only that fallback sets degraded=True.
- route(text: str, office_names: set[str]) -> Intent; greeting -> fee -> office -> rule.
  Unmatched handbook search becomes unknown in service. Greeting baseline uses stripped lowercase exact
  hi/hello/hey/xin chao; punctuation expansion would be a documented behavior change.
- parse_credits(text: str) -> tuple[int, int]; tuition(credits: int, retake: int, rate: int,
  retake_multiplier: float, max_credits: int) -> int. Pure functions; credits 1..max, retake integer >=0;
  missing/negative invalid. Formula credits*rate + retake*rate*retake_multiplier.
  Service converts InvalidRequest into fee guidance with degraded=False.
- OfficeDirectory.from_csv(path: Path), names, find(text); names supplies router vocabulary. Case-insensitive
  name substring, ties preserve file order. Return record name/room/hours or None.
- Handbook.from_json(path: Path), search(query) -> Rule | None; score query tokens longer than 3 as
  substring matches in rule.text, preserve repeated token scoring and first rule on ties; zero -> None.
  Load once, UTF-8/Path; missing/malformed/schema-invalid input -> DataError.
- Settings/load_settings(): ASSISTANT_DATA_DIR=data, LLM_PROVIDER=stub, LLM_API_KEY=empty,
  CREDIT_RATE_VND=450000, RETAKE_MULTIPLIER=1.5, MAX_CREDITS=30, LOG_LEVEL=INFO.
  Existing environment wins over .env. Positive numeric domains; unsupported provider invalid;
  stub/template need no key. Huy finalizes concrete Settings signature with dependent owners.
- CLI always calls service; stdout answers, stderr logs/errors; expected runtime error exit 1,
  argparse usage error exit 2. JSON CLI and exact rule-ID lookup are later H1 extensions.

Scope excludes history/stats/save, help, FastAPI/UI and actual LLM calls. This PR implements only package import.
