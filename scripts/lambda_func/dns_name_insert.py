import boto3
import logging

# Configuración del logger para Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Crear clientes de EC2 y Route 53
ec2_client = boto3.client('ec2')
route53_client = boto3.client('route53')

def lambda_handler(event, context):
    # Log inicial cuando se recibe el evento
    logger.info("Evento recibido: %s", event)
    
    # ID de la zona hospedada de Route 53 (reemplaza con tu zona)
    hosted_zone_id = 'Z06113313M7JJFJ9M7HM8'
    
    try:
        # Obtener el ID de la instancia desde el evento
        instance_id = event['detail']['instance-id']
        logger.info(f"Obtenido ID de la instancia: {instance_id}")

        # Describir la instancia para obtener los tags y la IP
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        
        # Obtener los tags de la instancia
        tags = response['Reservations'][0]['Instances'][0]['Tags']
        logger.info(f"Tags de la instancia: {tags}")

        # Buscar el valor de los tags 'DNS_NAME' y 'g2'
        dns_name = next((tag['Value'] for tag in tags if tag['Key'] == 'DNS_NAME'), None)
        g2_tag = next((tag['Value'] for tag in tags if tag['Key'] == 'g2'), None)
        
        # Verificar que ambos tags existen
        if dns_name and g2_tag:
            logger.info(f"Tag 'DNS_NAME' encontrado: {dns_name}")
            logger.info(f"Tag 'g2' encontrado: {g2_tag}")
            
            # Obtener la IP pública de la instancia (si existe)
            public_ip = response['Reservations'][0]['Instances'][0].get('PublicIpAddress', None)
            if public_ip:
                logger.info(f"IP pública de la instancia: {public_ip}")
                
                # Crear el registro A para la instancia en Route 53
                change_batch = {
                    'Changes': [
                        {
                            'Action': 'UPSERT',  # 'UPSERT' crea o actualiza el registro
                            'ResourceRecordSet': {
                                'Name': f"{dns_name}.campusdual.mkcampus.com",  # Nombre del subdominio
                                'Type': 'A',
                                'TTL': 100,  # Tiempo de vida del registro
                                'ResourceRecords': [{'Value': public_ip}]
                            }
                        }
                    ]
                }

                # Aplicar el cambio en Route 53
                try:
                    logger.info("Aplicando cambios en Route 53...")
                    route53_client.change_resource_record_sets(
                        HostedZoneId=hosted_zone_id,
                        ChangeBatch=change_batch
                    )
                    logger.info(f"Registro DNS {dns_name}.campusdual.mkcampus.com con IP {public_ip} añadido correctamente.")
                    return {
                        'statusCode': 200,
                        'body': f"Registro DNS {dns_name}.campusdual.mkcampus.com con IP {public_ip} añadido correctamente."
                    }
                except Exception as e:
                    logger.error(f"Error al aplicar el cambio en Route 53: {str(e)}")
                    return {
                        'statusCode': 500,
                        'body': f"Error al crear el registro DNS: {str(e)}"
                    }
            else:
                logger.warning(f"La instancia {instance_id} no tiene una IP pública.")
                return {
                    'statusCode': 400,
                    'body': f"La instancia {instance_id} no tiene una IP pública."
                }
        else:
            logger.warning(f"No se encontraron los tags 'DNS_NAME' y 'g2' para la instancia {instance_id}.")
            return {
                'statusCode': 404,
                'body': f"No se encontraron los tags 'DNS_NAME' y 'g2' para la instancia {instance_id}."
            }
    except Exception as e:
        logger.error(f"Error procesando la función Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error al procesar el evento: {str(e)}"
        }
