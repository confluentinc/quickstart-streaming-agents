# Flink Docs Publisher

This directory contains scripts to publish Flink documentation to Kafka in Avro format.

## Setup

1. **Create virtual environment** (from project root):
   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```

2. **Deploy infrastructure** (AWS or Azure):
   ```bash
   # For AWS
   cd terraform/aws/lab2-vector-search
   terraform init && terraform apply

   # For Azure
   cd terraform/azure/lab2-vector-search
   terraform init && terraform apply
   ```

## Usage

### AWS Deployment
```bash
cd terraform/aws/lab2-vector-search
../../../.venv/bin/python publish_docs.py
```

### Azure Deployment
```bash
cd terraform/azure/lab2-vector-search
../../../.venv/bin/python publish_docs.py
```

## What it does

1. **Extracts credentials** from Terraform state (both local and core infrastructure)
2. **Parses ~210 Flink docs** with YAML frontmatter and markdown content
3. **Publishes to Kafka** using Avro schema:
   ```json
   {
     "document_id": "string",
     "document_text": "string"
   }
   ```
4. **Publishes to topic**: `documents`

## Architecture

- **Main script**: `publish_docs.py` - Core document processing and Kafka publishing
- **AWS wrapper**: `terraform/aws/lab2-vector-search/publish_docs.py`
- **Azure wrapper**: `terraform/azure/lab2-vector-search/publish_docs.py`
- **Test script**: `test_parser.py` - Validates document parsing

The wrapper scripts handle cloud-specific credential extraction from Terraform state, then call the main publisher with the required environment variables.