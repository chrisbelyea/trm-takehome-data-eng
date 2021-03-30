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
      - App packaged as container, deployed with K8s config and/or Helm chart
      - Database as container, deployed with K8s config and/or Helm chart
   - What is your monitoring strategy?
   - What is the HA/disaster recovery process?
      - Use a regional (instead of zonal) GKE cluster
      - PV disk snapshots
      - pg_dump might not be performant enough for huge databases
      - maybe create a sidecar or K8s cronjob that does a postgres checkpoint to flush everything and then call GCP API to create the snapshot
   - What is the regular deployment process?
   - How would you apply security patches or other updates?
      - Update containers and use K8s rolling updates
   - How would you extend your deployment if we had to add additional services (e.g., message queues, caching, etc)?
      -

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

The system has two components: app & database. The app is a simple Python Flask app that connects to the database. The database is a PostgreSQL cluster with Pgpool as the connection broker.

In general, the solution must:
- Pass SOC2 certification standard
- Deploy in a repeatable and mostly automated manner across multiple Customer VPCs
- Follow the Open/Close principle—hard to modify, but easy to extend

To achieve this:
- The solution generally aligns with SOC2 standards
- Deployment is codified and dynamic enough to run in other customers' GCP VPCs
- The application is "sealed" in a container image but can be extended by making derivative images and/or adding anciallary capabilities to the environment (e.g. a message queue) that connect with each other via K8s services

The app must:

- Limit access to a subset of one or more Public or VPC IPs
- Run multiple instances of the Python application
- Execute "zero-downtime" deployments

To achieve this:

- App runs as a deployment scaled to multiple pods on GKE
- For internal (VPC) clients, the app has a service tied to an internal load balancer
- For external (non-VPC) clients, the app has an Ingress (HTTP LB)
- Load balancers can be protected by VPC firewall rules as needed
- The application can scale by adjusting the deployment's replica count
- The application can scale automatically via HPA
- The application uses K8s rolling deployments, which can be used to roll out patches or other updates
- For use with by customers, the app container image should be versioned & published via a pipeline and distributed via a shared registry
- **Application can be monitored**

The database must:

- Use PostgreSQL or, optionally, CitusDB
- Update the DB software independent of the data on disk
- Tune DB configuration parameters easily
- Dynamically configure cluster size, and machine configuration (e.g, instance types)

To achieve this:

- PostgreSQL cluster (StatefulSet) is deployed via Helm chart
   - For real-world use, more performant storage should be used
   - Database is running on K8s for the ability to scale nodes horizontally in a StatefulSet, but running on VMs may well be a better option for a number of reasons including performance and configuration flexibility
- Pgpool facilitates connections to the cluster
- Database nodes use PersistentVolumes for their storage, so the DB engine pod can be upgraded
- If necessary, can take a snapshot of PersistentVolumes and mount to another system (e.g., migrate to a VM and mount the database storage)
   - This assumes that `pg_dump` would not be performant enough for extremely large data sets, so storage snapshots would be more feasible
   - Another potential solution to ensure consistency: Create a K8s CronJob that connects the the database, does a PostgreSQL CHECKPOINT to flush everything to disk and then calls GCP API to snapshot the underlying PV disk.
- Helm release values can be used to alter DB configuration (ConfigMaps)
- StatefulSet scale can be changed to change cluster size
- Can set resource requests & limits to add CPU & memory
- **Database can be monitored**

## Notes

### Cloud Run

- does not run within project's VPC
- might be able to restrict IP access (whitelist) using a [Network Endpoint Group](https://cloud.google.com/load-balancing/docs/negs/)

### GKE

- [Network Overview](https://cloud.google.com/kubernetes-engine/docs/concepts/network-overview)
- Can use an Internal Load Balancer attached to a K8s service to manage traffic coming from within the same VPC network.
- [Citus K8s support](https://github.com/citusdata/citus/issues/425)
- [how do I add a firewall rule to a gke service?](https://stackoverflow.com/questions/53455197/how-do-i-add-a-firewall-rule-to-a-gke-service)

### App Engine

- Standard mode does not run within project's VPC (Flex mode does)

## Assumptions

1. On-premises deployment is out of scope for this exercise. But must be deployable on GCP by customers into their VPCs.
1. This is not intended to handle massive traffic or amounts of data but could be scaled to do so. This implementation is not multi-region.
1. This needs to run in GCP. (Of AWS/Azure/GCP I am by far the least knowledgable about GCP so I had to do a lot of research to translate what I know from the other two.)

## Future Enhancements
1. Use CitusDB instead of PostgreSQL. This may also result in a move from running the database on K8s to running on VMs. Would need more/different bootstrapping to bring a cluster and manage nodes and data.
1. Use DNS to provide friendly URLs for the API.
1. Use TLS to secure API acccess. Ensure that connections to the database are encrypted.
1. If app continues to run in K8s, potentially package as a Helm chart for easier customer adoption and to further enforce open/close principal.

## Options

### Database

- Cloud SQL (with [proxy](https://cloud.google.com/sql/docs/mysql/connect-kubernetes-engine))
- PostgreSQL (+Citus) on Compute Engine
- PostgreSQL on GKE?
- Citus DB on GKE (https://hub.docker.com/r/citusdata/citus & https://github.com/citusdata/docker); appears to support clustering with docker-compose
- [Use Azure Arc to deploy on GCP K8s?](https://docs.microsoft.com/en-us/azure/azure-arc/data/create-postgresql-hyperscale-server-group)
- [Crunchy Data PostgreSQL K8s Operator](https://github.com/CrunchyData/postgres-operator)
- [Azure Arc](https://azure.microsoft.com/en-us/services/azure-arc/hybrid-data-services/#pricing) is a way to run Citus on K8s
- [Postgres HA on Compute Engine](https://github.com/chrisbelyea/trm-takehome-data-eng)
- [How to deploy a PostgreSQL Cluster on Kubernetes + OpenEBS](https://containerized.me/how-to-deploy-a-postgresql-cluster-on-kubernetes-openebs/)


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

Prometheus to StackDriver?

### What is the HA/disaster recovery process?

RTO/RPO?

### What is the regular deployment process?

Distinguish between TRM Labs publishing, and

### How would you apply security patches or other updates?
VERIFY THAT DEPLOYMENT SPECIFIES ROLLING UPDATES

### How would you extend your deployment if we had to add additional services (e.g., message queues, caching, etc)?
