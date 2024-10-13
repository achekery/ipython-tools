import sys

def get_session_frontend():
    if "google.colab" in sys.modules:
        return "colab"
    if "ipykernel" in sys.modules:
        return "jupyter"
    if "IPython" in sys.modules:
        return "terminal"
    return None
