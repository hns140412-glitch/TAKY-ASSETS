import os
import sys

def ensure_openai_api_key():
    if os.getenv("OPENAI_API_KEY"):
        return True
    if sys.platform != "win32":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
            value, _ = winreg.QueryValueEx(key, "OPENAI_API_KEY")
        if value:
            os.environ["OPENAI_API_KEY"] = value
            return True
    except OSError:
        return False
    return False

if __name__ == "__main__":
    print("OPENAI_API_KEY_READY" if ensure_openai_api_key() else "OPENAI_API_KEY_MISSING")
