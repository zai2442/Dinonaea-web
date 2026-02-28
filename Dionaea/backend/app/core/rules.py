import re
import logging

logger = logging.getLogger(__name__)

class RuleEngine:
    def __init__(self, rule_file: str):
        self.rule_file = rule_file
        self.rules = {}  # {category: [regex_pattern, ...]}
        self.load_rules()

    def load_rules(self):
        """
        Parses the reg.txt file.
        Format:
        Category Name
        Regex
        Regex
        ...
        """
        try:
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            current_category = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Heuristic to detect category vs regex
                # A regex rule in our system MUST start with (?i) or a backslash \ or a bracket [ or a parenthesis (
                # or contain other common regex operators like *, +, ?, |, ^, $, #, -
                is_regex = line.startswith('(?i)') or any(c in line for c in '()*+?\\|^$[]{}#') or line.startswith('--')
                
                if not is_regex:
                    current_category = line
                    if current_category not in self.rules:
                        self.rules[current_category] = []
                elif current_category:
                    try:
                        # Compile regex for performance
                        self.rules[current_category].append(re.compile(line))
                    except re.error as e:
                        logger.error(f"Invalid regex in {self.rule_file}: {line} - {e}")
                        
            logger.info(f"Loaded {sum(len(r) for r in self.rules.values())} rules across {len(self.rules)} categories.")
            
        except Exception as e:
            logger.error(f"Failed to load rules from {self.rule_file}: {e}")

    def match(self, log_content: str) -> str:
        """
        Matches the log content against loaded rules.
        Returns the first matching category name, or None.
        """
        if not log_content:
            return None
            
        for category, patterns in self.rules.items():
            for pattern in patterns:
                if pattern.search(log_content):
                    return category
        return None
