import aws_cdk as core
import aws_cdk.assertions as assertions

from wantra_infra.wantra_infra_stack import WantraInfraStack

# example tests. To run these tests, uncomment this file along with the example
# resource in wantra_infra/wantra_infra_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = WantraInfraStack(app, "wantra-infra")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
