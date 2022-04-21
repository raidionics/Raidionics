!define APP_NAME "Raidionics"
!define COMP_NAME "SINTEF"
!define VERSION "1.0.0"
!define DESCRIPTION "Application"
!define INSTALLER_NAME "Raidionics-1.0.0-win.exe"
!define MAIN_APP_EXE "Raidionics.exe"
!define INSTALL_TYPE "SetShellVarContext current"
!define REG_ROOT "HKLM"  
# "HKCU" or "HKLM" : https://nsis.sourceforge.io/Add_uninstall_information_to_Add/Remove_Programs

!define REG_APP_PATH "Software\Microsoft\Windows\CurrentVersion\App Paths\${MAIN_APP_EXE}"
!define UNINSTALL_PATH "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"

!define REG_START_MENU "Start Menu Folder"

var SM_Folder

######################################################################

SetCompressor ZLIB
Name "${APP_NAME}"
Caption "${APP_NAME}"
# Icon ".\images\raidionics-logo.ico"
OutFile "${INSTALLER_NAME}"
BrandingText "${APP_NAME}"
XPStyle on
InstallDirRegKey "${REG_ROOT}" "${REG_APP_PATH}" ""
InstallDir "$PROGRAMFILES\Raidionics"

!include 'MUI.nsh'

# icon
!define MUI_ICON ".\images\raidionics-logo.ico"

!define MUI_ABORTWARNING
!define MUI_UNABORTWARNING

# !insertmacro MUI_PAGE_WELCOME

!insertmacro MUI_PAGE_DIRECTORY

!ifdef REG_START_MENU
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "Raidionics"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "${REG_ROOT}"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${UNINSTALL_PATH}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "${REG_START_MENU}"
!insertmacro MUI_PAGE_STARTMENU Application $SM_Folder
!endif

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

# name the installer
OutFile "${INSTALLER_NAME}"


####################### UNINSTALL BEFORE UPGRADE #####################

Section "" SecUninstallPrevious

    Call UninstallPrevious

SectionEnd

Function UninstallPrevious

    ; Check for uninstaller.
    DetailPrint "Checking for previous Raidionics versions"
    ReadRegStr $R0 HKCU "$INSTDIR" "UninstallString"

    ${If} $R0 == ""        
         ReadRegStr $R0 HKLM "$INSTDIR" "UninstallString"
        ${If} $R0 == ""        
            DetailPrint "No previous installation found"    
            Goto Done
        ${EndIf}
    ${EndIf}

    DetailPrint "Removing previous installation."    
    ; Run the uninstaller silently.
    ExecWait '"$R0" /S _?=$INSTDIR' $0
    DetailPrint "Uninstaller returned $0"

    Done:

FunctionEnd

######################################################################
 
# default section start; every NSIS script has at least one section.

######################################################################

Section -MainProgram
${INSTALL_TYPE}
SetOverwrite ifnewer
SetOutPath "$INSTDIR"
#File "vcredist_x86_2013.exe"
#File "vcredist_x86.exe"
#ExecWait '"$INSTDIR\vcredist_x86_2013.exe" /passive /norestart'
#ExecWait '"$INSTDIR\vcredist_x86.exe" /passive /norestart'
#RmDir /r "$INSTDIR\extensions"
#File /r "release\*.*"
SectionEnd

######################################################################

Section -Icons_Reg
SetOutPath "$INSTDIR"
WriteUninstaller "$INSTDIR\uninstall.exe"

!ifdef REG_START_MENU
!insertmacro MUI_STARTMENU_WRITE_BEGIN Application
CreateDirectory "$SMPROGRAMS\$SM_Folder"
CreateShortCut "$SMPROGRAMS\$SM_Folder\${APP_NAME}.lnk" "$INSTDIR\${MAIN_APP_EXE}" "" ".\images\raidionics-logo.ico" 0
CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${MAIN_APP_EXE}" "" ".\images\raidionics-logo.ico" 0
CreateShortCut "$SMPROGRAMS\$SM_Folder\Uninstall ${APP_NAME}.lnk" "$INSTDIR\uninstall.exe"

!insertmacro MUI_STARTMENU_WRITE_END
!endif

# define the output path for this file
SetOutPath $INSTDIR

WriteRegStr ${REG_ROOT} "${REG_APP_PATH}" "" "$INSTDIR\${MAIN_APP_EXE}"
WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "DisplayName" "${APP_NAME}"
WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "UninstallString" "$INSTDIR\uninstall.exe"
WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "DisplayIcon" ".\images\raidionics-logo"
WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "DisplayVersion" "${VERSION}"
WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "Publisher" "${COMP_NAME}"

# Create directory
CreateDirectory $INSTDIR

# PACKAGE ENTIRE CONTENT OF BUNDLE THE NEW BINARY!
File /nonfatal /a /r ".\dist\Raidionics\*"
ExecWait "$INSTDIR\Raidionics-installed.exe"

# default section end
SectionEnd

######################################################################

Section Uninstall
${INSTALL_TYPE}
RmDir /r "$INSTDIR"

!ifdef REG_START_MENU
!insertmacro MUI_STARTMENU_GETFOLDER "Application" $SM_Folder
Delete "$SMPROGRAMS\$SM_Folder\${APP_NAME}.lnk"
Delete "$SMPROGRAMS\$SM_Folder\Uninstall ${APP_NAME}.lnk"
Delete "$DESKTOP\${APP_NAME}.lnk"

RmDir "$SMPROGRAMS\$SM_Folder"
!endif

DeleteRegKey ${REG_ROOT} "${REG_APP_PATH}"
DeleteRegKey ${REG_ROOT} "${UNINSTALL_PATH}"
SectionEnd

######################################################################
