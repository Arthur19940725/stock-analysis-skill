#!/usr/bin/env python3
"""Deterministic scenario-return and rating calculator for stock-analysis."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


EVIDENCE_ALLOWED = {
    "source_quality": {0, 10, 20, 30},
    "freshness_sync": {0, 8, 14, 20},
    "critical_coverage": {0, 10, 18, 25},
    "cross_validation": {0, 5, 10, 15},
    "assumption_transparency": {0, 4, 7, 10},
}


class InputError(ValueError):
    """Raised when deterministic rating inputs are incomplete or inconsistent."""


def _number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{field} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise InputError(f"{field} must be a finite number")
    return result


def _evidence_score(values: Any) -> tuple[int, str]:
    if not isinstance(values, dict):
        raise InputError("evidence must be an object")
    total = 0
    for field, allowed in EVIDENCE_ALLOWED.items():
        if field not in values:
            raise InputError(f"evidence.{field} is required")
        value = values[field]
        if isinstance(value, bool) or value not in allowed:
            choices = ", ".join(str(item) for item in sorted(allowed))
            raise InputError(f"evidence.{field} must be one of: {choices}")
        total += int(value)
    grade = "A" if total >= 80 else "B" if total >= 65 else "C" if total >= 50 else "D"
    return total, grade


def _base_rating(etr: float, hurdle: float) -> str:
    if etr >= hurdle + 0.10:
        return "强力买入"
    if etr >= hurdle:
        return "买入"
    if etr >= -0.05:
        return "持有/观察"
    if etr >= -0.15:
        return "减持/弱于大盘"
    return "卖出/回避"


def calculate(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise InputError("input must be a JSON object")

    current_price = _number(payload.get("current_price"), "current_price")
    if current_price <= 0:
        raise InputError("current_price must be greater than zero")

    raw_scenarios = payload.get("scenarios")
    if not isinstance(raw_scenarios, list) or len(raw_scenarios) != 3:
        raise InputError("scenarios must contain exactly bull, base, and bear")

    scenarios: dict[str, dict[str, float]] = {}
    probability_sum = 0.0
    for index, raw in enumerate(raw_scenarios):
        if not isinstance(raw, dict):
            raise InputError(f"scenarios[{index}] must be an object")
        name = str(raw.get("name", "")).strip().lower()
        if name not in {"bull", "base", "bear"} or name in scenarios:
            raise InputError("scenario names must be unique: bull, base, bear")
        target = _number(raw.get("target_price"), f"scenarios[{index}].target_price")
        cash = _number(
            raw.get("cash_distribution", 0),
            f"scenarios[{index}].cash_distribution",
        )
        probability = _number(raw.get("probability"), f"scenarios[{index}].probability")
        if target < 0 or probability < 0 or probability > 1:
            raise InputError("target_price must be non-negative and probability in [0, 1]")
        total_return = (target - current_price + cash) / current_price
        scenarios[name] = {
            "target_price": target,
            "cash_distribution": cash,
            "probability": probability,
            "total_return": total_return,
        }
        probability_sum += probability

    if set(scenarios) != {"bull", "base", "bear"}:
        raise InputError("scenarios must contain bull, base, and bear")
    if not math.isclose(probability_sum, 1.0, rel_tol=0.0, abs_tol=1e-9):
        raise InputError(f"scenario probabilities must sum to 1.0; got {probability_sum:.12g}")

    minimum_return = _number(
        payload.get("minimum_required_return", 0.10),
        "minimum_required_return",
    )
    active_premium = _number(
        payload.get("active_return_premium", 0.03),
        "active_return_premium",
    )
    benchmark_raw = payload.get("benchmark_expected_return")
    benchmark_return = (
        None
        if benchmark_raw is None
        else _number(benchmark_raw, "benchmark_expected_return")
    )
    hurdle = (
        minimum_return
        if benchmark_return is None
        else max(minimum_return, benchmark_return + active_premium)
    )

    etr = sum(item["probability"] * item["total_return"] for item in scenarios.values())
    expected_upside = sum(
        item["probability"] * max(item["total_return"], 0.0)
        for item in scenarios.values()
    )
    expected_downside = sum(
        item["probability"] * max(-item["total_return"], 0.0)
        for item in scenarios.values()
    )
    payoff_coverage = (
        None if math.isclose(expected_downside, 0.0, abs_tol=1e-15)
        else expected_upside / expected_downside
    )

    stress_return = _number(
        payload.get("independent_stress_total_return"),
        "independent_stress_total_return",
    )
    stress_loss = min(scenarios["bear"]["total_return"], stress_return)
    evidence_score, evidence_grade = _evidence_score(payload.get("evidence"))

    data_gate_passed = payload.get("data_gate_passed")
    positive_veto = payload.get("positive_rating_veto", False)
    unmodelable_veto = payload.get("unmodelable_veto", False)
    for field, value in (
        ("data_gate_passed", data_gate_passed),
        ("positive_rating_veto", positive_veto),
        ("unmodelable_veto", unmodelable_veto),
    ):
        if not isinstance(value, bool):
            raise InputError(f"{field} must be boolean")

    base_rating = _base_rating(etr, hurdle)
    downgrade_reasons: list[str] = []

    if not data_gate_passed or evidence_score < 50 or unmodelable_veto:
        final_rating = "暂不评级"
        if not data_gate_passed:
            downgrade_reasons.append("数据闸门未通过")
        if evidence_score < 50:
            downgrade_reasons.append("ECS<50")
        if unmodelable_veto:
            downgrade_reasons.append("存在损失无法建模的关键否决项")
    elif base_rating in {"强力买入", "买入"}:
        buy_gate = (
            payoff_coverage is not None
            and payoff_coverage >= 1.3
            and stress_loss > -0.50
            and evidence_score >= 60
            and not positive_veto
        )
        strong_gate = (
            payoff_coverage is not None
            and payoff_coverage >= 2.0
            and stress_loss > -0.35
            and evidence_score >= 75
            and not positive_veto
        )
        if base_rating == "强力买入" and strong_gate:
            final_rating = "强力买入"
        elif buy_gate:
            final_rating = "买入"
            if base_rating == "强力买入":
                downgrade_reasons.append("未同时满足强力买入的 PCR/SL/ECS 门槛")
        else:
            final_rating = "持有/观察"
            if payoff_coverage is None:
                downgrade_reasons.append("PCR=N/M，无法验证正面评级覆盖门槛")
            elif payoff_coverage < 1.3:
                downgrade_reasons.append("PCR<1.3")
            if stress_loss <= -0.50:
                downgrade_reasons.append("SL<=-50%")
            if evidence_score < 60:
                downgrade_reasons.append("ECS<60")
            if positive_veto:
                downgrade_reasons.append("存在正面评级否决项")
    elif base_rating == "卖出/回避" and evidence_score < 70:
        final_rating = "减持/回避新增仓位"
        downgrade_reasons.append("ECS<70，不支持高确信度卖出")
    else:
        final_rating = base_rating

    return {
        "current_price": current_price,
        "scenarios": scenarios,
        "probability_sum": probability_sum,
        "benchmark_expected_return": benchmark_return,
        "benchmark_fallback_used": benchmark_return is None,
        "hurdle_return": hurdle,
        "expected_total_return": etr,
        "expected_upside_contribution": expected_upside,
        "expected_downside_contribution": expected_downside,
        "payoff_coverage_ratio": payoff_coverage,
        "stress_loss": stress_loss,
        "evidence_score": evidence_score,
        "evidence_grade": evidence_grade,
        "base_rating": base_rating,
        "final_rating": final_rating,
        "downgrade_reasons": downgrade_reasons,
    }


def _load_payload(argv: list[str]) -> dict[str, Any]:
    if len(argv) > 2:
        raise InputError("usage: decision_math.py [input.json]")
    if len(argv) == 2:
        path = Path(argv[1])
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise InputError(f"cannot read {path}: {exc}") from exc
    else:
        text = sys.stdin.read()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise InputError("input must be a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    args = sys.argv if argv is None else argv
    try:
        result = calculate(_load_payload(args))
    except InputError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
