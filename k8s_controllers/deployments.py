import random

import pandas as pd

from k8s_controllers.pod import PodsActions 
from kubernetes import client, config
from kubernetes.stream import stream
from kubernetes.client.rest import ApiException


class DeploymentActions:
    
    def __init__(self):
        self.core_api = client.CoreV1Api()
        self.app_api = client.AppsV1Api()
        self.pod = PodsActions()
        
        
    def list_deployments(self):
        "List the deployments within a namespace specified by the user"
        namespace_names = self.pod.list_namespaces()
        namespace_choice = input("Enter your number choice: ").strip()
    
        if namespace_choice and 1 <= int(namespace_choice) <= len(namespace_names):
            selected_namespace = namespace_names[int(namespace_choice) - 1]
        else:
            selected_namespace = "default"
    
        deployment_data = []
    
        try:
            deployments = self.app_api.list_namespaced_deployment(selected_namespace)
            
            for deployment in deployments.items:
                image_version = deployment.spec.template.spec.containers[0].image.split(":")[-1]
    
                deployment_info = {
                    "Name": deployment.metadata.name,
                    "Replicas": deployment.spec.replicas,
                    "Version": image_version,
                    "Namespace": selected_namespace  # Include the namespace in the table
                }
                deployment_data.append(deployment_info)
    
            # Create a DataFrame with the correct column order
            df = pd.DataFrame(deployment_data, columns=["Name", "Replicas","Version", "Namespace"])
    
            # Print the information in a tabular format
            print("\nAvailable Deployments: \n")
            print(df)
            return deployment_data
                
        except Exception as e:
            print(f"Error: {e}")


    def create_deployment(self):
        "creates deployment based on the image selected by the user"
        while True:
            print("\nSelect an Image to Deploy")
            print("1. nginx:1.22.1")
            print("2. busybox:1.34.1")
            print("3. Exit")
            
            image_dict = {"1": "nginx:1.22.1", "2": "busybox:1.34.1"}
            
            image_input = input("\nEnter your choice: ").strip()
            
            if image_input in image_dict:
                image_name_with_tag = image_dict[image_input]
                default_image_name = image_name_with_tag.split(":")[0]
                random_number = random.randint(1, 9999)
                modified_pod_name = f"{default_image_name}{random_number}"
                image_name = input(f"Enter the image name for this deployment (default: {modified_pod_name}): ").strip() or modified_pod_name 
                
                try:
                    deployment_name = f"{image_name}-deployment"
                    app_label = f"{image_name}-app"
                    container_image = image_input
                    
                    # Set container port or command based on the chosen image
                    if image_input == "1":  # nginx
                        container_port = 80
                        command = None
                    elif image_input == "2":  # busybox
                        container_port = 81
                        command = ["tail", "-f", "/dev/null"] #added this so that the image keeps running as its not a server.
                    else:
                        print("Invalid image choice.")
                        continue
                    
                    deployment = client.V1Deployment(
                        api_version="apps/v1",
                        kind="Deployment",
                        metadata=client.V1ObjectMeta(name=deployment_name),
                        spec=client.V1DeploymentSpec(
                            replicas=2,
                            selector=client.V1LabelSelector(match_labels={"app": app_label}),
                            template=client.V1PodTemplateSpec(
                                metadata=client.V1ObjectMeta(labels={"app": app_label}),
                                spec=client.V1PodSpec(
                                    containers=[
                                        client.V1Container(
                                            name=image_name,
                                            image=image_name_with_tag,
                                            ports=[client.V1ContainerPort(container_port=container_port)],
                                            command=command
                                        )
                                    ]
                                )
                            )
                        )
                    )
                    
                    resp = self.app_api.create_namespaced_deployment(
                        body=deployment, namespace="default"
                    )
                    
                    print(f"\nDeployment created. Status='{resp.metadata.name}'")
                    return
                    
                except ApiException as e:
                    print(f"Error creating deployment: {e}")
                    
            elif image_input == "3":
                return
            else:
                print("Invalid choice. Please select a valid option.")
                
    def scale_deployment_util(self):
        "A method utilized to scale deployment"
        deployment_list = self.list_deployments()
        
        if not deployment_list:
            print("No deployments found.")
            return
    
        while True:
            deployment_index = input("Enter your number choice: ").strip()
            
            if deployment_index.lower() == 'exit':
                break  # Exit the loop
    
            try:
                deployment_choice = int(deployment_index)
                if 0 <= deployment_choice <= len(deployment_list):
                    deployment_info = deployment_list[deployment_choice]
                    deployment_name = deployment_info["Name"]
                    deployment_namespace = deployment_info["Namespace"]
                
                    return deployment_name, deployment_namespace
                else:
                    print("Invalid pod choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a valid number or 'exit'.")
        
    def scale_deployment(self):
        "It increases or reduces number of replica in a deployment"
        
        deployment_name, deployment_namespace = self.scale_deployment_util()
                
        replica_choice = input("\nEnter the number of Replicas: ").strip()
        try:
            replica_count = int(replica_choice)
            resp = self.app_api.patch_namespaced_deployment_scale(
                name=deployment_name, namespace=deployment_namespace, body={"spec": {"replicas": replica_count}}
            )
            print(f"Deployment scaled. Replicas='{resp.spec.replicas}'")
        except Exception as ex:
            print(f"Error scaling deployment: {ex}")
        
    
    def update_deployment(self):
        "Performs a rolling update on a deployment."
        try:
            deployment_name, deployment_namespace = self.scale_deployment_util()
        
            new_image_version = input("Enter new version to deploy: ").strip()
    
            # Get the current deployment
            current_deployment = self.app_api.read_namespaced_deployment(name=deployment_name, namespace=deployment_namespace)
    
            # Update the image version in the deployment
            current_deployment.spec.template.spec.containers[0].image = new_image_version
    
            # Perform the rolling update
            resp = self.app_api.patch_namespaced_deployment(
                name=deployment_name,
                namespace="default",
                body=current_deployment
            )
    
            print(f"\nRolling update initiated for Deployment '{deployment_name}'. Status='{resp.metadata.name}'")
    
        except ApiException as e:
            print(f"Error performing rolling update: {e}")
            
            
    def delete_deployment(self):
        "Deletes a deployment"
        try:
            deployment_name, deployment_namespace = self.scale_deployment_util()
    
            # Delete the deployment
            self.app_api.delete_namespaced_deployment(name=deployment_name, namespace=deployment_namespace)
    
            print(f"\nDeployment '{deployment_name}' in namespace '{deployment_namespace}' deleted successfully.")
    
    
        except ApiException as e:
            print(f"Error deleting deployment: {e}")


def manage_deployments():
    "provides an interactive menu for managing deployments"
    
    config.load_kube_config()
    action = DeploymentActions()
    while True:
        print("\nSelect a Deployment Action")
        print("1. List Deployments")
        print("2. Create Deployment")
        print("3. Scale Deployment")
        print("4. Update Deployment")
        print("5. Delete Deployment")
        print("6. Back to 'Docker Actions' Menu")
        
        choice = input("Enter your choice: ")
        if choice == "1":
            action.list_deployments()
        elif choice == "2":
            action.create_deployment()
        elif choice == "3":
            action.scale_deployment()
        elif choice == "4":
           action.update_deployment()
        elif choice == "5":
           action.delete_deployment()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please select a valid option.")
