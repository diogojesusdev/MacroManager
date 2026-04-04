import ast
from dataclasses import dataclass
from datetime import datetime
import os
import re
import shutil
import subprocess
import sys
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
home_dir = os.path.expanduser("~")

# Join the home directory with "MacroManager" to form the full path
MACROS_BASE_PATH = os.path.join(home_dir, "MacroManager")
MACRO_TEMPLATE_SCRIPT_NAME = 'macro_template.py'
MACRO_TEMPLATE_SCRIPT_PATH = os.path.join(BASE_DIR, "code_templates", MACRO_TEMPLATE_SCRIPT_NAME)
MACRO_TEMPLATE_SCRIPT_DESTINATION_PATH = os.path.join(MACROS_BASE_PATH, MACRO_TEMPLATE_SCRIPT_NAME)

DEFAULT_MACRO_NAME = "macro.py"
VSCODE_CONFIG_FOLDER_PATH = os.path.join(BASE_DIR, ".vscode")
DEFAULT_MACRO_SCRIPT_PATH = os.path.join(BASE_DIR, "code_templates", DEFAULT_MACRO_NAME)
CODE_EDITOR_PATH = sys.argv[1] if len(sys.argv) > 1 else "code"
PYTHON_FRAMEWORK_NAME = "DesktopAutomationFramework"
PythonFrameworkGithubVersionFile = "https://raw.githubusercontent.com/48302-DiogoJesus/DesktopMacroFramework/main/version.txt"

def _normalize_path(path: str) -> str:
	return os.path.normcase(os.path.normpath(path))

def _get_repo_path() -> str:
	return BASE_DIR.replace('\\', '/')

def _run_pip_command(*args: str) -> subprocess.CompletedProcess[str]:
	return subprocess.run(
		[sys.executable, "-m", "pip", *args],
		check=False,
		capture_output=True,
		text=True
	)

def _get_pythonw_executable() -> str:
	pythonw_path = shutil.which("pythonw")
	if pythonw_path:
		return pythonw_path

	python_dir = os.path.dirname(os.path.abspath(sys.executable))
	pythonw_candidate = os.path.join(python_dir, "pythonw.exe")
	if os.path.exists(pythonw_candidate):
		return pythonw_candidate

	return sys.executable

def _open_with_default_application(path: str) -> None:
	os.startfile(path)

def _open_directory_in_file_explorer(path: str, focus_window: bool = False) -> None:
	absolute_path = os.path.abspath(path)
	if os.name != "nt":
		_open_with_default_application(absolute_path)
		return

	creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
	subprocess.Popen(["explorer.exe", absolute_path], creationflags=creation_flags)
	if not focus_window:
		return

	escaped_path = absolute_path.replace("'", "''")
	command = f"""
Add-Type @\"
using System;
using System.Runtime.InteropServices;
public static class User32 {{
	public static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
	public static readonly IntPtr HWND_NOTOPMOST = new IntPtr(-2);

	[DllImport(\"user32.dll\")]
	public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);

	[DllImport(\"user32.dll\")]
	public static extern bool SetForegroundWindow(IntPtr hWnd);

	[DllImport(\"user32.dll\")]
	public static extern bool BringWindowToTop(IntPtr hWnd);

	[DllImport(\"user32.dll\")]
	public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

	[DllImport(\"user32.dll\")]
	public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
}}
\"@

$targetPath = [System.IO.Path]::GetFullPath('{escaped_path}')
$deadline = (Get-Date).AddSeconds(2)

do {{
	$shell = New-Object -ComObject Shell.Application
	$window = $null

	foreach ($candidate in $shell.Windows()) {{
		try {{
			$candidatePath = [System.IO.Path]::GetFullPath($candidate.Document.Folder.Self.Path)
			if ($candidatePath -eq $targetPath) {{
				$window = $candidate
				break
			}}
		}} catch {{
		}}
	}}

	if ($window -ne $null) {{
		$hwnd = [IntPtr]::new([int64]$window.HWND)
		# ALT keypress is a standard workaround for Windows foreground-lock restrictions.
		[User32]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
		[User32]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
		[User32]::ShowWindowAsync($hwnd, 9) | Out-Null
		[User32]::BringWindowToTop($hwnd) | Out-Null
		[User32]::SetWindowPos($hwnd, [User32]::HWND_TOPMOST, 0, 0, 0, 0, 0x0001 -bor 0x0002) | Out-Null
		[User32]::SetWindowPos($hwnd, [User32]::HWND_NOTOPMOST, 0, 0, 0, 0, 0x0001 -bor 0x0002) | Out-Null
		[User32]::SetForegroundWindow($hwnd) | Out-Null
		break
	}}

	Start-Sleep -Milliseconds 100
}} while ((Get-Date) -lt $deadline)
"""

	subprocess.run(
		["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
		check=False,
		capture_output=True,
		text=True,
		creationflags=creation_flags,
	)

def _schedule_manager_restart() -> None:
	run_script = os.path.join(BASE_DIR, "installers", "Run.vbs")
	command = f'ping 127.0.0.1 -n 3 >nul && cscript //B "{run_script}"'
	creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
	subprocess.Popen(["cmd", "/c", command], creationflags=creation_flags)

def create_environment_if_not_exists():
	# Without this, it's not possible to do "git rev-parse HEAD" to check versions if this is installed on an external device (e.g., pendrive)
	repo_path = _get_repo_path()
	existing_safe_directories = subprocess.run(
		["git", "config", "--global", "--get-all", "safe.directory"],
		check=False,
		capture_output=True,
		text=True
	)
	configured_paths = {
		_normalize_path(path.replace('\\', '/'))
		for path in existing_safe_directories.stdout.splitlines()
		if path.strip()
	}
	if _normalize_path(repo_path) not in configured_paths:
		subprocess.run(["git", "config", "--global", "--add", "safe.directory", repo_path], check=False)
 
	os.makedirs(MACROS_BASE_PATH, exist_ok=True)

	if not os.path.exists(MACRO_TEMPLATE_SCRIPT_DESTINATION_PATH):
		shutil.copy(MACRO_TEMPLATE_SCRIPT_PATH, MACRO_TEMPLATE_SCRIPT_DESTINATION_PATH)
	
	print("Environment created successfully...")

@dataclass
class Macro:
	name: str
	path: str
	last_run: Optional[str]

@dataclass
class MacroInvocationVariableMetadata:
	type: str
	accepted_values: Optional[list[str]]

@dataclass
class MacroInvocationVariablesMetadata:
	variables: dict[str, MacroInvocationVariableMetadata]

@dataclass 
class Versions:
	should_update: bool
	current_version: str
	remote_version: str

class MacroManager:
	# Returns the full path of the macro
	@staticmethod
	def create_macro(macro_name: str) -> str:
		create_environment_if_not_exists()
		folderFullPath = os.path.join(MACROS_BASE_PATH, macro_name)
		pythonFilePath = os.path.join(folderFullPath, DEFAULT_MACRO_NAME)

		# Create the macro folder
		os.makedirs(folderFullPath)
		# Copy macro template script to macro folder
		shutil.copy(DEFAULT_MACRO_SCRIPT_PATH, pythonFilePath)
		shutil.copytree(VSCODE_CONFIG_FOLDER_PATH, os.path.join(folderFullPath, ".vscode"))
		
		return pythonFilePath

	@staticmethod
	def open_macros_folder() -> None:
		_open_directory_in_file_explorer(MACROS_BASE_PATH, focus_window=True)
			
	@staticmethod
	def open_macro_in_code_editor(absolute_macro_path: str) -> None:
		create_environment_if_not_exists()
		print(absolute_macro_path)
		folder_path = os.path.dirname(absolute_macro_path)
		if not os.path.isdir(folder_path):
			raise FileNotFoundError(f"Could not find macro folder at {folder_path}")
		subprocess.Popen([CODE_EDITOR_PATH, folder_path])
	
	@staticmethod
	def open_macro_in_file_explorer(absolute_macro_path: str) -> None:
		create_environment_if_not_exists()
		_open_directory_in_file_explorer(os.path.dirname(absolute_macro_path), focus_window=True)
		
	@staticmethod 
	def open_task_scheduler() -> None:
		create_environment_if_not_exists()
		_open_with_default_application("taskschd.msc")
	
	@staticmethod
	def open_macro_template() -> None:
		create_environment_if_not_exists()
		subprocess.Popen([CODE_EDITOR_PATH, MACRO_TEMPLATE_SCRIPT_DESTINATION_PATH])
	
	@staticmethod
	def get_macros_flat() -> list[Macro]:
		create_environment_if_not_exists()
		try:
			file_list: list[Macro] = []
   
			def search(directory: str):
				files = os.listdir(directory)

				for file in files:
					file_path = os.path.join(directory, file)

					if os.path.isdir(file_path):
							# Recursively search subdirectories
							search(file_path)
					elif os.path.isfile(file_path) and file.endswith('.py'):
							with open(file_path, 'r', encoding='utf-8') as f:
								file_contents = f.read()
							if '@Macro' in file_contents:
								folder_name = os.path.basename(directory)
								logs_path = os.path.join(directory, 'logs')

								last_run = None

								if os.path.exists(logs_path):
									log_files = os.listdir(logs_path)
									if log_files:
										log_files.sort(reverse=True, key=lambda x: os.path.getmtime(os.path.join(logs_path, x)))
										latest_log_file = os.path.join(logs_path, log_files[0])

										# Extract date and time from file name
										date_time_part = os.path.basename(latest_log_file).replace('.txt', '')
										date_part, time_part = date_time_part.split(' ')

										year, month, day = map(int, date_part.split('-'))
										hour, minute, second = map(int, time_part.split('.'))
										last_run = datetime(year, month, day, hour, minute, second)
										last_run = last_run.strftime('%Y-%m-%d %H:%M:%S')

								file_list.append(Macro(folder_name, file_path, last_run))

			search(MACROS_BASE_PATH)
			return [file for file in file_list if file.path != MACRO_TEMPLATE_SCRIPT_DESTINATION_PATH]
		except Exception as e:
			print(f'Error searching Python files: {e}')
			return []
		
	@staticmethod
	def get_latest_macro_logs(absolute_macro_path: str) -> list[str]:
		create_environment_if_not_exists()
		logs_folder = os.path.join(os.path.dirname(absolute_macro_path), "logs")

		if not os.path.exists(logs_folder):
				raise FileNotFoundError(f"Could not find logs folder at {logs_folder}")

		log_files = os.listdir(logs_folder)

		if not log_files:
				raise FileNotFoundError(f"No log files found in {logs_folder}")

		log_files.sort(reverse=True, key=lambda x: os.path.getmtime(os.path.join(logs_folder, x)))
		latest_log_file = os.path.join(logs_folder, log_files[0])

		with open(latest_log_file, 'r', encoding='utf-8') as f:
				log_contents = f.read().splitlines()

		return log_contents

	@staticmethod
	def get_macro_invocation_variables_metadata(absolute_macro_path: str) -> MacroInvocationVariablesMetadata:
		with open(absolute_macro_path, 'r', encoding='utf-8') as file:
			tree = ast.parse(file.read(), filename="MACRO")

			invocation_variables_metadata = MacroInvocationVariablesMetadata(variables={})

			class VarsCallVisitor(ast.NodeVisitor):
				def visit_Call(self, node: ast.Call):
					if isinstance(node.func, ast.Attribute) and node.func.attr in {"getNumber", "getString"}:
						if isinstance(node.func.value, ast.Name) and node.func.value.id == "vars":
							type_ = "number" if node.func.attr == "getNumber" else "string"
							varname = None
							accepted_values = None

							if node.args and isinstance(node.args[0], ast.Constant):
								varname = node.args[0].value
							if len(node.keywords) > 0:
								for keyword in node.keywords:
									if keyword.arg == "accepted_values" and isinstance(keyword.value, ast.List):
										accepted_values = [elt.value for elt in keyword.value.elts if isinstance(elt, ast.Constant)]
							if varname:
								invocation_variables_metadata.variables[varname] = MacroInvocationVariableMetadata(type_, accepted_values)

					self.generic_visit(node)

			visitor = VarsCallVisitor()
			visitor.visit(tree)

		return invocation_variables_metadata

	@staticmethod
	def run_macro(
		absolute_macro_path: str,
		invocation_variables: dict[str, str] = {},
		time_between_instructions_s: Optional[str] = None,
  		auto_run: bool = False,
  		exit_after_run: bool = False
	) -> None:
		create_environment_if_not_exists()
		command = [_get_pythonw_executable(), absolute_macro_path]
		command.extend([f'{key}={value}' for key, value in invocation_variables.items()])
		if time_between_instructions_s:
			command.append(f'--interval_s={time_between_instructions_s}')
		if auto_run:
			command.append('--auto-run')
		if exit_after_run:
			command.append('--exit-after-run')
	
		subprocess.run(command, check=False)

	@staticmethod
	def get_framework_versions() -> Versions:
		remote_version_command = f'curl {PythonFrameworkGithubVersionFile}'
		remote_version_process = subprocess.Popen(remote_version_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		remote_version_stdout, _ = remote_version_process.communicate()
		remote_version = remote_version_stdout.decode().strip()

		current_version_process = _run_pip_command("show", PYTHON_FRAMEWORK_NAME)
		current_version_output = current_version_process.stdout.strip()
		version_match = re.search(r'Version: (.+)', current_version_output)
		current_version = (version_match.group(1) if version_match else "").strip()
		framework_installed = current_version != ""
  
		return Versions(
			# Determine if update is needed
		  	should_update=(not framework_installed) or (remote_version != "" and current_version != remote_version),
		  	current_version=current_version,
		  	remote_version=remote_version
	  	)

	@staticmethod
	def should_update_manager() -> bool:
		# Fetch current version (local HEAD)
		current_version_process = subprocess.Popen("git rev-parse HEAD", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		current_version_stdout, _ = current_version_process.communicate()
		current_version = current_version_stdout.decode().replace("HEAD", "").strip()

		# Fetch remote version (origin HEAD)
		remote_version_process = subprocess.Popen("git ls-remote origin HEAD", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		remote_version_stdout, _ = remote_version_process.communicate()
		remote_version = remote_version_stdout.decode().replace("HEAD", "").strip()

		# Compare versions
		return current_version != remote_version

	@staticmethod
	def update_framework() -> None:
		process = _run_pip_command(
			"install",
			"--upgrade",
			"--force-reinstall",
			"git+https://github.com/diogojesusdev/DesktopMacroFramework"
		)
		print(f"update_framework() => {process.stdout.strip()}")
		returncode = process.returncode
		if returncode != 0:
			raise RuntimeError(f"Error updating framework. Command returned non-zero exit code {returncode}.")

	@staticmethod
	def update_manager() -> None:
		command = "git fetch origin && git reset --hard origin/main && git clean -fd"
		process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = process.communicate()
		print(f"update_manager() => {stdout.decode().strip()}")
		returncode = process.returncode
		if returncode != 0:
			raise RuntimeError(f"Error updating manager. Command returned non-zero exit code {returncode}.")

		# Restart the manager with the new code version
		_schedule_manager_restart()
		raise SystemExit()