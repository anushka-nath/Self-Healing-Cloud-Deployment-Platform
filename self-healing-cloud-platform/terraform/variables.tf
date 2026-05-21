# AWS region for all resources.
variable "aws_region" {
  description = "AWS region where infrastructure will be provisioned."
  type        = string
  default     = "ap-south-1"
}

# Instance size (kept free-tier friendly where possible).
variable "instance_type" {
  description = "EC2 instance type for the platform node."
  type        = string
  default     = "t2.micro"
}

# Human-readable name for the compute node.
variable "instance_name" {
  description = "Name tag assigned to the EC2 instance."
  type        = string
  default     = "self-healing-platform-node"
}

# Optional key pair for SSH access.
variable "key_pair_name" {
  description = "Optional existing AWS key pair name for SSH access."
  type        = string
  default     = ""
}

# CIDR that is allowed to access SSH on port 22.
variable "allowed_ssh_cidr" {
  description = "CIDR block allowed for SSH."
  type        = string
  default     = "0.0.0.0/0"
}

# CIDR that is allowed to access HTTP on port 80.
variable "allowed_http_cidr" {
  description = "CIDR block allowed for HTTP traffic."
  type        = string
  default     = "0.0.0.0/0"
}

# CIDR that is allowed to access app port 5000.
variable "allowed_app_cidr" {
  description = "CIDR block allowed for Flask app port 5000."
  type        = string
  default     = "0.0.0.0/0"
}

# Additional tags for compliance or cost visibility.
variable "additional_tags" {
  description = "Additional tags merged into all Terraform-managed resources."
  type        = map(string)
  default     = {}
}
