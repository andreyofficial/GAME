[Setup]
AppName=GAME
AppVersion=1.0
DefaultDirName={autopf}\GAME
DefaultGroupName=GAME
OutputDir=installer
OutputBaseFilename=GAME-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\GAME\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\GAME"; Filename: "{app}\GAME.exe"; IconFilename: "{app}\sword.ico"
Name: "{commondesktop}\GAME"; Filename: "{app}\GAME.exe"; IconFilename: "{app}\sword.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\GAME.exe"; Description: "Launch GAME"; Flags: nowait postinstall skipifsilent
