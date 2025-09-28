variable "region" {
  description = "The region in which the resources will be created."
  default     = "<location>"
}

variable "project_id" {
  description = "The project ID in which the resources will be created."
  default     = "<your-project-name>"
}

variable "project_number" {
  description = "The project ID in which the resources will be created."
  default     = "<your-project-id>"
}

variable "iap_allowed_principals" {
  type    = list(string)
  default = ["<your-principal>"]
}

variable "rotation_days" {
  type    = number
  default = 90
}
