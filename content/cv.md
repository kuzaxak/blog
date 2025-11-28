---
title: "CV"
description: "Vladimir Kuznichenkov - Staff Infrastructure Engineer"
date: 2025-11-28
slug: "cv"
---

## Profile

Staff Infrastructure Engineer with over 10 years of experience designing scalable, cloud-native systems. Expert in
navigating the intersection of complex networking requirements (Telco/VoIP) and modern container orchestration.
Proven track record in establishing Developer Experience (DevEx) initiatives, optimizing petabyte-scale data pipelines,
and driving cost-efficient architectural migrations on AWS. Dedicated to building reliable platforms that accelerate
engineering velocity and ensuring high availability for mission-critical SaaS products.

---

## Experience

### Staff Infrastructure Engineer | Glia
*Tallinn, Estonia | 2023 — Present*

*   **Cost Engineering & Observability Architecture:** Architected a next-generation logging platform by migrating from
    Elasticsearch to Quickwit (Rust-based search). Designed an async ingestion pipeline via AWS Lambda, achieving a
    fully stateless runtime on EKS and 100% write durability during traffic spikes. Reduced annual infrastructure costs
    while scale the system to petabyte-level retention.
*   **Kubernetes Networking (Telecom/VoIP):** Engineered a Kubernetes-native networking solution for SIP signaling and
    WebRTC media workloads.
    *   Implemented a custom **Multus CNI** integration to provision direct public identities for pods, achieving **zero port translation (NAT-less)** connectivity for Kamailio nodes.
    *   Standardized the implementation to maintain Developer Experience, allowing teams to deploy complex telecom stacks using standard K8s primitives without managing low-level networking.
*   **Capacity Planning:** Led load-testing initiatives to benchmark system limits, optimizing database subsystems to
    enable the reliable onboarding of enterprise-tier customers with high-concurrency requirements.

### Senior Infrastructure Engineer | Glia
*Tallinn, Estonia | 2019 — 2023*

> Glia is an all-in-one digital customer service platform with call-centre capabilities. Operating as a cloud-native SaaS offering in AWS based on the EKS stack.

* Directed the adoption of Istio as the cluster-wide Service Mesh, implementing a Zero Trust architecture via mTLS encryption to meet strict SOC2 and enterprise security compliance.
* Achieved successful implementation of CD strategies for infrastructure management using Helm and Terraform alongside Jenkins pipelines
* Developer Experience (DevEx): spearheaded the creation of ephemeral, on-demand sandbox environments. This parallelized the testing process, eliminating bottlenecks for a growing engineering organization.
* Contributed significantly to establishing a dedicated Developer Experience (DevExp) team, focusing on building tools, automating processes, and creating a streamlined development environment

### **Solution Architect** | Insly
*Tallinn, Estonia | 2018 — 2019*
*   **Cloud Transformation:** Architected and executed the strategic migration from a single-tenant on-premise legacy solution to a multi-tenant, cloud-native SaaS platform on Kubernetes.
*   **DevOps Culture:** Built the initial CI/CD pipelines using Kubernetes and Jenkins, significantly reducing the "feature time-to-deliver" and modernizing the development lifecycle.

### **Senior PHP Developer** | Insly
*Tallinn, Estonia | 2016 — 2018*
*   Refactored the core legacy framework to utilize the Active Record pattern, improving maintainability and database abstraction.
*   Containerized the local development environment using `Docker`, solving environment consistency issues ("works on my machine") for the team.
*   Designed a microservice-based calculation gateway and led the codebase migration from PHP 5.5 to 7.0 to utilize strict typing and performance improvements.

### **Prior Experience**
*   **PHP Developer, Pictagram** (2015 — 2016): Designed hardware-software integration for IoT vending machines using Socket communication and VPN tunnelling.
*   **PHP Developer, Unex Group** (2013 — 2015): Developed logistics management software focused on route optimization and resource allocation.

---

## Technical Skills

*   **Container Orchestration:** Kubernetes, EKS, Kops, Helm, Istio, Multus CNI.
*   **Infrastructure as Code:** Terraform, AWS CDK, Ansible.
*   **CI/CD & DevOps:** Jenkins, ArgoCD, GitHub Actions, GitLab CI, Buildkite.
*   **Cloud Providers:** AWS (Deep expertise), GCP, DigitalOcean.
*   **Backend & Scripting:** Python, Go, Rust, PHP, Elixir, Bash.
*   **Observability:** Prometheus, Victoria, Grafana, ELK Stack / OpenSearch, Quickwit.
*   **Telecom/VoIP:** Kamailio, FreeSWITCH, SIP/RTP, WebRTC
---

## Education

**Bachelor's Degree**
Belarusian State University of Informatics and Radioelectronics
*Minsk, Belarus — 2017*

---

Email: [vladimir.kuznichenkov@gmail.com](mailto:vladimir.kuznichenkov@gmail.com)

Tallinn, Estonia
