@echo off
echo Tarefa de Tempo de Reacao em Serie (SRTT)
echo ====================================
echo.
echo Instalando dependencias...
pip install -r requirements.txt
echo.
echo Iniciando experimento...
python srtt_experiment.py
echo.
pause
