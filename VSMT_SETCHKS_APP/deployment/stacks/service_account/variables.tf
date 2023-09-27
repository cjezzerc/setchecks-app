##################################################################################
# INFRASTRUCTURE COMPONENT VERSION
##################################################################################
variable "version_tag" {
  description = "The infrastructure component version assigned by Texas development. The version MUST be incremented when changed <major version>.<minor version>"
  default     = "1.0"
}

##################################################################################
# AWS COMMON
##################################################################################
variable "aws_region" {
  description = "The AWS region"
}

#######
# TEXAS COMMON
#######
variable "envdomain" {
  description = "The environment-related part of the domain e.g. texasdev, texastest or texasplatform"
}

variable "env" {
  description = "dev, live, test"
}

variable "envtype1" {
  description = "The environment type used in AWS resource names (format 1) - either k8s or mgmt"
}

variable "envtype2" {
  description = "The environment type used in AWS resource names (format 2) - either lk8s or mgmt"
}

variable "subenv" {
  description = "The sub-environment where multiple enviroments are contained within a primary environment e.g. prod & nonprod within live. Must be either '', '-nonprod' or '-prod' - note the hyphens!"
}

#######
# TERRAFORM COMMON
#######

variable "terraform_service_state_s3_bucket" {
  description = "Name of the S3 bucket used to store the Terraform state"
}

variable "service_name" {
  default     = "vsmt"
  description = "Name of the kubernetes service"
}

variable "service_prefix" {
  default     = "vsmt"
  description = "Name of the kubernetes service"
}
