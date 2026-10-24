# Test ownership

This foundation has no runtime behavior tests yet. CI checks editable/wheel installation and import,
not fabricated business assertions. Add real tests with each owner's implementation.
Pytest discovers `tests/test_*.py`; CI will run pytest once at least one such file exists.
Required cases: greeting, 18+2 tuition = 9450000, Library room/hours, thesis source H26-5.3,
unknown, provider fallback/source/degraded, invalid text/credits, malformed data, config/log streams.
