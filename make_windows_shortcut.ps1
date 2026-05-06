$gameDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$shortcutPath = Join-Path $gameDir "terarianth.lnk"
$targetPath = Join-Path $gameDir "terarianth.bat"
$iconPath = Join-Path $gameDir "sword.ico"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $targetPath
$shortcut.WorkingDirectory = $gameDir
$shortcut.IconLocation = $iconPath
$shortcut.Save()

Write-Host "Created Windows shortcut:" $shortcutPath
