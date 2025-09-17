variable "prefix" {
  description = "Resource name prefix"
  type        = string
  default     = "streaming-agents"
}

variable "cloud_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "MONGODB_CONNECTION_STRING" {
  description = "MongoDB connection string for vector database"
  type        = string
  sensitive   = true
}

variable "MONGODB_DATABASE" {
  description = "MongoDB database name for vector storage"
  type        = string
  default     = "vector_search"
}

variable "MONGODB_COLLECTION" {
  description = "MongoDB collection name for document vectors"
  type        = string
  default     = "documents"
}

variable "MONGODB_INDEX_NAME" {
  description = "MongoDB vector search index name"
  type        = string
  default     = "vector_index"
}