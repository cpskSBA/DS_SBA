locals {
  region       = data.aws_region.current.name
  account_id   = data.aws_caller_identity.current.account_id
  account_name = contains(["stg", "prod"], terraform.workspace) ? "upper" : "lower"
  account_ids = {
    demo = "997577316207"
    stg  = "222484291001"
    prod = "222484291001"
  }
  sns_alarms = {
    # green    = "arn:aws:sns:us-east-1:502235151991:alarm-green"
    # yellow   = "arn:aws:sns:us-east-1:502235151991:alarm-yellow"
    # red      = "arn:aws:sns:us-east-1:502235151991:alarm-red"
    # security = "arn:aws:sns:us-east-1:502235151991:alarm-security"
    green    = data.aws_sns_topic.alerts["green"].arn
    yellow   = data.aws_sns_topic.alerts["yellow"].arn
    red      = data.aws_sns_topic.alerts["red"].arn
    security = data.aws_sns_topic.alerts["security"].arn
  }
  all = {
    default = {
      service_name          = "oppl"
      ecr_name              = "certify/datahub-dashboard"
      dashboard_port        = "8501"
      task_cpu_dashboard    = "4096"
      task_memory_dashboard = "10240"
      log_bucket            = "${local.account_id}-us-east-1-logs"

      desired_capacity_dashboard    = 1
      min_container_count_dashboard = 1
      max_container_count_dashboard = 1
      scaling_metric                = "memory"
      scaling_threshold             = "75"
    }
    demo = {
      domain_name    = "demo.sba-one.net"
      cert_domain    = "sba-one.net"
      max_sba_issuer = "demo-certify-sba-gov"
      #oai_id               = "E1PVFJGLUVYCEO"
    }
    stg = {
      domain_name = "stg.certify.sba.gov"
      cert_domain = "stg.certify.sba.gov"
      #oai_id               = "E13BTMXKQCJ8EC"

      # MAX
      max_saml_url           = "https://login.max.gov/idp/profile/SAML2/Redirect/SSO"
      max_password_reset_url = "https://max.gov/maxportal/resetPasswordForm.action"
      max_sba_issuer         = "staging-certify.sba-gov"

      desired_capacity_rails    = 2
      min_container_count_rails = 2
      max_container_count_rails = 2
    }
    prod = {
      domain_name = "certify.sba.gov"
      cert_domain = "certify.sba.gov"
      #oai_id               = "E1HEQ3JCZ916O8"

      desired_capacity_dashboard    = 2
      min_container_count_dashboard = 2
      max_container_count_dashboard = 6

      # MAX
      max_saml_url           = "https://login.max.gov/idp/profile/SAML2/Redirect/SSO"
      max_password_reset_url = "https://max.gov/maxportal/resetPasswordForm.action"
      max_sba_issuer         = "certify-sba-gov"
    }
  }
  # Condense all config into a single `local.env.*`
  env = merge(local.all.default, try(local.all[terraform.workspace], {}))

  service_fqdn = "${local.env.service_name}.${local.env.domain_name}"

  # Convenience prefixes for AWS Resources
  prefix_bucket          = "arn:aws:s3:::"
  prefix_ecr             = "222484291001.dkr.ecr.${local.region}.amazonaws.com"
  prefix_parameter_store = "arn:aws:ssm:${local.region}:${local.account_id}:parameter"
}