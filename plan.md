# Clean Bifurcation Plan: Complete AWS/Azure Separation

## Context
We were experiencing Azure provider authentication issues when running setup.py for AWS deployments. The original shared `terraform/core/` approach had conditional logic trying to handle both AWS and Azure providers, which caused Terraform to always validate both providers even when using just one.

## Solution Overview
Complete separation of AWS and Azure concerns by creating dedicated directories at the root level with embedded modules, eliminating all provider conflicts and the terraform/ wrapper directory.

## Target Structure
```
/
├── aws/
│   ├── core/                    # AWS-only core terraform
│   │   ├── modules/            # AWS modules (aws-ai, aws)
│   │   ├── main.tf             # AWS-only resources
│   │   ├── versions.tf         # AWS providers only
│   │   └── ...
│   ├── lab1-tool-calling/
│   └── lab2-vector-search/
├── azure/
│   ├── core/                   # Azure-only core terraform
│   │   ├── modules/           # Azure modules (azure-ai, azure)
│   │   ├── main.tf            # Azure-only resources
│   │   ├── versions.tf        # Azure providers only
│   │   └── ...
│   ├── lab1-tool-calling/
│   └── lab2-vector-search/
└── setup.py                   # Updated paths
```

## Progress Made ✅

### 1. Reverted Core Terraform to Clean State ✅
- `git checkout HEAD -- terraform/core/versions.tf` (restored working version)
- Removed messy provider files (`terraform/core/providers-*.tf*`)
- Cleaned terraform state

### 2. AWS Directory Structure Creation ✅ (Mostly Complete)
- ✅ Created `aws/core/` directory
- ✅ Copied `terraform/core/` → `aws/core/`
- ✅ Created `aws/core/modules/` and copied AWS modules from `terraform/modules/aws*`
- ✅ Updated `aws/core/versions.tf`:
  - Removed azurerm provider
  - Simplified AWS provider (removed conditional logic)
  - Kept only: confluent, random, aws providers
- ✅ Updated `aws/core/main.tf`:
  - Changed module path: `../modules/aws-ai` → `./modules/aws-ai`
  - Removed Azure module: `module "azure_ai_services"`
  - Removed Azure Flink statement resources: `llm_textgen_model_azure`, `llm_embedding_model_azure`
  - Removed conditional counts from AWS resources (since AWS-only now)
- ✅ Updated `aws/core/variables.tf`:
  - Removed `azure_subscription_id` variable
- ✅ Updated `aws/core/outputs.tf`:
  - Removed `azure_subscription_id` output
  - Simplified outputs to remove conditional logic (direct module references)

## Remaining Tasks 🚧

### 3. Create Azure Directory Structure (NEXT)
- Create `azure/core/` directory
- Copy `terraform/core/` → `azure/core/`
- Copy `terraform/modules/azure*` → `azure/core/modules/`
- Update `azure/core/versions.tf` (remove AWS, keep azurerm)
- Update `azure/core/main.tf` (remove AWS module/resources, update paths)
- Update `azure/core/variables.tf` (remove AWS-specific vars)
- Update `azure/core/outputs.tf` (remove AWS conditional logic)

### 4. Move Labs to Root Level
- Move `terraform/aws/` → `aws/` (merge with new structure)
- Move `terraform/azure/` → `azure/` (merge with new structure)
- Update lab module references from `../../core` → `../core`

### 5. Update setup.py
- Keep good improvements (MongoDB notes, error handling, etc.)
- Update terraform_dir paths:
  - `terraform/core` → `aws/core` or `azure/core` based on cloud_provider
  - `terraform/{cloud}/lab*` → `{cloud}/lab*`
- Remove all complex provider file switching logic
- Remove Azure environment variable workarounds

### 6. Clean Up
- Remove entire `terraform/` directory
- Update any documentation references

### 7. Test Both AWS and Azure Paths
- Test AWS: `python setup.py` with cloud_provider=aws
- Test Azure: `python setup.py` with cloud_provider=azure

## Key Benefits
- ✅ **Complete isolation** - AWS and Azure never interact
- ✅ **No authentication conflicts** - Each environment is self-contained
- ✅ **Simpler setup.py** - Just change directory paths, no file manipulation
- ✅ **Cleaner structure** - No nested terraform/ directory
- ✅ **Self-contained modules** - Each cloud has its own module copies

## Current Working Directory
Currently in: `/Users/brenner/Public/quickstart-streaming-agents/terraform/core`

## Files Created/Modified So Far
- ✅ `aws/core/` - Complete AWS-only terraform environment
- ✅ `aws/core/modules/` - AWS modules copied and ready
- 🚧 Need to continue with Azure structure creation

## Context for Next Steps
The AWS core is fully cleaned up and ready. Need to:
1. Create Azure equivalent (remove AWS refs, update paths)
2. Move existing lab directories up to root level
3. Update setup.py path logic
4. Test both environments work independently