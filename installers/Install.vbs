Option Explicit

' Add script to Startup
Dim WshShell
Dim fso
Dim scriptDirectory
Dim scriptFileName
Dim scriptPath
Dim registryKeyPath
Dim registryEntryName

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDirectory = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDirectory
scriptFileName = "Run.vbs"
scriptPath = scriptDirectory & "\" & scriptFileName
registryKeyPath = "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run"
registryEntryName = "Macro Manager"

WshShell.RegWrite registryKeyPath & "\" & registryEntryName, Quote(scriptPath), "REG_SZ"

Function Quote(value)
	Quote = Chr(34) & value & Chr(34)
End Function