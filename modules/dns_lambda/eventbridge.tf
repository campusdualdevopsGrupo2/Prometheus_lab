# 1. Crear la regla de EventBridge para cuando la instancia pase al estado 'running'
resource "aws_cloudwatch_event_rule" "ec2_instance_launch_rule" {
  name        = "EC2InstanceLaunchRule"
  description = "Regla para lanzar una Lambda cuando una instancia EC2 pasa al estado 'running'."
  event_pattern = jsonencode({
    source = ["aws.ec2"]
    detail-type = ["EC2 Instance State-change Notification"]
    detail = {
      state = ["running"]
    }
  })
  state = "ENABLED"
}

# 2. Crear los permisos para que EventBridge invoque la Lambda cuando la instancia esté 'running'
resource "aws_lambda_permission" "allow_eventbridge_invoke_launch" {
  statement_id  = "545646548646546847651684"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ec2_instance_launch_rule.arn
}

# 3. Asociar la Lambda con la regla de EventBridge para el estado 'running'
resource "aws_cloudwatch_event_target" "ec2_instance_target_launch" {
  rule      = aws_cloudwatch_event_rule.ec2_instance_launch_rule.name
  arn       = aws_lambda_function.lambda_function.arn
  target_id = "target_1"  # ID único para este destino
}

# 4. Crear la regla de EventBridge para cuando la instancia pase al estado 'stopped' o 'terminated'
resource "aws_cloudwatch_event_rule" "ec2_instance_state_change_rule" {
  name        = "EC2InstanceStateChangeRule"
  description = "Regla para lanzar una Lambda cuando una instancia EC2 pasa al estado 'stopped' o 'terminated'."
  event_pattern = jsonencode({
    source = ["aws.ec2"]
    detail-type = ["EC2 Instance State-change Notification"]
    detail = {
      state = ["stopped", "terminated"]
    }
  })
  state = "ENABLED"
}

# 5. Crear los permisos para que EventBridge invoque la Lambda cuando la instancia esté 'stopped' o 'terminated'
resource "aws_lambda_permission" "allow_eventbridge_invoke_state_change" {
  statement_id  = "545646548646546847651685"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function2.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ec2_instance_state_change_rule.arn
}

# 6. Asociar la Lambda con la regla de EventBridge para los estados 'stopped' o 'terminated'
resource "aws_cloudwatch_event_target" "ec2_instance_target_state_change" {
  rule      = aws_cloudwatch_event_rule.ec2_instance_state_change_rule.name
  arn       = aws_lambda_function.lambda_function2.arn
  target_id = "target_2"  # ID único para este destino
}
