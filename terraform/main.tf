provider "aws" {
  region = var.aws_region
}

module "ec2" {
  source = "../modules/ec2"

  project_name         = var.project_name
  environment          = var.environment
  vpc_id              = var.vpc_id
  subnet_ids          = var.subnet_ids[0]
  private_key_path=var.private_key_path
  public_key_path=var.public_key_path
  ami_id= var.ami_id
  dns_name = var.dns_name
  #region=var.region
  depends_on = [ module.lambda ]
}

module "lambda" {
  source = "../modules/dns_lambda"

}
