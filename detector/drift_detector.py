import json
import boto3
from pathlib import Path
from risk_engine import calculate_risk


REGION = "ap-south-1"


EXPECTED_CONFIG = Path(__file__).resolve().parent.parent / "expected_config.json"

ec2 = boto3.client("ec2", region_name=REGION)


def load_expected_config():
    with open(EXPECTED_CONFIG, "r") as file:
        return json.load(file)


def get_security_group(name):
    response = ec2.describe_security_groups(
        Filters=[
            {
                "Name": "group-name",
                "Values": [name]
            }
        ]
    )

    if not response["SecurityGroups"]:
        raise Exception(f"Security group '{name}' not found")

    return response["SecurityGroups"][0]


def get_actual_rules(security_group):
    rules = []

    for permission in security_group["IpPermissions"]:
        protocol = permission.get("IpProtocol")
        from_port = permission.get("FromPort")
        to_port = permission.get("ToPort")

        for ip_range in permission.get("IpRanges", []):
            rules.append({
                "protocol": protocol,
                "from_port": from_port,
                "to_port": to_port,
                "cidr": ip_range["CidrIp"]
            })

    return rules


def normalize(rule):
    return (
        rule["protocol"],
        rule["from_port"],
        rule["to_port"],
        rule["cidr"]
    )


def detect_drift(expected_rules, actual_rules):
    expected = {normalize(rule) for rule in expected_rules}
    actual = {normalize(rule) for rule in actual_rules}

    added = actual - expected
    removed = expected - actual

    return added, removed

def get_rule_data(rule):
    return {
        "protocol": rule[0],
        "from_port": rule[1],
        "to_port": rule[2],
        "cidr": rule[3]
    }

def main():
    config = load_expected_config()

    security_group = get_security_group(
        config["security_group"]
    )

    actual_rules = get_actual_rules(security_group)

    added, removed = detect_drift(
        config["inbound_rules"],
        actual_rules
    )

    print("=" * 55)
    print("             DRIFTGUARD SCAN")
    print("=" * 55)

    print(f"Resource : {security_group['GroupName']}")
    print(f"Region   : {REGION}")

    if not added and not removed:
        print("\nSTATUS: NO DRIFT")
        return

    print("\nSTATUS:  DRIFT DETECTED")

    if added:
        print("\nUnauthorized / Added Rules:")
        for rule in sorted(added):
            print(
                f"  {rule[0]} "
                f"{rule[1]}-{rule[2]} "
                f"{rule[3]}"
            )

    if removed:
        print("\nMissing Expected Rules:")
        for rule in sorted(removed):
            print(
                f"  {rule[0]} "
                f"{rule[1]}-{rule[2]} "
                f"{rule[3]}"
            )


if __name__ == "__main__":
    main()