from python_on_whales import DockerClient


def start_docker_compose():
    compose_file = input("Enter docker compose filename: ").strip() 
    docker = DockerClient(compose_files=[
            f"./{compose_file}"
        ])
    print("starting up docker compose containers ...")
    docker.compose.up(detach=True)
    print("Docker Compose started successfully.")

def stop_docker_compose():
    compose_file = input("Enter docker compose filename: ").strip()
    docker = DockerClient(compose_files=[
            f"./{compose_file}"
        ])
    print("stopping docker compose containers ...")
    docker.compose.down(timeout=1)

def dockercompose():
    "provides an interactive menu for running composed docker containers"
    
    while True:
        print("\nSelect a 'Docker Compose' Action")
        print("1. Start Docker Compose Containers")
        print("2. Stop Docker Compose Containers")
        print("3. Back to 'Docker Actions' Menu")
        
        choice = input("\nEnter your choice: ")
        if choice == "1":
            start_docker_compose()
        elif choice == "2":
            stop_docker_compose()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please select a valid option.")