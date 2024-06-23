import subprocess

# Path to python env
venv_activate = ".venv\\Scripts\\python.exe"

scripts = [
   "src\\generate_img.py",
   "scripts\\create_json.py", 
   "scripts\\create_pdf.py"
]

try:
    # Run the scripts in child process
    for script in scripts:
        result = subprocess.run([venv_activate, script], check=True)
        print(f"Executed {script} successfully.")

    print("All script executed successfully within the virtual environment.")

except subprocess.CalledProcessError as e:
    print(f"An error occurred while trying to run the command in the virtual environment: {e}")
