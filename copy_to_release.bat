del /f "..\release" 
mkdir "..\release"
xcopy .\generator ..\release\ /e
xcopy .\Notes ..\release\ /e
xcopy .\zone_random ..\release\ /e
cp .\big_title.jpg ..\release\
cp .\dolphinAutoTransfer.py ..\release\
cp .\globalVars.py ..\release\
cp .\index.css ..\release\
cp .\index.html ..\release\
cp .\LATEST ..\release\
cp .\LICENSE ..\release\
cp main_v1.py ..\release\
cp navbar.css ..\release\
cp process.html ..\release\
cp randomise_zones_.py ..\release\
cp read_zones.py ..\release\
cp README.md ..\release\
cp start.bat ..\release\
cp start.sh ..\release\
cp u8_m.py ..\release\
cp Util.py ..\release\

PAUSE