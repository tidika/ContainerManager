import os

import docker

class OrchestrateDockerActions:
    
    def __init__(self):
        self.client = docker.from_env()
    
    def orchestrate_docker_operations(self):
        """Orchestrating docker operations"""
        print("Type 'exit' to leave")
        python_version = input("Enter the Python version (from 3.6 and above): ").strip().lower()
        if python_version == "exit":
            return
        path_to_program = input("Enter the path to the Python program: ").strip().lower()
        if python_version == "exit":
            return
        image_name = input("Enter the desired image name: ").strip().lower()
        if python_version == "exit":
            return
    
        self.create_dockerfile(path_to_program, python_version)
        image = self.build_image(image_name )
        self.run_and_manage_container(image)

    def create_dockerfile(self, path_to_program, python_version):
        """Create a Dockerfile based on user inputs"""
        print("\nCreating dockerfile ...")
        dockerfile_content = f"""
        FROM python:{python_version}
        WORKDIR /app
        COPY {path_to_program} /app
        EXPOSE 8000
        CMD ["python", "{path_to_program}"]"  
        """
        with open("Dockerfile", "w") as dockerfile:
            dockerfile.write(dockerfile_content)
        print("Dockerfile created successfully.")
    
    def build_image(self, image_name):
        """Build a Docker image from the Dockerfile"""
        print(f"Building the {image_name} image")
        try:
            image = self.client.images.build(path=".", tag=image_name)
            print(f"Image '{image_name}' created successfully.")
            print("here is the created image", image)
            return image[0]
        except docker.errors.BuildError as ex:
            print(f"Error occurred while building the image: {ex}")
        except docker.errors.APIError as ex:
            print(f"Error occurred due to Docker API issue: {ex}")
    
    def run_and_manage_container(self, image):
        """Run a container and manage its state"""
        try:
            container = self.client.containers.run(image, detach=True, ports={'8000/tcp': 8005})
            print(f"Container '{container.name}' is running.")
    
            # Pause the container
            container.pause()
            print("Container paused.")
    
            # Unpause the container after 5 seconds
            import time
            time.sleep(5)
            container.unpause()
            print("Container unpaused.")
    
            # Print container logs/output
            print(container.logs().decode('utf-8'))
        except docker.errors.APIError as ex:
            print(f"Error occurred while running the container: {ex}")
        

def orchestratedocker():
    "provides an interactive menu for orchestrating Docker containers"
    
    action = OrchestrateDockerActions()
    while True:
        print("\nSelect an 'Orchestration' Action")
        print("1. Build and Run a Container Image")
        print("2. Back to 'Docker Actions' Menu")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            action.orchestrate_docker_operations()
        elif choice == "2":
            break
        else:
            print("Invalid choice. Please select a valid option.")

        