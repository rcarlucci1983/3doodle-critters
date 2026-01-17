Set WshShell = WScript.CreateObject("WScript.Shell")
strDesktop = WshShell.SpecialFolders("Desktop")

Set oShellLink = WshShell.CreateShortcut(strDesktop & "\3Doodle Critters.lnk")
oShellLink.TargetPath = WshShell.CurrentDirectory & "\Launch 3Doodle Critters.bat"
oShellLink.WorkingDirectory = WshShell.CurrentDirectory
oShellLink.WindowStyle = 1
oShellLink.Description = "3Doodle Critters Inventory Manager"
oShellLink.Save

MsgBox "Desktop shortcut created!", vbInformation, "3Doodle Critters"
