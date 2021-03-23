Your mission, if you choose to accept it, is to help us operationalize a Stateless Application Layer, that is backed by Stateful Data Layer in a Virtual Private Cloud.

# General System Requirements

---

Overall:

- Must pass the [SOC 2](https://www.imperva.com/learn/data-security/soc-2-compliance/) certification standard
- Ability to deploy in a repeatable, and mostly automated manner across multiple Customer VPCs
- Follow the Open/Close principle — hard to modify, but easy to extend

Application Layer ([Python](https://github.com/trmlabs/trm-takehome-data-eng))

- Limit access to a subset of one or more Public or VPC IPs
- Run multiple instances of the Python application
- Execute "zero-downtime" deployments

Data Layer (Postgres)

- The data layer of choice is [Postgres](https://www.postgresql.org/download/).
  - [BONUS] It would be even better if your Data Layer could support [CitusDB](https://www.citusdata.com/product/community) (a sharded version of Postgres)
- Update the DB software independent of the data on disk
- Tune DB configuration parameters easily
- Dynamically configure cluster size, and machine configuration (e.g, instance types)

These system requirements are not exhaustive. Please feel free to ask additional clarifying questions via Slack or Email.

## Part 1: Design your system

---

1. **Create a schematic (e.g, UML diagram, or something else) that describes your proposed architecture for deploying the application described above?**

   In your answer, be sure to address:

   - How will you package your solution?
   - What is your monitoring strategy?
   - What is the HA/disaster recovery process?
   - What is the regular deployment process?
   - How would you apply security patches or other updates?
   - How would you extend your deployment if we had to add additional services (e.g., message queues, caching, etc)?

2. **Describe what other solutions you considered before arriving at your final solution, and why?**

## Part 2: Implement your design

---

In Part 2, you will be implementing your design from Part 1. In order to get you started, we have (a) created a toy Python app [here](https://github.com/trmlabs/trm-takehome-data-eng) that you can use to mock the "application layer", and (b) access to [Postgres](https://www.postgresql.org/download/) or the [Citus Community Edition](https://www.citusdata.com) to mimic the data layer.

1. **Write the necessary code required to implement your design from Part 1.**

   If you need any non-cloud services, please feel free to message via Slack. We will try to give you access or ask you to explain how it would have fit into your implementation.

   Currently, the API layer doesn't actually connect to a DB. You will have to update that interface based on your deployment configuration. That said, the actual data does NOT matter — what's important is that the App can connect securely to the Data Layer

2. **If there are parts of your solution that you are unable to code, please write a functional design document that you could handoff to a contractor or a colleague**

## Submission Guidlines

- Your submission will be due by **11:59p PST on Friday**, **August 28th**. If you require additional time, please let us know ahead of time. To keep our process fair, we like each candidate exactly a week to complete the task.
- For all code written, you can package it via a **private** Github repo [preferred], or via a zip file with the relevant
- For any design ideas or any written analysis or design, please feel free to use any tools at your disposal. Google Docs, Notion, or any other tool is OK.

---

# Design

## Assumptions

1. On-premises is out of scope for this exercise. But must be deployable on GCP into customers' VPCs

## Options

### Database

- Cloud SQL
- PostgreSQL (+Citus) on Compute Engine
- PostgreSQL on GKE?
- Citus DB on GKE (https://hub.docker.com/r/citusdata/citus)

### App

In order of preference, with the most immutable options first.

1. Cloud Run
1. GKE
1. Cloud Functions
1. App Engine
1. Compute Engine

Helm charts?

**DO THIS: MAKE A LIST OF THEIR QUESTIONS AND ANSWER ONE BY ONE**

## Design Questions

### How will you package your solution?

App packaged in container. Infrastructure deployed via Terraform/Deployment Manager. If on K8s, a Helm chart.

### What is your monitoring strategy?

### What is the HA/disaster recovery process?

RTO/RPO?

### What is the regular deployment process?

Distinguish between TRM Labs publishing, and

### How would you apply security patches or other updates?

### How would you extend your deployment if we had to add additional services (e.g., message queues, caching, etc)?
