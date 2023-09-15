data "aws_secretsmanager_secret" "account_ids" {
  name = "aws_account_ids"
}

data "aws_secretsmanager_secret_version" "account_ids" {
  secret_id = data.aws_secretsmanager_secret.account_ids.id
}

locals {
  aws_account_ids          = jsondecode(data.aws_secretsmanager_secret_version.account_ids.secret_string)
  aws_account_id           = local.aws_account_ids["${var.env}-${var.envtype2}${var.subenv}"]
  live_mgmt_aws_account_id = jsondecode(data.aws_secretsmanager_secret_version.account_ids.secret_string)["live-mgmt"]
}

data "terraform_remote_state" "eks" {
  backend = "s3"

  config = {
    bucket = var.terraform_state_s3_bucket
    key    = "eks/terraform.tfstate"
    region = var.aws_region
  }
}

data "aws_secretsmanager_secret" "texas_infra" {
  name = "texas_infrastructure"
}

data "aws_secretsmanager_secret_version" "texas_infra" {
  secret_id = data.aws_secretsmanager_secret.texas_infra.id
}