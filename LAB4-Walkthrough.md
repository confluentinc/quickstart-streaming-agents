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

This publishes ~36,000 synthetic claims across 8 Florida cities over a 14-day period following Hurricane Helena (March 1, 2025).

The data includes:
- **`claims`** table – FEMA disaster assistance claims with applicant info, damage assessments, claim amounts, and detailed narratives

**Data Pattern:**
- **7 cities** show normal exponential decay (claims decrease over time)
- **1 city (Naples)** shows an anomalous spike on Days 10-11, containing 47 specifically designed claims with fraud indicators, policy violations, and legitimate claims for testing

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
        AVG(CAST(claim_amount AS DOUBLE)) AS avg_claim_amount,
        SUM(CAST(damage_assessed AS DOUBLE)) AS total_damage_assessed
    FROM TABLE(
        TUMBLE(TABLE claims, DESCRIPTOR(claim_timestamp), INTERVAL '3' HOUR)
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
                'minTrainingSize' VALUE 16,
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
    anomaly_result.is_anomaly AS is_fraud_spike
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
city   | window_time         | claim_count | total_claim_amount | expected_claim_amount | is_fraud_spike
-------|---------------------|-------------|--------------------|-----------------------|----------------
Naples | 2025-03-03 08:59:59 | 47          | 5863000           | 2826604               | true
```

You should see **1 anomaly** detected in Naples on Day 3, containing 47 claims in the 3-hour window.

![Anomaly Screenshot](./assets/lab4/lab4-anomaly-results.png)

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
    a.is_fraud_spike
FROM claims c
INNER JOIN claims_anomalies_by_city a
    ON c.city = a.city
    AND c.claim_timestamp >= a.window_time - INTERVAL '3' HOUR
    AND c.claim_timestamp <= a.window_time;
```

This creates a table with all 47 claims from the Naples anomaly window. Now query it to identify fraud patterns:

```sql
SELECT * FROM claims_to_investigate ORDER BY claim_timestamp;
```

**Look for fraud indicators in the claims:**

#### Policy Violations - Basement/Below-Grade Items
```sql
-- FEMA does not cover basement items, crawl spaces, or below-grade damage
SELECT claim_id, applicant_name, claim_amount, claim_narrative
FROM claims_to_investigate
WHERE claim_narrative LIKE '%basement%'
   OR claim_narrative LIKE '%crawl space%'
   OR claim_narrative LIKE '%garden level%';
```

**Red Flag:** Claims for basement items (home theaters, furniture in basements) are not covered by FEMA

#### Policy Violations - Non-Primary Residence
```sql
-- FEMA only covers primary residences
SELECT claim_id, applicant_name, claim_amount, is_primary_residence, claim_narrative
FROM claims_to_investigate
WHERE is_primary_residence = 'no'
   OR claim_narrative LIKE '%vacation rental%'
   OR claim_narrative LIKE '%second home%';
```

**Red Flag:** Vacation rentals, investment properties not eligible

#### Policy Violations - Ineligible Items
```sql
-- Pools, landscaping, boats, fences are not covered
SELECT claim_id, applicant_name, claim_amount, claim_narrative
FROM claims_to_investigate
WHERE claim_narrative LIKE '%pool%'
   OR claim_narrative LIKE '%landscape%'
   OR claim_narrative LIKE '%boat%'
   OR claim_narrative LIKE '%RV%'
   OR claim_narrative LIKE '%fence%'
   OR claim_narrative LIKE '%deck%';
```

**Red Flag:** Non-essential items not covered by FEMA Individual Assistance

#### Timeline Violations - Pre-Disaster Assessments
```sql
-- Claims assessed BEFORE the disaster occurred (March 1, 2025)
SELECT claim_id, applicant_name, assessment_date, disaster_date,
       claim_amount, damage_assessed
FROM claims_to_investigate
WHERE assessment_date < disaster_date;
```

**Red Flag:** Assessment dated February 27-28 before March 1 disaster = impossible/fraud

#### Self-Assessment Fraud
```sql
-- Self-assessed claims often inflated
SELECT claim_id, applicant_name, claim_amount, damage_assessed,
       assessment_source, claim_narrative
FROM claims_to_investigate
WHERE assessment_source = 'Self';
```

**Red Flag:** Self-assessments with very high amounts or vague justification

#### Duplicate Benefits
```sql
-- Already received insurance or SBA loans for same damage
SELECT claim_id, applicant_name, claim_amount, insurance_amount, claim_narrative
FROM claims_to_investigate
WHERE claim_narrative LIKE '%Insurance company paid%'
   OR claim_narrative LIKE '%SBA%loan%'
   OR claim_narrative LIKE '%already received%';
```

**Red Flag:** Requesting FEMA funds for damage already compensated

---

### 3. Fraud Analysis Summary

Query the breakdown of the 47 claims in the anomaly window:

```sql
SELECT
    CASE
        WHEN claim_narrative LIKE '%basement%'
          OR claim_narrative LIKE '%crawl space%'
          OR claim_narrative LIKE '%garden level%'
          OR claim_narrative LIKE '%pool%'
          OR claim_narrative LIKE '%landscape%'
          OR claim_narrative LIKE '%boat%'
          OR claim_narrative LIKE '%RV%'
          OR claim_narrative LIKE '%fence%'
          OR is_primary_residence = 'no'
          OR claim_narrative LIKE '%vacation rental%'
            THEN 'Policy Violation'
        WHEN assessment_date < disaster_date
          OR assessment_source = 'Self'
          OR claim_amount > damage_assessed * 2
            THEN 'Clear Fraud'
        WHEN claim_amount > damage_assessed * 1.3
          OR claim_narrative LIKE '%Insurance company paid%'
          OR claim_narrative LIKE '%foundation%'
            THEN 'Suspicious/Edge Case'
        ELSE 'Legitimate'
    END as category,
    COUNT(*) as count,
    ROUND(AVG(CAST(claim_amount AS DOUBLE)), 0) as avg_claim_amount
FROM claims_to_investigate
GROUP BY category
ORDER BY count DESC;
```

**Expected Distribution:**
- ~15 Policy Violations (basement, pools, non-primary residence, ineligible items)
- ~10 Clear Fraud (pre-disaster assessments, self-assessed, heavily inflated)
- ~12 Suspicious/Edge Cases (borderline issues requiring review)
- ~10 Legitimate (should be approved)

---

## Conclusion

By using Confluent's ML_DETECT_ANOMALIES function, we've built an always-on, real-time fraud detection system that:

1. **Detects** suspicious claim patterns in 3-hour windows across cities
2. **Identifies** exactly when and where fraud is occurring (Naples, Day 3)
3. **Enables** rapid investigation of flagged claims with SQL queries

The system detected 1 anomalous window with 47 claims, revealing:
- **15 Policy Violations** - Basement items, pools, non-primary residences, ineligible items
- **10 Clear Fraud** - Pre-disaster assessments, self-assessed inflated claims
- **12 Suspicious/Edge Cases** - Duplicate benefits, foundation issues, underinsurance
- **10 Legitimate Claims** - Should be approved

All in real-time, protecting taxpayer dollars while ensuring legitimate disaster victims get help fast.

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
