@echo off
REM Cross-platform build and test script for Windows

setlocal EnableDelayedExpansion

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%
cd /d "%PROJECT_ROOT%"

REM Colors for output (Windows doesn't support ANSI colors by default, but we'll try)
set "INFO_COLOR=[96m"
set "SUCCESS_COLOR=[92m"
set "WARN_COLOR=[93m"
set "ERROR_COLOR=[91m"
set "RESET_COLOR=[0m"

:log_info
echo %INFO_COLOR%[INFO]%RESET_COLOR% %~1
goto :eof

:log_success
echo %SUCCESS_COLOR%[SUCCESS]%RESET_COLOR% %~1
goto :eof

:log_warn
echo %WARN_COLOR%[WARN]%RESET_COLOR% %~1
goto :eof

:log_error
echo %ERROR_COLOR%[ERROR]%RESET_COLOR% %~1
goto :eof

:find_python
REM Function to find Python executable
for %%i in (python.exe python3.exe py.exe) do (
    where %%i >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_CMD=%%i
        goto :found_python
    )
)

call :log_error "Python not found! Please install Python from python.org"
exit /b 1

:found_python
goto :eof

:check_venv
if defined VIRTUAL_ENV (
    call :log_info "Running in virtual environment: %VIRTUAL_ENV%"
) else (
    call :log_warn "Not in a virtual environment. Consider using one for isolation."
)
goto :eof

:setup_venv
set venv_dir=%PROJECT_ROOT%\venv

if not exist "%venv_dir%" (
    call :log_info "Creating virtual environment..."
    %PYTHON_CMD% -m venv "%venv_dir%"
    if !errorlevel! neq 0 (
        call :log_error "Failed to create virtual environment"
        exit /b 1
    )
)

call :log_info "Activating virtual environment..."
call "%venv_dir%\Scripts\activate.bat"
if !errorlevel! neq 0 (
    call :log_error "Failed to activate virtual environment"
    exit /b 1
)

REM Upgrade pip
python -m pip install --upgrade pip
goto :eof

:install_system_deps
call :log_info "Checking system dependencies..."

REM Check if we have chocolatey
where choco >nul 2>&1
if !errorlevel! equ 0 (
    call :log_info "Installing dependencies with chocolatey..."
    choco install cmake git visualstudio2022buildtools -y
) else (
    call :log_warn "Chocolatey not found. Please install the following manually:"
    call :log_warn "- CMake (https://cmake.org/download/)"
    call :log_warn "- Git (https://git-scm.com/download/win)"
    call :log_warn "- Visual Studio Build Tools (https://visualstudio.microsoft.com/visual-cpp-build-tools/)"
)
goto :eof

:check_cmake
where cmake >nul 2>&1
if !errorlevel! neq 0 (
    call :log_error "CMake not found! Please install CMake first."
    call :log_info "Download from: https://cmake.org/download/"
    call :log_info "Or install with chocolatey: choco install cmake"
    exit /b 1
)
goto :eof

:show_help
echo LC-3 Simulator Cross-Platform Build Script
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo     --clean                 Clean build directory first
echo     --no-test              Build only, skip tests
echo     --test-only            Run tests only, skip build
echo     --categories CATS      Test categories to run (basic, instructions, memory, io, integration, pipeline)
echo     --coverage             Generate coverage report
echo     --html-report          Generate HTML test report
echo     --parallel             Run tests in parallel
echo     --verbose, -v          Verbose output
echo     --install-deps         Install Python dependencies
echo     --check-deps           Check dependencies only
echo     --install-system-deps  Install system dependencies (requires admin)
echo     --use-venv             Create and use virtual environment
echo     --help, -h             Show this help
echo.
echo Examples:
echo     %~nx0                                    # Full build and test
echo     %~nx0 --clean --verbose                 # Clean build with verbose output
echo     %~nx0 --categories basic instructions   # Run only basic and instruction tests
echo     %~nx0 --test-only --coverage            # Run tests with coverage (no build)
echo     %~nx0 --install-system-deps --use-venv  # Setup complete environment
echo.
goto :eof

:main
call :log_info "LC-3 Simulator Cross-Platform Build Script"
call :log_info "Platform: Windows %PROCESSOR_ARCHITECTURE%"

REM Find Python
call :find_python
if !errorlevel! neq 0 exit /b 1

call :log_info "Using Python: %PYTHON_CMD%"

REM Check virtual environment
call :check_venv

REM Parse arguments for special cases
set INSTALL_SYSTEM_DEPS=false
set USE_VENV=false
set REMAINING_ARGS=

:parse_args
if "%~1"=="" goto :done_parsing
if "%~1"=="--install-system-deps" (
    set INSTALL_SYSTEM_DEPS=true
    shift
    goto :parse_args
)
if "%~1"=="--use-venv" (
    set USE_VENV=true
    shift
    goto :parse_args
)
if "%~1"=="--help" goto :show_help_and_exit
if "%~1"=="-h" goto :show_help_and_exit

set REMAINING_ARGS=%REMAINING_ARGS% %1
shift
goto :parse_args

:show_help_and_exit
call :show_help
exit /b 0

:done_parsing

REM Install system dependencies if requested
if "%INSTALL_SYSTEM_DEPS%"=="true" (
    call :install_system_deps
)

REM Setup virtual environment if requested
if "%USE_VENV%"=="true" (
    call :setup_venv
    if !errorlevel! neq 0 exit /b 1
    set PYTHON_CMD=python
)

REM Check CMake
call :check_cmake
if !errorlevel! neq 0 exit /b 1

REM Run the Python build script
call :log_info "Running build and test..."
%PYTHON_CMD% build_and_test.py %REMAINING_ARGS%
if !errorlevel! equ 0 (
    call :log_success "Build and test completed successfully!"
    exit /b 0
) else (
    call :log_error "Build and test failed!"
    exit /b 1
)

:eof
REM Entry point
call :main %*
