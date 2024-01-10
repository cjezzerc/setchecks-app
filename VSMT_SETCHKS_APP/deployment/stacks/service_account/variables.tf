##################################################################################
# AWS COMMON
##################################################################################
variable "aws_region" {
  description = "The AWS region"
}

#######
# TEXAS COMMON
#######

variable "env" {
  description = "dev, live, test"
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

variable "name_prefix" {
  description = "Prefix used for naming resources"
  type = string
  default = "live-lk8s-nonprod"  
}

variable "regional_domain_name" {
	description = "The top level Texas domain name"
	type = string
}

variable "texas_account" {
  description = "Name of Texas account"
}
