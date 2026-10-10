@echo off
rem VS 2026 has no MSBuild support for the v143 toolset, so build with v145 on top of the compiler picked by vcvars.
"%VSINSTALLDIR%MSBuild\Current\Bin\amd64\MSBuild.exe" %* /property:PlatformToolset=v145 /property:VCToolsVersion=%VCToolsVersion%
exit /b %errorlevel%
