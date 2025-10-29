### 0. Install prerequisites

**Mac:**

```sh
# install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

```
brew install uv git python pkg-config && brew tap hashicorp/tap && brew install hashicorp/tap/terraform && brew install --cask confluent-cli docker-desktop && brew install librdkafka && brew install awscli
```

**Windows:**

```
winget install astral-sh.uv Git.Git Docker.DockerDesktop Hashicorp.Terraform ConfluentInc.Confluent-CLI pkgconf Python.Python Amazon.AWSCLI # or Microsoft.AzureCLI
```


------

### **1. Log into the Workshop Studio console**

You’ll get a link like `https://workshop.aws/xyz` or similar.

Click **“Start Lab”** or **“Open Console”** — this provisions your temporary AWS account.

------

### **2. Open the “Show” or “AWS CLI” tab in the instructions**

Workshop Studio usually provides:

- **Access Key ID**
- **Secret Access Key**
- **Session Token**
- (and sometimes the Region)

It might be under a section called **“AWS CLI”**, **“AWS Details”**, or **“Show” → “AWS CLI credentials”**.

------

### **3. Set the credentials in your CLI environment**

#### **Option A — Use** **`aws configure set`**

```
aws configure set aws_access_key_id <YOUR_ACCESS_KEY_ID> --profile workshop
aws configure set aws_secret_access_key <YOUR_SECRET_ACCESS_KEY> --profile workshop
aws configure set aws_session_token <YOUR_SESSION_TOKEN> --profile workshop
aws configure set region <YOUR_REGION> --profile workshop
```

Then test:

```
aws sts get-caller-identity --profile workshop
```

#### **Option B — Temporarily export them as environment variables (quickest):**

```
export AWS_ACCESS_KEY_ID=<YOUR_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<YOUR_SECRET_ACCESS_KEY>
export AWS_SESSION_TOKEN=<YOUR_SESSION_TOKEN>
export AWS_DEFAULT_REGION=<YOUR_REGION>
```

Then run:

```
aws sts get-caller-identity
```

These variables will last for your terminal session and expire when your workshop credentials expire (after today).

------

### 4. Request access to Claude Sonnet 3.7 in Bedrock Model Playground

- ⚠️ **IMPORTANT:** To access Claude Sonnet 3.7 you must request access to the model by filling out an Anthropic use case form (or someone in your org must have previously done so) for your cloud region. To do so, visit the [Model Catalog](https://console.aws.amazon.com/bedrock/home#/model-catalog), select Claude 3.7 Sonnet and open it it in the Playground, then send a message in the chat - the form will appear automatically. ⚠️

### 5. [Sign up for Confluent Cloud](https://www.confluent.io/get-started/?utm_campaign=tm.pmm_cd.q4fy25-quickstart-streaming-agents&utm_source=github&utm_medium=demo) and add a credit card

### 6. [Sign up for Zapier free account](https://zapier.com/sign-up), create remote MCP server with add tools

Add: `Gmail` send email tool, and `Zapier Webhooks: GET` tools.

Copy and save the `zapier_sse_endpoint`.

[Zapier step-by-step instructions here](./LAB1-Walkthrough.md#zapier-mcp-server-setup)

### 6. Run `uv run deploy`

Follow instructions in [LAB1-Walkthrough.md](./LAB1-Walkthrough.md) to deploy the lab.

------

### **7. Clean up afterward**

When you’re done, don't forget to:

```uv run destroy
uv run destroy

confluent logout

unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_DEFAULT_REGION
```
