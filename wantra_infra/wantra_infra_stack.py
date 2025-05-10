from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2
)
from constructs import Construct

class WantraInfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC básica
        vpc = ec2.Vpc(self, "WantraVPC", max_azs=2)

        # Security Group para la instancia
        sg = ec2.SecurityGroup(
            self, "WantraSG",
            vpc=vpc,
            description="Allow SSH and HTTP",
            allow_all_outbound=True
        )
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "SSH")
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "HTTP")

        # Key Pair ya creado manualmente (o puedes automatizarlo luego)
        key_name = "wantra-key"

        user_data_script = ec2.UserData.for_linux()
        user_data_script.add_commands(
            "yum update -y",
            "amazon-linux-extras enable docker",
            "yum install -y docker",
            "systemctl start docker",
            "usermod -a -G docker ec2-user",
            "chkconfig docker on"
        )

        # EC2 con Amazon Linux 2 (ARM64)
        instance = ec2.Instance(
            self, "WantraInstance",
            instance_type=ec2.InstanceType("t4g.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(
                cpu_type=ec2.AmazonLinuxCpuType.ARM_64
            ),
            vpc=vpc,
            security_group=sg,
            key_name=key_name
            user_data=user_data_script
        )

        # Imprime la IP para usarla con Kamal
        self.instance_public_ip = instance.instance_public_ip
