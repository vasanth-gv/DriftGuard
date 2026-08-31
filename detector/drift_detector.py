import json
import boto3
from pathlib import Path
from risk_engine import calculate_risk


REGION = "ap-south-1"

EXPECTED_CONFIG = (
    Path(__file__).resolve().parent.parent / "expected_config.json"
)

REPORT_DIR = (
    Path(__file__).resolve().parent.parent / "reports"
)

REPORT_FILE = REPORT_DIR / "drift_report.json"

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
        raise Exception(
            f"Security group '{name}' not found"
        )

    return response["SecurityGroups"][0]


def get_actual_rules(security_group):
    rules = []

    for permission in security_group["IpPermissions"]:
        protocol = permission.get("IpProtocol")
        from_port = permission.get("FromPort")
        to_port = permission.get("ToPort")

        for ip_range in permission.get("IpRanges", []):
            rules.append(
                {
                    "protocol": protocol,
                    "from_port": from_port,
                    "to_port": to_port,
                    "cidr": ip_range["CidrIp"]
                }
            )

    return rules


def normalize(rule):
    return (
        rule["protocol"],
        rule["from_port"],
        rule["to_port"],
        rule["cidr"]
    )


def detect_drift(expected_rules, actual_rules):

    expected = {
        normalize(rule)
        for rule in expected_rules
    }

    actual = {
        normalize(rule)
        for rule in actual_rules
    }

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


def create_report(
    security_group,
    added,
    removed
):

    added_rules = []
    removed_rules = []

    highest_score = 0
    highest_risk = {
        "level": "LOW",
        "score": 0,
        "reason": "No security risk detected"
    }

    for rule in sorted(added):

        rule_data = get_rule_data(rule)
        risk = calculate_risk(rule_data)

        added_rules.append(
            {
                **rule_data,
                "risk": risk
            }
        )

        if risk["score"] > highest_score:
            highest_score = risk["score"]
            highest_risk = risk

    for rule in sorted(removed):

        rule_data = get_rule_data(rule)

        removed_rules.append(rule_data)

    if added or removed:
        status = "DRIFT_DETECTED"
    else:
        status = "NO_DRIFT"

    report = {
        "resource": security_group["GroupName"],
        "region": REGION,
        "status": status,
        "added_rules": added_rules,
        "removed_rules": removed_rules,
        "risk": highest_risk
    }

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(REPORT_FILE, "w") as file:
        json.dump(
            report,
            file,
            indent=4
        )

    return report


def print_scan(report):

    print("=" * 55)
    print("             DRIFTGUARD SCAN")
    print("=" * 55)

    print(
        f"Resource : {report['resource']}"
    )

    print(
        f"Region   : {report['region']}"
    )

    if report["status"] == "NO_DRIFT":

        print("\nSTATUS: NO DRIFT")

    else:

        print("\nSTATUS: DRIFT DETECTED")

        if report["added_rules"]:

            print(
                "\nUnauthorized / Added Rules:"
            )

            for rule in report["added_rules"]:

                print(
                    f"  {rule['protocol']} "
                    f"{rule['from_port']}-"
                    f"{rule['to_port']} "
                    f"{rule['cidr']}"
                )

                print(
                    f"    Risk Level : "
                    f"{rule['risk']['level']}"
                )

                print(
                    f"    Risk Score : "
                    f"{rule['risk']['score']}"
                )

                print(
                    f"    Reason     : "
                    f"{rule['risk']['reason']}"
                )

        if report["removed_rules"]:

            print(
                "\nMissing Expected Rules:"
            )

            for rule in report["removed_rules"]:

                print(
                    f"  {rule['protocol']} "
                    f"{rule['from_port']}-"
                    f"{rule['to_port']} "
                    f"{rule['cidr']}"
                )

    print(
        f"\nReport saved: {REPORT_FILE}"
    )


def main():

    config = load_expected_config()

    security_group = get_security_group(
        config["security_group"]
    )

    actual_rules = get_actual_rules(
        security_group
    )

    added, removed = detect_drift(
        config["inbound_rules"],
        actual_rules
    )

    report = create_report(
        security_group,
        added,
        removed
    )

    print_scan(report)


if __name__ == "__main__":
    main()