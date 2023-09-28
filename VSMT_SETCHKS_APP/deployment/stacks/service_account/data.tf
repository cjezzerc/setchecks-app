data "aws_secretsmanager_secret" "vsmt_ontoserver_access" {
  name = "vsmt-ontoserver-access"
}

data "aws_secretsmanager_secret_version" "vsmt_ontoserver_access" {
  secret_id = data.aws_secretsmanager_secret.vsmt_ontoserver_access.id
}

locals {
  aws_account_id = jsondecode(data.aws_secretsmanager_secret_version.vsmt_ontoserver_access.secret_string)["nonprod_account_id"]
  docdb_username = jsondecode(data.aws_secretsmanager_secret_version.vsmt_ontoserver_access.secret_string)["DOCUMENTDB_USERNAME"]
  docdb_password = jsondecode(data.aws_secretsmanager_secret_version.vsmt_ontoserver_access.secret_string)["DOCUMENTDB_PASSWORD"]
  tags = {
    Service     = var.service_name
    Environment = var.environment_tag
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
            "${var.envtype2}${var.subenv}.${var.texas_domain}"
        ]
    }
}

data "aws_subnets" "private_subnets" {
    filter {
        name   = "tag:Name"
        values = [
            "${var.envtype2}${var.subenv}.${var.texas_domain}-private-${var.aws_region}a",
            "${var.envtype2}${var.subenv}.${var.texas_domain}-private-${var.aws_region}b",
            "${var.envtype2}${var.subenv}.${var.texas_domain}-private-${var.aws_region}c"
        ] 
    }
}

data "aws_security_group" "eks-worker-sg" {
  name = "${var.name_prefix}-live-leks-cluster-sg"
}