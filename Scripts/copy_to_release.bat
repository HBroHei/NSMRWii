del /f "..\..\release" 
mkdir "..\..\release"
xcopy ..\generator ..\..\release\generator\ /e
xcopy ..\Notes ..\..\release\Notes\ /e
xcopy .\zone_random ..\..\release\Scripts\zone_random\ /e
copy ..\big_title.jpg ..\..\release\
copy .\dolphinAutoTransfer.py ..\..\release\Scripts\
copy .\globalVars.py ..\..\release\Scripts\
copy ..\index.css ..\..\release\
copy ..\index.html ..\..\release\
copy ..\LATEST ..\..\release\
copy ..\LICENSE ..\..\release\
copy .\config_autoCopy.json ..\..\release\Scripts\
copy main_v1.py ..\..\release\Scripts\
copy nsmbw.py ..\..\release\Scripts\
copy ..\navbar.css ..\..\release\
copy ..\process.html ..\..\release\
copy randomise_zones_.py ..\..\release\Scripts\
copy read_zones.py ..\..\release\Scripts\
copy ..\README.md ..\..\release\
copy start.bat ..\..\release\Scripts\
copy start.sh ..\..\release\Scripts\
copy u8_m.py ..\..\release\Scripts\
copy Util.py ..\..\release\Scripts\

PAUSE