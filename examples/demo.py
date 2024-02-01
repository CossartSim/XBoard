from xboard import XBoard
import time

myboard = XBoard("192.168.43.207")

myboard.libre()
time.sleep(2)
myboard.endurance(20)
time.sleep(2)
myboard.explosivite()
time.sleep(2)
myboard.concours()
time.sleep(2)

time.sleep(.5)
for _ in range(50):
    print("Force: {}kg, temps: {}s".format(myboard.data[0][-1], myboard.timestamp[0][-1]))
    time.sleep(0.2)
time.sleep(2)