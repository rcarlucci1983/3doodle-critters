Set WshShell = CreateObject("WScript.Shell")
Set oShortcut = WshShell.CreateShortcut("C:\Users\richa\OneDrive\Desktop\3Doodle Critters Inventory.lnk")
oShortcut.TargetPath = "pythonw.exe"
oShortcut.Arguments = """C:\Users\richa\Documents\3-doodle-critters\inventory_app.py"""
oShortcut.WorkingDirectory = "C:\Users\richa\Documents\3-doodle-critters"
oShortcut.IconLocation = "C:\Users\richa\Documents\3-doodle-critters\3doodle-critters.ico"
oShortcut.Description = "3Doodle Critters Inventory Manager"
oShortcut.Save
