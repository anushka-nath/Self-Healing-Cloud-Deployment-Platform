# Terraform version and provider constraints for reproducible deployments.
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# AWS provider configuration.
provider "aws" {
  region = var.aws_region
}
