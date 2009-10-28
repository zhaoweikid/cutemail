!include "MUI2.nsh"

Name "CuteMail"
OutFile "CuteMail 0.8.6.exe"

InstallDir "$PROGRAMFILES\CuteMail"

InstallDirRegKey HKCU "Software\CuteMail" ""

RequestExecutionLevel user

Var StartMenuFolder

!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_LICENSE "${NSISDIR}\Docs\Modern UI\License.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY

!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
!define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\CuteMail" 
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
  
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
  
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "SIMPCHINESE"

Section "CuteMail主程序" SecUmbra

    SetOutPath "$INSTDIR"
    
    File /r "dist\*.*"
     
    WriteRegStr HKCU "Software\CuteMail" "" $INSTDIR
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    
    !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\CuteMail.lnk" "$INSTDIR\cutemail.exe"
    CreateShortCut "$DESKTOP\CuteMail.lnk" "$INSTDIR\cutemail.exe"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
    !insertmacro MUI_STARTMENU_WRITE_END

SectionEnd

LangString DESC_SecDummy ${LANG_SIMPCHINESE} "CuteMail安装."

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecUmbra} $(DESC_SecDummy)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section "Uninstall"
    ;ADD YOUR OWN FILES HERE...

    Delete "$INSTDIR\Uninstall.exe"

    RMDir /r "$INSTDIR"

    DeleteRegKey /ifempty HKCU "Software\CuteMail"

    Delete "$DESKTOP\CuteMail.lnk"

    RMDir /r  "$SMPROGRAMS\$StartMenuFolder"
SectionEnd


