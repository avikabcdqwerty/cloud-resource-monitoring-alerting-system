# Cloud Resource Monitoring & Alerting System

## Overview

<<<<<<< HEAD
A modular, extensible system for proactive monitoring and alerting of cloud resources. Enables real-time detection and resolution of operational and security issues, centralized metric visualization, automated alerting, incident logging, and seamless onboarding of new resources.

**Key Features:**
- Collects metrics (CPU, memory, network, storage) from all provisioned cloud resources
- Centralized dashboard visualization (Grafana, React UI)
- Automated alerting via email and Slack
- Incident management and audit trail (immutable logs)
- Security event detection and notification
- Automated onboarding of new resources
- RESTful CRUD operations for products

## Architecture

- **Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** React, TypeScript
- **Monitoring:** AWS CloudWatch (extensible to Azure/GCP), Grafana
- **Alerting:** SMTP (email), Slack API
- **Infrastructure:** Terraform, Docker
- **Testing:** pytest
=======
The **Cloud Resource Monitoring & Alerting System** provides automated, scalable, and secure monitoring for AWS cloud resources. It collects operational and security metrics, visualizes them in centralized dashboards, and delivers proactive alerts to response teams via email and messaging platforms (Slack/MS Teams). The system ensures rapid incident response, comprehensive audit trails, and compliance with organizational standards.

---

## Features

- **Automated Onboarding:** New AWS resources are automatically included in monitoring and alerting coverage.
- **Comprehensive Metrics:** Collects CPU, memory, network, and storage metrics from all provisioned resources.
- **Centralized Dashboards:** Visualizes metrics using AWS CloudWatch Dashboards.
- **Configurable Alerts:** Thresholds for resource metrics are defined and enforced; alerts are triggered and delivered via email and messaging platforms.
- **Security Event Detection:** Monitors CloudTrail for unauthorized access and configuration changes, generating security alerts.
- **Audit Logging:** All alert generation and resolution events are logged in a tamper-resistant DynamoDB table.
- **Misconfiguration Detection:** Notifies DevOps of misconfigurations or missing monitoring coverage.
- **Extensible Architecture:** Easily add support for new resource types and alerting channels.

---

## Architecture

- **Infrastructure as Code:** Provisioned using Terraform for repeatability and compliance.
- **AWS Lambda:** Automates onboarding, alert processing, and security event monitoring.
- **AWS CloudWatch:** Centralized dashboards, metrics, and alarms.
- **AWS SNS:** Alert delivery to email and Lambda for messaging integrations.
- **Amazon DynamoDB:** Tamper-resistant audit log storage.
- **AWS CloudTrail:** Security event logging and detection.
- **AWS S3:** Stores configuration and documentation.
- **Slack/MS Teams:** Integrated for rapid alert delivery.

See [architecture_notes](#) for detailed diagrams and flow.

---
>>>>>>> d1a4f7c08d028ec8162fb4bc59a7a78deb583177

## Directory Structure

```
<<<<<<< HEAD
.
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── crud.py
│   ├── monitoring.py
│   ├── alerting.py
│   ├── security_events.py
│   ├── audit_log.py
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
├── infra/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── grafana-dashboard.json
└── README.md
```

=======
/
├── infrastructure/
│   └── main.tf                # Terraform configuration
├── lambda/
│   ├── onboarding/
│   │   └── onboard_resource.py    # Lambda: resource onboarding
│   ├── alerting/
│   │   └── alert_handler.py       # Lambda: alert processing
│   └── security/
│       └── security_event_monitor.py # Lambda: security event monitoring
├── config/
│   ├── dashboard_config.json   # CloudWatch dashboard config
│   ├── alert_thresholds.json   # Alert thresholds config
│   └── audit_log_schema.json   # Audit log schema (DynamoDB)
├── docs/
│   └── incident_log.md         # Incident logging & resolution procedures
└── README.md                   # Project overview (this file)
```

---

>>>>>>> d1a4f7c08d028ec8162fb4bc59a7a78deb583177
## Setup Instructions

### Prerequisites

<<<<<<< HEAD
- Docker & Docker Compose
- Terraform >= 1.5.0
- AWS account (for CloudWatch, SNS, IAM, KMS resources)
- Node.js & npm (for frontend)
- Python 3.11+

### Backend API

1. **Configure Environment Variables:**

   - `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASS`, `EMAIL_FROM`, `EMAIL_TO`
   - `SLACK_WEBHOOK_URL`
   - `DATABASE_URL` (PostgreSQL connection string)

2. **Install Dependencies:**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Run Backend Locally:**

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Run Backend in Docker:**

   ```bash
   docker build -t cloud-monitoring-backend .
   docker run -p 8000:8000 --env-file .env cloud-monitoring-backend
   ```

5. **Run Tests:**

   ```bash
   pytest
   ```

### Frontend UI

1. **Install Dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Configure API Endpoint:**

   - Set `REACT_APP_API_BASE` in `.env` (default: `http://localhost:8000`)

3. **Run Frontend:**

   ```bash
   npm start
   ```

### Infrastructure Provisioning

1. **Configure Terraform Variables:**

   - Edit `infra/terraform/variables.tf` or use `terraform.tfvars` for:
     - `aws_region`
     - `alert_email`
     - `slack_webhook_url`
     - `ec2_instance_id`

2. **Initialize & Apply:**

   ```bash
   cd infra/terraform
   terraform init
   terraform apply
   ```

### Grafana Dashboard

1. **Import Dashboard:**
   - Open Grafana UI
   - Import `infra/grafana-dashboard.json`
   - Set up CloudWatch datasource

## API Endpoints

- **Health Check:** `GET /health`
- **Products CRUD:** `GET/POST/PUT/DELETE /products/`
- **Resource Metrics:** `GET /monitoring/resources/metrics`
- **Alerts:** `GET /alerting/alerts/`, `POST /alerting/alerts/{id}/resolve`, `POST /alerting/alerts/{id}/deliver`
- **Security Events:** `POST /security-events/detect`, `GET /security-events/types`
- **Audit Log:** `GET /audit-log/`

## Security & Compliance

- All sensitive data encrypted in transit and at rest
- Audit logs are immutable and securely stored (CloudWatch + KMS)
- Follows organizational security and privacy policies

## Extensibility

- Easily add support for new cloud providers, resource types, and alert channels
- Modular backend and frontend codebase

## Troubleshooting

- Check logs in Docker container (`docker logs <container_id>`)
- Ensure environment variables are set correctly
- Verify AWS credentials and permissions for Terraform resources

## License

MIT

## Authors

Cloud Resource Monitoring & Alerting System Team

## Contact

For support or feature requests, open an issue or contact the DevOps team.
=======
- AWS CLI configured with appropriate permissions
- Terraform >= 1.5.0
- Python 3.11 for Lambda packaging
- Access to Slack/MS Teams webhook URLs (if using messaging integrations)

### 1. Clone the Repository

```bash
git clone <repo-url>
cd cloud-resource-monitoring-alerting
```

### 2. Configure Variables

Edit `infrastructure/main.tf` or use a `terraform.tfvars` file to set:

- `aws_region`
- `alert_email_addresses`
- `slack_webhook_url` / `teams_webhook_url`
- `lambda_s3_bucket` (optional)

### 3. Deploy Infrastructure

```bash
cd infrastructure
terraform init
terraform apply
```

This will provision all AWS resources, including Lambda functions, SNS topics, DynamoDB tables, CloudWatch dashboards, and IAM roles.

### 4. Deploy Lambda Code

Package and upload Lambda functions to the designated S3 bucket:

```bash
# Example for onboarding Lambda
cd lambda/onboarding
zip onboard_resource.zip onboard_resource.py
aws s3 cp onboard_resource.zip s3://<lambda_s3_bucket>/onboarding/onboard_resource.zip

# Repeat for alerting and security Lambda functions
```

### 5. Update CloudWatch Dashboard & Alert Configs

Edit `config/dashboard_config.json` and `config/alert_thresholds.json` as needed, then upload to the S3 bucket specified in Terraform.

### 6. Test the System

- Add a new AWS resource (e.g., EC2 instance) and verify onboarding, metrics collection, and alerting.
- Trigger an alert (e.g., simulate high CPU) and confirm notifications are delivered.
- Simulate a security event (e.g., unauthorized access) and verify security alerting and audit logging.

---

## Operational Procedures

- **Incident Logging:** Follow the [incident_log.md](docs/incident_log.md) template for all incidents.
- **Audit Trail:** All alert and incident events are logged in DynamoDB per [audit_log_schema.json](config/audit_log_schema.json).
- **Monitoring Review:** Regularly review dashboard and alert configurations for completeness and security.
- **Configuration Management:** Store and version all configuration files in the `/config` directory and S3.

---

## Security & Compliance

- **Tamper-resistant Audit Logs:** All events are logged in DynamoDB with TTL for compliance retention.
- **Least Privilege IAM:** Lambda and other resources use least-privilege roles.
- **Alert Delivery:** Supports both email and messaging platforms for redundancy.
- **Extensibility:** Easily add new resource types and alert channels as requirements evolve.

---

## Troubleshooting

- **Lambda Errors:** Check CloudWatch Logs for Lambda function errors.
- **Alert Delivery Issues:** Verify SNS topic subscriptions and webhook URLs.
- **Audit Log Issues:** Ensure DynamoDB table exists and Lambda has write permissions.
- **Resource Coverage:** Use onboarding Lambda logs to detect missing monitoring.

---

## References

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS SNS Documentation](https://docs.aws.amazon.com/sns/)
- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [AWS CloudTrail Documentation](https://docs.aws.amazon.com/cloudtrail/)

---

## Maintainers

- DevOps/Security Team  
- For support or questions, contact: `<team-email-or-slack-channel>`

---

*This documentation is maintained and reviewed regularly to ensure operational and security completeness.*
>>>>>>> d1a4f7c08d028ec8162fb4bc59a7a78deb583177
