install_mysql_client() {
    if command -v mysql &> /dev/null; then
        echo "mysql-client is already installed."
        return
    fi

    echo "mysql-client is not installed. Installing..."

    if [ "$(uname)" == "Darwin" ]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install mysql-client
        else
            echo "Homebrew is not installed. Please install Homebrew first."
            exit 1
        fi
    elif [ -f /etc/os-release ]; then
        . /etc/os-release
        if [ "$ID" == "ubuntu" ] || [ "$ID" == "debian" ]; then
            sudo apt update
            sudo apt install -y mysql-client
        elif [ "$ID" == "centos" ] || [ "$ID" == "rhel" ] || [ "$ID" == "fedora" ]; then
            sudo yum install -y mysql
        else
            echo "Unsupported Linux distribution."
            exit 1
        fi
    else
        echo "Unsupported operating system."
        exit 1
    fi

    if ! command -v mysql &> /dev/null; then
        echo "Failed to install mysql-client."
        exit 1
    fi
}

install_mysql_client