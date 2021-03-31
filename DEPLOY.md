# Deployment instructions
Instructions on how to build and deploy the solution.

## GCP Infrastructure
You'll need to build the following infrastructure, which will require Google Cloud SDK installed and configured.
- Container Registry
- GKE Cluster

You'll need to enable APIs in the Console or with `gcloud` as appropriate, e.g. `gcloud services enable container.googleapis.com`.

### Build Container Registry


### Build GKE Cluster
Build a new GKE Cluster with Autopilot mode enabled.

> I started to do this with Terraform, but then discovered [it wasn't _quite_ available yet](https://github.com/hashicorp/terraform-provider-google/issues/8553#issuecomment-810623650). I would always recommend defining infrastructure in code versus using CLI commands; definitely a future enhancement.

```shell
gcloud container clusters create-auto exercise1 --region us-east4 --project=trm-takehome-chris-b
```

## Docker Image
Images _should_ have appropriate labels to allow for rolling deployment updates.

### GCP Cloud Registry
```shell
export PROJECT=trm-takehome-chris-b
docker build -t gcr.io/$PROJECT/trmapp .
docker push gcr.io/$PROJECT/trmapp
```

### Local
Useful for testing.
```shell
# Export environment variables as needed
docker build -t chrisbelyea/trmapp .
docker run --rm -p 8080:8080 -e DB_HOST=$DB_HOST -e DB_PASS=$DB_PASS -e DB_USER=$DB_USER chrisbelyea/trmapp
curl -4 http://127.0.0.1:8080/address/exposure/direct?address=1BQAPyku1ZibWGAgd8QePpW1vAKHowqLez
```

## Kubernetes Resources
Create these resources in K8s to get everything running.

## Database
The PostgreSQL database is deployed using Bitnami's [postgresql-ha](https://artifacthub.io/packages/helm/bitnami/postgresql-ha) chart. It's not CitusDB, and it might not be the _best_ way to do it, but for the purposes of this exercise it's the most expedient. Since `helm` is already installed there, it's easiest to deploy this using GCP's Cloud Shell.

> Beyond the factors mentioned here, any serious use would likely need a highly-performant storage class configured.

```shell
# Get K8s cluster credentials
gcloud container clusters get-credentials exercise1 --region us-east4 --project trm-takehome-chris-b

# Create a K8s namespace for the database
kubectl create namespace trmdb1

# Add the Bitnami chart repo
helm repo add bitnami https://charts.bitnami.com/bitnami

# Deploy the chart
helm install dbproto bitnami/postgresql-ha --namespace trmdb1
```

This could take a few minutes to come up. Once it does, note the following values (you'll need these for the App step, note if you switch between Cloud Shell & local):

- **DB (Pgpool) target.** This will be output by Helm but can also be constructed with the following.
  ```shell
  SVCNAME=$(kubectl --namespace trmdb1 get services -l app.kubernetes.io/component=pgpool -o jsonpath="{.items[0].metadata.name}")
  SVCNS=$(kubectl --namespace trmdb1 get services -l app.kubernetes.io/component=pgpool -o jsonpath="{.items[0].metadata.namespace}")
  export DB_HOST=$SVCNAME.$SVCNS.svc.cluster.local
  ```
- **DB Password.** For any meaningful use, a separate user should be created in the database with only enough privileves to allow the app to `SELECT` the information it needs to respond to its `GET` requests. But for now, capture the `postgres` user password.
  ```shell
  export POSTGRES_PASSWORD=$(kubectl get secret --namespace trmdb1 dbproto-postgresql-ha-postgresql -o jsonpath="{.data.postgresql-password}" | base64 --decode)
  ```

## App
To deploy the app (which depends on the database to already exist) you must create the database secret and the app deployment. This can be run locally (you'll need to get K8s cluster credentials; see section above) or in Cloud Shell, but you'll need the repo cloned wherever you are.

### Namespace
Create a namespace for the app.
```shell
kubectl create namespace trmapp1
```

### Database Secret
Before deploying the app in K8s, the database secret must be created. The secret contains the database credentials and hostname. The hostname could have been captured as a separate ConfigMap since it isn't sensitive, but for simplicity they're all together in the secret since they'll probably have a similar lifecycle.

```shell
kubectl --namespace trmapp1 create secret generic database \
  --from-literal=username=postgres \
  --from-literal=password=$POSTGRES_PASSWORD \
  --from-literal=host=$DB_HOST
```

### App
To deploy the app, simply run
```shell
kubectl apply -f trmapp.yaml
```
to deploy the app's namespace and deployment.

> The `loadBalancerSourceRanges` list in the YAML can be altered to allow inbound access from selected networks.

## Validate
To validate the app, `curl` the internal and external endpoints.

### Internal endpoint
The `curl` command needs to be run from some system in the VPC, like a VM.
```shell
# Get the endpoint
export INTERNAL_ENDPOINT=$(kubectl --namespace trmapp1 get service trmapp1-service --output jsonpath="{.status.loadBalancer.ingress[0].ip}")
echo "Internal endpoint: $INTERNAL_ENDPOINT"

# curl it; this must be done from a VM in the VPC
curl http://$INTERNAL_ENDPOINT/address/exposure/direct?address=1BQAPyku1ZibWGAgd8QePpW1vAKHowqLez
```

### External endpoint
```shell
# Get the endpoint
export EXTERNAL_ENDPOINT=$(kubectl --namespace trmapp1 get ingress trmapp1-ingress-external --output json | jq -r .status.loadBalancer.ingress[0].ip)
echo "External endpoint: $EXTERNAL_ENDPOINT"

# curl it
curl http://$EXTERNAL_ENDPOINT/address/exposure/direct?address=1BQAPyku1ZibWGAgd8QePpW1vAKHowqLez
```

## Expected output
In both internal and external cases, the output should be the same. Note the new `database` key; the only entry in that list should be returned live from the database.

```json
{
  "data": [
    {
      "address": "1FGhgLbMzrUV5mgwX9nkEeqHbKbUK29nbQ",
      "inflows": "0",
      "outflows": "0.01733177",
      "total_flows": "0.01733177"
    },
    {
      "address": "1Huro4zmi1kD1Ln4krTgJiXMYrAkEd4YSh",
      "inflows": "0.01733177",
      "outflows": "0",
      "total_flows": "0.01733177"
    }
  ],
  "database": [
    "PostgreSQL 11.11 on x86_64-pc-linux-gnu, compiled by gcc (Debian 8.3.0-6) 8.3.0, 64-bit"
  ],
  "success": true
}
```
