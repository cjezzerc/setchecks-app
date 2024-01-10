data "aws_secretsmanager_secret" "vsmt_ontoserver_access" {
  name = "vsmt-ontoserver-access"
}

data "aws_secretsmanager_secret_version" "vsmt_ontoserver_access" {
  secret_id = data.aws_secretsmanager_secret.vsmt_ontoserver_access.id
}

data "aws_secretsmanager_secret" "aws_account_ids" {
  name = "aws_account_ids"
}

data "aws_secretsmanager_secret_version" "aws_account_ids" {
  secret_id = data.aws_secretsmanager_secret.aws_account_ids.id
}

locals {
  aws_account_id = jsondecode(data.aws_secretsmanager_secret_version.aws_account_ids.secret_string)["${var.texas_account}"]
  docdb_username = jsondecode(data.aws_secretsmanager_secret_version.vsmt_ontoserver_access.secret_string)["DOCUMENTDB_USERNAME"]
  docdb_password = jsondecode(data.aws_secretsmanager_secret_version.vsmt_ontoserver_access.secret_string)["DOCUMENTDB_PASSWORD"]
  tags = {
    Service     = var.service_name
  }
}

data "aws_eks_cluster" "eks" {
    name = "live-leks-cluster"
}

#####################################
# Data sources to get VPC and subnets
#####################################

data "aws_vpc" "cluster_vpc" {
    filter {
        name    = "tag:Name"
        values  = [
            "${var.regional_domain_name}"
        ]
    }
}

data "aws_subnets" "private_subnets" {
    filter {
        name   = "tag:Name"
        values = [
            "${var.regional_domain_name}-private-${var.aws_region}a",
            "${var.regional_domain_name}-private-${var.aws_region}b",
            "${var.regional_domain_name}-private-${var.aws_region}c"
        ] 
    }
}

data "aws_security_group" "eks-worker-sg" {
  name = "${var.name_prefix}-live-leks-cluster-sg"
}

data "aws_security_group" "openvpn_sg" {
  name = "${var.name_prefix}-openvpn-sg"
}