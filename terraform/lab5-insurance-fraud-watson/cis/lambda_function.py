import json

# Claims Investigation Service (CIS) — static data for all 17 claims
# from the Naples FL hurricane surge window (2026-02-11).
# Keyed by claim_id. Each record contains 4 sections:
#   claim        — submission details and narrative
#   policy       — policy owner, coverage, status, history
#   clue_history — cross-insurer claims history (CLUE)
#   identity_verification — IP/bank origin, identity and SSN checks

CLAIMS = {

    # ── APPROVE claims ──────────────────────────────────────────────────────────

    "34102-03672": {
        "claim": {
            "claim_id": "34102-03672",
            "applicant_name": "Robert Martinez",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 95000,
            "claim_amount": 95000,
            "deductible": 2500,
            "assessment_date": "2026-02-17",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (3rd party)",
            "narrative": (
                "Hurricane flooded my finished basement destroying my home theater system, "
                "pool table, and stored furniture worth $45,000. Also roof damage to main house "
                "assessed at $50,000. Total damage $95,000. My deductible is $2,500."
            )
        },
        "policy": {
            "policy_owner_name": "Robert Martinez",
            "coverage_amount": 200000,
            "status": "active",
            "history": "Purchased 2019-03-15. Renewed 2024-03-15. No changes to coverage limits."
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    "34102-03684": {
        "claim": {
            "claim_id": "34102-03684",
            "applicant_name": "Linda Chen",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 75000,
            "claim_amount": 75000,
            "deductible": 2000,
            "assessment_date": "2026-02-15",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (in-house)",
            "narrative": (
                "Severe flooding filled our crawl space, destroying HVAC equipment, water heater, "
                "and stored seasonal items totaling $35,000. First floor also has water damage of "
                "$40,000. Total damage $75,000. Our deductible is $2,000."
            )
        },
        "policy": {
            "policy_owner_name": "Linda Chen",
            "coverage_amount": 175000,
            "status": "active",
            "history": (
                "Purchased 2017-08-01. Renewed 2023-08-01. "
                "Coverage increased from $150,000 to $175,000 on 2023-08-01."
            )
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    "34102-04032": {
        "claim": {
            "claim_id": "34102-04032",
            "applicant_name": "Frank Rivera",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 265000,
            "claim_amount": 265000,
            "deductible": 5000,
            "assessment_date": "2026-02-13",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (in-house)",
            "narrative": (
                "Hurricane destroyed my 4,000 sq ft waterfront home. Insurance adjuster assessed "
                "$265,000 in total damage including structural ($145,000), interior ($80,000), "
                "and mechanical systems ($40,000). My deductible is $5,000."
            )
        },
        "policy": {
            "policy_owner_name": "Frank Rivera",
            "coverage_amount": 350000,
            "status": "active",
            "history": (
                "Purchased 2015-06-20. Renewed 2024-06-20. "
                "Coverage increased from $300,000 to $350,000 on 2020-06-20."
            )
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    "34102-04044": {
        "claim": {
            "claim_id": "34102-04044",
            "applicant_name": "Ruth Campbell",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 210000,
            "claim_amount": 210000,
            "deductible": 5000,
            "assessment_date": "2026-02-18",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (3rd party)",
            "narrative": (
                "Home is total loss per insurance adjuster. Structural damage $120,000, interior "
                "destruction $55,000, all mechanical and electrical systems $35,000. Total assessed "
                "damage $210,000. Deductible is $5,000. Currently living in temporary shelter."
            )
        },
        "policy": {
            "policy_owner_name": "Ruth Campbell",
            "coverage_amount": 300000,
            "status": "active",
            "history": "Purchased 2012-09-10. Renewed 2024-09-10. No changes to coverage limits."
        },
        "clue_history": (
            "2018-10-15: Hurricane Michael wind damage. Claim filed with AllState. "
            "Property: 445 Tamiami Trail, Naples FL. Amount requested: $32,000. "
            "Amount paid: $28,500. Repair recorded: yes."
        ),
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    "34102-04116": {
        "claim": {
            "claim_id": "34102-04116",
            "applicant_name": "Alice Evans",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 43000,
            "claim_amount": 43000,
            "deductible": 1500,
            "assessment_date": "2026-02-13",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (3rd party)",
            "narrative": (
                "Hurricane Helene's 120 mph winds removed 60% of my roof on the day the storm made "
                "landfall. Insurance adjuster confirmed $43,000 in structural damage two days later. "
                "My deductible is $1,500."
            )
        },
        "policy": {
            "policy_owner_name": "Alice Evans",
            "coverage_amount": 100000,
            "status": "active",
            "history": "Purchased 2020-01-05. Renewed 2025-01-05. No changes to coverage limits."
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    "34102-04140": {
        "claim": {
            "claim_id": "34102-04140",
            "applicant_name": "Harold Stewart",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 28000,
            "claim_amount": 28000,
            "deductible": 1000,
            "assessment_date": "2026-02-16",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (in-house)",
            "narrative": (
                "Hurricane caused severe wind damage to roof, broken windows, and water infiltration "
                "throughout the house. Adjuster assessed total damage at $28,000. My deductible is $1,000."
            )
        },
        "policy": {
            "policy_owner_name": "Harold Stewart",
            "coverage_amount": 75000,
            "status": "active",
            "history": "Purchased 2021-11-12. Renewed 2024-11-12. No changes to coverage limits."
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    "34102-04188": {
        "claim": {
            "claim_id": "34102-04188",
            "applicant_name": "Eugene Bailey",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 45000,
            "claim_amount": 45000,
            "deductible": 2000,
            "assessment_date": "2026-02-15",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (3rd party)",
            "narrative": (
                "Hurricane caused catastrophic damage: roof failure ($22,000), window breakage ($8,000), "
                "interior flooding damage ($15,000). Total assessed at $45,000. Deductible is $2,000."
            )
        },
        "policy": {
            "policy_owner_name": "Eugene Bailey",
            "coverage_amount": 120000,
            "status": "active",
            "history": "Purchased 2018-04-22. Renewed 2024-04-22. No changes to coverage limits."
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    "34102-04212": {
        "claim": {
            "claim_id": "34102-04212",
            "applicant_name": "Victor Diaz",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 39000,
            "claim_amount": 39000,
            "deductible": 1500,
            "assessment_date": "2026-02-18",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (in-house)",
            "narrative": (
                "Severe hurricane damage including roof damage ($18,000), siding replacement ($8,000), "
                "interior water damage ($13,000). Total damage assessed at $39,000. My deductible is $1,500."
            )
        },
        "policy": {
            "policy_owner_name": "Victor Diaz",
            "coverage_amount": 100000,
            "status": "active",
            "history": "Purchased 2019-07-30. Renewed 2025-07-30. No changes to coverage limits."
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    "34102-04224": {
        "claim": {
            "claim_id": "34102-04224",
            "applicant_name": "Tina Howard",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 35000,
            "claim_amount": 35000,
            "deductible": 1500,
            "assessment_date": "2026-02-16",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (3rd party)",
            "narrative": (
                "Hurricane Helene damaged my home requiring roof repair ($15,000), interior water damage "
                "restoration ($12,000), window replacement ($8,000). Total assessed damage $35,000. "
                "Deductible is $1,500."
            )
        },
        "policy": {
            "policy_owner_name": "Tina Howard",
            "coverage_amount": 90000,
            "status": "active",
            "history": "Purchased 2022-02-14. Renewed 2025-02-14. No changes to coverage limits."
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    # ── REQUEST_MORE_INFO claims ─────────────────────────────────────────────────

    "34102-03792": {
        "claim": {
            "claim_id": "34102-03792",
            "applicant_name": "Charles Brown",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 140000,
            "claim_amount": 140000,
            "deductible": 3000,
            "assessment_date": "2026-02-18",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (3rd party)",
            "narrative": (
                "Received $75,000 SBA disaster loan for initial emergency repairs but total contractor "
                "estimates came to $140,000. Structural engineer confirmed additional foundation and framing "
                "damage not covered by the initial loan. Filing insurance claim for full $140,000 in "
                "assessed damage. Deductible is $3,000."
            )
        },
        "policy": {
            "policy_owner_name": "Charles Brown",
            "coverage_amount": 200000,
            "status": "active",
            "history": "Purchased 2016-05-18. Renewed 2024-05-18. No changes to coverage limits."
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    "34102-03996": {
        "claim": {
            "claim_id": "34102-03996",
            "applicant_name": "Paul Thompson",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 102000,
            "claim_amount": 102000,
            "deductible": 2500,
            "assessment_date": "2026-02-19",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (3rd party)",
            "narrative": (
                "Complete property restoration needed after hurricane: house structural repairs $65,000, "
                "property perimeter restoration including retaining wall and drainage system $22,000, "
                "utility connections and meters $15,000. Total assessed damage $102,000. Deductible is $2,500."
            )
        },
        "policy": {
            "policy_owner_name": "Paul Thompson",
            "coverage_amount": 150000,
            "status": "active",
            "history": "Purchased 2018-10-03. Renewed 2024-10-03. No changes to coverage limits."
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    # ── DENY_INELIGIBLE claim ────────────────────────────────────────────────────

    "34102-03780": {
        "claim": {
            "claim_id": "34102-03780",
            "applicant_name": "Mary Johnson",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 140000,
            "claim_amount": 140000,
            "deductible": 2500,
            "assessment_date": "2026-02-13",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (in-house)",
            "narrative": (
                "Hurricane caused $140,000 in damage to our family home where we've lived for 22 years. "
                "Roof completely destroyed, interior flooded, all mechanical systems non-functional. "
                "Filing claim for full assessed damage. Deductible is $2,500."
            )
        },
        "policy": {
            "policy_owner_name": "Mary Johnson",
            "coverage_amount": 200000,
            "status": "expired",
            "history": (
                "Purchased 2014-07-01. Renewed 2020-07-01. Renewed 2023-07-01. "
                "Policy lapsed 2025-07-01 - renewal payment not received. Coverage terminated."
            )
        },
        "clue_history": (
            "2020-09-12: Tropical Storm Eta minor water damage. Claim filed with Nationwide. "
            "Property: 891 Pine Ridge Rd, Naples FL. Amount requested: $8,500. "
            "Amount paid: $7,200. Repair recorded: yes."
        ),
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    # ── DENY_FRAUD claims ────────────────────────────────────────────────────────

    "34102-03972": {
        "claim": {
            "claim_id": "34102-03972",
            "applicant_name": "Dorothy Harris",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 96000,
            "claim_amount": 96000,
            "deductible": 2000,
            "assessment_date": "2026-02-16",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (3rd party)",
            "narrative": (
                "Hurricane damage includes: roof replacement ($45,000), interior water damage ($28,000), "
                "window replacement ($15,000), electrical system repairs ($8,000). Total assessed damage "
                "$96,000. My deductible is $2,000."
            )
        },
        "policy": {
            "policy_owner_name": "Dorothy Harris",
            "coverage_amount": 150000,
            "status": "active",
            "history": "Purchased 2017-03-10. Renewed 2024-03-10. No changes to coverage limits."
        },
        "clue_history": (
            "2025-04-12: Hail storm roof damage. Claim filed with StateFarm. "
            "Property: 2240 Airport Rd S, Naples FL. Amount requested: $24,000. "
            "Amount paid: $22,000. Repair recorded: no."
        ),
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    "34102-03984": {
        "claim": {
            "claim_id": "34102-03984",
            "applicant_name": "Kenneth Martin",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 118000,
            "claim_amount": 118000,
            "deductible": 2500,
            "assessment_date": "2026-02-14",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (3rd party)",
            "narrative": (
                "Major structural damage from hurricane: foundation cracking and wall separation ($55,000), "
                "HVAC system destroyed by flooding ($18,000), all windows blown out ($22,000), hardwood "
                "flooring warped ($15,000), electrical panel damaged ($8,000). Total damage $118,000. "
                "Deductible is $2,500."
            )
        },
        "policy": {
            "policy_owner_name": "Kenneth Martin",
            "coverage_amount": 200000,
            "status": "active",
            "history": "Purchased 2019-11-25. Renewed 2024-11-25. No changes to coverage limits."
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "North Korea",
            "bank_account_country": "Unverifiable",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    "34102-03708": {
        "claim": {
            "claim_id": "34102-03708",
            "applicant_name": "Jennifer Sullivan",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 88000,
            "claim_amount": 88000,
            "deductible": 2000,
            "assessment_date": "2026-02-18",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (3rd party)",
            "narrative": (
                "Hurricane caused severe damage to my home. Roof torn off by wind ($45,000), extensive "
                "interior water and wind damage throughout first and second floors ($43,000). Total assessed "
                "at $88,000. Deductible is $2,000. Need repairs urgently before rainy season."
            )
        },
        "policy": {
            "policy_owner_name": "Jennifer Sullivan",
            "coverage_amount": 175000,
            "status": "active",
            "history": "Purchased 2016-04-08. Renewed 2024-04-08. No changes to coverage limits."
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": False,
            "ssn_matches_policyholder": False,
            "identity_theft_history": True
        }
    },

    "34102-03744": {
        "claim": {
            "claim_id": "34102-03744",
            "applicant_name": "James Rodriguez",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 125000,
            "claim_amount": 125000,
            "deductible": 2500,
            "assessment_date": "2026-02-19",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (in-house)",
            "narrative": (
                "Storm surge caused catastrophic damage to our waterfront home at 123 Gulf Shore Blvd. "
                "Foundation undermined ($40,000), load-bearing walls compromised ($50,000), complete "
                "interior gutting required ($35,000). Total damage $125,000. Deductible is $2,500."
            )
        },
        "policy": {
            "policy_owner_name": "James Rodriguez",
            "coverage_amount": 200000,
            "status": "active",
            "history": "Purchased 2018-12-01. Renewed 2024-12-01. No changes to coverage limits."
        },
        "clue_history": (
            "2026-03-22: Hurricane wind/flood damage. Claim filed with Allstate. "
            "Property: 123 Gulf Shore Blvd, Naples FL. Policyholder name: James Rodriguez. "
            "Amount requested: $125,000. Amount paid: pending. Repair recorded: no. | "
            "2026-03-23: Hurricane wind/flood damage. Claim filed with Progressive. "
            "Property: 123 Gulf Shore Blvd, Naples FL. Policyholder name: Maria Lopez. "
            "Amount requested: $125,000. Amount paid: pending. Repair recorded: no. | "
            "2026-03-23: Hurricane wind/flood damage. Claim filed with GEICO. "
            "Property: 123 Gulf Shore Blvd, Naples FL. Policyholder name: Carlos Mendez. "
            "Amount requested: $125,000. Amount paid: pending. Repair recorded: no."
        ),
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

    "34102-03768": {
        "claim": {
            "claim_id": "34102-03768",
            "applicant_name": "Thomas White",
            "city": "Naples",
            "is_primary_residence": True,
            "damage_assessed": 90000,
            "claim_amount": 90000,
            "deductible": 2500,
            "assessment_date": "2026-02-15",
            "disaster_date": "2026-02-11",
            "assessment_source": "Insurance adjuster (3rd party)",
            "narrative": (
                "Hurricane caused devastating damage to my home. Entire roof system destroyed ($35,000), "
                "interior flooding ruined all flooring and drywall ($33,000), HVAC and electrical systems "
                "non-functional ($22,000). Total damage assessed at $90,000. Deductible is $2,500."
            )
        },
        "policy": {
            "policy_owner_name": "Thomas White",
            "coverage_amount": 250000,
            "status": "active",
            "history": "Purchased 2026-02-09. Initial coverage set to $250,000. No prior insurance history on file."
        },
        "clue_history": "No prior claims on file.",
        "identity_verification": {
            "ip_country": "United States",
            "bank_account_country": "United States",
            "identity_verified": True,
            "ssn_matches_policyholder": True,
            "identity_theft_history": False
        }
    },

}


def lambda_handler(event, context):
    """
    AWS Lambda handler for the Claims Investigation Service (CIS).

    Routes:
      GET /health                        → {"status": "ok"}
      GET /investigation/{claim_id}      → full CIS record or 404
    """
    path = event.get("path", "")

    if path == "/health":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"status": "ok"})
        }

    path_params = event.get("pathParameters") or {}
    claim_id = path_params.get("claim_id", "").strip()

    if claim_id not in CLAIMS:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Claim not found", "claim_id": claim_id})
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(CLAIMS[claim_id])
    }
