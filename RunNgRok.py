import os
import subprocess
import threading
import signal



if __name__ == '__main__':

    subprocess.call('ngrok http --domain=loved-baboon-willingly.ngrok-free.app 5000', shell=True)


