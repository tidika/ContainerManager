from kubernetes import client, config


class ServicesActions:
    def __init__(self):
        self.core_api = client.CoreV1Api()
        self.app_api = client.AppsV1Api()

    def create_deployment(self, name, image, replicas, env_vars):
        "creates a deployment"
        
        deployment_manifest = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {"name": name},
                "spec": {
                    "replicas": replicas,
                    "selector": {"matchLabels": {"app": name}},
                    "template": {
                        "metadata": {"labels": {"app": name}},
                        "spec": {
                            "containers": [{
                                "name": name,
                                "image": image,
                                "env": [{"name": key, "value": value} for key, value in env_vars.items()],
                            }]
                        }
                    }
                }
            }
        self.app_api.create_namespaced_deployment(namespace="default", body=deployment_manifest)

    def create_service(self, name, selector, service_type, ports):
        "creates a service"
        
        service_manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": name},
            "spec": {
                "selector": selector,
                "ports": [{"protocol": "TCP", "port": port} for port in ports],
                "type": service_type
            }
        }

        self.core_api.create_namespaced_service(namespace="default", body=service_manifest)

    def orchestrate_services(self):
        "Orchestrates Deployment and Services for WordPress and MySQL"
        try:
    
            # Create MySQL Deployment
            self.create_deployment("mysql", "mysql:5", replicas=2, env_vars={"MYSQL_ROOT_PASSWORD": "root"})
    
            # Create WordPress Deployment
            self.create_deployment("web", "vulhub/wordpress:4.6", replicas=2, env_vars={
                "WORDPRESS_DB_HOST": "mysql:3306",
                "WORDPRESS_DB_USER": "root",
                "WORDPRESS_DB_PASSWORD": "root",
                "WORDPRESS_DB_NAME": "wordpress"
            })
    
            # Create MySQL Service
            self.create_service("mysql", selector={"app": "mysql"}, service_type="ClusterIP", ports=[3306])
    
            # Create WordPress Service with LoadBalancer
            self.create_service("web", selector={"app": "web"}, service_type="LoadBalancer", ports=[80])
    
            print("WordPress and MySQL Services deployed successfully.")
    
        except Exception as e:
            print(f"Error: {e}")
            
def manage_services():
    "provides an interactive menu for managing services"
    
    config.load_kube_config()
    action = ServicesActions()
    while True:
        print("\nSelect an 'Interact with Pods' Action")
        print("1. Run WordPress Microservice")
        print("2. Back to 'Docker Actions' Menu")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            action.orchestrate_services()
        elif choice == "2":
            break
        else:
            print("Invalid choice. Please select a valid option.")


