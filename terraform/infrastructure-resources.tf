# vpc
data "aws_vpc" "selected" {
  tags = {
    Name = "${terraform.workspace}-vpc"
  }
}

# subnet ids
data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
  filter {
    name = "tag:Name"
    values = [
      "${terraform.workspace}-private-subnet-*"
    ]
  }
}
data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
  filter {
    name = "tag:Name"
    values = [
      "${terraform.workspace}-public-subnet-*"
    ]
  }
}

## hosted zone
data "aws_route53_zone" "selected" {
  name = "${local.env.domain_name}."
}

## acm
data "aws_acm_certificate" "selected" {
  domain      = local.env.cert_domain
  statuses    = ["ISSUED"]
  most_recent = true
}

data "aws_ssm_parameter" "origin_token" {
  name            = "/${terraform.workspace}/waf/x-ussba-origin-token"
  with_decryption = true
}


## ecs cluster
data "aws_ecs_cluster" "selected" {
  cluster_name = terraform.workspace
}

data "aws_sns_topic" "alerts" {
  for_each = toset(["green", "yellow", "red", "security"])
  name     = "${local.account_name}-teams-${each.value}-notifications"
}

data "aws_s3_bucket" "logs" {
  bucket = "${local.account_ids[terraform.workspace]}-${local.region}-logs"
}