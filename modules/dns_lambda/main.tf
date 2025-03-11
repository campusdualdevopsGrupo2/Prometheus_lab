# provider.tf - Configuración del proveedor AWS
provider "aws" {
  region  = var.aws_region
  profile= "superuser"
}

# Variable de entorno para la región y credenciales
variable "aws_region" {
  type        = string
  description = "AWS region"
  default= "eu-west-3"
}

# Crear el rol IAM para Lambda (con política de confianza)
resource "aws_iam_role" "lambda_execution_role" {
  name               = var.role_name
  assume_role_policy = file(var.allow_lambda_policy)

  tags = {
    Name = "lambda_execution_role",
    Grupo="g2"
  }
}

# Crear la política IAM para Lambda
resource "aws_iam_policy" "lambda_policy" {
  name        = var.policy_name
  policy      = file(var.policy_file)

  tags = {
    Name = "lambda_policy",
    Grupo="g2"
  }
}

# Adjuntar la política al rol IAM
resource "aws_iam_role_policy_attachment" "lambda_role_policy_attachment" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Crear la función Lambda
resource "aws_lambda_function" "lambda_function" {
  function_name = var.lambda_name
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "dns_name_insert.lambda_handler"
  filename      = var.lambda_zip_file
  source_code_hash = filebase64sha256(var.lambda_zip_file)

  tags = {
    Name = "dns_name_insert_stb",
    Grupo="g2"
  }
}


resource "aws_lambda_function" "lambda_function2" {
  function_name = var.lambda_name2
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "dns_name_delete.lambda_handler"
  filename      = var.lambda_zip_file2
  source_code_hash = filebase64sha256(var.lambda_zip_file2)

  tags = {
    Name = "dns_name_delete_stb",
    Grupo="g2"
  }
}
