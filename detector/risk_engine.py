def calculate_risk(rule):
    """
    Calculate risk based on the type of security group change.
    """

    from_port = rule["from_port"]
    to_port = rule["to_port"]
    cidr = rule["cidr"]

    # Critical: SSH/RDP exposed to the entire internet
    if cidr == "0.0.0.0/0":

        if from_port == 22 or to_port == 22:
            return {
                "level": "CRITICAL",
                "score": 100,
                "reason": "SSH exposed to the internet"
            }

        if from_port == 3389 or to_port == 3389:
            return {
                "level": "CRITICAL",
                "score": 100,
                "reason": "RDP exposed to the internet"
            }

    # High: Other public inbound access
    if cidr == "0.0.0.0/0":
        return {
            "level": "HIGH",
            "score": 75,
            "reason": "Public inbound access detected"
        }

    # Medium: Restricted unexpected inbound access
    return {
        "level": "MEDIUM",
        "score": 50,
        "reason": "Unexpected inbound rule detected"
    }


if __name__ == "__main__":

    test_rule = {
        "protocol": "tcp",
        "from_port": 22,
        "to_port": 22,
        "cidr": "0.0.0.0/0"
    }

    result = calculate_risk(test_rule)

    print("Risk Level :", result["level"])
    print("Risk Score :", result["score"])
    print("Reason     :", result["reason"])