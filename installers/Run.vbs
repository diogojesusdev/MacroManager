Option Explicit

Dim WshShell
Dim fso
Dim repoRoot
Dim mainScriptPath
Dim command

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

repoRoot = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
mainScriptPath = repoRoot & "\main.py"

WshShell.CurrentDirectory = repoRoot

command = "python " & Quote(mainScriptPath)

WshShell.Run command, 0, False

Function Quote(value)
	Quote = Chr(34) & value & Chr(34)
End Function
