# resource "aws_elasticache_cluster" "replica" {
#   count = 1

#   cluster_id           = "tf-rep-group-1-${count.index}"
#   replication_group_id = aws_elasticache_replication_group.example.id
# }

resource "aws_security_group" "elasticache_security_group" {
  name        = "vsmt-cache-sg-${var.env}"
  description = "VSMT Elasticache Security Group"
  vpc_id      = data.aws_vpc.cluster_vpc.id

  ingress {
    description      = "ingress from vpc to ElastiCache"
    from_port        = 6379
    to_port          = 6379
    protocol         = "tcp"
    security_groups  = [data.aws_security_group.eks-worker-sg.id]
  }

  ingress {    
    description      = "ingress from vpc to DocumentDB"
    from_port        = 27017
    to_port          = 27017
    protocol         = "tcp"
    security_groups  = [data.aws_security_group.eks-worker-sg.id]
  }

    ingress {    
    description      = "ingress from vpn to Elasticache"
    from_port        = 6379
    to_port          = 6379
    protocol         = "tcp"
    security_groups  = [data.aws_security_group.openvpn_sg.id]
  }

    ingress {    
    description      = "ingress from vpn to DocumentDB"
    from_port        = 27017
    to_port          = 27017
    protocol         = "tcp"
    security_groups  = [data.aws_security_group.openvpn_sg.id]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = local.tags
}

resource "aws_elasticache_subnet_group" "elasticache_subnet_group" {
  name       = "vsmt-cache-subnet-group-${var.env}"
  subnet_ids = data.aws_subnets.private_subnets.ids
  tags       = local.tags
}

resource "aws_elasticache_parameter_group" "elasticache_parameter_group" {
  name   = "${var.service_name}-parameter-group-${var.env}"
  family = "redis7"
  tags = local.tags
}

resource "aws_elasticache_replication_group" "redis_replication_group" {
  automatic_failover_enabled  = false
  replication_group_id        = "vsmt-redis-replication-group-${var.env}"
  description                 = "example description"
  node_type                   = "cache.t3.micro"
  parameter_group_name        = aws_elasticache_parameter_group.elasticache_parameter_group.name
  port                        = 6379
  security_group_ids          = [aws_security_group.elasticache_security_group.id]
  at_rest_encryption_enabled  = true 
  transit_encryption_enabled  = true
  subnet_group_name           = aws_elasticache_subnet_group.elasticache_subnet_group.name
  engine_version              = "7.0"
  tags                        = {Service = "vsmt"}
}