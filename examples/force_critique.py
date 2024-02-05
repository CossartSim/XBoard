from xboard import XBoard
import matplotlib.pyplot as plt
import numpy as np
import time

myboard = XBoard("192.168.4.1")

## Parametres Force critique
nom_user = "Sim"
temps_debut = []
temps_fin = []
Nombre_repetitions = 10 # 24 suspensions en tout
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

    temps_fin.append(time.perf_counter() - myboard.time_init)
    myboard.programme("Pause...".format(repetition), nom_user, False, True, 0, [1500, 1000, 750], [75, 100, 100])
    time.sleep(temps_off/2)
    myboard.programme("Pause...".format(repetition), nom_user, False, True, 0, [0], [0], 1) # Calibration sur les pauses
    time.sleep(temps_off/2)

time.sleep(1)
myboard.programme("Fin exercice", nom_user, False, True, 0, [1500, 1000, 750, 1500, 1000, 750], [75, 100, 100, 75, 100, 100])
myboard.stop_reception()

## Analyse des données

# On redimensionne les tableau de données
len_temps = len(myboard.timestamp[0])
len_data = len(myboard.data[0])
len_plot = np.minimum(len_temps, len_data)
temps_debut_exo = temps_debut[0]
force = np.array(myboard.data[0][:len_plot])
temps = np.array(myboard.timestamp[0][:len_plot])

# On synchronise les données avec le début de l'exercice
indice_debut = np.argmin(abs(temps - temps_debut_exo))
force = force[indice_debut - 10:]
temps = temps[indice_debut - 10:]

force_max = np.max(force)


# on recherche le centre de chaque repetition
indice_centre = []
for i in range(len(temps_debut)):
    arg_debut = np.argmin(np.abs(temps - temps_debut[i]))
    arg_fin = np.argmin(np.abs(temps - temps_fin[i]))
    indice_centre.append((arg_debut + arg_fin)//2)

# on trouve la plage de données valide pour chaque répétitions
seuil = (force>5)
reps = np.zeros([len(temps_debut), len(seuil)])*False
indice_debut = []
indice_fin = []
for indice in enumerate(indice_centre):
    i = indice[1]
    while seuil[i] == True:
        i -= 1
    indice_debut.append(i) # debut de la plage de donnée

    i = indice[1]
    while seuil[i] == True:
        i += 1
    indice_fin.append(i) # fin de la plage de donnée

    reps[indice[0], indice_debut[-1]:indice_fin[-1]] = True

# Calcul de la force moyenne pour chaque répétitions
force_moyenne = np.round((reps*force).sum(axis=1)/reps.sum(axis=1), 2)

# Valeur de la force moyenne pour 85% des valeurs les plus grandes
force_moyenne_85 = np.round(np.sort(force_moyenne)[::-1][:int(.85*len(force_moyenne))].mean(), 2)

# force maximum pour chaque répétition
force_max = (reps*force).max(axis = 1)
arg_force_max = np.argmax(reps*force, axis = 1)




plt.show()
## Affichage

plt.figure(figsize=(15,8))
plt.plot(temps[arg_force_max], force_max, "rx", linewidth=2, markersize=12)
for i in range(len(force_max)):
    plt.text(temps[arg_force_max[i]]+1, force_max[i]+1, np.round(force_max[i], 1), fontsize="x-large", color="red", weight="demibold")

plt.plot(temps, force)
for i in range(len(force_moyenne)):
    plt.plot([temps[indice_debut[i]], temps[indice_fin[i]]], [force_moyenne[i], force_moyenne[i]], "k")
for i in range(len(force_max)):
    plt.text(temps[indice_debut[i]], force_moyenne[i]-4, np.round(force_moyenne[i], 1), fontsize="x-large", weight="bold")

plt.ylabel("Force [kg]")
plt.xlabel("Temps [s]")
plt.title("Exercice force critique, {}, reglette 22mm, force moyenne 85%: {}kg".format(nom_user, force_moyenne_85))
# plt.ylim([-10,100])
plt.grid()
plt.show()

