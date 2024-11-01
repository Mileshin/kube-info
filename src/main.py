from flask import Flask, request, jsonify
from kubernetes import client, config
import logging

app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)

## Load Kubernetes configuration

try:
    # This only works in k8s pods
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

v1 = client.CoreV1Api()


def get_external_ip(node, ip_version='ipv4'):
    """
    Helper function to get external IP of a node based on IP version.
    """
    for address in node.status.addresses:
        if address.type == 'ExternalIP':
            if ip_version == 'ipv4' and '.' in address.address:
                return address.address
            elif ip_version == 'ipv6' and ':' in address.address:
                return address.address
    return None


@app.route('/node-external-ip', methods=['GET'])
@app.route('/node-external-ip/<node_name>', methods=['GET'])
async def get_node_exteranl_ip(node_name=None):
    """
    Endpoint to get node information with external IPs.
    Supports filtering by IP version.
    """
    try:
        ip_version = request.args.get('ip_version', 'ipv4').lower()
        
        if node_name:
            node = v1.read_node(name=node_name)
            external_ip = get_external_ip(node, ip_version=ip_version)
                    
            if not external_ip:
                logging.warning(f"External IP not found for node: {node_name}")
                return jsonify({"error": "External IP not found"}), 404
            
            return jsonify({"node_name": node_name, "external_ip": external_ip})
        else:
            nodes = v1.list_node()
            node_ips = [
                        {
                            "node_name": node.metadata.name,
                            "external_ip": get_external_ip(node, ip_version=ip_version)
                        }
                        for node in nodes.items if get_external_ip(node, ip_version=ip_version)
                    ]
            if not node_ips:
                logging.warning("No external IPs found for nodes")
                return jsonify({"error": "No external IPs found"}), 404
            return jsonify(node_ips)
    except client.exceptions.ApiException as e:
        logging.error(f"Kubernetes API exception: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

## Get nodeports
@app.route('/nodeports', methods=['GET'])
async def get_nodeports():
    """
    Endpoint to list NodePort services in specified namespace and with label selector.
    """
    try:
        namespace = request.args.get('namespace', '') or None
        label_selector = request.args.get('label_selector', '') or None
    
        services = (v1.list_namespaced_service(namespace, label_selector=label_selector)
                            if namespace else v1.list_service_for_all_namespaces(label_selector=label_selector))
        
        nodeports = []
        for svc in services.items:
            if svc.spec.type == 'NodePort':
            # We need to use a loop because V1ServicePort is not in JSON format
                for port in svc.spec.ports:
                        nodeports.append({
                            "name": svc.metadata.name,
                            "namespace": svc.metadata.namespace,
                            "port_name": port.name,
                            "port": port.port,
                            "node_port": port.node_port,
                            "protocol": port.protocol,
                            "target_port": port.target_port
                        })
        if not nodeports:
            logging.info("No NodePort services found")
            return jsonify({"error": "No NodePort services found"}), 404
        return jsonify(nodeports)
    except client.exceptions.ApiException as e:
        logging.error(f"Kubernetes API exception: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
