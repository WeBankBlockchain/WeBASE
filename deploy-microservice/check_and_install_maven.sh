#!/bin/bash

# Function to check if Maven is installed
check_maven() {
    if command -v mvn &> /dev/null; then
        echo "Maven is already installed."
        return 0
    else
        echo "Maven is not installed."
        return 1
    fi
}

# Function to install Maven on Ubuntu
install_maven_ubuntu() {
    echo "Installing Maven on Ubuntu..."
    sudo apt update
    sudo apt install -y maven
}

# Function to install Maven on CentOS
install_maven_centos() {
    echo "Installing Maven on CentOS..."
    sudo yum install -y maven
}

# Function to determine OS and install Maven
install_maven() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        if [ "$OS" = "ubuntu" ]; then
            install_maven_ubuntu
        elif [ "$OS" = "centos" ]; then
            install_maven_centos
        else
            echo "Unsupported OS: $OS"
            exit 1
        fi
    else
        echo "Cannot determine OS type."
        exit 1
    fi
}

# Main script logic
if ! check_maven; then
    install_maven
fi

echo "Maven installation check and installation (if necessary) completed."
