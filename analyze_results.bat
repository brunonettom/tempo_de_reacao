@echo off
echo Analise de Resultados SRTT
echo ====================================
echo.
echo Instalando dependencias...
pip install -r requirements.txt
echo.
echo Iniciando ferramenta de analise...
python srtt_analysis.py
echo.
pause
