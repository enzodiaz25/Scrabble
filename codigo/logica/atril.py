from configuracion import*
from bolsa_fichas import*
import random

class Atril():
    '''
        Recibe la bolsa de fichas y la cantidad de fichas 
        que se deben repartir en la partida.
        Sus métodos son devolver una ficha determinando su posición,
        cambiar todas las fichas del atril si es que hay fichas en la bolsa
        mostrar el atril íntegro
        devolver la cantidad de fichas disponibles
    '''
    def __init__ (self,bolsa_fichas,cant_fichas):
        random.shuffle(bolsa_fichas)
        self._cant_Fichas = cant_fichas
        self._lista_Fichas = []
        for i in range(cant_fichas):
            self._lista_Fichas.append(bolsa_fichas[0])
            bolsa_fichas.remove(bolsa_fichas[0])
            
    def get_ficha(self, pos): 
        return self._lista_Fichas[pos]
    
    def cambiar_fichas (self,bolsa_fichas,cant_fichas):
        self._cant_Fichas = 0
        self._lista_Fichas = []
        while bolsa_fichas and self._cant_Fichas < cant_fichas:
            self._lista_Fichas.append(bolsa_fichas[0])
            bolsa_fichas.remove(bolsa_fichas[0])
            self._cant_Fichas += 1

    def ver_atril(self):
        return self._lista_Fichas
    
    def get_cant_fichas(self):
        return self._cant_Fichas

#Hay que ver cómo exportar el nivel de dificultad
'''
conf = nivel_dificil()
bolsa_fichas = crear_bolsa(conf['cant_fichas'],conf['puntaje_ficha'])
FICHAS = 7
jugador = Atril (bolsa_fichas, FICHAS)
print (jugador.ver_atril())'''
