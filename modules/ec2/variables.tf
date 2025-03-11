variable "project_name" {
  type        = string
  description = "Nombre del proyecto"
  default     = "simple-worker-g2"
}

variable "environment" {
  type        = string
  description = "Ambiente (dev/prod)"
  default     = "dev"
}

variable "dns_name" {
  type        = string
   
}

variable "vpc_id" {
  type        = string
  description = "ID de la VPC"

}

variable "subnet_ids" {
  type        = string
  description = "IDs de las subnets privadas"

}




variable "volume_size" {
  type        = number
  description = "Tamaño del volumen EBS en GB"
  default     = 100
}
variable "private_key_path" {
  description = "Ruta al archivo de la clave privada SSH para acceder a las instancias EC2."
  type        = string
}

variable "public_key_path" {
  description = "Ruta al archivo de la clave pública SSH asociada a la clave privada para acceder a las instancias EC2."
  type        = string
}



variable "performance_mode" {
  description = "Modo de rendimiento del sistema de archivos EFS"
  type        = string
  default     = "generalPurpose"
}

variable "encrypted" {
  description = "Indica si el sistema de archivos EFS está encriptado"
  type        = bool
  default     = true
}
variable "tags" {
  description = "Mapa de etiquetas a asignar al sistema de archivos EFS"
  type        = map(string)
  default     = {}
}
variable "ami_id" {
  type        = string
}