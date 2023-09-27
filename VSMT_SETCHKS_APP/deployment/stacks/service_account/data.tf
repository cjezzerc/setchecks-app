data "aws_secretsmanager_secret" "vsmt_ontoserver_access" {
  name = "vsmt-ontoserver-access"
}

data "aws_secretsmanager_secret_version" "vsmt_ontoserver_access" {
  secret_id = data.aws_secretsmanager_secret.vsmt_ontoserver_access.id
}

locals {
  aws_account_id = jsondecode(data.aws_secretsmanager_secret_version.vsmt_ontoserver_access.secret_string)["nonprod_account_id"]
}

data "aws_eks_cluster" "eks" {
    name = "live-leks-cluster"
}