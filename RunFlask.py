
import subprocess
import sys

if __name__ == "__main__":

    leverage = sys.argv[1]
    stop_loss = sys.argv[2]

    subprocess.call(f"python FlaskMainII.py {leverage} {stop_loss}")


    

