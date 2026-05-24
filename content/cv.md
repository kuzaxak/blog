---
title: "CV"
description: "Vladimir Kuznichenkov - Staff Infrastructure Engineer"
date: 2025-11-28
slug: "cv"
---

**Vladimir Kuznichenkov** — Staff Infrastructure Engineer

Tallinn, Estonia | [Email](mailto:vladimir.kuznichenkov@gmail.com) | [GitHub](https://github.com/kuzaxak) | [LinkedIn](https://www.linkedin.com/in/u-kuznichenkau/) | [Website](https://kuzaxak.dev/)

[Download PDF version](/cv.pdf)

## Profile

Staff Infrastructure / Platform Engineer with 10+ years building AWS and Kubernetes platforms for SaaS and telecom
workloads. Recent work includes cutting logging infrastructure costs by 60% through an Elasticsearch-to-Quickwit
migration, designing NAT-less Kubernetes networking for SIP/WebRTC workloads, and replacing AWS Managed VPN with
vSRX/BGP to reduce monthly VPN spend from $10k+ to ~$1k. I work across platform architecture, production operations,
and developer experience, turning complex infrastructure into reliable primitives product teams can use safely.

---

## Work history

### Staff Infrastructure Engineer | Glia
*Tallinn, Estonia | July 2024 — Present*

*   **Cost Engineering & Observability Architecture:** Architected an Elasticsearch-to-Quickwit logging migration with an async AWS Lambda ingestion pipeline and stateless EKS runtime. Reduced annual infrastructure costs by 60% while supporting petabyte-scale retention and durable writes during traffic spikes.
*   **Kubernetes Networking (Telecom/VoIP):** Led the design and implementation of a Kubernetes-native networking solution for SIP signaling and WebRTC media workloads.
    *   Partnered with platform and telecom teams to implement a custom Multus CNI integration, provisioning direct public identities for pods and achieving zero port translation (NAT-less) connectivity for Kamailio nodes.
    *   Standardized the implementation so teams could deploy telecom workloads with normal Kubernetes primitives instead of managing low-level networking.
*   **VPN Cost Optimization:** Designed a Site-to-Site VPN solution using vSRX and BGP with AWS Transit Gateway for high availability, replacing AWS Managed VPN and reducing costs from $10k+/month to $1k/month.
*   **Capacity Planning & Cross-functional Collaboration:** Led load-testing initiatives to benchmark system limits, optimizing database subsystems to enable 3x growth in enterprise customer onboarding. Worked closely with Customer Success to resolve production audio issues, demonstrating effective cross-functional problem-solving.

### Senior Infrastructure Engineer | Glia
*Tallinn, Estonia | August 2019 — July 2024*

> Glia is an all-in-one digital customer service platform with contact-center capabilities, operating as a cloud-native SaaS offering on AWS and EKS.

* Led cross-team adoption of Istio as the cluster-wide Service Mesh, implementing a Zero Trust architecture via mTLS encryption to meet strict SOC2 and enterprise security compliance, achieving 99.99% service availability.
* Implemented CD strategies for infrastructure management using Helm and Terraform alongside Jenkins pipelines, supporting 50+ microservices across multiple environments.
*   **Developer Experience (DevEx):** Collaborated with 8 engineering teams to spearhead the creation of ephemeral, on-demand sandbox environments, reducing environment provisioning from days to minutes and eliminating testing bottlenecks.
* Co-founded and helped grow a dedicated Developer Experience (DevEx) team serving 60+ engineers, focusing on building tools, automating processes, and creating a streamlined development environment.

### Solution Architect | Insly
*Tallinn, Estonia | January 2018 — June 2019*

*   **Cloud Transformation:** Led a team of 3 engineers to architect and execute the strategic migration from a single-tenant on-premise legacy solution to a multi-tenant, cloud-native SaaS platform on Kubernetes, increasing release cadence from monthly deployments to daily deployments.
*   **DevOps Culture:** Evangelized DevOps practices across the organization, building the initial CI/CD pipelines using Kubernetes and Jenkins, significantly reducing feature time-to-deliver and modernizing the development lifecycle.

### Senior PHP Developer | Insly
*Tallinn, Estonia | September 2016 — January 2018*

* Mentored junior developers while refactoring the core legacy framework to utilize the Active Record pattern, improving maintainability and database abstraction.
* Collaborated with QA and product teams to containerize the local development environment using Docker, solving environment consistency issues across the team.
* Designed a microservice-based calculation gateway and led the codebase migration from PHP 5.5 to 7.0 to utilize strict typing and performance improvements.

### **Prior Experience**
*   **PHP Developer, Pictagram** (2015 — 2016): Designed hardware-software integration for IoT vending machines using socket communication and VPN tunneling.
*   **PHP Developer, Unex Group** (2013 — 2015): Developed logistics management software focused on route optimization and resource allocation.

---

## Technical Skills

*   **Container Orchestration:** Kubernetes, EKS, Kops, Helm, Istio, Multus CNI
*   **Infrastructure as Code:** Terraform, AWS CDK, Ansible
*   **CI/CD & DevOps:** Jenkins, ArgoCD, GitHub Actions, GitLab CI, Buildkite
*   **Cloud Providers:** AWS (Deep expertise), GCP, DigitalOcean
*   **Backend & Scripting:** Python, Go, Rust, PHP, Elixir, Bash
*   **Observability:** Prometheus, VictoriaMetrics, Grafana, ELK Stack / OpenSearch, Quickwit
*   **Telecom/VoIP:** Kamailio, FreeSWITCH, SIP/RTP, WebRTC
---

## Education

**Bachelor's Degree, Medical Engineering**
Belarusian State University of Informatics and Radioelectronics
*Minsk, Belarus — 2017*

---

Email: [vladimir.kuznichenkov@gmail.com](mailto:vladimir.kuznichenkov@gmail.com)

Tallinn, Estonia
