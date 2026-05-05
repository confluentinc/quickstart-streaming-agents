#!/usr/bin/env python3
"""
One-off script to generate synthetic claims_reviewed data for all 50 US states
and produce to the claims_reviewed Kafka topic.

Generates ~1000-1500 records with Florida as the #1 state (~100 records),
and 10-50 records for each other state roughly proportional to population.

Usage:
    uv run generate_claims_reviewed --dry-run          # Generate CSV only
    uv run generate_claims_reviewed                    # Generate + produce to Kafka
    uv run generate_claims_reviewed --seed 42          # Reproducible generation
"""

import argparse
import csv
import json
import logging
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

try:
    from confluent_kafka import SerializingProducer
    from confluent_kafka.schema_registry import SchemaRegistryClient
    from confluent_kafka.schema_registry.avro import AvroSerializer
    from confluent_kafka.serialization import StringSerializer
    CONFLUENT_KAFKA_AVAILABLE = True
except ImportError:
    CONFLUENT_KAFKA_AVAILABLE = False

from .common.cloud_detection import auto_detect_cloud_provider, validate_cloud_provider, suggest_cloud_provider
from .common.terraform import extract_kafka_credentials, validate_terraform_state, get_project_root
from .common.logging_utils import setup_logging


# ---------------------------------------------------------------------------
# Avro schema for claims_reviewed topic
# ---------------------------------------------------------------------------
CLAIMS_REVIEWED_VALUE_SCHEMA_STR = json.dumps({
    "type": "record",
    "name": "claims_reviewed_value",
    "namespace": "org.apache.flink.avro.generated.record",
    "fields": [
        {"name": "claim_id", "type": "string"},
        {"name": "applicant_name", "type": ["null", "string"], "default": None},
        {"name": "city", "type": "string"},
        {"name": "claim_amount", "type": "string"},
        {"name": "policy_coverage_amount", "type": ["null", "string"], "default": None},
        {"name": "policy_status", "type": ["null", "string"], "default": None},
        {"name": "verdict", "type": ["null", "string"], "default": None},
        {"name": "payment_amount", "type": ["null", "string"], "default": None},
        {"name": "issues_found", "type": ["null", "string"], "default": None},
        {"name": "summary", "type": ["null", "string"], "default": None},
        {"name": "raw_response", "type": ["null", "string"], "default": None},
    ],
})

# ---------------------------------------------------------------------------
# Timestamp range from existing data (epoch millis)
# ---------------------------------------------------------------------------
TIMESTAMP_MIN = 1776302022751
TIMESTAMP_MAX = 1776302238848

# ---------------------------------------------------------------------------
# Name pools
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
    "Frank", "Rachel", "Alexander", "Carolyn", "Patrick", "Janet", "Jack", "Catherine",
    "Dennis", "Maria", "Jerry", "Heather", "Tyler", "Diane",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
    "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
    "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
    "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales",
    "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson",
    "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward",
    "Richardson", "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray",
    "Mendoza", "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel",
    "Myers", "Long", "Ross", "Foster", "Jimenez", "Powell",
]

# ---------------------------------------------------------------------------
# State data: weight (relative population), zip prefix, cities
# ---------------------------------------------------------------------------
STATES = {
    "FL": {"weight": 22, "zip_prefix": "34102", "cities": ["Naples", "Miami", "Orlando", "Tampa", "Jacksonville", "Fort Lauderdale", "St. Petersburg"]},
    "CA": {"weight": 39, "zip_prefix": "90001", "cities": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "San Jose"]},
    "TX": {"weight": 30, "zip_prefix": "75001", "cities": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth"]},
    "NY": {"weight": 19, "zip_prefix": "10001", "cities": ["New York", "Buffalo", "Rochester", "Albany", "Syracuse"]},
    "PA": {"weight": 13, "zip_prefix": "19101", "cities": ["Philadelphia", "Pittsburgh", "Harrisburg", "Allentown", "Erie"]},
    "IL": {"weight": 12, "zip_prefix": "60601", "cities": ["Chicago", "Aurora", "Naperville", "Rockford", "Springfield"]},
    "OH": {"weight": 12, "zip_prefix": "43001", "cities": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron"]},
    "GA": {"weight": 11, "zip_prefix": "30301", "cities": ["Atlanta", "Augusta", "Savannah", "Columbus", "Macon"]},
    "NC": {"weight": 10, "zip_prefix": "27601", "cities": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem"]},
    "MI": {"weight": 10, "zip_prefix": "48201", "cities": ["Detroit", "Grand Rapids", "Ann Arbor", "Lansing", "Flint"]},
    "NJ": {"weight": 9, "zip_prefix": "07001", "cities": ["Newark", "Jersey City", "Trenton", "Paterson", "Elizabeth"]},
    "VA": {"weight": 9, "zip_prefix": "23219", "cities": ["Virginia Beach", "Norfolk", "Richmond", "Arlington", "Chesapeake"]},
    "WA": {"weight": 8, "zip_prefix": "98101", "cities": ["Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue"]},
    "AZ": {"weight": 7, "zip_prefix": "85001", "cities": ["Phoenix", "Tucson", "Mesa", "Scottsdale", "Chandler"]},
    "MA": {"weight": 7, "zip_prefix": "02101", "cities": ["Boston", "Worcester", "Springfield", "Cambridge", "Lowell"]},
    "TN": {"weight": 7, "zip_prefix": "37201", "cities": ["Nashville", "Memphis", "Knoxville", "Chattanooga", "Clarksville"]},
    "IN": {"weight": 7, "zip_prefix": "46201", "cities": ["Indianapolis", "Fort Wayne", "Evansville", "South Bend", "Carmel"]},
    "MO": {"weight": 6, "zip_prefix": "63101", "cities": ["Kansas City", "St. Louis", "Springfield", "Columbia", "Independence"]},
    "MD": {"weight": 6, "zip_prefix": "21201", "cities": ["Baltimore", "Annapolis", "Frederick", "Rockville", "Gaithersburg"]},
    "WI": {"weight": 6, "zip_prefix": "53201", "cities": ["Milwaukee", "Madison", "Green Bay", "Kenosha", "Racine"]},
    "CO": {"weight": 6, "zip_prefix": "80201", "cities": ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Boulder"]},
    "MN": {"weight": 6, "zip_prefix": "55101", "cities": ["Minneapolis", "St. Paul", "Rochester", "Duluth", "Bloomington"]},
    "SC": {"weight": 5, "zip_prefix": "29201", "cities": ["Columbia", "Charleston", "Greenville", "Myrtle Beach", "Rock Hill"]},
    "AL": {"weight": 5, "zip_prefix": "35201", "cities": ["Birmingham", "Montgomery", "Huntsville", "Mobile", "Tuscaloosa"]},
    "LA": {"weight": 5, "zip_prefix": "70112", "cities": ["New Orleans", "Baton Rouge", "Shreveport", "Lafayette", "Lake Charles"]},
    "KY": {"weight": 4, "zip_prefix": "40201", "cities": ["Louisville", "Lexington", "Bowling Green", "Owensboro", "Covington"]},
    "OR": {"weight": 4, "zip_prefix": "97201", "cities": ["Portland", "Salem", "Eugene", "Bend", "Medford"]},
    "OK": {"weight": 4, "zip_prefix": "73101", "cities": ["Oklahoma City", "Tulsa", "Norman", "Broken Arrow", "Edmond"]},
    "CT": {"weight": 4, "zip_prefix": "06101", "cities": ["Hartford", "New Haven", "Stamford", "Bridgeport", "Waterbury"]},
    "UT": {"weight": 3, "zip_prefix": "84101", "cities": ["Salt Lake City", "Provo", "Ogden", "St. George", "Orem"]},
    "IA": {"weight": 3, "zip_prefix": "50301", "cities": ["Des Moines", "Cedar Rapids", "Davenport", "Sioux City", "Iowa City"]},
    "NV": {"weight": 3, "zip_prefix": "89101", "cities": ["Las Vegas", "Reno", "Henderson", "North Las Vegas", "Sparks"]},
    "AR": {"weight": 3, "zip_prefix": "72201", "cities": ["Little Rock", "Fort Smith", "Fayetteville", "Springdale", "Jonesboro"]},
    "MS": {"weight": 3, "zip_prefix": "39201", "cities": ["Jackson", "Gulfport", "Hattiesburg", "Biloxi", "Meridian"]},
    "KS": {"weight": 3, "zip_prefix": "66101", "cities": ["Wichita", "Overland Park", "Kansas City", "Topeka", "Olathe"]},
    "NM": {"weight": 2, "zip_prefix": "87101", "cities": ["Albuquerque", "Santa Fe", "Las Cruces", "Rio Rancho", "Roswell"]},
    "NE": {"weight": 2, "zip_prefix": "68101", "cities": ["Omaha", "Lincoln", "Bellevue", "Grand Island", "Kearney"]},
    "ID": {"weight": 2, "zip_prefix": "83701", "cities": ["Boise", "Meridian", "Nampa", "Idaho Falls", "Pocatello"]},
    "WV": {"weight": 2, "zip_prefix": "25301", "cities": ["Charleston", "Huntington", "Morgantown", "Parkersburg", "Wheeling"]},
    "HI": {"weight": 1, "zip_prefix": "96801", "cities": ["Honolulu", "Hilo", "Kailua", "Pearl City", "Kapolei"]},
    "NH": {"weight": 1, "zip_prefix": "03301", "cities": ["Manchester", "Nashua", "Concord", "Dover", "Rochester"]},
    "ME": {"weight": 1, "zip_prefix": "04101", "cities": ["Portland", "Lewiston", "Bangor", "Auburn", "Augusta"]},
    "MT": {"weight": 1, "zip_prefix": "59601", "cities": ["Billings", "Missoula", "Great Falls", "Bozeman", "Helena"]},
    "RI": {"weight": 1, "zip_prefix": "02901", "cities": ["Providence", "Warwick", "Cranston", "Pawtucket", "Newport"]},
    "DE": {"weight": 1, "zip_prefix": "19901", "cities": ["Wilmington", "Dover", "Newark", "Middletown", "Smyrna"]},
    "SD": {"weight": 1, "zip_prefix": "57101", "cities": ["Sioux Falls", "Rapid City", "Aberdeen", "Brookings", "Watertown"]},
    "ND": {"weight": 1, "zip_prefix": "58101", "cities": ["Fargo", "Bismarck", "Grand Forks", "Minot", "West Fargo"]},
    "AK": {"weight": 1, "zip_prefix": "99501", "cities": ["Anchorage", "Fairbanks", "Juneau", "Sitka", "Ketchikan"]},
    "VT": {"weight": 1, "zip_prefix": "05401", "cities": ["Burlington", "Montpelier", "Rutland", "Barre", "Brattleboro"]},
    "WY": {"weight": 1, "zip_prefix": "82001", "cities": ["Cheyenne", "Casper", "Laramie", "Gillette", "Rock Springs"]},
}

# ---------------------------------------------------------------------------
# Policy coverage tiers
# ---------------------------------------------------------------------------
POLICY_COVERAGE_OPTIONS = [
    75000, 90000, 100000, 125000, 150000, 175000, 200000,
    250000, 300000, 350000, 400000, 500000,
]

# ---------------------------------------------------------------------------
# Denial reason templates
# ---------------------------------------------------------------------------
DENY_TEMPLATES = [
    {
        "rule": "RULE 1 — COVERAGE FRAUD",
        "issues": (
            "- RULE 1 — COVERAGE FRAUD: Policy was purchased on {purchase_date}, "
            "only {days_before} days before the disaster on 2026-02-11. "
            "Policy was acquired suspiciously close to the disaster date, "
            "indicating potential pre-knowledge or opportunistic fraud.\n"
        ),
        "summary": (
            "Claim denied. The policy was purchased only {days_before} days before "
            "the disaster, which is below the 30-day minimum threshold. This suggests "
            "the policy may have been acquired with foreknowledge of the impending disaster."
        ),
    },
    {
        "rule": "RULE 2 — PRE-EXISTING DAMAGE",
        "issues": (
            '- RULE 2 — PRE-EXISTING DAMAGE: CLUE history shows "{clue_date}: '
            "{damage_type} damage. Claim filed with {insurer}. "
            "Property: {address}, {city} {state_abbr}. "
            'Amount requested: ${clue_amount:,}. Amount paid: ${clue_paid:,}. '
            'Repair recorded: no." Current claim includes {current_damage}. '
            "Prior unrepaired damage matches current claim damage type.\n"
        ),
        "summary": (
            "Claim denied. CLUE records show previous {damage_type} damage that was "
            "not repaired, yet the current claim requests {current_damage} due to "
            "hurricane damage. This indicates potential fraud through claiming "
            "pre-existing damage as new hurricane damage."
        ),
    },
    {
        "rule": "RULE 3 — SANCTIONED COUNTRY / UNVERIFIABLE BANK",
        "issues": (
            '- RULE 3 — SANCTIONED COUNTRY / UNVERIFIABLE BANK: ip_country = "{country}" '
            'and bank_account_country = "Unverifiable". Claim originates from sanctioned '
            "country with unverifiable banking information.\n"
        ),
        "summary": (
            "Claim denied. The claim was filed from {country}, a sanctioned country, "
            "and the bank account country is unverifiable, indicating potential fraud "
            "or sanctions violations."
        ),
    },
    {
        "rule": "RULE 4 — IDENTITY FAILURE",
        "issues": (
            "- RULE 4 — IDENTITY FAILURE: identity_verified = false and "
            "ssn_matches_policyholder = false. Additionally, identity_theft_history "
            "= true, indicating compromised identity records.\n"
        ),
        "summary": (
            "Claim denied. The applicant failed identity verification checks. "
            "SSN does not match the policyholder, identity could not be verified, "
            "and there is a history of identity theft associated with this policy."
        ),
    },
    {
        "rule": "RULE 5 — INACTIVE POLICY",
        "issues": (
            '- Policy status is "expired" — not active. Policy lapsed {lapse_date} '
            "when renewal payment was not received, and coverage was terminated.\n"
        ),
        "summary": (
            "Claim denied. The policy is expired and coverage was terminated on "
            "{lapse_date} due to non-payment of renewal premium. No coverage "
            "exists for this claim under an inactive policy."
        ),
    },
    {
        "rule": "DUPLICATE CLAIMS",
        "issues": (
            "- CLUE history shows {dup_count} separate claims filed for the same "
            "property ({address}, {city} {state_abbr}) on nearly identical dates "
            "by {dup_count} different policyholders. Each claim requests exactly "
            "${claim_amount:,} for hurricane wind/flood damage at the same address. "
            "This pattern indicates coordinated insurance fraud with multiple "
            "parties filing duplicate claims on the same property.\n"
        ),
        "summary": (
            "Claim denied. Investigation reveals {dup_count} separate insurance "
            "claims filed by different individuals for the identical property "
            "and damage amount within 24 hours, indicating a coordinated fraud scheme."
        ),
    },
]

# ---------------------------------------------------------------------------
# Approval summary templates
# ---------------------------------------------------------------------------
APPROVE_SUMMARIES = [
    (
        "All fraud detection rules passed. Policy purchased {purchase_date}, "
        "disaster occurred 2026-02-11 (active for {years_active} years). "
        "No prior claims, identity verified, SSN matches, US-based IP and "
        "bank account, policy status active. Claim approved for {reason}."
    ),
    (
        "All fraud detection rules pass. Policy has been active since "
        "{purchase_date}, well before the 2026-02-11 disaster date. No prior "
        "claims, identity verified, policy active, and all geographic/identity "
        "checks clear. Claim approved for {reason}."
    ),
    (
        "All fraud detection rules passed. Policy has been active since "
        "{year}, no prior claims, identity verified, and all verification "
        "checks cleared. Claim approved for {reason}."
    ),
    (
        "All fraud detection rules pass. Policy purchased {purchase_date}, "
        "well over 30 days before disaster. No prior claims. Identity verified, "
        "SSN matches, US-based IP and bank account. Policy status is active. "
        "Claim approved for {reason}."
    ),
    (
        "All fraud detection rules passed. Policy has been active since "
        "{purchase_date}, no prior claims, identity verified, US-based, "
        "policy active. Claim approved for {reason}."
    ),
    (
        "Claim approved. All fraud detection rules passed. {name}'s policy "
        "is active, identity verified, no coverage fraud or pre-existing "
        "damage indicators. {reason}."
    ),
    (
        "All fraud detection rules pass. Policy was purchased {purchase_date}, "
        "disaster occurred 2026-02-11 (over {years_active} years active). "
        "No pre-existing unrepaired damage. Identity verified, SSN matches, "
        "US-based IP and bank account. Policy status is active. Claim approved "
        "for {reason}."
    ),
]

# ---------------------------------------------------------------------------
# Helper data for denial template filling
# ---------------------------------------------------------------------------
SANCTIONED_COUNTRIES = ["North Korea", "Iran", "Syria", "Russia", "Cuba"]
DAMAGE_TYPES = ["Hail storm roof", "Water pipe burst", "Foundation crack", "Wind storm siding", "Flood basement"]
CURRENT_DAMAGE_TYPES = ["roof replacement", "structural repair", "foundation work", "siding replacement", "water damage restoration"]
INSURERS = ["StateFarm", "Allstate", "GEICO", "Progressive", "Liberty Mutual", "Nationwide", "USAA"]
STREET_NAMES = [
    "Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine St", "Elm St",
    "Washington Blvd", "Park Ave", "Lake Dr", "River Rd", "Sunset Blvd",
    "Highland Ave", "Forest Dr", "Meadow Ln", "Valley Rd", "Spring St",
    "Beach Rd", "Gulf Shore Blvd", "Ocean Ave", "Harbor Dr",
]


# ===================================================================
# Data generation functions
# ===================================================================

def format_currency(amount: int) -> str:
    """Format integer as '$XX,XXX'."""
    return f"${amount:,}"


def generate_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def generate_claim_id(zip_prefix: str, used_ids: Set[str]) -> str:
    """Generate a unique claim ID in format XXXXX-NNNNN."""
    for _ in range(1000):
        num = random.randint(0, 99999)
        claim_id = f"{zip_prefix}-{num:05d}"
        if claim_id not in used_ids:
            used_ids.add(claim_id)
            return claim_id
    raise RuntimeError(f"Could not generate unique claim_id for zip {zip_prefix}")


def generate_claim_amount() -> int:
    """Gaussian distribution centered ~$100k, range $25k-$300k."""
    amount = int(random.gauss(100000, 50000))
    amount = max(25000, min(300000, amount))
    # Round to nearest $1000
    return round(amount / 1000) * 1000


def pick_policy_coverage(claim_amount: int) -> int:
    """Pick a coverage amount that is >= claim_amount."""
    valid = [c for c in POLICY_COVERAGE_OPTIONS if c >= claim_amount]
    if not valid:
        return POLICY_COVERAGE_OPTIONS[-1]
    return random.choice(valid)


def random_purchase_date(years_back_min: int = 1, years_back_max: int = 12) -> Tuple[str, int]:
    """Return (date_string, years_active) for a policy purchase date."""
    years = random.randint(years_back_min, years_back_max)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    year = 2026 - years
    date_str = f"{year}-{month:02d}-{day:02d}"
    return date_str, years


def random_recent_purchase_date(days_before: int) -> str:
    """Return a date string for a policy purchased N days before disaster."""
    from datetime import timedelta
    disaster = datetime(2026, 2, 11)
    purchase = disaster - timedelta(days=days_before)
    return purchase.strftime("%Y-%m-%d")


def random_lapse_date() -> str:
    """Return a plausible policy lapse date."""
    year = random.choice([2024, 2025])
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def random_clue_date() -> str:
    """Return a plausible CLUE history date."""
    year = random.choice([2023, 2024, 2025])
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def random_address(city: str) -> str:
    """Generate a plausible street address."""
    num = random.randint(100, 9999)
    street = random.choice(STREET_NAMES)
    return f"{num} {street}, {city}"


def build_raw_response(record: Dict[str, Any]) -> str:
    """Assemble the 6-section plain-text format matching Flink REGEX_EXTRACT patterns."""
    return (
        f"Policy Coverage Amount: {record['policy_coverage_amount']}\n\n"
        f"Policy Status: {record['policy_status']}\n\n"
        f"Verdict: {record['verdict']}\n\n"
        f"Payment Amount: {record['payment_amount']}\n\n"
        f"Issues Found:\n{record['issues_found']}\n"
        f"Summary:\n{record['summary']}"
    )


def generate_approve_record(
    claim_id: str, name: str, city: str, state_abbr: str, claim_amount: int,
) -> Dict[str, Any]:
    """Generate a full APPROVE record."""
    coverage = pick_policy_coverage(claim_amount)
    purchase_date, years_active = random_purchase_date()

    # ~50% apply deductible
    if random.random() < 0.5:
        deductible = random.choice([1000, 1500, 2000, 2500, 3000, 5000])
        payment = claim_amount - deductible
        reason = (
            f"the full assessed damage amount of {format_currency(claim_amount)} "
            f"minus {format_currency(deductible)} deductible equals "
            f"{format_currency(payment)} payment"
        )
    else:
        payment = claim_amount
        reason = f"the full assessed damage amount of {format_currency(claim_amount)}"

    year = purchase_date.split("-")[0]

    summary_template = random.choice(APPROVE_SUMMARIES)
    summary = summary_template.format(
        purchase_date=purchase_date,
        years_active=years_active,
        year=year,
        name=name,
        reason=reason,
    )

    issues = "None — all checks pass.\n"

    raw_response = build_raw_response({
        "policy_coverage_amount": format_currency(coverage),
        "policy_status": "active",
        "verdict": "APPROVE",
        "payment_amount": format_currency(payment),
        "issues_found": issues,
        "summary": summary,
    })

    record = {
        "claim_id": claim_id,
        "applicant_name": name,
        "city": city,
        "claim_amount": str(claim_amount),
        "policy_coverage_amount": format_currency(coverage),
        "policy_status": "active",
        "verdict": "APPROVE",
        "payment_amount": format_currency(payment),
        "issues_found": issues,
        "summary": summary,
        "raw_response": raw_response,
    }
    return record


def generate_deny_record(
    claim_id: str, name: str, city: str, state_abbr: str, claim_amount: int,
) -> Dict[str, Any]:
    """Generate a full DENY record."""
    coverage = pick_policy_coverage(claim_amount)
    template = random.choice(DENY_TEMPLATES)

    # Fill template-specific placeholders
    address = random_address(city)
    damage_idx = random.randint(0, len(DAMAGE_TYPES) - 1)

    fill = {
        "city": city,
        "state_abbr": state_abbr,
        "address": address,
        "claim_amount": claim_amount,
        "name": name,
    }

    rule = template["rule"]
    if "COVERAGE FRAUD" in rule:
        days = random.randint(3, 25)
        fill["days_before"] = days
        fill["purchase_date"] = random_recent_purchase_date(days)
        policy_status = "active"
    elif "PRE-EXISTING" in rule:
        fill["clue_date"] = random_clue_date()
        fill["damage_type"] = DAMAGE_TYPES[damage_idx].lower()
        fill["current_damage"] = CURRENT_DAMAGE_TYPES[damage_idx]
        fill["insurer"] = random.choice(INSURERS)
        fill["clue_amount"] = random.randint(8000, 35000)
        fill["clue_paid"] = fill["clue_amount"] - random.randint(1000, 3000)
        policy_status = "active"
    elif "SANCTIONED" in rule:
        fill["country"] = random.choice(SANCTIONED_COUNTRIES)
        policy_status = "active"
    elif "IDENTITY" in rule:
        policy_status = "active"
    elif "INACTIVE" in rule:
        fill["lapse_date"] = random_lapse_date()
        policy_status = "expired"
    elif "DUPLICATE" in rule:
        fill["dup_count"] = random.choice([2, 3, 4])
        policy_status = "active"
    else:
        policy_status = "active"

    issues = template["issues"].format(**fill)
    summary = template["summary"].format(**fill)

    raw_response = build_raw_response({
        "policy_coverage_amount": format_currency(coverage),
        "policy_status": policy_status,
        "verdict": "DENY",
        "payment_amount": "$0",
        "issues_found": issues,
        "summary": summary,
    })

    record = {
        "claim_id": claim_id,
        "applicant_name": name,
        "city": city,
        "claim_amount": str(claim_amount),
        "policy_coverage_amount": format_currency(coverage),
        "policy_status": policy_status,
        "verdict": "DENY",
        "payment_amount": "$0",
        "issues_found": issues,
        "summary": summary,
        "raw_response": raw_response,
    }
    return record


def calculate_state_counts() -> Dict[str, int]:
    """
    Calculate number of records per state.

    FL gets 85 new records (existing 15 bring total to ~100).
    Others get 10-50 proportional to weight.
    """
    counts = {}
    non_fl_states = {k: v for k, v in STATES.items() if k != "FL"}

    # Florida: 85 new records
    counts["FL"] = 85

    # Other states: proportional to weight, clamped to [10, 50]
    total_weight = sum(s["weight"] for s in non_fl_states.values())
    for state_abbr, state_data in non_fl_states.items():
        raw = (state_data["weight"] / total_weight) * 49 * 25  # target ~25 avg per state
        count = max(10, min(50, int(round(raw))))
        counts[state_abbr] = count

    return counts


def generate_all_records() -> List[Tuple[int, Dict[str, Any]]]:
    """Generate all records with timestamps. Returns list of (timestamp_ms, record)."""
    logger = logging.getLogger(__name__)
    counts = calculate_state_counts()
    used_ids: Set[str] = set()
    records = []

    total = sum(counts.values())
    logger.info(f"Generating {total} records across {len(counts)} states")

    for state_abbr, count in sorted(counts.items()):
        state_data = STATES[state_abbr]
        for _ in range(count):
            name = generate_name()
            city = random.choice(state_data["cities"])
            claim_id = generate_claim_id(state_data["zip_prefix"], used_ids)
            claim_amount = generate_claim_amount()

            # ~65% approve, ~35% deny
            if random.random() < 0.65:
                record = generate_approve_record(claim_id, name, city, state_abbr, claim_amount)
            else:
                record = generate_deny_record(claim_id, name, city, state_abbr, claim_amount)

            # Random timestamp within existing range
            ts = random.randint(TIMESTAMP_MIN, TIMESTAMP_MAX)
            records.append((ts, record))

    # Sort by timestamp
    records.sort(key=lambda x: x[0])

    # Log state breakdown
    state_summary = {s: counts[s] for s in sorted(counts.keys())}
    logger.info(f"State breakdown: {json.dumps(state_summary, indent=2)}")

    approve_count = sum(1 for _, r in records if r.get("verdict") == "APPROVE")
    deny_count = total - approve_count
    logger.info(f"Verdict split: {approve_count} APPROVE ({100*approve_count/total:.0f}%), "
                f"{deny_count} DENY ({100*deny_count/total:.0f}%)")

    return records


def save_to_csv(records: List[Tuple[int, Dict[str, Any]]], output_path: Path) -> None:
    """Save generated records to CSV."""
    logger = logging.getLogger(__name__)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "timestamp", "claim_id", "applicant_name", "city", "claim_amount",
        "policy_coverage_amount", "policy_status", "verdict",
        "payment_amount", "issues_found", "summary", "raw_response",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for ts, record in records:
            row = {"timestamp": ts}
            for field in fieldnames:
                if field == "timestamp":
                    continue
                val = record.get(field)
                row[field] = val if val is not None else ""
            writer.writerow(row)

    logger.info(f"Saved {len(records)} records to {output_path}")


# ===================================================================
# Kafka publisher
# ===================================================================

class ClaimsReviewedPublisher:
    """Publisher for claims_reviewed records."""

    def __init__(
        self,
        bootstrap_servers: str,
        kafka_api_key: str,
        kafka_api_secret: str,
        schema_registry_url: str,
        schema_registry_api_key: str,
        schema_registry_api_secret: str,
        dry_run: bool = False,
    ):
        self.dry_run = dry_run
        self.logger = logging.getLogger(__name__)

        self.string_serializer = StringSerializer("utf_8")
        self.producer = None

        if not dry_run:
            sr_client = SchemaRegistryClient({
                "url": schema_registry_url,
                "basic.auth.user.info": f"{schema_registry_api_key}:{schema_registry_api_secret}",
            })

            avro_serializer = AvroSerializer(
                sr_client,
                CLAIMS_REVIEWED_VALUE_SCHEMA_STR,
            )

            self.producer = SerializingProducer({
                "bootstrap.servers": bootstrap_servers,
                "sasl.mechanisms": "PLAIN",
                "security.protocol": "SASL_SSL",
                "sasl.username": kafka_api_key,
                "sasl.password": kafka_api_secret,
                "key.serializer": self.string_serializer,
                "value.serializer": avro_serializer,
                "linger.ms": 10,
                "batch.size": 16384,
                "compression.type": "snappy",
            })

    def delivery_callback(self, err, msg):
        if err:
            self.logger.error(f"Message delivery failed: {err}")
        else:
            self.logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    def publish(
        self,
        records: List[Tuple[int, Dict[str, Any]]],
        topic: str,
    ) -> Dict[str, int]:
        """Publish records to Kafka. Each record is (timestamp_ms, record_dict)."""
        results = {"success": 0, "failed": 0, "total": len(records)}
        self.logger.info(f"Publishing {len(records)} records to '{topic}'")

        for idx, (ts, record) in enumerate(records, 1):
            try:
                claim_id = record["claim_id"]
                if self.dry_run:
                    self.logger.debug(f"[DRY RUN] Would publish {claim_id}")
                    results["success"] += 1
                    continue

                self.producer.produce(
                    topic=topic,
                    key=claim_id,
                    value=record,
                    timestamp=ts,
                    on_delivery=self.delivery_callback,
                )
                results["success"] += 1

            except Exception as e:
                self.logger.error(f"Failed to publish {record.get('claim_id', '?')}: {e}")
                results["failed"] += 1

            if not self.dry_run and idx % 100 == 0:
                self.producer.poll(0)

            if not self.dry_run and idx % 500 == 0:
                self.producer.flush()
                self.logger.info(
                    f"Progress: {idx}/{results['total']} "
                    f"({results['success']} ok, {results['failed']} failed)"
                )

        if not self.dry_run and self.producer:
            self.logger.info("Flushing remaining messages...")
            self.producer.flush()

        return results

    def close(self):
        if self.producer:
            self.producer.flush()


# ===================================================================
# Main
# ===================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic claims_reviewed data for all 50 US states and produce to Kafka",
    )
    parser.add_argument("--cloud-provider", choices=["aws", "azure"], help="Cloud provider (auto-detected if not specified)")
    parser.add_argument("--topic", default="claims_reviewed", help="Kafka topic (default: claims_reviewed)")
    parser.add_argument("--output-csv", type=Path, help="CSV output path (default: assets/lab5/data/claims_reviewed_synthetic.csv)")
    parser.add_argument("--dry-run", action="store_true", help="Generate CSV only, don't produce to Kafka")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--seed", type=int, help="Random seed for reproducible generation")
    args = parser.parse_args()

    logger = setup_logging(args.verbose)

    if not args.dry_run and not CONFLUENT_KAFKA_AVAILABLE:
        logger.error("confluent-kafka not available. Install with: uv pip install confluent-kafka")
        return 1

    if args.seed is not None:
        random.seed(args.seed)
        logger.info(f"Random seed: {args.seed}")

    try:
        project_root = get_project_root()
    except Exception as e:
        logger.error(f"Could not find project root: {e}")
        return 1

    # Generate data
    logger.info("Generating synthetic claims_reviewed data...")
    records = generate_all_records()

    # Save CSV
    output_csv = args.output_csv or (project_root / "assets" / "lab5" / "data" / "claims_reviewed_synthetic.csv")
    save_to_csv(records, output_csv)

    if args.dry_run:
        print(f"\n[DRY RUN] Generated {len(records)} records -> {output_csv}")
        print("[DRY RUN] No messages produced to Kafka.")
        return 0

    # Cloud detection
    cloud_provider = args.cloud_provider
    if not cloud_provider:
        cloud_provider = auto_detect_cloud_provider()
        if not cloud_provider:
            suggestion = suggest_cloud_provider(project_root)
            if suggestion:
                logger.info(f"Auto-detected cloud provider: {suggestion}")
                cloud_provider = suggestion
            else:
                logger.error("Could not auto-detect cloud provider.")
                return 1

    logger.info(f"Target cloud provider: {cloud_provider.upper()}")

    if not validate_cloud_provider(cloud_provider):
        logger.error(f"Invalid cloud provider: {cloud_provider}")
        return 1

    try:
        if not validate_terraform_state(cloud_provider, project_root):
            logger.error("Terraform validation failed")
            return 1
    except Exception as e:
        logger.error(f"Terraform validation failed: {e}")
        return 1

    try:
        credentials = extract_kafka_credentials(cloud_provider, project_root)
    except Exception as e:
        logger.error(f"Failed to extract Kafka credentials: {e}")
        return 1

    try:
        publisher = ClaimsReviewedPublisher(
            bootstrap_servers=credentials["bootstrap_servers"],
            kafka_api_key=credentials["kafka_api_key"],
            kafka_api_secret=credentials["kafka_api_secret"],
            schema_registry_url=credentials["schema_registry_url"],
            schema_registry_api_key=credentials["schema_registry_api_key"],
            schema_registry_api_secret=credentials["schema_registry_api_secret"],
            dry_run=args.dry_run,
        )
    except Exception as e:
        logger.error(f"Failed to initialize publisher: {e}")
        return 1

    try:
        results = publisher.publish(records, args.topic)

        print(f"\n{'=' * 60}")
        print("CLAIMS_REVIEWED DATA GENERATION SUMMARY")
        print(f"{'=' * 60}")
        print(f"Records generated: {len(records)}")
        print(f"CSV saved to:      {output_csv}")
        print(f"Published:         {results['success']}/{results['total']}")
        print(f"Failed:            {results['failed']}")
        print(f"{'=' * 60}")

        env_name = credentials.get("environment_name")
        if env_name:
            print(f"\nPublished to environment: {env_name}")
        print(f"{results['success']} records -> '{args.topic}'")

        return 0 if results["failed"] == 0 else 1
    finally:
        publisher.close()


if __name__ == "__main__":
    sys.exit(main())
