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

variable "mongodb_username" {
  description = "MongoDB Atlas database user username (project-specific, NOT your Atlas account username). Create this in Atlas: Database Access -> Database Users -> Add New Database User. Example: 'confluent-user'"
  type        = string
  sensitive   = true
}

variable "mongodb_password" {
  description = "MongoDB Atlas database user password (for the database user created above, NOT your Atlas account password). Set when creating the database user."
  type        = string
  sensitive   = true
}
