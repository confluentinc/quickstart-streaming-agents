variable "cloud_region" {
  description = "AWS region for deployment"
  type        = string
}

variable "mongodb_connection_string" {
  description = "MongoDB connection string for vector database"
  type        = string
  sensitive   = true
  default     = "mongodb+srv://cluster0.c79vrkg.mongodb.net/"
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
  default     = "workshop-user"
}

variable "mongodb_password" {
  description = "MongoDB Atlas database user password (for the database user created above, NOT your Atlas account password). Set when creating the database user."
  type        = string
  sensitive   = true
  default     = "xr6PvJl9xZz1uoKa"
}

variable "workshop_mode" {
  description = "Enable workshop mode (uses pre-populated MongoDB database)"
  type        = bool
  default     = false
}
