import boto3

ec2 = boto3.client("ec2", region_name="ap-south-1")

response = ec2.describe_security_groups(
    GroupNames=["driftguard-web-sg"]
)

for sg in response["SecurityGroups"]:
    print("Security Group:", sg["GroupName"])
    print("Group ID:", sg["GroupId"])