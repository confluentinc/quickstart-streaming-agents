# Lab4: FEMA Fraud Detection Using Confluent Intelligence

![FEMA Fraud Detection](./assets/lab4/lab4-fraud-detection-logo.png)

This demo showcases an intelligent, real-time fraud detection system that autonomously identifies suspicious claim patterns in FEMA disaster assistance applications. Built on [Confluent Intelligence](https://www.confluent.io/product/confluent-intelligence/), the system combines stream processing, anomaly detection, and AI-powered analysis to detect organized fraud rings and policy violations in real-time.

## What This System Does

The system continuously monitors FEMA disaster assistance claims in real time and performs automated fraud detection:

1. **Anomaly Detection** – Detects unusual spikes in claim amounts across different cities using Flink's [ML_DETECT_ANOMALIES function](https://docs.confluent.io/cloud/current/ai/builtin-functions/detect-anomalies.html).
2. **Pattern Recognition** – Identifies organized fraud rings through shared accounts, phone numbers, and timeline violations.
3. **Contextual Understanding** – Analyzes claim narratives using LLMs to detect vague descriptions, exaggerated amounts, and suspicious patterns.

All of this runs in real time on **Confluent Cloud for Apache Flink**, with no external orchestration required.

---

## Prerequisites

**Installation instructions:**

```bash
brew install uv git python && brew tap hashicorp/tap && brew install hashicorp/tap/terraform && brew install --cask confluent-cli
```

**Windows:**
```powershell
winget install astral-sh.uv Git.Git Hashicorp.Terraform ConfluentInc.Confluent-CLI Python.Python
```

Once software is installed, you'll need:
- **LLM Access:** AWS Bedrock API keys **OR** Azure OpenAI endpoint + API key
  - **Easy key creation:** Run `uv run api-keys create` to quickly auto-generate credentials

---

## Deploy the Demo

First, clone the repo:

```bash
git clone https://github.com/confluentinc/quickstart-streaming-agents.git
cd quickstart-streaming-agents
```

Once you have your credentials ready, run the deployment script and choose **Lab4**:

```bash
uv run deploy
```

The deployment script will prompt you for your:
- Cloud provider (AWS/Azure)
- LLM API keys (Bedrock keys or Azure OpenAI endpoint/key)
- Confluent Cloud credentials

Select **"Lab 4: FEMA Fraud Detection"** from the menu.

---

## Use Case Walkthrough

### Data Generation

Generate synthetic FEMA claims data:

```bash
uv run lab4_datagen
```

This publishes ~36,000 synthetic claims across 8 Florida cities over a 14-day period following Hurricane Helene (March 1, 2025).

The data includes:
- **`claims`** table – FEMA disaster assistance claims with applicant info, damage assessments, claim amounts, and detailed narratives

**Data Pattern:**
- **7 cities** show normal exponential decay (claims decrease over time)
- **1 city (Naples)** shows an anomalous spike on Day 3, containing specifically designed claims with fraud indicators, policy violations, and legitimate claims for testing

---

### 1. Detect Fraud Spikes Using `ML_DETECT_ANOMALIES`

This step identifies unexpected surges in claim amounts for each city in real time using Flink's built-in anomaly detection function. We analyze claim amounts over 3-hour windows and compare them against expected baselines derived from historical trends.

Read the [blog post](https://docs.confluent.io/cloud/current/ai/builtin-functions/detect-anomalies.html) and view the [documentation](https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html#flink-sql-ml-anomaly-detect-function) on Flink anomaly detection for more details.

**Run this query in the [Flink UI](https://confluent.cloud/go/flink) to create the anomaly detection table:**

```sql
SET 'sql.state-ttl' = '14 d';

CREATE TABLE claims_anomalies_by_city AS
WITH windowed_claims AS (
    SELECT
        window_start,
        window_end,
        window_time,
        city,
        COUNT(*) AS claim_count,
        SUM(CAST(claim_amount AS DOUBLE)) AS total_claim_amount,
        CAST(ROUND(AVG(CAST(claim_amount AS DOUBLE))) AS BIGINT) AS avg_claim_amount,
        SUM(CAST(damage_assessed AS DOUBLE)) AS total_damage_assessed
    FROM TABLE(
        TUMBLE(TABLE claims, DESCRIPTOR(claim_timestamp), INTERVAL '6' HOUR)
    )
    GROUP BY window_start, window_end, window_time, city
),
anomaly_detection AS (
    SELECT
        city,
        window_time,
        claim_count,
        total_claim_amount,
        avg_claim_amount,
        total_damage_assessed,
        ML_DETECT_ANOMALIES(
            CAST(total_claim_amount AS DOUBLE),
            window_time,
            JSON_OBJECT(
                'minTrainingSize' VALUE 8,
                'maxTrainingSize' VALUE 50,
                'confidencePercentage' VALUE 95.0,
                'enableStl' VALUE FALSE
            )
        ) OVER (
            PARTITION BY city
            ORDER BY window_time
            RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS anomaly_result
    FROM windowed_claims
)
SELECT
    city,
    window_time,
    claim_count,
    total_claim_amount,
    avg_claim_amount,
    total_damage_assessed,
    CAST(ROUND(anomaly_result.forecast_value) AS BIGINT) AS expected_claim_amount,
    anomaly_result.upper_bound AS upper_bound,
    anomaly_result.lower_bound AS lower_bound,
    anomaly_result.is_anomaly AS is_anomaly
FROM anomaly_detection
WHERE anomaly_result.is_anomaly = true
  AND total_claim_amount > anomaly_result.upper_bound;
```

**What it does:**
1. **Sets state TTL** to 14 days to prevent infinite state growth
2. **Aggregates** claims into 3-hour tumbling windows per city
3. **Applies ML_DETECT_ANOMALIES** using ARIMA time-series forecasting:
   - `minTrainingSize: 16` – Needs 2 days (16 windows) of baseline before detecting
   - `maxTrainingSize: 50` – Caps training data; prevents memory issues
   - `confidencePercentage: 95.0` – Detects significant deviations
   - `enableStl: FALSE` – No seasonal decomposition (disaster claims lack seasonality)
4. **Filters** to only anomalous spikes (above upper confidence bound)

**View the results:**

```sql
SELECT * FROM claims_anomalies_by_city;
```

**Expected Results:**

```
city   | window_time         | claim_count | total_claim_amount | expected_claim_amount | is_anomaly
-------|---------------------|-------------|--------------------|-----------------------|----------------
Naples | 2025-03-03 08:59:59 | 47          | 5863000           | 2826604               | true
```

You should see **1 anomaly** detected in Naples on Day 3, containing all claims from that 3-hour window.

---

### 2. Investigate Fraudulent Claims

Once anomalies are detected, use this query to create a table with all claims from the anomaly window for investigation:

```sql
SET 'sql.state-ttl' = '14 d';

CREATE TABLE claims_to_investigate AS
SELECT
    c.claim_id,
    c.applicant_name,
    c.city,
    c.claim_amount,
    c.damage_assessed,
    c.has_insurance,
    c.insurance_amount,
    c.is_primary_residence,
    c.claim_narrative,
    c.assessment_date,
    c.disaster_date,
    c.assessment_source,
    c.shared_account,
    c.shared_phone,
    c.previous_claims_count,
    c.last_claim_date,
    c.claim_timestamp,
    a.window_time AS anomaly_window_time,
    a.total_claim_amount AS anomaly_total_amount,
    a.is_anomaly
FROM claims c
INNER JOIN claims_anomalies_by_city a
    ON c.city = a.city
    AND c.claim_timestamp >= a.window_time - INTERVAL '6' HOUR
    AND c.claim_timestamp <= a.window_time
WHERE c.claim_narrative <> ''
LIMIT 10;
```

This creates a table with all claims from the Naples anomaly window. Now query it to see what was flagged:

```sql
SELECT * FROM claims_to_investigate;
```

```sql
 SET 'sql.state-ttl' = '14 d';
                                    
  CREATE TABLE claims_to_investigate_with_policies AS                 
  WITH embedded AS (                                                   
      SELECT
          c.*,
          e.embedding AS narrative_embedding
      FROM claims_to_investigate c,
      LATERAL TABLE(ML_PREDICT('llm_embedding_model', c.claim_narrative)) e
  )
  SELECT
      c.claim_id,
      c.applicant_name,
      c.city,
      c.claim_amount,
      c.damage_assessed,
      c.has_insurance,
      c.insurance_amount,
      c.is_primary_residence,
      c.claim_narrative,
      c.assessment_date,
      c.disaster_date,
      c.assessment_source,
      c.shared_account,
      c.shared_phone,
      c.previous_claims_count,
      c.last_claim_date,
      c.claim_timestamp,
      c.anomaly_window_time,
      c.anomaly_total_amount,
      c.is_anomaly,
      vs.search_results[1].chunk AS policy_chunk_1,
      vs.search_results[1].score AS policy_score_1,
      vs.search_results[1].pages AS policy_pages_1,
      vs.search_results[1].section_reference AS policy_section_1,
      vs.search_results[1].title AS policy_title_1,
      vs.search_results[1].fraud_categories AS policy_fraud_cats_1,
      vs.search_results[1].policy_keywords AS policy_keywords_1,
      vs.search_results[2].chunk AS policy_chunk_2,
      vs.search_results[2].score AS policy_score_2,
      vs.search_results[2].pages AS policy_pages_2,
      vs.search_results[2].section_reference AS policy_section_2,
      vs.search_results[2].title AS policy_title_2,
      vs.search_results[2].fraud_categories AS policy_fraud_cats_2,
      vs.search_results[2].policy_keywords AS policy_keywords_2,
      vs.search_results[3].chunk AS policy_chunk_3,
      vs.search_results[3].score AS policy_score_3,
      vs.search_results[3].pages AS policy_pages_3,
      vs.search_results[3].section_reference AS policy_section_3,
      vs.search_results[3].title AS policy_title_3,
      vs.search_results[3].fraud_categories AS policy_fraud_cats_3,
      vs.search_results[3].policy_keywords AS policy_keywords_3
  FROM embedded c,
  LATERAL TABLE(
      VECTOR_SEARCH_AGG(
          fema_policies_vectordb,
          DESCRIPTOR(embedding),
          c.narrative_embedding,
          3
      )
  ) vs;
```

Then view the results:
```sql
SELECT * FROM `claims_to_investigate_with_policies`;
```



---

### 3. Define the Fraud Detection Agent

With each claim enriched with FEMA policy context, the next step is to define an AI agent that analyzes every claim holistically — checking the arithmetic, cross-referencing the narrative against structured fields, and citing specific FEMA IAPPG policy sections to justify each verdict.

Unlike the anomaly detection and RAG steps, which are pure SQL transforms, this agent performs multi-step reasoning: it evaluates each claim against a checklist of policy violations in sequence, weighs competing signals, and produces a structured verdict.

See [CREATE AGENT documentation](https://docs.confluent.io/cloud/current/flink/reference/statements/create-agent.html).

```sql
CREATE AGENT `fema_fraud_agent`
USING MODEL `llm_textgen_model`
USING PROMPT 'OUTPUT RULES — read before anything else:
1. Respond with ONLY these four labeled sections, in this exact order:
   Verdict:
   Issues Found:
   Policy Basis:
   Summary:
2. NO markdown. No asterisks, no bold, no headers, no pound signs. Plain text only.
3. The Verdict line must contain exactly one word: APPROVE, APPROVE_PARTIAL, REQUEST_DOCS, DENY_INELIGIBLE, or DENY_FRAUD.

Correct format example:
Verdict: DENY_INELIGIBLE

Issues Found:
- Property is not a primary residence. Narrative states "our Naples beach house we rent out seasonally."
- is_primary_residence = "no" confirmed in structured data.

Policy Basis:
FEMA IAPPG Section 3 — IHP Housing Assistance is restricted to the applicants primary dwelling. Rental and vacation properties are categorically excluded.

Summary:
Claim denied. The property is a seasonal rental, not a primary residence, and is therefore ineligible for IHP assistance regardless of the damage amount.

---

You are a FEMA IHP fraud detection agent reviewing Hurricane Helene (March 1, 2025) disaster assistance claims.

CHECKLIST — evaluate all nine in order:

1. CLAIM CEILING: Does claim_amount > damage_assessed? Auto-violation — FEMA cannot pay above verified assessed damage.
2. DUPLICATION OF BENEFITS: Does claim_amount > (damage_assessed minus insurance_amount)? FEMA covers only the uncompensated gap.
3. PRIMARY RESIDENCE: Is is_primary_residence = "no"? IHP covers primary dwellings only — vacation homes, investment properties, and rentals are ineligible.
4. ASSESSMENT SOURCE: Is assessment_source = "Self"? Self-assessments are not accepted. Flag if narrative claims a "FEMA inspection" but source = "Contractor".
5. PROPERTY USE (narrative): Does the narrative reveal a vacation rental, second home, or income-producing property?
6. INELIGIBLE ITEMS (narrative): Does the narrative claim pools, boats, landscaping, fences, outdoor furniture, or other non-essential property?
7. PRE-EXISTING DAMAGE (narrative): Does the narrative disclose wear, deterioration, or damage that predates the disaster?
8. EXPLICIT DUPLICATION (narrative): Does the narrative admit receiving insurance payment for the same damage while also claiming FEMA funds?
9. PRIOR CLAIMS: Does previous_claims_count > 0? Weight more heavily when combined with other violations.

VERDICTS:
- APPROVE: All checks pass, claim eligible as submitted.
- APPROVE_PARTIAL: Property is eligible and damage is verified, but the claim amount exceeds the allowable ceiling or includes specific ineligible items. Approve the eligible portion. State the calculated eligible amount in Issues Found (e.g., "Eligible amount: $45,000 (damage_assessed ceiling)").
- REQUEST_DOCS: No clear violation, but a determination requires additional documentation before a final decision.
- DENY_INELIGIBLE: Property or claim is categorically ineligible regardless of amount — non-primary residence declared in structured data, vacation rental or income-producing property revealed in narrative, or self-assessment with no third-party verification. No portion is approvable.
- DENY_FRAUD: Deliberate misrepresentation — false primary residence claim, explicit insurance duplication, or mathematically impossible amounts. Refer to OIG.

In Issues Found: cite dollar amounts and quote key phrases from the narrative. For APPROVE_PARTIAL, state the eligible amount. Write "None — claim passes all checks." if APPROVE.
In Policy Basis: cite specific section titles and references from the retrieved FEMA policy chunks.

REMINDER: Plain text only. No asterisks, no bold, no markdown of any kind.'
WITH (
  'max_iterations' = '10'
);
```

---

### 4. Run the Agent on All Flagged Claims

Now invoke the agent continuously against every claim in `claims_to_investigate_with_policies`. As each claim streams through, the agent receives the full structured data plus the three most relevant FEMA policy chunks, performs its checklist analysis, and writes a structured verdict to the output table.

The `REGEXP_EXTRACT` calls parse the four labeled sections from the agent's free-text response into typed columns.

See [AI_RUN_AGENT documentation](https://docs.confluent.io/cloud/current/flink/reference/functions/model-inference-functions.html#flink-sql-ai-run-agent-function).

```sql
SET 'sql.state-ttl' = '14 d';

CREATE TABLE claims_reviewed (
    PRIMARY KEY (claim_id) NOT ENFORCED
)
WITH ('changelog.mode' = 'append')
AS SELECT
    claim_id,
    TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '\*{0,2}Verdict:\*{0,2}\s*([A-Z_]+)', 1)) AS verdict,
    TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '\*{0,2}Summary:\*{0,2}\n([\s\S]+?)$', 1)) AS summary,
    TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '\*{0,2}Issues Found:\*{0,2}\n([\s\S]+?)(?=\n\*{0,2}(?:Policy Basis|Summary|Verdict):|$)', 1)) AS issues_found,
    TRIM(REGEXP_EXTRACT(CAST(response AS STRING), '\*{0,2}Policy Basis:\*{0,2}\n([\s\S]+?)(?=\n\*{0,2}(?:Summary|Verdict):|$)', 1)) AS policy_basis,
    applicant_name,
    claim_amount,
    damage_assessed,
    insurance_amount,
    is_primary_residence,
    assessment_source,
    previous_claims_count,
    CAST(response AS STRING) AS raw_response
FROM claims_to_investigate_with_policies,
LATERAL TABLE(AI_RUN_AGENT(
    `fema_fraud_agent`,
    CONCAT(
        'CLAIM FOR REVIEW: ', claim_id, '\n',
        'Applicant: ', applicant_name, '\n',
        'Claim Amount: $', claim_amount, '\n',
        'Total Damage Assessed: $', COALESCE(CAST(damage_assessed AS STRING), '0'), '\n',
        'Insurance Payout: $', COALESCE(CAST(insurance_amount AS STRING), '0'), '\n',
        'Uncompensated Gap (damage minus insurance): $',
            CAST(CAST(
                COALESCE(CAST(damage_assessed AS DOUBLE), 0.0) -
                COALESCE(CAST(insurance_amount AS DOUBLE), 0.0)
            AS BIGINT) AS STRING), '\n',
        'Is Primary Residence: ', COALESCE(is_primary_residence, 'unknown'), '\n',
        'Assessment Source: ', COALESCE(assessment_source, 'unknown'), '\n',
        'Prior FEMA Claims: ', COALESCE(CAST(previous_claims_count AS STRING), '0'), '\n',
        '\nCLAIM NARRATIVE:\n', COALESCE(claim_narrative, '(none)'), '\n',
        '\nRETRIEVED FEMA POLICY SECTIONS:\n',
        '1. ', COALESCE(policy_title_1, 'N/A'), ' (', COALESCE(policy_section_1, 'N/A'), '):\n',
        COALESCE(policy_chunk_1, ''), '\n\n',
        '2. ', COALESCE(policy_title_2, 'N/A'), ' (', COALESCE(policy_section_2, 'N/A'), '):\n',
        COALESCE(policy_chunk_2, ''), '\n\n',
        '3. ', COALESCE(policy_title_3, 'N/A'), ' (', COALESCE(policy_section_3, 'N/A'), '):\n',
        COALESCE(policy_chunk_3, '')
    ),
    MAP['debug', 'true']
));
```

```sql
SELECT * FROM `claims_reviewed`;
```



## Conclusion

By chaining these streaming components together, we've built an always-on, real-time fraud detection pipeline that:

1. **Detects** anomalous claim spikes in 3-hour windows across cities using `ML_DETECT_ANOMALIES`
2. **Isolates** the suspicious window and enriches every claim with relevant FEMA IAPPG policy sections using vector search
3. **Investigates** each claim autonomously using an AI agent that checks arithmetic, cross-references narrative against structured fields, and cites specific policy violations

The result is a streaming verdict for every flagged claim — approve, request documentation, deny for policy violation, or deny for fraud — delivered in real time as claims arrive, with specific FEMA policy citations to support each decision.

---

## Troubleshooting

<details>
<summary>Click to expand</summary>

### No anomalies detected?

**Check:**
1. Data publishing completed: `uv run lab4_datagen`
2. Claims published to topic: `SELECT COUNT(*) FROM claims;` (should be ~36,000)
3. Wait for baseline: ARIMA needs 16 windows (2 days with 3-hour windows) before detecting

The anomaly should appear after data publishing completes and Flink processes all windows up to Day 3.

### Error: Table `claims_anomalies_by_city` does not exist?

**Solution:**

Run the CREATE TABLE query in the Flink UI (see Step 1 above). The anomaly detection table is created manually, not via Terraform.

### Query returns 0 rows?

**Check:**
1. Terraform deployed: `terraform output` should show table IDs
2. Data exists: `SELECT * FROM claims LIMIT 10;`
3. Wait for processing: Flink may take 1-2 minutes to process all windows

### Too many or too few anomalies?

The ARIMA parameters are tuned to detect exactly 1 anomaly (Naples, Day 3).

If you see different results:
- **0 anomalies:** Decrease `confidencePercentage` to 90.0
- **>1 anomalies:** Increase `confidencePercentage` to 99.0
- **Wrong timing:** Re-publish data: `uv run lab4_datagen`

</details>

---

## 🧹 Clean-up

When you're done with the lab:

```bash
uv run destroy
```

Choose your cloud provider when prompted to remove all lab-related resources.

---

## Navigation

- **← Back to Overview**: [Main README](./README.md)
- **← Previous Lab**: [Lab3: Agentic Fleet Management](./LAB3-Walkthrough.md)
- **🧹 Cleanup**: [Cleanup Instructions](./README.md#cleanup)
