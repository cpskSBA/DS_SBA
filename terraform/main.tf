data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

terraform {
  required_version = "~> 1.5"
  required_providers {
    aws = {
      version = "~> 5.0"
      source  = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region              = "us-east-1"
  allowed_account_ids = [local.account_ids[terraform.workspace]]
}

terraform {
  backend "s3" {
    bucket               = "sba-certify-terraform-remote-state"
    region               = "us-east-1"
    dynamodb_table       = "terraform-state-locktable"
    acl                  = "bucket-owner-full-control"
    key                  = "datahub-oppl.tfstate"
    workspace_key_prefix = "datahub-oppl"
  }
}
