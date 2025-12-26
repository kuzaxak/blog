---
title: "CV"
description: "Vladimir Kuznichenkov - Staff Infrastructure Engineer"
date: 2025-11-28
slug: "cv"
---

[Download PDF version](/cv.pdf)

## Profile

Staff Infrastructure Engineer with over 10 years of experience designing scalable, cloud-native systems. Expert in
navigating the intersection of complex networking requirements (Telco/VoIP) and modern container orchestration.
Effective communicator who bridges technical and business stakeholders, with a proven track record in establishing
Developer Experience (DevEx) initiatives, optimizing petabyte-scale data pipelines, and driving cost-efficient
architectural migrations on AWS. Passionate about mentoring engineers and fostering cross-functional collaboration
to build reliable platforms that accelerate engineering velocity.

---

## Work history

### Staff Infrastructure Engineer | Glia
*Tallinn, Estonia | July 2024 — Present*

*   **Cost Engineering & Observability Architecture:** Collaborated with product and platform teams to architect a next-generation logging platform by migrating from Elasticsearch to Quickwit (Rust-based search). Designed an async ingestion pipeline via AWS Lambda, achieving a fully stateless runtime on EKS and 100% write durability during traffic spikes. Reduced annual infrastructure costs by 60% while scaling the system to petabyte-level retention.
*   **Kubernetes Networking (Telecom/VoIP):** Led the design and implementation of a Kubernetes-native networking solution for SIP signaling and WebRTC media workloads.
    *   Partnered with platform and telecom teams to implement a custom Multus CNI integration, provisioning direct public identities for pods and achieving zero port translation (NAT-less) connectivity for Kamailio nodes.
    *   Standardized the implementation to maintain Developer Experience, allowing teams to deploy complex telecom stacks using standard K8s primitives without managing low-level networking.
*   **VPN Cost Optimization:** Designed a Site-to-Site VPN solution using vSRX and BGP with AWS Transit Gateway for high availability, replacing AWS Managed VPN and reducing costs from $10k+/month to $1k/month.
*   **Capacity Planning & Cross-functional Collaboration:** Led load-testing initiatives to benchmark system limits, optimizing database subsystems to enable 3x growth in enterprise customer onboarding. Worked closely with Customer Success to resolve production audio issues, demonstrating effective cross-functional problem-solving.

### Senior Infrastructure Engineer | Glia
*Tallinn, Estonia | August 2019 — July 2024*

> Glia is an all-in-one digital customer service platform with call-centre capabilities. Operating as a cloud-native SaaS offering in AWS based on the EKS stack.

* Led cross-team adoption of Istio as the cluster-wide Service Mesh, implementing a Zero Trust architecture via mTLS encryption to meet strict SOC2 and enterprise security compliance, achieving 99.99% service availability.
* Implemented CD strategies for infrastructure management using Helm and Terraform alongside Jenkins pipelines, supporting 50+ microservices across multiple environments.
*   **Developer Experience (DevEx):** Collaborated with 8 engineering teams to spearhead the creation of ephemeral, on-demand sandbox environments, reducing environment provisioning from days to minutes and eliminating testing bottlenecks.
* Co-founded and helped grow a dedicated Developer Experience (DevExp) team serving 60+ engineers, focusing on building tools, automating processes, and creating a streamlined development environment.

### Solution Architect | Insly
*Tallinn, Estonia | January 2018 — June 2019*

*   **Cloud Transformation:** Led a team of 3 engineers to architect and execute the strategic migration from a single-tenant on-premise legacy solution to a multi-tenant, cloud-native SaaS platform on Kubernetes, reducing deployment frequency from monthly to daily.
*   **DevOps Culture:** Evangelized DevOps practices across the organization, building the initial CI/CD pipelines using Kubernetes and Jenkins, significantly reducing feature time-to-deliver and modernizing the development lifecycle.

### Senior PHP Developer | Insly
*Tallinn, Estonia | September 2016 — January 2018*

* Mentored junior developers while refactoring the core legacy framework to utilize the Active Record pattern, improving maintainability and database abstraction.
* Collaborated with QA and product teams to containerize the local development environment using Docker, solving environment consistency issues across the team.
* Designed a microservice-based calculation gateway and led the codebase migration from PHP 5.5 to 7.0 to utilize strict typing and performance improvements.

### **Prior Experience**
*   **PHP Developer, Pictagram** (2015 — 2016): Designed hardware-software integration for IoT vending machines using Socket communication and VPN tunnelling.
*   **PHP Developer, Unex Group** (2013 — 2015): Developed logistics management software focused on route optimization and resource allocation.

---

## Technical Skills

*   **Container Orchestration:** Kubernetes, EKS, Kops, Helm, Istio, Multus CNI
*   **Infrastructure as Code:** Terraform, AWS CDK, Ansible
*   **CI/CD & DevOps:** Jenkins, ArgoCD, GitHub Actions, GitLab CI, Buildkite
*   **Cloud Providers:** AWS (Deep expertise), GCP, DigitalOcean
*   **Backend & Scripting:** Python, Go, Rust, PHP, Elixir, Bash
*   **Observability:** Prometheus, Victoria, Grafana, ELK Stack / OpenSearch, Quickwit
*   **Telecom/VoIP:** Kamailio, FreeSWITCH, SIP/RTP, WebRTC
---

## Education

**Bachelor's Degree**
Belarusian State University of Informatics and Radioelectronics
*Minsk, Belarus — 2017*

---

Email: [vladimir.kuznichenkov@gmail.com](mailto:vladimir.kuznichenkov@gmail.com)

Tallinn, Estonia
