# Streaming Agents on Confluent Cloud Quickstart

![Streaming Agents Intro Slide](./assets/streaming-agents-intro-slide.png)

This repository demonstrates how an online retailer can use [Streaming Agents](https://docs.confluent.io/cloud/current/ai/streaming-agents/overview.html) on Confluent Cloud to perform real-time price matching on sales orders. Whenever a customer makes a purchase, the AI agent automatically scrapes a competitor's product page for the item via tool calling. If the competitor offers the same item at a lower price, the agent adjusts the order price accordingly, and sends an updated confirmation email to the customer — also using tool calling.

![Architecture Diagram](./assets/arch.png)

## Demo Video

[![Watch on YouTube](https://img.youtube.com/vi/F4bUUsVDBVE/hqdefault.jpg)](https://www.youtube.com/watch?v=F4bUUsVDBVE "Watch on YouTube")

## 🎯 Essential Setup (Complete First!)

Before proceeding with any other steps, you **must** complete these essential prerequisites:

### 1. 🔑 Create Required Accounts & API Keys

1. **Confluent Cloud Account**

   [![Sign up for Confluent Cloud](https://img.shields.io/badge/Sign%20up%20for%20Confluent%20Cloud-007BFF?style=for-the-badge&logo=apachekafka&logoColor=white)](https://confluent.cloud/signup)

   [Log into your account](https://confluent.cloud/login)
   - Create [Cloud Resource Management API Keys with Organization Admin permissions](https://docs.confluent.io/cloud/current/security/authenticate/workload-identities/service-accounts/api-keys/overview.html#resource-scopes)

2. **Zapier MCP Server** - [Sign up for free](https://zapier.com/sign-up)
   - Get your MCP server URL (detailed instructions below)

<details>
<summary>🔧 <strong>Zapier MCP Server Setup Instructions</strong></summary>

### Setting up your Zapier Remote MCP Server

1. **Create Zapier Account**

   - Sign up for an account at [https://zapier.com/sign-up].
   - Click the verification link they send to your email.

2. **Create MCP Server**

   - Visit [https://mcp.zapier.com/mcp/servers](https://mcp.zapier.com/mcp/servers) to create an MCP server.
   - For "MCP Client", choose **"Other"**
   - Give your MCP server a name.
   - Click **"Create MCP Server."**

   <img src="./assets/zapier/3.png" alt="Create MCP Server" width="400">

3. **Add Tools**

   - Click **"Add tool."**

     <img src="./assets/zapier/4.png" alt="Add Gmail Tool" width="400">

   - Add **Webhooks by Zapier: GET** tool.

   - Add **Gmail: Send Email** tool (authenticate via SSO).

4. **Get Your MCP Server URL**

   - From the Zapier MCP server main screen, click **"Connect."**

     <img src="./assets/zapier/6.png" alt="Connect and Get URL" width="400">

   - Under "Transport", change from "Streamable HTTP" to **"SSE Endpoint."**

   - Click **"Copy URL"** in the bottom right.

     <img src="./assets/zapier/7.png" alt="Copy SSE Endpoint URL" width="400">

   - Your URL format will be: `https://mcp.zapier.com/api/mcp/s/<<long-API-key>>/sse`

   - ⭐ **Save this URL** - you'll need it for your `terraform.tfvars` file
   

</details>

## 📋 Install Required Software

- **AWS CLI or Azure CLI** 
- **Confluent CLI**
- **Docker**
- **Terraform**

<details>
<summary>Installing prerequisites on Mac</summary>

```bash
# Core tools
brew install git && brew tap hashicorp/tap && brew install hashicorp/tap/terraform && brew install --cask confluent-cli && brew install --cask docker-desktop
```

**Cloud provider CLI (choose based on your preference):**

```bash
brew install awscli
```

or:
```bash
brew install azure-cli
```

</details>

<details>
<summary>Installing prerequisites on Windows</summary>

```powershell
# Core tools
winget install --id Git.Git -e && winget install --id Hashicorp.Terraform -e && winget install --id ConfluentInc.Confluent-CLI -e && winget install --id Docker.DockerDesktop -e
```

**Cloud provider CLI (choose based on your preference):**

```powershell
winget install --id Amazon.AWSCLI -e
```

or:
```powershell
winget install --id Microsoft.AzureCLI -e
```

</details>

## 🚀 Quick Start Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/confluentinc/quickstart-streaming-agents.git
cd quickstart-streaming-agents/terraform
```

### 2. Configure Your Credentials

#### Option A (Mac only): `setup.py`helper  script

At this point you can run the `setup.py` helper script or you can continue with the manual setup instructions below. Please note that the script has only been tested on Mac.

To run the script you will need to be logged into Confluent CLI, and the AWS or Azure CLI tool. The `setup.py` helper script automatically generates new Confluent Cloud API keys with the proper `Organization Admin` role, activates the proper cloud environment, and deploys Terraform. You will still need to provide a `ZAPIER_SSE_ENDPOINT` for the script to use by [following these instructions](#setting-up-your-zapier-remote-mcp-server).

```sh
python setup.py
```

Or, you can continue with the manual setup instructions below.

#### Option B (Mac/Windows): Manual setup

Open the `terraform.tfvars` file:

macOS:

```bash
open -a TextEdit terraform.tfvars
```

Windows:

```bash
notepad terraform.tfvars
```

Fill out the values for `prefix`, `cloud_provider`, `cloud_region`, `confluent_cloud_api_key`, `confluent_cloud_api_secret`, and `ZAPIER_SSE_ENDPOINT` and save the file.

<details>
<summary><strong>📋 Supported Regions</strong> (Click to expand)</summary>

**Azure Regions:**
- **US**: East US, East US 2, Central US, North Central US, South Central US, West US, West US 2, West US 3
- **Europe**: North Europe, West Europe, UK South, UK West, France Central, Germany West Central
- **Asia**: East Asia, Southeast Asia, Japan East, Japan West, Korea Central, Korea South

**AWS Regions:**
- **US**: us-east-1, us-east-2, us-west-2
- **Europe**: eu-west-1, eu-west-2, eu-central-1
- **Asia**: ap-southeast-1, ap-southeast-2, ap-northeast-1

</details>

### 2A. [AWS ONLY] 🔓 Enable Claude Sonnet 3.7

<details>
<summary>🔧 Extra step required for AWS users</summary>

To enable **Claude 3.7 Sonnet** in your AWS account via Amazon Bedrock:

1. Open the [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/home?/overview), make sure you are in the same region.
2. In the left sidebar, under **Configure and learn**, click **Model access**.
3. Locate **Claude 3.7 Sonnet** in the list of available models.
4. Click **Available to request**, then select **Request model access**.
5. In the request wizard, click **Next** and follow the prompts to complete the request.

![Model Access in Bedrock Console](./assets/enablemodelbedrock.png)

⏱️ *Provisioning may take 5–10 minutes.*

</details>

### 3. Deploy with Terraform


<details>
<summary>Deploying on Azure</summary>

1. Enable the `providers-azure.tf` file

macOS:

```bash
mv providers-azure.tf.disabled providers-azure.tf 
```
Windows:

```bash
rename providers-azure.tf.disabled providers-azure.tf
```
2. Apply the terraform script

```bash
terraform init
terraform apply --auto-approve
```

</details>

<details>
<summary>Deploying on AWS</summary>

1. Enable the `providers-aws.tf` file

macOS:

```bash
mv providers-aws.tf.disabled providers-aws.tf 
```
Windows:

```bash
rename providers-aws.tf.disabled providers-aws.tf
```
2. Apply the terraform script

```bash
terraform init
terraform apply --auto-approve
```

</details>


## Set up Flink MCP connection

The Terraform script has already created a Flink connection to your chosen LLM model (AWS or Azure).

To enable **Flink tool calling**, you also need to create a Flink connection to your **MCP server**.

1. Open the `mcp_commands.txt` file (auto-generated by the terraform script) located in the `terraform` directory of this repository.
   <details>
   <summary>macOS:</summary>
   
   ```bash
   open mcp_commands.txt
   ```
   
   </details>
   

   <details>
   <summary>Windows:</summary>
   
   ```bash
   notepad mcp_commands.txt
   ```
   </details>
   
3. Log in with Confluent CLI, then run the `confluent flink connection create` command at the top of `mcp_commands.txt`. It should look like this:
  
   ```bash
   confluent flink connection create zapier-mcp-connection \
     --cloud AZURE \
     --region eastus \
     --type mcp_server \
     --endpoint https://mcp.zapier.com/api/mcp/s/<<long-API-key>> \
     --api-key api_key \
     --environment env-xxxxx \
     --sse-endpoint https://mcp.zapier.com/api/mcp/s/<<long-API-key>>/sse
   ```

## 📊 Data Generation

After successful terraform deployment, generate sample data:

```bash
cd data-gen/
```

Download the ShadowTraffic license file:

```bash
curl -O https://raw.githubusercontent.com/ShadowTraffic/shadowtraffic-examples/master/free-trial-license-docker.env
```

<details>
<summary>Click to expand Unix instructions</summary>

Run ShadowTraffic to generate data:
```bash
chmod +x run.sh && ./run.sh
```

</details>

<details>
<summary>Click to expand Windows instructions</summary>

Run ShadowTraffic to generate data:
```cmd
run.bat
```

</details>

🎉 **Data is now flowing through your streaming pipeline! Proceed to the labs!**

## Topics

**Next topic:** [Lab1: Price Matching Using Tool Calling](./LAB1-Tool-Calling/LAB1.md)

## 🧹 Cleanup

To destroy all resources when you're done with the labs:

```bash
cd ../terraform
terraform destroy --auto-approve
```

---

## ⚡ Summary Checklist

- [ ] Created Confluent Cloud account with API keys
- [ ] Set up Zapier MCP server and copied SSE endpoint URL
- [ ] Installed required software (Terraform, Confluent CLI, Docker)
- [ ] Cloned repository and configured `terraform.tfvars`
- [ ] [AWS only] Enabled Claude Sonnet 3.7 in Bedrock
- [ ] Deployed infrastructure with Terraform
- [ ] Generated sample data with ShadowTraffic

Need help? Check that all prerequisites are completed and credentials are correctly entered in your `terraform.tfvars` file.