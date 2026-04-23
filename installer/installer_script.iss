; Geometry Wars - Inno Setup Kurulum Betiği
; Inno Setup 6.x ile derlenmesi gerekir.
; https://jrsoftware.org/isinfo.php

#define MyAppName "Geometry Wars"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "GW Studios"
#define MyAppExeName "GeometryWars.exe"
#define MyAppURL "https://github.com/example/geometry-wars"

[Setup]
; Uygulama meta bilgileri
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Kurulum dizini
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; Çıktı dosyası
OutputDir=output
OutputBaseFilename=GeometryWars_Setup_v{#MyAppVersion}

; Sıkıştırma ayarları
Compression=lzma2/ultra64
SolidCompression=yes
LZMANumBlockThreads=4

; Görünüm
WizardStyle=modern
WizardSizePercent=120

; Yönetici hakları gerektir (registry yazma için)
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Kurulum öncesi kontrol etmek için
MinVersion=6.1

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startmenuicon"; Description: "Başlat menüsüne kısayol ekle"; GroupDescription: "Kısayollar:"

[Files]
; Ana çalıştırılabilir dosya (PyInstaller çıktısı)
Source: "..\dist\GeometryWars\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{#MyAppName} Kaldır"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Kurulum tamamlandıktan sonra oyunu başlat (isteğe bağlı)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Kurulum kaydını registry'e yaz - tekli kurulum kilidini sağlar
Root: HKLM; Subkey: "SOFTWARE\GeometryWars"; ValueType: string; ValueName: "Installed"; ValueData: "1"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\GeometryWars"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"
Root: HKLM; Subkey: "SOFTWARE\GeometryWars"; ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}"
Root: HKLM; Subkey: "SOFTWARE\GeometryWars"; ValueType: string; ValueName: "DisplayName"; ValueData: "{#MyAppName}"
Root: HKLM; Subkey: "SOFTWARE\GeometryWars"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"

; Windows Programlar ve Özellikler listesi için
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GeometryWars"; ValueType: string; ValueName: "DisplayName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GeometryWars"; ValueType: string; ValueName: "UninstallString"; ValueData: "{uninstallexe}"
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GeometryWars"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#MyAppVersion}"
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GeometryWars"; ValueType: string; ValueName: "Publisher"; ValueData: "{#MyAppPublisher}"
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GeometryWars"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GeometryWars"; ValueType: dword; ValueName: "NoModify"; ValueData: "1"
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GeometryWars"; ValueType: dword; ValueName: "NoRepair"; ValueData: "1"

[Code]
{ Pascal kodu: Kurulum öncesinde tek kurulum kilidini kontrol et }

function IsAlreadyInstalled(): Boolean;
var
  InstalledValue: String;
begin
  Result := False;
  if RegQueryStringValue(HKLM, 'SOFTWARE\GeometryWars',
                          'Installed', InstalledValue) then
  begin
    if InstalledValue = '1' then
      Result := True;
  end;
end;

function GetInstalledVersion(): String;
var
  Version: String;
begin
  Result := 'Bilinmiyor';
  if RegQueryStringValue(HKLM, 'SOFTWARE\GeometryWars',
                          'Version', Version) then
    Result := Version;
end;

function InitializeSetup(): Boolean;
begin
  Result := True;

  { Zaten kuruluysa uyar ve seçenek sun }
  if IsAlreadyInstalled() then
  begin
    if MsgBox(
      'Geometry Wars sürüm ' + GetInstalledVersion() + ' zaten kurulu.' + #13#10 +
      'Üzerine yüklemek istiyor musunuz?' + #13#10 +
      #13#10 +
      '"Evet" - Üzerine yükle (güncelle)' + #13#10 +
      '"Hayır" - Kurulumu iptal et',
      mbConfirmation,
      MB_YESNO
    ) = IDNO then
    begin
      Result := False;  { Kurulumu iptal et }
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  { Kaldırma tamamlandığında kullanıcıya bilgi ver }
  if CurUninstallStep = usPostUnInstall then
  begin
    MsgBox(
      'Geometry Wars başarıyla kaldırıldı.' + #13#10 +
      'Oynadığınız için teşekkürler!',
      mbInformation,
      MB_OK
    );
  end;
end;
