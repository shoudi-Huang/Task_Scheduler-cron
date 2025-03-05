# Task Scheduler

## Project Overview
This project involves creating a Python-based task scheduler similar to the Unix `cron` system. The scheduler consists of two programs: `runner.py`, which runs in the background and executes programs at specified times, and `runstatus.py`, which retrieves and displays the current status of scheduled tasks. The system reads a configuration file (`~/.runner.conf`) to determine which programs to run and when.

## Key Features
- **Task Scheduling**:
  - Schedule programs to run at specific times or periodically (e.g., every Tuesday at 11 AM).
  - Supports multiple days and times for recurring tasks.
- **Status Monitoring**:
  - `runstatus.py` retrieves the status of scheduled tasks by sending a signal to `runner.py` and reading the status file (`~/.runner.status`).
- **Error Handling**:
  - Comprehensive error checking for configuration file issues, file access errors, and task execution failures.
- **Background Execution**:
  - `runner.py` runs as a background process (daemon) and manages task execution.

## Technical Details
- **Programming Language**: Python
- **Configuration File**:
  - Specifies programs, execution times, and parameters.
  - Example: `every Tuesday at 1100 run /bin/echo hello`.
- **Status Output**:
  - Displays when tasks were last run, errors encountered, and when they will run next.

## Learning Outcomes
- **Process Management**: Use `fork`/`exec` to run programs.
- **File Handling**: Manage configuration and status files.
- **Error Handling**: Implement robust error checking and reporting.
- **Background Processes**: Develop a daemon-like program.

## How to Run
1. Run runner.py in the background:
   ```bash
   python3 runner.py
2. Check the status of tasks:
   ```bash
   python3 runstatus.py
