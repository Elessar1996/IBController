
import subprocess
import sys

if __name__ == "__main__":

    leverage = sys.argv[1]
    stop_loss = sys.argv[2]
    use_cdv = sys.argv[3]
    use_cvd = sys.argv[4]

    subprocess.call(f"python FlaskMainII.py {leverage} {stop_loss} {use_cdv} {use_cvd}")


    

