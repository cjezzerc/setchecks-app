####################################################################################
# !!!!!! L I V E !!!!!!!!!
####################################################################################
env            = "live"    # dev, test or live
envdomain      = "texasplatform"
envtype1       = "k8s"      # k8s or mgmt
envtype2       = "lk8s"     # lk8s or mgmt
subenv         = "-prod" # empty, '-prod' or '-prod' - note the hyphens!

# TODO replace billing code and environment tag with below
regional_domain_name = "lk8s-prod.texasplatform.uk"
domain_name          = "k8s-prod.texasplatform.uk"

####################################################################################
# TERRAFORM COMMON
####################################################################################
# TODO what domain name should we use
billing_code_tag                      = "k8s-prod.texasplatform.uk"
environment_tag                       = "lk8s-prod.texasplatform.uk"
terraform_service_state_s3_bucket     = "nhsd-texasplatform-terraform-service-state-store-lk8s-prod"
