import random

from kubernetes import client, config
from kubernetes.stream import stream

from kubernetes.client.rest import ApiException
import pandas as pd

class PodsActions:
    "implements methods for interacting with kubernetes Pods"
    
    def __init__(self):
        self.core_api = client.CoreV1Api()
        self.app_api = client.AppsV1Api()
        
        
    def list_pods(self):
        "Lists the pods within a namespace"
        
        try:
            namespace_names = self.list_namespaces()
            selected_namespace = self.get_selected_namespace(namespace_names)
            pod_names = self.get_pods_in_namespace(selected_namespace)
    
            print(f"\nAvailable Pods in the {selected_namespace} Namespace:")
            for i, pod in enumerate(pod_names, start=1):
                print(f"{i}. {pod}")
    
            return pod_names, selected_namespace
    
        except ApiException as ex:
            print(f"Error listing pods: {ex}")
    
    
    def list_namespaces(self):
        "lists all the namespaces at the kubernetes cluster"
    
        pods = self.core_api.list_pod_for_all_namespaces(watch=False)
        namespace_names = list(sorted(set([pod.metadata.namespace for pod in pods.items])))
        
        # Ask the user to choose a namespace 
        print("\nChoose from Available Namespaces:")
        for i, ns in enumerate(namespace_names, start=1):
            print(f"{i}. {ns}")
            
        return namespace_names
        
    def get_selected_namespace(self, namespace_names):
        "Fetches the namespace selected by the user"
        try:
            namespace_choice = input("Enter your number choice: ").strip()
            if namespace_choice.isdigit() and 1 <= int(namespace_choice) <= len(namespace_names):
                return namespace_names[int(namespace_choice) - 1]
        except ValueError as ex:
            print("Error: Unable to validate the input due to - ", ex)  # 
    
        return "default"      
    
    def get_pods_in_namespace(self, selected_namespace):
        "Fetches the pods within a namespace"
        try:
            pods = self.core_api.list_namespaced_pod(namespace=selected_namespace, watch=False)
            return [pod.metadata.name for pod in pods.items]
        except ApiException as ex:
            print(f"Error listing pods: {ex}")
            return []

    def describe_pod(self):
        "Describes a pod attributes."
        try:
            pod_list, selected_namespace = self.list_pods()
    
            while True:
                podname_index = self.get_valid_input("Enter your number choice (or 'exit' to quit): ",
                                                lambda x: x.lower() == 'exit' or self.is_valid_pod_index(x, pod_list))
    
                if podname_index.lower() == 'exit':
                    break  # Exit the loop
    
                selected_podname = pod_list[int(podname_index) - 1]
    
                pod = self.core_api.read_namespaced_pod(name=selected_podname, namespace=selected_namespace)
    
                verbosity = self.get_valid_input("Enter 'verbose' for detailed description or 'short' for an abridged version: ",
                                            lambda x: x.lower() in ['verbose', 'short'])
    
                if verbosity == 'verbose':
                    print(pod)
                elif verbosity == 'short':
                    print(f"\nPod Name: {pod.metadata.name}, Namespace: {pod.metadata.namespace}")
                    print(f"Host IP: {pod.status.host_ip}")
                    print(f"Pod IP: {pod.status.pod_ip}")
                    print(f"Image: {pod.spec.containers[0].image}")
                    print(f"Container Name: {pod.spec.containers[0].name}")
                    print(f"Creation Timestamp: {pod.metadata.creation_timestamp}")
                else:
                    print("Invalid verbosity option. Please enter 'verbose' or 'short.'")
    
        except ApiException as ex:
            print(f"Error describing pod: {ex}")
        except Exception as ex:
            print(f"An unexpected error occurred: {ex}")
            
    def get_valid_input(self, prompt, validator):
        "Validates the value specified by the user when choosing a pod."
        while True:
            user_input = input(prompt).strip()
            if validator(user_input):
                return user_input
            else:
                print("Invalid input. Please try again.")

    def is_valid_pod_index(self,value, pod_list):
        "validates the pod index specified by the user when choosing a pod"
        
        try:
            pod_index = int(value)
            return 1 <= pod_index <= len(pod_list)
        except ValueError:
            return False

    def execute_command(self):
        "Executes a shell command on a pod specified by the user"
        try:
            pod_list, selected_namespace = self.list_pods()
    
            selected_podname = self.get_pod_choice(pod_list)
    
            if selected_podname is None:
                return  # Exit if 'exit' is chosen
    
            container_names = self.get_containers_in_pod(selected_podname, selected_namespace)
            container_name = container_names[0] if container_names else None
    
            if not container_name:
                print("No containers found in the selected pod.")
                return
            
            while True: 
                exec_command = ['/bin/sh']
                resp = stream(self.core_api.connect_get_namespaced_pod_exec,
                              name=selected_podname,
                              namespace=selected_namespace,
                              command=exec_command,
                              container=container_name,
                              stdin=True,
                              stdout=True,
                              stderr=True,
                              tty=False,
                              _preload_content=False)
        
                command = input("\nEnter the command to run (or 'exit' to quit): ").strip()
                
                if command.lower() == 'exit':
                    return None
        
                count = 0
                count2 = 2
                responseCommandFull=""
                resp.write_stdin(command)
                
                while resp.is_open():
                    print("WHILEEEE ::: %s"%resp.is_open())
                    resp.update(timeout=1)
                    if resp.peek_stdout():
                        count = count+1
                        responseCom = resp.read_stdout()
                        print("STDIN :: %s"%responseCom)
                        #if len(responseCom)!= 1:
                        responseCommandFull="%s\n%s"%(responseCommandFull,responseCom)
                    if resp.peek_stderr():
                        count = count+1
                        responseCom = resp.read_stderr()
                        print("STDERR :: %s"%responseCom)
                        responseCommandFull="%s\n%s"%(responseCommandFull,responseCom)
                    else:
                        if count2 == count:
                                print("Executing command sucessfully.")
                                break
                        count2 = count
                resp.close()
                print(responseCommandFull)
                
        except ApiException as e:
            print(f"Error executing command: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            
    def get_pod_choice(self, pod_list):
        "Fetches the pod selected by the user"
        while True:
            podname_index = self.get_valid_input("\nEnter your number choice (or 'exit' to quit): ",
                                            lambda x: x.lower() == 'exit' or x.isdigit() and 1 <= int(x) <= len(pod_list))
    
            if podname_index.lower() == 'exit':
                return None
            else:
                return pod_list[int(podname_index) - 1]

    def get_containers_in_pod(self, pod_name, namespace):
        "Fetches the containers inside a pod"
        try:
            # Retrieve the pod information
            pod = self.core_api.read_namespaced_pod(name=pod_name, namespace=namespace)
    
            # Extract container names from the pod's spec
            container_names = [container.name for container in pod.spec.containers]
    
            return container_names
    
        except Exception as e:
            print(f"Error getting containers in pod: {e}")
         
    def create_pods(self):
        "creates a pod at different worker node"
        try:
            user_image_with_tag = input("Enter the container image: ").strip()
            user_image = user_image_with_tag.split(":")[0]
            default_podname = f"{user_image}-pod"
            user_pod_name = input(f"Enter the pod name (default is {default_podname}): ").strip() or default_podname
            print("")
            
            namespace_names = self.list_namespaces()
            namespace_choice = input("\nEnter your number choice: ").strip()
            
            if namespace_choice and 1 <= int(namespace_choice) <= len(namespace_names):
                selected_namespace = namespace_names[int(namespace_choice) - 1]
            else:
                selected_namespace = "default"
    
            # Get the list of nodes
            nodes = self.core_api.list_node().items
    
            for node in nodes:
                # Skip master nodes
                if "node-role.kubernetes.io/master" in node.metadata.labels:
                    continue
    
                node_name = node.metadata.name
    
                # Check if the modified pod name already exists
                while True:
                    random_number = random.randint(1, 9999)
                    modified_pod_name = f"{user_pod_name}{random_number}"
    
                    # Query existing pods to check for name collision
                    existing_pods = self.core_api.list_namespaced_pod(namespace=selected_namespace).items
                    existing_pod_names = [pod.metadata.name for pod in existing_pods]
    
                    if modified_pod_name not in existing_pod_names:
                        break  # The modified pod name is unique, exit the loop
    
                # Specify the pod definition
                pod_manifest = {
                    "apiVersion": "v1",
                    "kind": "Pod",
                    "metadata": {"name": modified_pod_name},
                    "spec": {
                        "containers": [
                            {
                                "name": f"{user_image}-container",
                                "image": user_image_with_tag,
                                # Add more container settings as needed
                            }
                        ]
                    }
                }
    
                # Add node selector to the pod manifest to deploy it on a specific node
                pod_manifest['spec']['nodeSelector'] = {'kubernetes.io/hostname': node_name}
    
                # Create the pod
                self.core_api.create_namespaced_pod(namespace=selected_namespace, body=pod_manifest)
    
                print(f"Pod '{modified_pod_name}' created successfully on node '{node_name}' in '{selected_namespace}' namespace")

        except Exception as ex:
            print(f"Error creating pod: {ex}")
    

def manage_pods():
    "provides an interactive menu for managing pods"
    
    config.load_kube_config()
    action = PodsActions()
    while True:
        print("\nSelect an 'Interact with Pods' Action")
        print("1. List All Pods")
        print("2. Describe Pods")
        print("3. Execute Pod Command")
        print("4. Create Pod on Worker Nodes")
        print("5. Back to 'Docker Actions' Menu")
        
        choice = input("Enter your choice: ")
        if choice == "1":
            action.list_pods()
        elif choice == "2":
            action.describe_pod()
        elif choice == "3":
            action.execute_command()
        elif choice == "4":
           action.create_pods()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please select a valid option.")
