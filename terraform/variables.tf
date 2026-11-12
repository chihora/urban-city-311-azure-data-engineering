
variable "pg_password" {
  description = "Administrator password for Azure PostgreSQL"
  type        = string
  sensitive   = true
}

variable "username" {
  description = "Administrator username for Azure PostgreSQL"
  type        = string
  default     = "adminadmin"
}
