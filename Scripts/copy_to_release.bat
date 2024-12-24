del /f "..\..\release" 
mkdir "..\..\release"
xcopy ..\generator ..\..\release\generator\ /e
xcopy ..\Notes ..\..\release\Notes\ /e
xcopy .\zone_random ..\..\release\Scripts\zone_random\ /e
cp ..\big_title.jpg ..\..\release\
cp .\dolphinAutoTransfer.py ..\..\release\Scripts\
cp .\globalVars.py ..\..\release\Scripts\
cp ..\index.css ..\..\release\
cp ..\index.html ..\..\release\
cp ..\LATEST ..\..\release\
cp ..\LICENSE ..\..\release\
cp .\config_autoCopy.json ..\..\release\Scripts\
cp main_v1.py ..\..\release\Scripts\
cp nsmbw.py ..\..\release\Scripts\
cp ..\navbar.css ..\..\release\
cp ..\process.html ..\..\release\
cp randomise_zones_.py ..\..\release\Scripts\
cp read_zones.py ..\..\release\Scripts\
cp ..\README.md ..\..\release\
cp start.bat ..\..\release\Scripts\
cp start.sh ..\..\release\Scripts\
cp u8_m.py ..\..\release\Scripts\
cp Util.py ..\..\release\Scripts\

PAUSE