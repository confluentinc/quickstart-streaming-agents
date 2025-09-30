# LAB2 Vector Search Configuration - Azure

# Basic Configuration
prefix = ""

# MongoDB Configuration for Vector Search
# REQUIRED: Replace with your MongoDB Atlas connection string for vector database
# In MongoDB Atlas CLI, get this string by running "atlas clusters connectionStrings describe <your-cluster-name>"
# Example format: "mongodb+srv://myclustername.bgvpswo.mongodb.net", no slash (/) at the end.
MONGODB_CONNECTION_STRING = ""

# MongoDB Database and Collection Settings
MONGODB_DATABASE   = "vector_search"
MONGODB_COLLECTION = "documents"
MONGODB_INDEX_NAME = "vector_index"

# MongoDB Authentication
# REQUIRED: Replace with your MongoDB Atlas credentials

# MongoDB Atlas database user username (project-specific, NOT your Atlas account username)
# Create this in Atlas: Database Access -> Database Users -> Add New Database User
# Example: 'confluent-user'
mongodb_username = ""

# MongoDB Atlas database user password (for the database user created above, NOT your Atlas account password)
# Set when creating the database user
mongodb_password = ""

# Finally, make sure to whitelist all IP addresses in MongoDB Atlas. From left sidebar, go to:
# Network Access -> IP Access List -> Add IP Address -> Allow Access from Anywhere (or enter 0.0.0.0 for Access List Entry).
