import os
import platform
import subprocess
import logging

def configure_platform_settings():
    """
    Configure platform-specific settings to ensure long-running tasks
    are not interrupted when the computer is locked.
    """
    system = platform.system()
    logging.info(f"Configuring platform-specific settings for: {system}")

    if system == "Darwin":  # macOS
        logging.info("macOS detected. Attempting to disable App Nap.")
        _disable_app_nap()
    elif system == "Windows":
        logging.info("Windows detected. Setting process priority to high.")
        _set_windows_foreground_priority()
    else:
        logging.warning(f"No specific settings required for platform: {system}")

def _disable_app_nap():
    """
    Disable App Nap on macOS to prevent the app from being suspended when idle.
    """
    try:
        # Use macOS defaults command to disable App Nap for this process
        process_name = os.path.basename(__file__)
        command = [
            "defaults",
            "write",
            "com.apple.PowerManagement",
            f"{process_name}",
            "Disabled"
        ]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.returncode == 0:
            logging.info("Successfully disabled App Nap on macOS.")
        else:
            logging.warning(f"Failed to disable App Nap. Command output: {result.stderr}")
    except Exception as e:
        logging.warning(f"Failed to disable App Nap: {e}")

def _set_windows_foreground_priority():
    """
    Set the Windows process priority to ensure tasks run in the foreground
    even when the computer is locked.
    """
    try:
        import ctypes
        # Set the process to stay in the foreground
        success = ctypes.windll.kernel32.SetPriorityClass(
            ctypes.windll.kernel32.GetCurrentProcess(), 0x00008000  # HIGH_PRIORITY_CLASS
        )
        if success:
            logging.info("Successfully set Windows process priority to high.")
        else:
            logging.warning("Failed to set Windows process priority: No error raised, but action unsuccessful.")
    except Exception as e:
        logging.warning(f"Failed to set Windows process priority: {e}")

if __name__ == "__main__":
    configure_platform_settings()
