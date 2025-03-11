variable "aws_region" {
  type        = string
  description = "Región de AWS"
  #default     = "eu-west-2"
}

variable "dns_name" {
  type        = string
   
}


variable "project_name" {
  type        = string
  description = "Nombre del proyecto"
  default     = "Prometheus"
  #default     = "simple-worker-g2"
}

variable "environment" {
  type        = string
  description = "Ambiente (dev/prod)"
  default     = "dev"
}

variable "vpc_id" {
  type        = string
  description = "ID de la VPC"
   #default     = "vpc-0c9f03551cb17af5d"
   default= "vpc-01c097d1d9b73fc50"
}

variable "subnet_ids" {
  type        = list(string)
  description = "IDs de las subnets privadas"
  #default     = ["subnet-0399f98a4db137765", "subnet-0b0842bc836a4b6cb", "subnet-0eb5d5076276d2346"]
  default=["subnet-0ea0184c208a85591","subnet-0f55161504b88d62b","subnet-0bcc525fc6ecfc2a2"]
}



variable "username"{
  type=string
  sensitive=true
}

variable "password"{
  type=string
  sensitive=true
}
variable "private_key_path" {
  description = "Ruta al archivo de la clave privada SSH para acceder a las instancias EC2."
  type        = string
}

variable "public_key_path" {
  description = "Ruta al archivo de la clave pública SSH asociada a la clave privada para acceder a las instancias EC2."
  type        = string
}
variable "ami_id" {
  type        = string
}


variable "public_subnet" {
  type = string
}