from xboard import XBoard
import matplotlib.pyplot as plt
import numpy as np
import time

myboard = XBoard()

## Parametres Force critique
nom_user = "Tom"
temps_debut = []
temsps_fin = []
Nombre_repetitions = 5 # 24 suspensions en tout
temps_on = 7 # 7s d'effort
temps_off = 3 # 3s de repos

## Force critique
myboard.programme("Force crit.", nom_user, True, True, 0, [1500], [75], 1)
time.sleep(1)

for i in range(5,0,-1): # compte a rebours du debut d'exercice
    myboard.programme("Attention {}s".format(i), nom_user, True, True, 0)
    time.sleep(1)

# debut exercice
for repetition in range(Nombre_repetitions):
    temps_debut.append(time.perf_counter() - myboard.time_init)
    myboard.programme("Rep {}".format(repetition+1), nom_user, True, False, 0, [750, 1000, 1500], [75, 100, 100])
    time.sleep(temps_on)

    temsps_fin.append(time.perf_counter() - myboard.time_init)
    myboard.programme("Pause...".format(repetition), nom_user, False, True, 0, [1500, 1000, 750], [75, 100, 100])
    time.sleep(temps_off/2)
    myboard.programme("Pause...".format(repetition), nom_user, False, True, 0, [0], [0], 1) # Calibration sur les pauses
    time.sleep(temps_off/2)

time.sleep(1)
myboard.programme("Fin exercice", nom_user, False, True, 0, [1500, 1000, 750, 1500, 1000, 750], [75, 100, 100, 75, 100, 100])
myboard.stop_reception()

## Affichage
len_temps = len(myboard.timestamp[0])
len_data = len(myboard.data[0])
len_plot = np.minimum(len_temps, len_data)
temps_debut_exo = temps_debut[0]
force = np.array(myboard.data[0][:len_plot])
temps = np.array(myboard.timestamp[0][:len_plot])
indice_debut = np.argmin(abs(temps - temps_debut_exo))

force = force[indice_debut - 10:]
temps = temps[indice_debut - 10:]

force_max = np.max(force)
for timer in temps_debut:
    plt.plot([timer, timer], [-10, force_max], "--r")
for timer in temsps_fin:
    plt.plot([timer, timer], [-10, force_max], "--k")

freq = round(1/(temps[-1] - temps[-2]), 2)
plt.plot(temps, force)
plt.ylabel("Force [kg]")
plt.xlabel("Temps [s]")
plt.title("Exercice force critique, {}".format(nom_user))
plt.ylim([-10,100])
plt.grid()
plt.show()