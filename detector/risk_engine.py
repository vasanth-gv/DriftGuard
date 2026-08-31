def calculate_risk(rule):
    """
    Calculate security risk for an unexpected inbound rule.
    """

    from_port = rule["from_port"]
    to_port = rule["to_port"]
    cidr = rule["cidr"]

    # CRITICAL: SSH exposed to the entire internet
    if cidr == "0.0.0.0/0" and from_port <= 22 <= to_port:
        return {
            "level": "CRITICAL",
            "score": 100,
            "reason": "SSH exposed to the internet"
        }

    # CRITICAL: RDP exposed to the entire internet
    if cidr == "0.0.0.0/0" and from_port <= 3389 <= to_port:
        return {
            "level": "CRITICAL",
            "score": 100,
            "reason": "RDP exposed to the internet"
        }

    # HIGH: Any other public inbound access
    if cidr == "0.0.0.0/0":
        return {
            "level": "HIGH",
            "score": 75,
            "reason": "Public inbound access detected"
        }

    # MEDIUM: Unexpected but restricted inbound access
    return {
        "level": "MEDIUM",
        "score": 50,
        "reason": "Unexpected restricted inbound rule"
    }