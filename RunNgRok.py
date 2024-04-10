import os
import subprocess
import threading
import signal



if __name__ == '__main__':

    subprocess.call('ngrok http --domain=kind-amoeba-divine.ngrok-free.app 5000', shell=True)


