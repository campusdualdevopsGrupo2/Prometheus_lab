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
    hosted_zone_id = 'Z06113313M7JJFJ9M7HM8'  # Reemplaza con tu zona hospedada
    
    try:
        # Obtener el ID de la instancia desde el evento
        instance_id = event['detail']['instance-id']
        logger.info(f"Obtenido ID de la instancia: {instance_id}")

        # Describir la instancia para obtener los tags
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        
        # Obtener los tags de la instancia
        tags = response['Reservations'][0]['Instances'][0]['Tags']
        logger.info(f"Tags de la instancia: {tags}")

        # Buscar el valor del tag DNS_NAME
        dns_name = next((tag['Value'] for tag in tags if tag['Key'] == 'DNS_NAME'), None)
        g2_tag = next((tag['Value'] for tag in tags if tag['Key'] == 'Grupo' and 'g2' in tag['Value']), None)
        
        if dns_name and g2_tag:
            logger.info(f"Tag 'DNS_NAME' encontrado: {dns_name}")
            logger.info(f"Tag 'g2' encontrado: {g2_tag}")

            # Listar todos los registros en la zona hospedada de Route 53
            logger.info(f"Obteniendo registros DNS de la zona hospedada {hosted_zone_id}...")
            record_sets = []
            paginator = route53_client.get_paginator('list_resource_record_sets')
            for page in paginator.paginate(HostedZoneId=hosted_zone_id):
                record_sets.extend(page['ResourceRecordSets'])

            # Filtrar los registros que contienen el DNS_NAME
            records_to_delete = [
                record for record in record_sets
                if dns_name in record['Name'] and record['Type'] == 'A'
            ]

            if records_to_delete:
                # Crear un batch de cambios para eliminar los registros
                change_batch = {
                    'Changes': [
                        {
                            'Action': 'DELETE',
                            'ResourceRecordSet': record
                        }
                        for record in records_to_delete
                    ]
                }

                # Aplicar el cambio en Route 53
                try:
                    logger.info("Aplicando cambios en Route 53...")
                    route53_client.change_resource_record_sets(
                        HostedZoneId=hosted_zone_id,
                        ChangeBatch=change_batch
                    )
                    logger.info(f"Se eliminaron los registros DNS que contienen '{dns_name}'.")
                    return {
                        'statusCode': 200,
                        'body': f"Registros DNS que contienen '{dns_name}' eliminados correctamente."
                    }
                except Exception as e:
                    logger.error(f"Error al aplicar el cambio en Route 53: {str(e)}")
                    return {
                        'statusCode': 500,
                        'body': f"Error al eliminar los registros DNS: {str(e)}"
                    }
            else:
                logger.info(f"No se encontraron registros DNS que contengan '{dns_name}'.")
                return {
                    'statusCode': 404,
                    'body': f"No se encontraron registros DNS que contengan '{dns_name}'."
                }

        else:
            logger.warning(f"No se encontró el tag 'DNS_NAME' para la instancia {instance_id}.")
            return {
                'statusCode': 404,
                'body': f"No se encontró el tag 'DNS_NAME' para la instancia {instance_id}."
            }
    except Exception as e:
        logger.error(f"Error procesando la función Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error al procesar el evento: {str(e)}"
        }
