import argparse
import boto3

REGION = "ap-south-1"
SECURITY_GROUP_NAME = "driftguard-web-sg"


def remove_rule(rule):
    ec2 = boto3.client("ec2", region_name=REGION)

    response = ec2.describe_security_groups(
        Filters=[
            {
                "Name": "group-name",
                "Values": [SECURITY_GROUP_NAME]
            }
        ]
    )

    security_group = response["SecurityGroups"][0]

    permission = {
        "IpProtocol": rule["protocol"],
        "FromPort": rule["from_port"],
        "ToPort": rule["to_port"],
        "IpRanges": [
            {
                "CidrIp": rule["cidr"]
            }
        ]
    }

    print("\n========================================")
    print("       DRIFTGUARD REMEDIATION")
    print("========================================")

    print(f"Resource : {SECURITY_GROUP_NAME}")
    print(f"Protocol : {rule['protocol']}")
    print(f"Port     : {rule['from_port']}")
    print(f"Source   : {rule['cidr']}")

    ec2.revoke_security_group_ingress(
        GroupId=security_group["GroupId"],
        IpPermissions=[permission]
    )

    print("\n✅ Unauthorized rule removed successfully.")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--cidr", required=True)

    args = parser.parse_args()

    rule = {
        "protocol": "tcp",
        "from_port": 22,
        "to_port": 22,
        "cidr": args.cidr
    }

    if not args.approve:
        print("⏳ APPROVAL REQUIRED")
        print("No AWS changes will be made.")
        print(f"\nPlanned removal: SSH 22 → {args.cidr}")
        print("\nUse --approve to authorize remediation.")
        return

    remove_rule(rule)


if __name__ == "__main__":
    main()