# 🛡️ DriftGuard

### Automated Cloud Infrastructure Drift Detection & Security Gate

DriftGuard is a DevSecOps automation project that continuously monitors AWS infrastructure for unauthorized configuration changes.

It detects infrastructure drift, analyzes the security risk, generates an HTML security report, sends real-time alerts through Email and Discord, and automatically blocks the Jenkins pipeline when a high-risk change is detected.

---

## 🚀 Project Overview

Infrastructure changes can happen outside Infrastructure-as-Code workflows.

For example, an administrator or attacker could manually modify an AWS Security Group and expose an application port to the public internet.

DriftGuard detects these unexpected changes and prevents them from silently reaching the deployment pipeline.

### Example

An unauthorized rule is added:

```text
Protocol : TCP
Port     : 8080
Source   : 0.0.0.0/0
