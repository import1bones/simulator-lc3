#!/bin/bash
# Cross-platform build and test script for Unix-like systems (Linux/macOS)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect Python executable
find_python() {
    for cmd in python3 python python3.11 python3.10 python3.9; do
        if command -v "$cmd" >/dev/null 2>&1; then
            echo "$cmd"
            return 0
        fi
    done
    log_error "Python not found!"
    exit 1
}

# Function to check if we're in a virtual environment
check_venv() {
    if [[ -n "$VIRTUAL_ENV" ]]; then
        log_info "Running in virtual environment: $VIRTUAL_ENV"
    else
        log_warn "Not in a virtual environment. Consider using one for isolation."
    fi
}

# Function to setup virtual environment if needed
setup_venv() {
    local python_cmd="$1"
    local venv_dir="$PROJECT_ROOT/venv"
    
    if [[ ! -d "$venv_dir" ]]; then
        log_info "Creating virtual environment..."
        "$python_cmd" -m venv "$venv_dir"
    fi
    
    log_info "Activating virtual environment..."
    source "$venv_dir/bin/activate"
    
    # Upgrade pip
    python -m pip install --upgrade pip
}

# Function to install system dependencies
install_system_deps() {
    log_info "Checking system dependencies..."
    
    # Detect package manager and install dependencies
    if command -v apt-get >/dev/null 2>&1; then
        # Ubuntu/Debian
        log_info "Installing dependencies with apt..."
        sudo apt-get update
        sudo apt-get install -y cmake build-essential python3-dev python3-pip git
    elif command -v yum >/dev/null 2>&1; then
        # RHEL/CentOS
        log_info "Installing dependencies with yum..."
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y cmake python3-devel python3-pip git
    elif command -v dnf >/dev/null 2>&1; then
        # Fedora
        log_info "Installing dependencies with dnf..."
        sudo dnf groupinstall -y "Development Tools" "Development Libraries"
        sudo dnf install -y cmake python3-devel python3-pip git
    elif command -v brew >/dev/null 2>&1; then
        # macOS with Homebrew
        log_info "Installing dependencies with brew..."
        brew install cmake python git
    elif command -v pacman >/dev/null 2>&1; then
        # Arch Linux
        log_info "Installing dependencies with pacman..."
        sudo pacman -S --needed cmake gcc python python-pip git
    else
        log_warn "Package manager not detected. Please install cmake, gcc/clang, python3-dev, and git manually."
    fi
}

# Main function
main() {
    log_info "LC-3 Simulator Cross-Platform Build Script"
    log_info "Platform: $(uname -s) $(uname -m)"
    
    cd "$PROJECT_ROOT"
    
    # Find Python
    PYTHON_CMD=$(find_python)
    log_info "Using Python: $PYTHON_CMD"
    
    # Check virtual environment
    check_venv
    
    # Parse arguments for special cases
    INSTALL_SYSTEM_DEPS=false
    USE_VENV=false
    
    for arg in "$@"; do
        case $arg in
            --install-system-deps)
                INSTALL_SYSTEM_DEPS=true
                shift
                ;;
            --use-venv)
                USE_VENV=true
                shift
                ;;
        esac
    done
    
    # Install system dependencies if requested
    if [[ "$INSTALL_SYSTEM_DEPS" == true ]]; then
        install_system_deps
    fi
    
    # Setup virtual environment if requested
    if [[ "$USE_VENV" == true ]]; then
        setup_venv "$PYTHON_CMD"
        PYTHON_CMD="python"  # Use the venv python
    fi
    
    # Check if CMake is available
    if ! command -v cmake >/dev/null 2>&1; then
        log_error "CMake not found! Please install CMake first."
        log_info "On Ubuntu/Debian: sudo apt-get install cmake"
        log_info "On macOS: brew install cmake"
        exit 1
    fi
    
    # Run the Python build script
    log_info "Running build and test..."
    if "$PYTHON_CMD" build_and_test.py "$@"; then
        log_success "Build and test completed successfully!"
        exit 0
    else
        log_error "Build and test failed!"
        exit 1
    fi
}

# Help function
show_help() {
    cat << EOF
LC-3 Simulator Cross-Platform Build Script

Usage: $0 [OPTIONS]

Options:
    --clean                 Clean build directory first
    --no-test              Build only, skip tests
    --test-only            Run tests only, skip build
    --categories CATS      Test categories to run (basic, instructions, memory, io, integration, pipeline)
    --coverage             Generate coverage report
    --html-report          Generate HTML test report
    --parallel             Run tests in parallel
    --verbose, -v          Verbose output
    --install-deps         Install Python dependencies
    --check-deps           Check dependencies only
    --install-system-deps  Install system dependencies (requires sudo)
    --use-venv             Create and use virtual environment
    --help, -h             Show this help

Examples:
    $0                                    # Full build and test
    $0 --clean --verbose                 # Clean build with verbose output
    $0 --categories basic instructions   # Run only basic and instruction tests
    $0 --test-only --coverage            # Run tests with coverage (no build)
    $0 --install-system-deps --use-venv  # Setup complete environment

EOF
}

# Check for help
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
fi

# Run main function
main "$@"
