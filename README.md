# kube_info

The `kube_info` service is designed to act as a real-time proxy for retrieving essential cluster data from the Kubernetes API. It does not rely on caching or scheduled data collection; instead, it queries the Kubernetes API directly whenever a request is made. This ensures that the information retrieved reflects the current state of the cluster.

## Node Info and NodePorts API

This API enables you to gather information about Kubernetes nodes and services of the `NodePort` type. It is built using Flask and communicates directly with the Kubernetes API.

### API Endpoints

#### 1. Get Node Information

##### **GET** `/node-external-ip`
- **Description**: Retrieves the external IP addresses for all nodes in the Kubernetes cluster.
- **Response**: Returns a list of nodes, each with its name and associated external IP address.

##### Example Request:
```bash
curl -X GET http://<service-ip>:8080/node-external-ip
```

##### Example Response:
```json
[
    {
        "external_ip": "xxx.xxx.xxx.xxx",
        "node_name": "node-1"
    },
    {
        "external_ip": "yyy.yyy.yyy.yyy",
        "node_name": "node-2"
    },
    {
        "external_ip": "zzz.zzz.zzz.zzz",
        "node_name": "node-3"
    }
]
```

#### **GET** `/node-external-ip/<node_name>`
- **Description**: Retrieves the external IP address for a specific node by its name.
- **Path Parameter**:
  - `node_name`: Name of the node for which information is requested.
- **Response**: Returns the external IP address and name of the specified node.

##### Example Request:
```bash
curl -X GET http://<service-ip>:8080/node-external-ip/node-1
```

##### Example Response:
```json
{
    "external_ip": "xxx.xxx.xxx.xxx",
    "node_name": "node-1"
}
```

#### 2. Get NodePort Services

##### **GET** `/nodeports`
- **Description**: Retrieves a list of services of type `NodePort`. The results can be filtered by namespace and labels.
- **Query Parameters**:
  - `namespace` (optional): Filter services by the specified namespace.
  - `label_selector` (optional): A comma-separated list of labels to filter services by, such as `app.kubernetes.io/component=myapp,app.kubernetes.io/instance=myapp`.
- **Response**: Returns a list of NodePort services with details for each.

##### Example Request (all namespaces, no label filter):
```bash
curl -X GET http://<service-ip>:8080/nodeports
```

##### Example Request (specific namespace):
```bash
curl -X GET "http://<service-ip>:8080/nodeports?namespace=default"
```

##### Example Request (namespace and label filter):
```bash
curl -X GET "http://<service-ip>:8080/nodeports?namespace=myapp&label_selector=app.kubernetes.io/component=server,app.kubernetes.io/instance=myapp"
```

##### Example Response:
```json
[
    {
        "name": "myapp-server-http-nodeport",
        "namespace": "myapp",
        "node_port": 30180,
        "port": 8080,
        "port_name": "http",
        "protocol": "TCP",
        "target_port": 80
    }
]
```

---

### Notes
- This API depends on Kubernetes in-cluster configuration, meaning it should be deployed within a Kubernetes cluster.
- Ensure that the service account running this application has appropriate permissions to list nodes and services within the cluster.

## Checking API

You can forward the service port to localhost to test the API:

```bash
kubectl port-forward service/nodeinfo-service 8080:8080 -n kube-info

curl -X GET http://localhost:8080/node-external-ip
```

Alternatively, create a temporary pod to test API access within the cluster:

```bash
kubectl run curl-pod --rm -it --image=curlimages/curl:8.9.1 -- curl http://kubeinfo-service.kube-info.svc.cluster.local:8080/node-external-ip
```

## Helm

This Helm chart deploys a DaemonSet named `kube-info` and configures the necessary roles, role bindings, and ServiceAccount for proper operation.  
The service is deployed using a DaemonSet.

**Required permissions:**

- **Resources**: `nodes`, `services`, `pods`
- **Actions**: `get`, `list`, `watch`
- **Access level**: cluster-wide (`ClusterRole`)

These permissions allow the `DaemonSet` to retrieve information about the specified resources in the cluster.

**Chart installation:**

```bash
helm install kube-info ./kube-info -n <namespace> --values values.yaml
```

**Chart removal:**

```bash
helm uninstall kube-info -n <namespace>
```