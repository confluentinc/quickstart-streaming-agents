# Lab 2: RAG Pipeline Using Vector Search

In this lab, we'll create a Retrieval-Augmented Generation (RAG) pipeline using Confluent Cloud's Apache Flink vector search capabilities. The pipeline processes documents, creates embeddings, and enables semantic search to power intelligent responses through retrieval of relevant context.

![Architecture Diagram](../assets/arch.png)

## Architecture Overview

This lab implements a complete RAG pipeline with the following components:

1. **Document Ingestion**: Raw documents are ingested into a Kafka topic
2. **Text Chunking & Embedding**: Documents are split into chunks and converted to vector embeddings
3. **Vector Storage**: Embeddings are stored in MongoDB for efficient similarity search
4. **Query Processing**: User queries are embedded and used for vector search
5. **Response Generation**: Retrieved context is used to generate intelligent responses

## Prerequisites

- Core Terraform infrastructure deployed (from `/terraform/core/`)
- MongoDB Atlas cluster or compatible MongoDB instance with vector search enabled
- Either AWS or Azure cloud provider configured

## Deployment

### Step 1: Configure MongoDB

Set up your MongoDB Atlas cluster with vector search capabilities. You'll need:
- Connection string
- Database and collection names
- Vector search index

### Step 2: Deploy Terraform Infrastructure

Navigate to your chosen cloud provider directory:

```bash
# For AWS
cd terraform/aws/lab2-vector-search

# For Azure
cd terraform/azure/lab2-vector-search
```

Update `terraform.tfvars` with your MongoDB connection details:

```hcl
MONGODB_CONNECTION_STRING = "mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
MONGODB_DATABASE = "vector_search"
MONGODB_COLLECTION = "documents"
MONGODB_INDEX_NAME = "vector_index"
```

Deploy the infrastructure:

```bash
terraform init
terraform plan
terraform apply
```

### Step 3: Set Up MongoDB Connection

After Terraform deployment, run the MongoDB connection command from the generated `mongodb_commands.txt` file:

```bash
confluent flink connection create mongodb-connection \
  --cloud [AWS|AZURE] \
  --region [your-region] \
  --type mongodb \
  --endpoint [your-mongodb-connection-string] \
  --username mongodb_username \
  --password mongodb_password \
  --environment [your-environment-id]
```

### Step 4: Create Vector Search Tables

In the Confluent Cloud Flink SQL workspace, run the remaining table creation commands from `mongodb_commands.txt`:

1. `documents_vectordb` - MongoDB vector store table
2. `search_results` - Vector search results table
3. `search_results_response` - RAG response generation table

## Using the RAG Pipeline

### 1. Insert Documents

```sql
INSERT INTO documents VALUES
('doc1', 'This is a document about machine learning and artificial intelligence...'),
('doc2', 'Customer support guidelines for handling pricing objections...'),
('doc3', 'Product documentation for our enterprise software solution...');
```

### 2. Submit Queries

```sql
INSERT INTO queries VALUES
('How do I handle pricing objections from customers?'),
('What are the key features of machine learning?');
```

### 3. View Results

```sql
-- See search results
SELECT * FROM search_results;

-- See generated responses
SELECT query, response FROM search_results_response;
```

## Tables Created

- **documents**: Raw document input table
- **documents_embed**: Documents with chunked text and embeddings
- **queries**: User query input table
- **queries_embed**: Queries with embeddings
- **documents_vectordb**: MongoDB vector store (manual setup)
- **search_results**: Vector search results (manual setup)
- **search_results_response**: Generated RAG responses (manual setup)

## Architecture Benefits

- **Real-time Processing**: Stream processing enables immediate document indexing and query responses
- **Scalable Vector Search**: MongoDB Atlas provides enterprise-grade vector search capabilities
- **Contextual Responses**: RAG combines retrieval with generation for accurate, relevant answers
- **Cloud Native**: Fully managed services eliminate infrastructure overhead

## Next Steps

- Experiment with different chunk sizes and overlap parameters
- Tune vector search parameters for your use case
- Integrate with front-end applications via Kafka consumers
- Add document metadata for enhanced filtering and search

## Cleanup

To tear down the lab infrastructure:

```bash
terraform destroy
```

**Previous topic:** [Lab 1 - Tool Calling](../LAB1-Tool-Calling/LAB1.md)

**Next topic:** [Clean-up](../README.md#-cleanup)