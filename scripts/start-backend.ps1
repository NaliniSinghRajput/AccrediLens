Set-Location $PSScriptRoot\..\backend
if (-Not (Test-Path ".venv")) {
  py -3.11 -m venv .venv
}
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
