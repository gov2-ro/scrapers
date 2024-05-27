import subprocess
import time

# Function to run a script and measure execution time
def run_script(script_name):
    start_time = time.time()
    subprocess.call(['python', script_name])
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"{script_name} executed in {execution_time:.2f} seconds")

if __name__ == "__main__":
    # script_filenames = ["get_index.py", "fetch_pdfs.py", "fetch_p3+.py"]
    script_filenames = ["get_index.py", "fetch_p3+.py"]

    for script in script_filenames:
        run_script(script)
