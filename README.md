# Cloud Resource Monitoring & Alerting System

## Overview

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

## Directory Structure

```
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

## Setup Instructions

### Prerequisites

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