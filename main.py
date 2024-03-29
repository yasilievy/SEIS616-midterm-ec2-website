#!/usr/bin/env python
from constructs import Construct
from cdktf import (
    App,
    Token,
    TerraformStack,
    TerraformOutput,
    RemoteBackend,
    NamedRemoteWorkspace,
    TerraformVariable,
    Fn
)

from cdktf_cdktf_provider_aws.aws.provider import AwsProvider
from cdktf_cdktf_provider_aws.aws.instance import Instance
from cdktf_cdktf_provider_aws.aws.data_aws_vpc import DataAwsVpc
from cdktf_cdktf_provider_aws.aws.network_interface import NetworkInterface, InstanceNetworkInterface
from cdktf_cdktf_provider_aws.aws.subnet import Subnet
from cdktf_cdktf_provider_aws.aws.vpc import Vpc
from cdktf_cdktf_provider_aws.aws.security_group import SecurityGroup
from cdktf_cdktf_provider_aws.aws.vpc_security_group_egress_rule import VpcSecurityGroupEgressRule
from cdktf_cdktf_provider_aws.aws.vpc_security_group_ingress_rule import VpcSecurityGroupIngressRule
from cdktf_cdktf_provider_aws.aws.data_aws_iam_policy_document import *

# from imports.aws.provider import AwsProvider
# from imports.aws.instance import Instance
# from imports.aws.data_aws_vpc import DataAwsVpc
# from imports.aws.network_interface import NetworkInterface, InstanceNetworkInterface
# from imports.aws.subnet import Subnet
# from imports.aws.vpc import Vpc
# from imports.aws.security_group import SecurityGroup
# from imports.aws.vpc_security_group_egress_rule import VpcSecurityGroupEgressRule
# from imports.aws.vpc_security_group_ingress_rule import VpcSecurityGroupIngressRule
# from imports.aws.data_aws_iam_policy_document import *

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        AwsProvider(self, "AWS", region="us-west-1")
        
        my_vpc = Vpc(self, "my_vpc",
            cidr_block="10.0.0.0/16",
            tags={
                "Name": "ec2-website"
            }
        )
        
        my_subnet = Subnet(self, "my_subnet",
            availability_zone="us-west-2a",
            cidr_block="10.0.0.0/16",
            tags={
                "Name": "ec2-website"
            },
            vpc_id=my_vpc.id
        )
        
        interface_network = NetworkInterface(self, "interface_network_one",
            private_ips=["172.16.10.100"],
            subnet_id=my_subnet.id,
            tags={
                "Name": "primary_network_interface"
            }
        )
        
        sg_one = SecurityGroup(self, "security-group-one",
            egress=[],
            ingress=[],
            name="sg",
            vpc_id=Token.as_string(my_vpc.id)
        )
        VpcSecurityGroupEgressRule(self, "allow_all_traffic_ipv4",
            cidr_ipv4="0.0.0.0/0",
            ip_protocol="-1",
            security_group_id=sg_one.id,
            from_port=0,
            to_port=0
        )
        
        VpcSecurityGroupIngressRule(self, "allow_tls_ipv4",
            cidr_ipv4="0.0.0.0/0",
            ip_protocol="tcp",
            security_group_id=sg_one.id,
            from_port=80,
            to_port=80
        )
        
        allow_access_from_another_account = DataAwsIamPolicyDocument(self, "allow_access_from_another_account",
            statement=[DataAwsIamPolicyDocumentStatement(
                actions=["s3:GetObject"],
                principals=[DataAwsIamPolicyDocumentStatementPrincipals(
                    identifiers=["123456789012"],
                    type="*"
                    )
                ],
                resources=[aws_s3_bucket.arn, "${" + aws_s3_bucket.arn + "}/*"]
                )
            ]
        )
        
        instance = Instance(self, "compute",
                            ami="ami-01456a894f71116f2",
                            instance_type="t2.micro",
                            network_interface=[InstanceNetworkInterface(
                                device_index=0,
                                network_interface_id=interface_network.id)],
                            vpc_security_group_ids=sg_one.id,
                            user_data = "configure.sh",
                            iam_instance_profile=allow_access_from_another_account.id
                            )
        
        TerraformOutput(self, "public_ip",value=instance.public_ip)
        # TerraformOutput(self, "arn", value=aws_s3_bucket.arn)
        # TerraformOutput(self, "bucket_domain_name", value=aws_s3_bucket.bucket_domain_name)
        # TerraformOutput(self, "bucket_regional_domain_name", value=aws_s3_bucket.bucket_regional_domain_name)

        


app = App()
stack = MyStack(app, "aws_instance")

# RemoteBackend(stack,
#               hostname='app.terraform.io',
#               organization='St Thomas Courses',
#               workspaces=NamedRemoteWorkspace('learn-cdktf')
#               )

app.synth()

