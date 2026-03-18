<p align="center">
  <img src="assets/platform_logo.png" width="700">
</p>

<p align="center">
  <!-- Languages / Framework -->
  <img src="https://img.shields.io/badge/python-3.11-blue" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-green" />
  <br/>
  <!-- Cloud / Infrastructure -->
  <img src="https://img.shields.io/badge/AWS-cloud-orange" />
  <img src="https://img.shields.io/badge/Terraform-IaC-purple" />
  <img src="https://img.shields.io/badge/Docker-container-blue" />
  <img src="https://img.shields.io/badge/Kubernetes-EKS-blue" />
  <br/>
  <!-- DevOps / Observability / Testing -->
  <img src="https://img.shields.io/badge/CI/CD-GitHub%20Actions-black" />
  <img src="https://img.shields.io/badge/Prometheus-monitoring-orange" />
  <img src="https://img.shields.io/badge/Grafana-dashboards-orange" />
  <img src="https://img.shields.io/badge/tests-pytest-blue" />
  <img src="https://img.shields.io/badge/Security-Trivy-red" />
</p>

>**Current Status**
> - Contract-first API and schema validation implemented.  
> - Data integration, infrastructure, and deployment layers are in progress.

## Overview

**FinOpsGuard** is a cloud-native platform for monitoring AWS cloud costs and estimating infrastructure carbon emissions, enabling engineers to identify cost optimization and sustainability opportunities.

### API Design:
The platform employs a contract-first FastAPI service with strictly validated schemas, exposing endpoints for cost analysis, carbon estimation, and optimization insights.
The system is architected to provide engineers clear visibility into both the financial and environmental dimensions of their infrastructure. 

### Architecture (in progress): 
Built using FastAPI and Pydantic, with planned integration of Terraform (IaC), Docker, Kubernetes (EKS), and GitHub Actions for deployment, automation, and scalability.

### Design Decisions:

**Strict scheme validation (`extra='forbid'`) on all models**
Pydantic models enforce strict schemas. Unknown or unexpected fields are rejected rather than silently ignored, ensuring predictable and secure API contract.

**Pinned dependencies (`==` not `>=`)**
Ensures consistent environments across local development, CI pipelines, and production containers.

---

### Tech Stack (Current)

| Layer | Technology |
|------|------------|
| Backend | FastAPI (Python) |
| Validation | Pydantic v2 |

### Tech Stack (Planned Integration)
| Layer | Technology |
|------|------------|
| Infrastructure (planned) | Terraform |
| Containerization (planned) | Docker |
| Orchestration (planned) | Kubernetes (EKS) |
| CI/CD (planned) | GitHub Actions |
| Observability (planned) | Prometheus, Grafana |
| Security (planned) | Trivy |

---

## Features

### Current

- **Project Structure** — Repository currently organized with planned scalability, with dedicated directories for API, infrastructure (Terraform), containerization (Docker/Kubernetes), CI/CD, testing, and documentation.

- **API** — FastAPI backend with validated request/response models and automatic OpenAPI documentation. Core endpoints (/health, /costs, /carbon, /report) are defined with structured schemas; data integration is in progress.

- **Enforced Schema Validation** — Strict data contracts enforced using Pydantic models for predictable type safe behavior (extra="forbid")

### Planned
- Integrate AWS cost ingestion
- Implement carbon estimation logic
- Add report generation and storage
- Provision infrastructure with Terraform
- Deploy with Docker and Kubernetes
- Implement CI/CD automation
- Add observability and monitoring
- Integrate security scanning

---

## Prerequisites

- Python 3.10+
- pip
- Git

---

## Environment

Development is being performed in **Linux environment**, as project is intended to align with cloud-native workflows. 
> Disclaimer: The application can be run on both Linux and Windows systems. Please follow the respective instructions below for your OS:


## Quick Start
```bash
git clone https://github.com/shafayet7546/finopsguard.git
cd finopsguard

python -m venv venv

# Linux | macOS
source venv/bin/activate
# Windows
1. Open **Powershell as Administrator**
2. Run: venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
#### Access Swagger UI: https://localhost:(port)/docs

#### Example of url: http://localhost:8000/docs

---

### API Endpoints

| Method | Endpoint | Description                  |
|--------|----------|------------------------------|
| GET    | /health  | Service health check (default/data pending)|
| GET    | /costs   | Monthly cloud cost metrics (mock/data pending)|
| GET    | /carbon  | Carbon footprint assessment  (mock/data pending)|
| GET    | /report  | PDF report generation status (mock/data pending)|

---

## Repository Structure
```
finopsguard/
├── app/
│   ├── main.py           # FastAPI entry point and route definitions
│   └── models.py         # Pydantic v2 response models
├── terraform/            # IaC — VPC, EKS, RDS, S3, IAM
├── k8s/                  # Helm charts + ArgoCD manifests
├── lambda/               # AWS Lambda functions for cost/carbon processing
├── tests/                # Pytest unit + Playwright E2E
├── .github/
│   └── workflows/        # GitHub Actions CI/CD pipeline
├── docs/                 # Architecture diagrams + cost reports
├── requirements.txt
└── README.md
```

---