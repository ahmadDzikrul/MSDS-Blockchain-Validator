How to use it:
# Fill .env file first

# Create Virtual Environment (there is already virtual environment in this repository but sometimes it's broken so you must recreate it)
python -m venv .venv

# Activate Virtual Environment
# In cmd.exe
.venv\Scripts\activate.bat
# In PowerShell
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

python msds_cli.py register --id MSDS-001 --file test_files/acetone_msds.txt
python msds_cli.py verify --id MSDS-001 --file test_files/acetone_msds.txt
python msds_cli.py revoke --id MSDS-001 --file test_files/acetone_msds.txt
