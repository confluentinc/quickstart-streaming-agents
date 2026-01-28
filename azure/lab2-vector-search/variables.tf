variable "mongodb_connection_string" {
  description = "MongoDB connection string for vector database (workshop mode uses hardcoded public readonly cluster)"
  type        = string
  sensitive   = true
  default     = "mongodb+srv://cluster0.xhgx1kr.mongodb.net/"
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
  description = "MongoDB Atlas database user username (workshop mode uses hardcoded public readonly user)"
  type        = string
  sensitive   = true
  default     = "public_readonly_user"
}

variable "mongodb_password" {
  description = "MongoDB Atlas database user password (workshop mode uses hardcoded public readonly password)"
  type        = string
  sensitive   = true
  default     = "sB948mVgIYqwUloX"
}

variable "workshop_mode" {
  description = "Enable workshop mode (uses pre-populated MongoDB database)"
  type        = bool
  default     = false
}
