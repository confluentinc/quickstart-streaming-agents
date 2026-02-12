"""Test SQL extraction from LAB3-Walkthrough.md."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.common.sql_extractors import extract_sql_from_lab_walkthroughs
from testing.e2e.test_lab3_workflow import parse_sql_statements


def test_sql_extraction():
    """Test extracting SQL from LAB3-Walkthrough.md."""
    walkthrough_path = PROJECT_ROOT / "LAB3-Walkthrough.md"

    # Extract SQL
    extracted_markdown = extract_sql_from_lab_walkthroughs(walkthrough_path)
    print(f"✅ Extracted {len(extracted_markdown)} chars of markdown")

    # Parse SQL statements
    sql_statements = parse_sql_statements(extracted_markdown)
    print(f"✅ Parsed {len(sql_statements)} SQL statements")

    # Verify all required statements
    required = ['anomalies_per_zone', 'anomalies_enriched', 'create_tool', 'create_agent', 'completed_actions']
    for stmt in required:
        assert stmt in sql_statements, f"Missing statement: {stmt}"
        print(f"  ✅ {stmt}: {len(sql_statements[stmt])} chars")

    print("✅ All required SQL statements extracted successfully")
