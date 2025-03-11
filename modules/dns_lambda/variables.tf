# Variables de entrada
variable "role_name" {
  type        = string
  default     = "lambda_execution_role_stb"
}

variable "policy_name" {
  type        = string
  default     = "lambda_policy_stb"
}

variable "allow_lambda_policy" {
  type        = string
  default     = "../modules/dns_lambda/role_lambda_allow.json"  # Ruta de la política de confianza
}

variable "policy_file" {
  type        = string
  default     = "../modules/dns_lambda/lambda_policy.json"  # Ruta del archivo de la política
}

variable "lambda_name" {
  type        = string
  default     = "dns_name_insert_stb"
}

variable "lambda_zip_file" {
  type        = string
  description = "Path to the Lambda deployment zip file"
  default     = "../scripts/lambda_func/lambda_function.zip"  # Ruta del archivo ZIP de la Lambda
}
variable "lambda_name2" {
  type        = string
  default     = "dns_name_delete_stb"
}

variable "lambda_zip_file2" {
  type        = string
  description = "Path to the Lambda deployment zip file"
  default     = "../scripts/lambda_func/lambda_function_delete.zip"  # Ruta del archivo ZIP de la Lambda
}
