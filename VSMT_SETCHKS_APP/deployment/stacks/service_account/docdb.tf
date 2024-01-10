resource "aws_docdb_cluster" "docdb" {
  cluster_identifier      = "vsmt-docdb-cluster-${var.env}"
  engine_version          = "5.0.0"
  master_username         = local.docdb_username
  master_password         = local.docdb_password
  backup_retention_period = 7
  preferred_backup_window = "02:00-04:00"
  db_subnet_group_name    = aws_docdb_subnet_group.vsmt_subnet_group.name
  storage_encrypted       = true
  port                    = 27017
  vpc_security_group_ids  = [aws_security_group.elasticache_security_group.id]
  tags                    = local.tags
}

resource "aws_docdb_cluster_instance" "cluster_instances" {
  count              = 1
  identifier         = "vsmt-docdb-cluster-instance-${var.env}-${count.index}"
  cluster_identifier = aws_docdb_cluster.docdb.id
  instance_class     = "db.t3.medium"
  tags               = local.tags
}

resource "aws_docdb_subnet_group" "vsmt_subnet_group" {
  name       = "vsmt-subnet-group-${var.env}"
  subnet_ids = data.aws_subnets.private_subnets.ids
  tags       = local.tags
}