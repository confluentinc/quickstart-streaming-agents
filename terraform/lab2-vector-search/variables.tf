variable "mongodb_connection_string" {
  description = "MongoDB connection string for vector database (leave empty to use cloud-specific default)"
  type        = string
  sensitive   = true
  default     = ""
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

variable "mongodb_username" {
  description = "MongoDB Atlas database user username (leave empty to use cloud-specific default)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "mongodb_password" {
  description = "MongoDB Atlas database user password (leave empty to use cloud-specific default)"
  type        = string
  sensitive   = true
  default     = ""
}
