import json
from pathlib import Path

import pytest

from rag.retriever import VARIANTS, retrieve


ROOT = Path(__file__).resolve().parents[2]
PORTFOLIO = json.loads((ROOT / "data/processed/demo_portfolio.json").read_text())


def test_every_documented_variant_returns_typed_evidence():
    for variant in VARIANTS:
        results = retrieve(["Python", "FastAPI", "forecasting"], PORTFOLIO, variant=variant, k=2)
        assert len(results) == 2
        assert all(result.id and result.title for result in results)


def test_unknown_variant_is_rejected():
    with pytest.raises(ValueError, match="Unknown retrieval variant"):
        retrieve(["Python"], PORTFOLIO, variant="not-a-variant")
