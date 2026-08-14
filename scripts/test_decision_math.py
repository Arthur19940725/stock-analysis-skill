from __future__ import annotations

import copy
import unittest

from decision_math import InputError, calculate


def valid_payload() -> dict:
    return {
        "current_price": 100,
        "scenarios": [
            {"name": "bear", "target_price": 75, "cash_distribution": 2, "probability": 0.15},
            {"name": "base", "target_price": 130, "cash_distribution": 2, "probability": 0.55},
            {"name": "bull", "target_price": 175, "cash_distribution": 2, "probability": 0.30},
        ],
        "minimum_required_return": 0.10,
        "benchmark_expected_return": 0.08,
        "active_return_premium": 0.03,
        "independent_stress_total_return": -0.30,
        "evidence": {
            "source_quality": 30,
            "freshness_sync": 20,
            "critical_coverage": 25,
            "cross_validation": 15,
            "assumption_transparency": 10,
        },
        "data_gate_passed": True,
        "positive_rating_veto": False,
        "unmodelable_veto": False,
    }


class DecisionMathTests(unittest.TestCase):
    def test_strong_buy_when_all_gates_pass(self) -> None:
        result = calculate(valid_payload())
        self.assertEqual(result["base_rating"], "强力买入")
        self.assertEqual(result["final_rating"], "强力买入")
        self.assertAlmostEqual(result["probability_sum"], 1.0)

    def test_positive_rating_is_capped_by_veto(self) -> None:
        payload = valid_payload()
        payload["positive_rating_veto"] = True
        result = calculate(payload)
        self.assertEqual(result["final_rating"], "持有/观察")
        self.assertIn("存在正面评级否决项", result["downgrade_reasons"])

    def test_data_gate_failure_returns_not_rated(self) -> None:
        payload = valid_payload()
        payload["data_gate_passed"] = False
        result = calculate(payload)
        self.assertEqual(result["final_rating"], "暂不评级")

    def test_weak_evidence_caps_sell_language(self) -> None:
        payload = valid_payload()
        payload["scenarios"] = [
            {"name": "bear", "target_price": 40, "cash_distribution": 0, "probability": 0.30},
            {"name": "base", "target_price": 70, "cash_distribution": 0, "probability": 0.50},
            {"name": "bull", "target_price": 90, "cash_distribution": 0, "probability": 0.20},
        ]
        payload["evidence"] = {
            "source_quality": 20,
            "freshness_sync": 14,
            "critical_coverage": 18,
            "cross_validation": 5,
            "assumption_transparency": 7,
        }
        result = calculate(payload)
        self.assertEqual(result["base_rating"], "卖出/回避")
        self.assertEqual(result["final_rating"], "减持/回避新增仓位")

    def test_probability_sum_must_equal_one(self) -> None:
        payload = copy.deepcopy(valid_payload())
        payload["scenarios"][0]["probability"] = 0.10
        with self.assertRaises(InputError):
            calculate(payload)

    def test_evidence_values_are_discrete(self) -> None:
        payload = valid_payload()
        payload["evidence"]["source_quality"] = 29
        with self.assertRaises(InputError):
            calculate(payload)

    def test_pcr_nm_caps_positive_rating_to_hold(self) -> None:
        """All scenario TR >= 0 => ED=0, PCR=N/M; positive base rating caps to 持有/观察."""
        payload = valid_payload()
        payload["scenarios"] = [
            {"name": "bear", "target_price": 100, "cash_distribution": 2, "probability": 0.15},
            {"name": "base", "target_price": 130, "cash_distribution": 2, "probability": 0.55},
            {"name": "bull", "target_price": 175, "cash_distribution": 2, "probability": 0.30},
        ]
        result = calculate(payload)
        self.assertIn(result["base_rating"], {"强力买入", "买入"})
        self.assertIsNone(result["payoff_coverage_ratio"])
        self.assertEqual(result["final_rating"], "持有/观察")
        self.assertIn("PCR=N/M，无法验证正面评级覆盖门槛", result["downgrade_reasons"])

    def test_stress_loss_blocks_buy_and_strong_buy(self) -> None:
        # SL <= -35% blocks 强力买入 but still allows 买入 when other buy gates pass.
        strong_payload = valid_payload()
        strong_payload["independent_stress_total_return"] = -0.40
        strong_result = calculate(strong_payload)
        self.assertEqual(strong_result["base_rating"], "强力买入")
        self.assertLessEqual(strong_result["stress_loss"], -0.35)
        self.assertGreater(strong_result["stress_loss"], -0.50)
        self.assertEqual(strong_result["final_rating"], "买入")
        self.assertIn("未同时满足强力买入的 PCR/SL/ECS 门槛", strong_result["downgrade_reasons"])

        # SL <= -50% blocks 买入 entirely.
        buy_payload = valid_payload()
        buy_payload["independent_stress_total_return"] = -0.50
        buy_result = calculate(buy_payload)
        self.assertIn(buy_result["base_rating"], {"强力买入", "买入"})
        self.assertLessEqual(buy_result["stress_loss"], -0.50)
        self.assertEqual(buy_result["final_rating"], "持有/观察")
        self.assertIn("SL<=-50%", buy_result["downgrade_reasons"])

    def test_missing_benchmark_falls_back_to_minimum_required_return(self) -> None:
        payload = valid_payload()
        del payload["benchmark_expected_return"]
        result = calculate(payload)
        self.assertIsNone(result["benchmark_expected_return"])
        self.assertTrue(result["benchmark_fallback_used"])
        self.assertAlmostEqual(result["hurdle_return"], payload["minimum_required_return"])

    def test_strong_buy_downgrades_to_buy_when_strong_gate_fails(self) -> None:
        """ETR qualifies for 强力买入, strong PCR/SL/ECS fails, buy gate passes => 买入."""
        payload = valid_payload()
        # Keep ETR in strong-buy territory; weaken ECS so strong gate fails but buy gate passes.
        payload["evidence"] = {
            "source_quality": 20,
            "freshness_sync": 14,
            "critical_coverage": 18,
            "cross_validation": 10,
            "assumption_transparency": 7,
        }
        result = calculate(payload)
        self.assertEqual(result["base_rating"], "强力买入")
        self.assertGreaterEqual(result["evidence_score"], 60)
        self.assertLess(result["evidence_score"], 75)
        self.assertEqual(result["final_rating"], "买入")
        self.assertIn("未同时满足强力买入的 PCR/SL/ECS 门槛", result["downgrade_reasons"])

    def test_missing_cash_distribution_defaults_to_zero(self) -> None:
        """Documented behavior: omitted cash_distribution is treated as 0 (not an error)."""
        payload = valid_payload()
        for scenario in payload["scenarios"]:
            del scenario["cash_distribution"]
        result = calculate(payload)
        for name in ("bull", "base", "bear"):
            self.assertAlmostEqual(result["scenarios"][name]["cash_distribution"], 0.0)


if __name__ == "__main__":
    unittest.main()
