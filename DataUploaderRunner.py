import subprocess

def DataUploaderRunner():
	pythonPath = r"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
	
	scriptPath = r"C:\Users\hchapman\OneDrive - Jackson County Missouri\Documents\Dashboards\Violence Dashboard - v2.0\DataUploader.py"

	subprocess.check_call([pythonPath, scriptPath])