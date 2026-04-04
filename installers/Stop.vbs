Option Explicit

Dim objWMIService
Dim colProcesses
Dim objProcess
Dim fso
Dim repoRoot
Dim mainScriptPath
Dim commandLine

' Create an object for WMI service
Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")
Set fso = CreateObject("Scripting.FileSystemObject")

repoRoot = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
mainScriptPath = LCase(repoRoot & "\main.py")

' Query Python processes and terminate only this application's process.
Set colProcesses = objWMIService.ExecQuery("SELECT * FROM Win32_Process WHERE Name = 'python.exe' OR Name = 'pythonw.exe'")

For Each objProcess In colProcesses
    commandLine = ""
    If Not IsNull(objProcess.CommandLine) Then
        commandLine = LCase(objProcess.CommandLine)
    End If

    If InStr(commandLine, mainScriptPath) > 0 Then
        objProcess.Terminate()
    End If
Next
