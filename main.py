from docker_controllers.interact import interactwithdocker
from docker_controllers.orchestrate import orchestratedocker
from docker_controllers.compose import dockercompose

from k8s_controllers.pod import manage_pods
from k8s_controllers.deployments import manage_deployments
from k8s_controllers.services import manage_services



def main_menu():
    "Main function for running the entire logic"
    
    while True:
        print("\nWelcome to Container Management Menu!!!")
        print("1. Connect to Docker ")
        print("2. Connect to Kubernetes ")
        print("3. Exit")
        
        choice = input("Enter your choice: ")
        if choice == "1":
            while True:
                print("\nSelect Docker Action")
                print("1. Interact with Docker ")
                print("2. Orchestrate Docker Operations")
                print("3. Run Docker Compose")
                print("4. Back to Container Main Menu")
                
                action_choice = input("Enter your choice: ")
                if action_choice == "1":
                  interactwithdocker()
                elif action_choice == "2":
                    orchestratedocker()
                elif action_choice == "3":
                     dockercompose()
                elif action_choice == "4":
                    break
                else:
                    print("Invalid choice. Please select a valid option.")

        elif choice == "2":
            while True:
                print("\nSelect Kubernetes Action")
                print("1. Manage Pods")
                print("2. Manage Deployments")
                print("3. Manage Services")
                print("4. Back to Container Management Menu")
                
                
                action_choice = input("Enter your choice: ")
                if action_choice == "1":
                    manage_pods()
                elif action_choice == "2":
                    manage_deployments()
                elif action_choice == "3":
                    manage_services()
                elif action_choice == "4":
                    break
                else:
                    print("Invalid choice. Please select a valid option.")

            
        elif choice == "3":
            print("Exiting the program. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main_menu()