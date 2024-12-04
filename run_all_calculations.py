import subprocess
import time
from datetime import datetime
from pathlib import Path

def find_calculation_scripts():
    questions_dir = Path("questions")
    return sorted(questions_dir.rglob("calculations.py"))

def run_scripts():
    print(f"Starting calculations at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    total_start_time = time.time()
    scripts = find_calculation_scripts()

    for script in scripts:
        print(f"\nExecuting 'uv run {script}'")
        start_time = time.time()

        try:
            subprocess.run(["uv", "run", str(script)], check=True)
            duration = time.time() - start_time
            print(f"✓ Completed in {duration:.2f} seconds")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed with error code {e.returncode}")

    total_duration = time.time() - total_start_time
    print("\n" + "-" * 50)
    print(f"All calculations completed in {total_duration:.2f} seconds")

if __name__ == "__main__":
    run_scripts()
