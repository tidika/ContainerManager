import os

import docker

class InteractWithDockerActions:
    
    def __init__(self):
        self.client = docker.from_env()
    
    def list_all_containers(self):
        """List all containers"""
        try:
            containers = self.client.containers.list()
            print("All Containers:")
            for container in containers:
                print(f"Container ID: {container.id}, Name: {container.name}")
        except docker.errors.APIError as e:
            print(f"Error: Unable to list all containers - {e}")
            
    def list_stopped_containers(self):
        """List all stopped/exited containers"""
        try:
            stopped_containers = self.client.containers.list(filters={'status': 'exited'})
            print("Stopped/Exited Containers:")
            for container in stopped_containers:
                print(f"Container ID: {container.id}, Name: {container.name}")
        except docker.errors.APIError as ex:
            print(f"Error: Unable to list stopped/exited containers - {ex}")
                
    def run_container(self):
        """Run a container with a user-specified or Docker-generated name"""
        # while True:
        image_name = input("\nEnter the image or type 'exit' to leave: ").strip().lower()

        if image_name == "exit":
            return

        container_name = input("Enter a name for the container (press Enter for a random name): ").strip()

        extra_params = {}
        if not container_name:
        # If the user didn't provide a name, let Docker generate a random one
            extra_params['name'] = None
        else:
            extra_params['name'] = container_name

        try:
            container = self.client.containers.run(image_name, detach=True, **extra_params)
            print(f"Container {container.name} is running.")
        except docker.errors.APIError as ex:
            print(f"Error: Unable to run a container with {image_name} image due to - {ex}")
                
    def view_port_mappings(self):
        """View port mappings for a specified container"""
        # Fetch all container IDs
        container_ids = self.get_all_container_ids()

        if not container_ids:
            print("No containers found.")
            return

        # Print container IDs with numbers
        print("\nSelect a container ID:")
        for idx, container_id in enumerate(container_ids, start=1):
            print(f"{idx}. {container_id}")
        
        while True:
            choice = input("\nEnter your number choice or type 'exit' to leave: ").strip().lower()

            if choice == "exit":
                return
        
            try:
                containerid_choice = int(choice)
                if 1 <= containerid_choice <= len(container_ids):
                    selected_container_id = container_ids[containerid_choice - 1]
                    break  # Break the loop if a valid choice is made
                else:
                    print("Invalid pod choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a valid number or 'exit'.")

        try:
            container = self.client.containers.get(selected_container_id)
            ports = container.attrs['NetworkSettings']
            ports_info = container.attrs['NetworkSettings'].get('Ports', {})

            if ports_info:
                print(f"\nPort mappings for Container {selected_container_id}:")
                for port,mapping in ports_info.items():
                    print(f"{port} -> {mapping}")
            else:
                print(f"\nNo port mapping found for container ID: {selected_container_id}")

        except (ValueError, IndexError) as ex:
            print(f"\nError: Invalid choice. Please enter a valid number.")
        except docker.errors.APIError as ex:
            print(f"\nError: Unable to fetch the port values for {selected_container_id} container due to - {ex}")

    def stop_and_remove_all_containers(self):
        """Stop and remove all containers"""
        containers = self.client.containers.list()
        for container in containers:
            try:
                print(f"Stopping and removing {container} container")
                container.stop()
                container.remove()
                print(f"{container} container stopped and removed.")
            except docker.errors.APIError as e:
                print(f"Error occurred while stopping/removing {container} container: {e}")
        print("All containers stopped and removed.")
    
    def save_image_to_tar(self):
        """Save an image to a tar file"""

        image_name = input("Enter the image name or type 'exit' to leave: ").strip().lower()
        if image_name == "exit":
            return
        
        output_filename =input("Enter the output filename or type 'exit' to leave: ").strip().lower()
        if output_filename =="exit":
            return
        try: 
            image = self.client.images.get(image_name)
            output_folder = "container_images" 
            output_filename = os.path.join(output_folder, f"{image_name}.tar")

            if not os.path.exists(output_folder):
                os.makedirs(output_folder) 

            with open(output_filename, 'wb') as f:
                for chunk in image.save():
                    f.write(chunk)
            print(f"Image {image_name} saved to {output_filename}")
        except docker.errors.APIError as ex:
            print(f"Error: unable to fetch the image due to - {ex}")
            print("Please enter a valid image name or type 'exit' to leave.")
        except Exception as ex:
            print(f"Error: Unable to save the image locally due to - {ex}")
            return 

    def get_all_container_ids(self):
        """Get a list of all container IDs"""
        container_ids = [container.id for container in self.client.containers.list()]
        return container_ids



def interactwithdocker():
    "provides an interactive menu for interacting with Docker containers"
    action = InteractWithDockerActions()
    while True:
        print("\nSelect an 'Interact with Docker' Action")
        print("1. List All Container")
        print("2. List all Stopped Containers")
        print("3. Run Containers")
        print("4. View Port Mappings")
        print("5. Stop and Remove all Containers")
        print("6. Save Image to File")
        print("7. Back to 'Docker Actions' Menu")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            action.list_all_containers()
        elif choice == "2":
            action.list_stopped_containers()
        elif choice == "3":
            action.run_container()
        elif choice == "4":
            action.view_port_mappings()
        elif choice == "5":
            action.stop_and_remove_all_containers()
        elif choice == "6":
            action.save_image_to_tar()
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please select a valid option.")

        