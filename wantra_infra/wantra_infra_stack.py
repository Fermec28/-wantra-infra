from aws_cdk import (
    # Duration,
    Stack,
    aws_iam as iam,
    aws_ec2 as ec2,
    CfnOutput,
    Tags
)

from constructs import Construct

class WantraInfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC básica
        vpc = ec2.Vpc(
            self, 
            "WantraVPC",
            cidr="10.100.0.0/16", 
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC
                ),
            ],
            restrict_default_security_group=False
        )

        # Security Group para la instancia
        sg = ec2.SecurityGroup(
            self, "WantraSG",
            vpc=vpc,
            description="Allow SSH and HTTP",
            allow_all_outbound=True
        )
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "SSH")
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "HTTP")
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "HTTPS")

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
        # IAM Role para la instancia
        instance_role = iam.Role(
            self, "WantraInstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
            ]
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
            key_name=key_name,
            user_data=user_data_script,
            role=instance_role,
            associate_public_ip_address=True
        )
        CfnOutput(self, "EC2PublicIP", value=instance.instance.attr_public_ip)
        instance.connections.allow_from(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))

        instance.connections.allow_from(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))
        Tags.of(instance).add("Project", "Wantra")
        # Imprime la IP para usarla con Kamal

