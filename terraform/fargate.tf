variable "image_tag" {
  type = string
}

locals {
  container_environment = {
    sbdh_warehouse = "SBA_US-EAST-1_${upper(terraform.workspace)}_WAREHOUSE"
    sbdh_database  = "SBA_US-EAST-1_${upper(terraform.workspace)}_RAW_DB"
    sbdh_schema    = "DATA_HUB"
    sbdh_role      = "ACCOUNTADMIN"
  }
  container_secrets_parameterstore = {
    sbdh_user         = "account/snowflake/service_account_username"
    sbdh_password     = "account/snowflake/service_account_password"
    sbdh_account      = "account/snowflake/account_ID"
    sbdh_HUD_key      = "account/snowflake/HUDkey"
    sbdh_Congress_key = "account/snowflake/Congresskey"
  }
}

module "dashboard" {
  source  = "USSBA/easy-fargate-service/aws"
  version = "~> 11.0"

  # cloudwatch logging
  log_group_name              = "/ecs/${terraform.workspace}/${local.env.service_name}"
  log_group_retention_in_days = 90

  # access logs
  # note: bucket permission may need to be adjusted
  # https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-access-logs.html#access-logging-bucket-permissions
  alb_log_bucket_name = local.env.log_bucket
  alb_log_prefix      = "alb/${local.env.service_name}/${terraform.workspace}"

  family      = "${terraform.workspace}-${local.env.service_name}"
  task_cpu    = local.env.task_cpu_dashboard
  task_memory = local.env.task_memory_dashboard
  #come back to this
  task_policy_json       = data.aws_iam_policy_document.fargate.json
  enable_execute_command = true
  ipv6                   = true
  #alb_idle_timeout       = 60

  # Deployment
  enable_deployment_rollbacks        = true
  wait_for_steady_state              = true
  deployment_maximum_percent         = 200
  deployment_minimum_healthy_percent = 100

  # Scaling and health
  desired_capacity           = local.env.desired_capacity_dashboard
  min_capacity               = local.env.desired_capacity_dashboard
  max_capacity               = local.env.desired_capacity_dashboard
  scaling_metric             = local.env.scaling_metric
  scaling_threshold          = local.env.scaling_threshold
  scheduled_actions          = try(local.env.scheduled_actions, [])
  scheduled_actions_timezone = try(local.env.scheduled_actions_timezone, "UTC")
  #health_check_path          = local.env.health_check_path
  # Unhealthy threshold is set for 10 (default). This container takes 5
  # minutes to run its precompile asset task and does not respond to
  # health checks until this is complete.
  health_check_interval            = 60
  health_check_timeout             = 30
  health_check_healthy_threshold   = 2
  health_check_unhealthy_threshold = 10

  # networking
  service_fqdn       = local.service_fqdn
  hosted_zone_id     = data.aws_route53_zone.selected.zone_id
  public_subnet_ids  = data.aws_subnets.public.ids
  private_subnet_ids = data.aws_subnets.private.ids
  vpc_id             = data.aws_vpc.selected.id
  certificate_arn    = data.aws_acm_certificate.selected.arn

  # container(s)
  cluster_name   = data.aws_ecs_cluster.selected.cluster_name
  container_port = "8501"
  container_definitions = [
    {
      name         = "datahub-dashboard"
      image        = "${local.prefix_ecr}/${local.env.ecr_name}:${var.image_tag}"
      cpu          = 1024
      memory       = 3072
      environment  = [for k, v in local.container_environment : { name = k, value = v }]
      secrets      = [for k, v in local.container_secrets_parameterstore : { name = k, valueFrom = "${local.prefix_parameter_store}/${v}" }]
      portMappings = [{ containerPort = 8501 }]
    }
  ]
}

data "aws_iam_policy_document" "fargate" {
  statement {
    sid = "ServiceSecrets"
    actions = [
      "ssm:GetParameters",
      "ssm:GetParameter",
      "secretsmanager:GetSecretValue"
    ]
    resources = [
      "arn:aws:ssm:us-east-1:222484291001:parameter/account/snowflake/service_account_username",
      "arn:aws:ssm:us-east-1:222484291001:parameter/account/snowflake/service_account_password",
      "arn:aws:ssm:us-east-1:222484291001:parameter/account/snowflake/account_ID"
    ]
  }
  statement {
    sid = "S3Logs"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:List*",
      "s3:GetBucketLocation",
    ]
    resources = [
      "${data.aws_s3_bucket.logs.arn}",
      "${data.aws_s3_bucket.logs.arn}/*"
    ]
  }
}
