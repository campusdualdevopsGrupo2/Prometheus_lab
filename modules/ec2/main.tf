resource "aws_key_pair" "key" {
  key_name   = "prometheus-key-g2"
  public_key = file(var.public_key_path)  # Ruta de tu clave pública en tu máquina local
}
data "aws_security_group" "default" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  filter {
    name   = "group-name"
    values = ["default"]
  }
}

resource "aws_instance" "ec2_node" {
  count           = 1  # Número de instancias EC2 que deseas lanzar
  #ami             = "ami-091f18e98bc129c4e" # Ubuntu 24 ami londres
  ami             = var.ami_id
  instance_type   = "t3.xlarge"
  subnet_id       = var.subnet_ids[(count.index % 3)]
  key_name        = aws_key_pair.key.key_name
  disable_api_stop = false
  

  # Seguridad
  vpc_security_group_ids = [aws_security_group.prometheus.id,data.aws_security_group.default.id]
  root_block_device {
    volume_size = 30  # Tamaño en GB del volumen raíz (aumentado a 50 GB en este ejemplo)
    volume_type = "gp2"  # Tipo de volumen (general purpose SSD)
    delete_on_termination = true  # El volumen raíz se elimina cuando la instancia se termina
  }

  tags = {
    Name = "Grupo2-prometheus-instance-${var.project_name}-${var.environment}-es-${count.index + 1}",
    Grupo="g2"
  }


  # Provisionar la instancia para montar el EFS
  provisioner "remote-exec" {
    inline = [
      # Instalar dependencias
      "sudo apt-get update -y",
      "sudo apt-get install -y nfs-common",
      
      # Montar EFS
      "sudo mkdir -p /mnt/efs",
      "sudo mount -t nfs4  fs-09f3adbae659e7e88.efs.eu-west-3.amazonaws.com:/ /mnt/efs",

      # Configuración persistente en fstab para asegurar el montaje después de reinicios
      "echo 'fs-09f3adbae659e7e88.efs.eu-west-3.amazonaws.com:/ /mnt/efs nfs4 defaults 0 0' | sudo tee -a /etc/fstab", 

      # Permisos a las carpetas donde se monta la unidad efs
      "sudo chown -R 1000:1000 /mnt/efs/",
      "sudo chmod -R 777 /mnt/efs/"
     
    ]
    connection {
      type        = "ssh"
      user        = "ubuntu"  # Usa "ec2-user" para AMIs de Amazon Linux, "ubuntu" para AMIs de Ubuntu
      private_key = file(var.private_key_path)  # Ruta a tu clave privada en tu máquina local
      host        = self.public_ip  # La IP pública de la instancia
    }
  }
}


resource "null_resource" "update_hosts_ini1" {
  provisioner "local-exec" {
    #command = "pwd"
    command = "echo [webservers] > ../modules/ec2/ansible/hosts.ini "
     }
  # Usar triggers para forzar la ejecución del recurso
  triggers = {
    always_run = "${timestamp()}"  # Usamos timestamp como valor cambiante
  }
}

resource "null_resource" "update_hosts_ini2" {
  provisioner "local-exec" {
    command = <<-EOT
      echo "${join("\n", [for ip in aws_instance.ec2_node[*].public_ip : "${ip} ansible_user=ubuntu ansible_ssh_private_key_file=../my-ec2-key "]) }" >> ../modules/ec2/ansible/hosts.ini && echo "algo"
      echo "listo"
    EOT
  }

  triggers = {
    always_run = "${timestamp()}"
  }

  depends_on = [
    null_resource.update_hosts_ini1,
    aws_instance.ec2_node
  ]
}



resource "null_resource" "provisioner1" {
  provisioner "local-exec" {

    command = "export ANSIBLE_CONFIG=../modules/ec2/ansible/ansible.cfg && ansible-playbook -i ../modules/ec2/ansible/hosts.ini ../modules/ec2/ansible/install.yml"
  }
  #Usar triggers para forzar la ejecución del recurso
  triggers = {
    #always_run = join(",", aws_instance.ec2_node[*].id) 
    always_run = "${timestamp()}"
  }
 
  depends_on = [null_resource.update_hosts_ini2]
}
resource "null_resource" "provisioner2" {
  provisioner "local-exec" {

    command = "export ANSIBLE_CONFIG=../modules/ec2/ansible/ansible.cfg && ansible-playbook -i ../modules/ec2/ansible/hosts.ini ../modules/ec2/ansible/install2.yml"
  }
  #Usar triggers para forzar la ejecución del recurso
  triggers = {
    #always_run = join(",", aws_instance.ec2_node[*].id) 
    always_run = "${timestamp()}"
  }
  
  depends_on = [null_resource.provisioner1]
}

