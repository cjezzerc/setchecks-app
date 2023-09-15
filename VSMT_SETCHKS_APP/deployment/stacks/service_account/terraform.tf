terraform {
  backend "s3" {
    encrypt = true
    # Other parameters are defined at runtime as
    # they differ dependent on the environment used
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.13.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}