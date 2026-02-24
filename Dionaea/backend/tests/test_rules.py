import unittest
import os
from app.core.rules import RuleEngine

class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        # Create a temporary rule file for testing
        self.test_rule_file = "test_reg.txt"
        with open(self.test_rule_file, "w", encoding="utf-8") as f:
            f.write("SQL Injection\n")
            f.write("(?i)UNION SELECT\n")
            f.write("XSS Attack\n")
            f.write("(?i)<script>\n")
        
        self.engine = RuleEngine(self.test_rule_file)

    def tearDown(self):
        if os.path.exists(self.test_rule_file):
            os.remove(self.test_rule_file)

    def test_load_rules(self):
        self.assertEqual(len(self.engine.rules), 2)
        self.assertIn("SQL Injection", self.engine.rules)
        self.assertIn("XSS Attack", self.engine.rules)

    def test_match_sql_injection(self):
        log = "GET /search?q=1 UNION SELECT * FROM users"
        category = self.engine.match(log)
        self.assertEqual(category, "SQL Injection")

    def test_match_xss(self):
        log = "POST /comment <script>alert(1)</script>"
        category = self.engine.match(log)
        self.assertEqual(category, "XSS Attack")

    def test_no_match(self):
        log = "Normal traffic"
        category = self.engine.match(log)
        self.assertIsNone(category)

if __name__ == "__main__":
    unittest.main()
