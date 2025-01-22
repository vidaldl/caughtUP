import os
import platform
import subprocess
import logging
import sys

def configure_platform_settings():
    """
    Configure platform-specific settings to ensure long-running tasks
    are not interrupted when the computer is locked.
    """
    system = platform.system()
    python_version = sys.version
    is_admin = "Yes" if os.name == "nt" and _is_windows_admin() else "Unknown on this platform"

    logging.info(f"Configuring platform-specific settings for: {system}")
    logging.info(f"Python version: {python_version}")
    logging.info(f"Running as admin: {is_admin}")

    if system == "Darwin":  # macOS
        logging.info("macOS detected. Attempting to disable App Nap.")
        _disable_app_nap()
    elif system == "Windows":
        logging.info("Windows detected. Setting process priority to high.")
        _set_windows_foreground_priority()
    else:
        logging.warning(f"No specific settings required for platform: {system}")

def _is_windows_admin():
    """
    Check if the current user has administrative privileges on Windows.
    """
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def _disable_app_nap():
    """
    Disable App Nap on macOS to prevent the app from being suspended when idle.
    """
    try:
        import ctypes
        from ctypes import c_void_p, c_uint, c_char_p, POINTER

        # Load Objective-C runtime
        objc = ctypes.cdll.LoadLibrary("/usr/lib/libobjc.A.dylib")
        foundation = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/Foundation.framework/Foundation")

        # Define return and argument types for Objective-C methods
        objc.objc_getClass.restype = c_void_p
        objc.objc_getClass.argtypes = [c_char_p]

        objc.sel_registerName.restype = c_void_p
        objc.sel_registerName.argtypes = [c_char_p]

        foundation.objc_msgSend.restype = c_void_p
        foundation.objc_msgSend.argtypes = [c_void_p, c_void_p]

        # Constants for preventing App Nap
        NSActivityUserInitiated = 0x00FFFFFF
        NSActivityIdleSystemSleepDisabled = 0x00000001

        # Get the NSProcessInfo singleton
        NSProcessInfo = objc.objc_getClass(b"NSProcessInfo")
        if not NSProcessInfo:
            logging.error("Failed to retrieve NSProcessInfo class. Objective-C runtime might not be functioning correctly.")
            return

        processInfoSelector = objc.sel_registerName(b"processInfo")
        processInfo = foundation.objc_msgSend(NSProcessInfo, processInfoSelector)
        if not processInfo:
            logging.error("Failed to retrieve processInfo instance. Ensure the Objective-C runtime is correctly loaded.")
            return

        # Call beginActivityWithOptions:reason:
        beginActivitySelector = objc.sel_registerName(b"beginActivityWithOptions:reason:")
        foundation.objc_msgSend.argtypes = [c_void_p, c_void_p, c_uint, c_char_p]
        result = foundation.objc_msgSend(
            processInfo,
            beginActivitySelector,
            NSActivityUserInitiated | NSActivityIdleSystemSleepDisabled,
            b"Prevent App Nap"
        )

        if result:
            logging.info("Successfully disabled App Nap programmatically on macOS.")
        else:
            logging.error("Failed to disable App Nap: Objective-C call did not create activity successfully.")

    except FileNotFoundError:
        logging.warning("Failed to disable App Nap: Required libraries not found. Ensure macOS runtime is intact.")
    except Exception as e:
        logging.error(f"Failed to disable App Nap due to an unexpected error: {e}", exc_info=True)

def _set_windows_foreground_priority():
    """
    Set the Windows process priority to ensure tasks run in the foreground
    even when the computer is locked.
    """
    try:
        import ctypes
        from ctypes import wintypes

        # Define argument and return types for Windows API functions
        ctypes.windll.kernel32.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        ctypes.windll.kernel32.SetPriorityClass.restype = wintypes.BOOL
        ctypes.windll.kernel32.GetCurrentProcess.restype = wintypes.HANDLE

        # Attempt to retrieve the pseudo-handle for the current process
        process = ctypes.windll.kernel32.GetCurrentProcess()
        if process == -1:  # Pseudo-handle is valid if it equals -1
            logging.info("Pseudo-handle retrieved for the current process.")
        else:
            logging.warning("Pseudo-handle not retrieved, attempting to open process handle.")

            # Fallback to explicitly open the process handle
            PROCESS_ALL_ACCESS = 0x1F0FFF
            process = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, os.getpid())
            if not process:
                logging.error("Failed to open process handle. Process priority cannot be set.")
                return

        # Attempt to set HIGH_PRIORITY_CLASS
        logging.info("Attempting to set process priority to HIGH_PRIORITY_CLASS.")
        success = ctypes.windll.kernel32.SetPriorityClass(process, 0x00008000)  # HIGH_PRIORITY_CLASS
        if not success:
            logging.warning("Failed to set HIGH_PRIORITY_CLASS. Trying ABOVE_NORMAL_PRIORITY_CLASS.")
            logging.info("Attempting to set process priority to ABOVE_NORMAL_PRIORITY_CLASS.")
            success = ctypes.windll.kernel32.SetPriorityClass(process, 0x00004000)  # ABOVE_NORMAL_PRIORITY_CLASS

        if success:
            logging.info("Successfully set Windows process priority.")
        else:
            error_code = ctypes.windll.kernel32.GetLastError()
            logging.warning(f"Failed to set Windows process priority. Error code: {error_code}")

        # Clean up handle if explicitly opened
        if process and process != -1:
            ctypes.windll.kernel32.CloseHandle(process)

    except Exception as e:
        logging.warning(f"Failed to set Windows process priority: {e}")

if __name__ == "__main__":
    configure_platform_settings()
