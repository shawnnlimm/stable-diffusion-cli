import subprocess

# Path to python env
# venv_activate = "C:\\Users\\shawn\\Desktop\\krux\\sd.webui\\webui\\venv\\Scripts\\python.exe"
venv_activate = "C:\\Users\\shawn\\Desktop\\diffusers-a1111\\.venv\\Scripts\\python.exe"

# Path to sd_script
# script_path = "C:\\Users\\shawn\\Desktop\\krux\\image_generator\\sd_script.py"
script_path = "C:\\Users\\shawn\\Desktop\\krux\\stable-diffusion-cli\\src\\generate_img.py"

# Path to csv_script
create_csv_path = "C:\\Users\\shawn\\Desktop\\krux\\stable-diffusion-cli\\src\\create_csv.py"

try:
    # Run the command in a new command prompt
    p = subprocess.Popen([venv_activate, script_path])
    p.wait()
    p1 = subprocess.Popen([venv_activate, create_csv_path])
    p1.wait()
    print("Script executed successfully within the virtual environment.")

except subprocess.CalledProcessError as e:
    print(f"An error occurred while trying to run the command in the virtual environment: {e}")
