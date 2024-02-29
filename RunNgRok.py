import os
import subprocess
import threading
import signal



if __name__ == '__main__':

    subprocess.call('ngrok http http://127.0.0.1:5000', shell=True)


