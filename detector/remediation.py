import argparse
import boto3

REGION = "ap-south-1"
SECURITY_GROUP_NAME = "driftguard-web-sg"


def remove_rule(rule):

    ec2 = boto3.client(
        "ec2",
        region_name=REGION
    )

    response = ec2.describe_security_groups(
        Filters=[
            {
                "Name": "group-name",
                "Values": [SECURITY_GROUP_NAME]
            }
        ]
    )

    if not response["SecurityGroups"]:
        raise Exception(
            f"Security group '{SECURITY_GROUP_NAME}' not found"
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

    print()
    print("=" * 45)
    print("       DRIFTGUARD REMEDIATION")
    print("=" * 45)

    print(f"Resource : {SECURITY_GROUP_NAME}")
    print(f"Protocol : {rule['protocol']}")
    print(
        f"Port     : "
        f"{rule['from_port']}-{rule['to_port']}"
    )
    print(f"Source   : {rule['cidr']}")

    ec2.revoke_security_group_ingress(
        GroupId=security_group["GroupId"],
        IpPermissions=[permission]
    )

    print()
    print("SUCCESS: Unauthorized rule removed.")


def main():

    parser = argparse.ArgumentParser(
        description="DriftGuard Security Group Remediation"
    )

    parser.add_argument(
        "--approve",
        action="store_true",
        help="Authorize AWS remediation"
    )

    parser.add_argument(
        "--cidr",
        required=True,
        help="CIDR block of the unauthorized rule"
    )

    args = parser.parse_args()

    rule = {
        "protocol": "tcp",
        "from_port": 22,
        "to_port": 22,
        "cidr": args.cidr
    }

    if not args.approve:

        print()
        print("APPROVAL REQUIRED")
        print("No AWS changes will be made.")

        print()
        print(
            f"Planned removal: "
            f"SSH 22 -> {args.cidr}"
        )

        print()
        print("Use --approve to authorize remediation.")

        return

    remove_rule(rule)


if __name__ == "__main__":
    main()