# Script para iniciar el servidor Django con el entorno virtual activado
cd $PSScriptRoot
.\venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000

