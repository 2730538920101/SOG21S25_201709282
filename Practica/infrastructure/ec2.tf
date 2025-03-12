resource "aws_key_pair" "PracticaSOG-key" {
  key_name   = "PracticaSOG"
  public_key = file(var.PATH_PUBLIC_KEYPAIR)
}

resource "aws_instance" "ec2_bastion" {
  ami                    = "ami-053b0d53c279acc90"
  instance_type          = "t2.micro"
  key_name               = aws_key_pair.PracticaSOG-key.key_name
  vpc_security_group_ids = [aws_security_group.PracticaSOG-sg.id]
  subnet_id              = aws_subnet.PublicS1.id
  depends_on             = [aws_db_instance.mysql-instance]
  
  provisioner "file" {
    source      = var.SQL_FILE_PATH
    destination = "/tmp/init.sql"

    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ubuntu" 
      private_key = file(var.PATH_KEYPAIR)
    }
  }

  provisioner "remote-exec" {
    inline = [
      "echo 'Updating the system...'",
      "sudo apt update -y",
      
      # Instalación de Docker
      "echo 'Installing Docker...'",
      "sudo apt install -y docker.io",
      "sudo systemctl enable docker",
      "sudo systemctl start docker",
      
      # Añadir el usuario ubuntu al grupo docker para evitar problemas de permisos
      "echo 'Adding ubuntu user to docker group...'",
      "sudo usermod -aG docker ubuntu",
      
      # Aplicar cambios de grupo sin necesidad de reiniciar la sesión
      "echo 'Applying group changes...'",
      "sudo chmod 666 /var/run/docker.sock",

      # Instalación de Docker Compose
      "echo 'Installing Docker Compose...'",
      "sudo curl -L \"https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)\" -o /usr/local/bin/docker-compose",
      "sudo chmod +x /usr/local/bin/docker-compose",
      
      # Instalación de MySQL
      "echo 'Installing MySQL...'",
      "sudo apt install mysql-client-core-8.0 -y",
      # Ejecutar el script SQL en la instancia RDS
      "echo 'Running MySQL script on RDS instance...'",
      "mysql -h ${aws_db_instance.mysql-instance.address} -u ${var.DATABASE_USER} -p${var.DATABASE_PASSWORD} ${var.DATABASE_NAME} < /tmp/init.sql"

      
    ]

    connection {
      type        = "ssh"
      host        = self.public_ip
      user        = "ubuntu"
      private_key = file(var.PATH_KEYPAIR)
    }
  }
}


resource "aws_security_group" "PracticaSOG-sg" {
  vpc_id = aws_vpc.PracticaSOG.id
  name   = "PracticaSOG-sg"
  egress = [
    {
      cidr_blocks      = ["0.0.0.0/0", ]
      description      = ""
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "-1"
      security_groups  = []
      self             = false
      to_port          = 0
    }
  ]
  ingress = [
    {
      cidr_blocks      = ["0.0.0.0/0", ]
      description      = ""
      from_port        = 22
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 22
    },
    {
      cidr_blocks      = ["0.0.0.0/0", ]
      description      = ""
      from_port        = 3306
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 3306
    },
    {
      cidr_blocks      = ["0.0.0.0/0", ]
      description      = ""
      from_port        = 8000
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 8000
    },
    {
      cidr_blocks      = ["0.0.0.0/0", ]
      description      = ""
      from_port        = 8888
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 8888
    }
  ]
}