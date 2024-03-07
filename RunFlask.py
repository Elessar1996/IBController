
import subprocess
import sys

if __name__ == "__main__":

    leverage = sys.argv[1]
    stop_loss = sys.argv[2]

    subprocess.call(f"python FlaskMain.py {leverage} {stop_loss}")


    

