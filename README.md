# Gentle Handling Project

Description

## Project Overview

The Gentle Handling project ...

### Key Components

- **Vision System**: Object detection and pose estimation using computer vision
- **Collaborative Robotics**: ...
- **Gentle Gripper**: ... 
- **ROS2 Humble**: Built on the latest ROS2 LTS distribution
- **Docker Integration**: Containerized development environment

## Project Structure

```
GentleHandlingProject/
├── .devcontainer.json      # VS Code dev container configuration
├── Dockerfile              # Docker image definition
├── .gitignore              # Git ignore rules
├── gente_handling.repos    # VCS repositories configuration
├── venv/                   # Python virtual environment for ROS2 nodes
└── ws/                     # ROS2 workspace (colcon workspace)
```

### Directory Details

- **`venv/`**: Contains the Python virtual environment with dependencies for the various ROS2 Python nodes
- **`ws/`**: Main ROS2 workspace containing packages, source code, and build artifacts
- **`gente_handling.repos`**: VCS import file for managing multiple repositories

## VCS Repositories File (.repos)

The `.repos` file follows the VCS import format for managing multiple repositories. Structure:

```yaml
repositories:
  package_name:
    type: git
    url: https://github.com/user/repo.git
    version: main
  another_package:
    type: git
    url: https://github.com/user/another-repo.git
    version: humble-devel
```

To import repositories:
```bash
vcs import ws/src < gente_handling.repos
```

## Development Setup with Visual Studio Code

### Prerequisites

Install the following VS Code extensions:
- **Dev Containers** (`ms-vscode-remote.remote-containers`)
- **Docker** (`ms-azuretools.vscode-docker`)
- **ROS** (`ms-iot.vscode-ros`)
- **Python** (`ms-python.python`)
- **C/C++** (`ms-vscode.cpptools`)

### Building and Starting the Container

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd GentleHandlingProject
   ```

2. **Open in VS Code**:
   ```bash
   code .
   ```

3. **Build and start the dev container**:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Dev Containers: Rebuild and Reopen in Container"
   - Select the command and wait for the container to build

4. **Alternative manual build**:
   ```bash
   docker build -t gentle_handling .
   docker run -it --rm gentle_handling
   ```

### Working in the Container

Once inside the container:

1. **Import repositories**:
   ```bash
   cd ws
   vcs import ws/src < ../gente_handling.repos
   ```

2. **Install dependencies**:
   ```bash
   rosdep update
   rosdep install --from-paths src --ignore-src -r -y
   ```

3. **Follow individual repository instructions**:
   ```bash
   # Navigate to each imported repository in ws/src/
   # Follow the specific installation and setup instructions
   # provided in each repository's README or documentation
   # This may include installing additional dependencies,
   # activating specific environments, or configuration steps
   ```

4. **Build the workspace**:
   ```bash
   colcon build
   source install/setup.bash
   ```

5. **Activate Python virtual environment** (if needed):
   ```bash
   source ../venv/<env_name>/bin/activate
   ```

## System Requirements

- Docker Engine 20.10+
- Visual Studio Code 1.60+
- At least 8GB RAM
- 20GB available disk space

## Getting Started

1. Ensure all VS Code extensions are installed
2. Open the project in VS Code
3. Use "Dev Containers: Rebuild and Reopen in Container"
4. Follow the workspace build instructions above
5. Launch your gentle handling applications

## Development Workflow for Contributors

### Initial Setup for Developers

1. **Fork and Clone the repository**:
   ```bash
   git clone https://github.com/your-username/GentleHandlingProject.git
   cd GentleHandlingProject
   ```

2. **Create your team branch**:
   ```bash
   # Use a descriptive name for your team/feature
   git checkout -b <your-branch>
   ```

### Adding Your Team's Repositories

1. **Edit the `gentle_handling.repos` file**:
   ```yaml
   repositories:
     # Existing repositories...
     
     # Add your team's packages
     your_package_name:
       type: git
       url: https://github.com/your-team/your-ros2-package.git
       version: main  # or your preferred branch
     
     your_second_package:
       type: git
       url: https://github.com/your-team/another-package.git
       version: humble-devel
   ```

2. **Test your integration locally**:
   ```bash
   # Import all repositories including yours
   cd ws
   vcs import src < ../gentle_handling.repos
   
   # Install dependencies
   rosdep update
   rosdep install --from-paths src --ignore-src -r -y
   
   # Build and test
   colcon build
   source install/setup.bash
   ```

### Pull Request Process

1. **Create Pull Request** on GitHub

2. **Pull Request Requirements**:
   - ✅ All builds pass in the container
   - ✅ Your code follows project conventions
   - ✅ Documentation updated (README, comments)
   - ✅ No conflicts with main branch
   - ✅ Tested integration with other components

3. **Review Process**:
   - Project coordinator will review your PR
   - Address any requested changes
   - Once approved, your changes will be merged into main

### Important Notes for Contributors

- **Repository Independence**: Each team maintains their own repositories. Only add entries to `gentle_handling.repos`
- **Testing**: Always test your integration in the Docker container before submitting

## License

This Docker is licensed under the Apache License 2.0 

## Maintainer

Davide Sapienza <sapienza.dav@gmail.com>
