import unittest

import scope2_emissions_ledger as app


class Scope2LedgerTests(unittest.TestCase):
    def test_scenario_is_deterministic_and_produces_both_methods(self):
        activity = app.generate_activity()
        self.assertEqual(activity, app.generate_activity())
        lines, report = app.calculate_ledger(activity)
        self.assertEqual(len(lines), 2 * len(activity))
        self.assertIn("location-based", report["totals_kg_co2e"])
        self.assertIn("market-based", report["totals_kg_co2e"])

    def test_simple_activity_calculates_expected_emissions(self):
        row = {
            "period": "test",
            "facility": "one",
            "electricity_kwh": "100",
            "location_factor_kg_co2e_per_kwh": "0.5",
            "market_factor_kg_co2e_per_kwh": "0.2",
            "factor_source": "test_placeholder",
        }
        lines, report = app.calculate_ledger([row])
        amounts = {line["method"]: float(line["emissions_kg_co2e"]) for line in lines}
        self.assertEqual(amounts, {"location-based": 50.0, "market-based": 20.0})
        self.assertEqual(report["market_minus_location_kg_co2e"], -30.0)

    def test_negative_consumption_or_factor_is_rejected(self):
        row = {
            "period": "test",
            "facility": "one",
            "electricity_kwh": "-1",
            "location_factor_kg_co2e_per_kwh": "0.5",
            "market_factor_kg_co2e_per_kwh": "0.2",
            "factor_source": "test_placeholder",
        }
        with self.assertRaises(ValueError):
            app.calculate_ledger([row])


if __name__ == "__main__":
    unittest.main()
