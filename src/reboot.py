import subprocess
import os
import signal
import time

def reboot_process(process_name, start_command):
    try:
        pid = subprocess.check_output(["pgrep", "-f", process_name]).decode().strip()
        print(f"Killing process: {pid}")
        os.kill(int(pid), signal.SIGKILL)
        time.sleep(1)
    except subprocess.CalledProcessError:
        print("Process not found or already stopped.")

    print("Restarting...")
    subprocess.Popen(start_command, shell=True)
    print("Done!")

# Example usage
if __name__ == "__main__":
    reboot_process("python your_script.py", "python your_script.py")