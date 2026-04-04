# MacroManager

MacroManager is a Windows desktop automation manager with a local Flask web UI. It creates macro folders from a template, launches macros, shows logs, opens macros in VS Code, and manages the local DesktopAutomationFramework dependency used by the generated macro scripts.

## Prerequisites

- Windows
- Python 3.11+ with `python` available on `PATH`
- Git with `git` available on `PATH`
- VS Code with `code` available on `PATH` if you want the editor integration

## Install Dependencies

### Python

Install Python from python.org and enable `Add python.exe to PATH` during setup.

Verify the installation:

```powershell
python --version
python -m pip --version
```

### Git

Install Git for Windows from git-scm.com.

Verify the installation:

```powershell
git --version
```

Git is required because the project uses it for update checks and because the automation framework can be installed directly from GitHub.

### VS Code

Install Visual Studio Code from code.visualstudio.com.

Enable the `code` command in `PATH` from VS Code:

```text
Command Palette -> Shell Command: Install 'code' command in PATH
```

Verify the installation:

```powershell
code --version
```

VS Code is optional for running the manager, but required for the `Open in code editor` actions.

### Python Packages

Install the manager runtime dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install the automation framework used by generated macro scripts:

```powershell
python -m pip install --upgrade --force-reinstall git+https://github.com/diogojesusdev/DesktopMacroFramework
```

## Run

Start the local web server:

```powershell
python main.py
```

The application serves the UI on `http://localhost:8181`.

On first run, the manager creates a `MacroManager` directory in your user home folder and copies the default macro template there.

## Optional Startup Installation

To register the manager to run at Windows logon, run:

```powershell
cscript installers\Install.vbs
```

To start it with the bundled launcher:

```powershell
cscript installers\Run.vbs
```

To stop the running manager process started through this project:

```powershell
cscript installers\Stop.vbs
```

## Notes

- The launcher scripts assume `python` is installed system-wide.
- `macro_template.py` depends on `DesktopAutomationFramework`; creating macros without that package installed will produce scripts that cannot run.
- The repository includes prebuilt frontend assets under `static/` and `templates/`; no Node.js setup is required to run the current checked-in version.
