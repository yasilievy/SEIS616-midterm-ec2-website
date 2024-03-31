#!/usr/bin/env python
from constructs import Construct
from cdktf import (
    App,
    Token,
    TerraformStack,
    TerraformOutput,
    NamedRemoteWorkspace,
    TerraformVariable,
    Fn
)

from imports.aws.provider import AwsProvider
from imports.aws.instance import Instance,InstanceNetworkInterface
from imports.aws.data_aws_vpc import DataAwsVpc
from imports.aws.network_interface import *
from imports.aws.subnet import Subnet
from imports.aws.vpc import Vpc
from imports.aws.security_group import *
from imports.aws.vpc_security_group_egress_rule import VpcSecurityGroupEgressRule
from imports.aws.vpc_security_group_ingress_rule import VpcSecurityGroupIngressRule
from imports.aws.data_aws_iam_policy_document import *

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)
        AwsProvider(self, "AWS", region="us-west-1")
        
        my_vpc = Vpc(self, "my_vpc",
            cidr_block="10.0.0.0/16",
            enable_dns_hostnames=True,
        )
        
        my_subnet = Subnet(self, "my_subnet",
            cidr_block="10.0.0.0/16",
            vpc_id=my_vpc.id
        )

        instance = Instance(self, "compute",
                            ami="ami-01456a894f71116f2",
                            instance_type="t2.micro",
                            user_data = "./configure.sh",
                            user_data_replace_on_change=True
                            )
        
        TerraformOutput(self, "public_ip",value=instance.public_ip)
        TerraformOutput(self, "public_dns",value=instance.public_dns)


app = App()
stack = MyStack(app, "aws_instance")

app.synth()

