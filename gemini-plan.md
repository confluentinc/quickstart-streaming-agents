# Terraform Simplification and Modularization - Final Plan

This document outlines the refactoring of the existing Terraform configuration into a modular, reusable, and scalable architecture.

## 1. High-Level Goals

- **Simplify Terraform:** Break down the monolithic configuration into smaller, manageable modules.
- **Support Multiple Labs:** Enable the easy addition of new labs, each with its own specific resources.
- **Shared Common Environment:** Use a single, common Confluent environment for all labs to reduce costs and complexity.
- **Independent Deployments:** Allow each lab to be deployed and destroyed independently.

## 2. Final Architecture

The new architecture is based on a separation of concerns between the core infrastructure, lab-specific resources, and cloud-provider-specific components.

### Directory Structure

```
/Users/brenner/PycharmProjects/quickstart-streaming-agents/
├── terraform/
│   ├── core/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── labs/
│   │   └── lab1-streaming-agents/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       ├── outputs.tf
│   │       └── data-gen/
│   ├── modules/
│   │   ├── aws-ai/
│   │   │   ├── main.tf
│   │   │   └── variables.tf
│   │   └── azure-ai/
│   │       ├── main.tf
│   │       └── variables.tf
│   └── providers.tf
└── gemini-plan.md
```

## 3. Execution Summary

This plan has been executed. The following changes were made:

- **Created New Directory Structure:** The directories `terraform/core`, `terraform/labs/lab1-streaming-agents`, `terraform/modules/aws-ai`, and `terraform/modules/azure-ai` were created.

- **Created a Unified `providers.tf`:** A single `providers.tf` file was created in the `terraform` directory to handle both AWS and Azure providers, replacing the previous system of using `.disabled` files.

- **Created the `core` Module:** The common infrastructure resources were moved from the root `confluent.tf` into `terraform/core/main.tf`. The `variables.tf` and `outputs.tf` files were also created for the core module.

- **Created the `lab1-streaming-agents` Lab Configuration:** A `main.tf` file was created in `terraform/labs/lab1-streaming-agents` that instantiates the `core` module. Lab-specific resources and outputs were moved into this directory.

- **Moved `data-gen` Directory:** The `data-gen` directory was moved to `terraform/labs/lab1-streaming-agents/`.

- **Created Cloud-Specific AI Modules:** Placeholder files for the `aws-ai` and `azure-ai` modules were created. These will be used to handle cloud-specific Flink connection logic.

- **Cleaned Up Root Directory:** The redundant `confluent.tf`, `outputs.tf`, `variables.tf`, `providers-aws.tf.disabled`, and `providers-azure.tf.disabled` files were deleted from the root `terraform` directory.

This completes the refactoring of the Terraform configuration into a modular and extensible architecture. The project is now ready for the addition of new labs and features.