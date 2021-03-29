# Deployment instructions
Instructions on how to build and deploy the solution.

## GCP Infrastructure
You'll need to build the following infrastructure.
- Cloud Registry
- GKE Cluster

## Docker Image
Images _should_ have appropriate labels to allow for rolling deployment updates.

### GCP Cloud Registry
```shell
export PROJECT=<GCP project name>
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
The PostgreSQL database is deployed using Bitnami's [postgresql-ha](https://artifacthub.io/packages/helm/bitnami/postgresql-ha) chart. It's not CitusDB, and it might not be the _best_ way to do it, but for the purposes of this exercise it's the most expedient. Since `helm` is already installed there, deploy this using GCP's Cloud Shell.

> Beyond the factors mentioned here, any serious use would likely need a highly-performant storage class configured.

```shell
# Add the Bitnami chart repo
helm repo add bitnami https://charts.bitnami.com/bitnami
# Deploy the chart
helm install dbproto bitnami/postgresql-ha --namespace trmdb1
```

This could take a few minutes to come up. Once it does, note the following values:

- **DB (Pgpool) target.** This will be output by Helm but can also be constructed with the following.
  ```shell
  SVCNAME=$(kubectl --namespace trmdb1 get services -l app.kubernetes.io/component=pgpool -o jsonpath="{.items[0].metadata.name}")
  SVCNS=$(kubectl --namespace trmdb1 get services -l app.kubernetes.io/component=pgpool -o jsonpath="{.items[0].metadata.namespace}")
  export DB_HOST=$SVCNAME.$SVCNS.svc.cluster.local
  ```
- **DB Password.** For any meaningful use, a separate user should be created in the database with only enough privileves to allow the app to `SELECT` the information it needs to respond to its `GET` requests. But for now, capture the `postgres` user password.
  ```shell
  export POSTGRES_PASSWORD=$(kubectl get secret --namespace trmdb1 trmdb-postgresql-ha-postgresql -o jsonpath="{.data.postgresql-password}" | base64 --decode)
  ```

## App
To deploy the app (which depends on the database to already exist) you must create the database secret and the app deployment.

### Database Secret
Before deploying the app in K8s, the database secret must be created. The secret contains the database credentials and hostname. The hostname could have been captured as a separate ConfigMap since it isn't sensitive, but for simplicity they're all together in the secret since they'll probably have a similar lifecycle.

```shell
kubectl --namespace trmapp1 create secret generic database \
  --from-literal=username=postgres \
  --from-literal=password='<PASSWORD GOES HERE>' \
  --from-literal=host='<DB HOSTNAME OR IP GOES HERE>'
```

### App
To deploy the app, simply run
```shell
kubectl apply -f trmapp.yaml
```
to deploy the app's namespace and deployment.

> The `loadBalancerSourceRanges` list in the YAML can be altered to allow inbound access from selected networks.
