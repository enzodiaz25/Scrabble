from codigo.logica.tablero import *
from codigo.logica.configuracion import *
from codigo.logica.preferencias import Preferencias
from codigo.logica.atril import Atril
from codigo.logica.bolsa_fichas import *
from codigo.interfaz.dibujar import Dibujar
import codigo.logica.check_palabra2 as cp
from codigo.logica.guardar_partida import Juego_Guardado
import os.path
import time
import random

#Datos de ejemplo para probar la partida
nombre_usuario = 'Enzo'
configuracion = nivel_medio()
preferencias = Preferencias(configuracion['filas'],configuracion['columnas'],configuracion['especiales'], configuracion['nivel'])
unTablero = Tablero(preferencias)
bolsa_fichas = crear_bolsa(configuracion['cant_fichas'],configuracion['puntaje_ficha'])
tiempo_partida = configuracion['tiempo']

#Crea un string con el directorio donde se almacenan las partidas. El formato
#de la ruta depende del sistema operativo en el que se esté ejecutando
ruta_guardado = os.path.join('guardados', '')

#Crea el objeto que gestionará el guardado y cargado de la partida
archivo_partida = Juego_Guardado(ruta_guardado)

#Carga una partida. Es True si se cargó con éxito, False en caso contrario
if (archivo_partida.cargar_guardado()):
    #Prepara la información extraída del archivo
    puntaje = archivo_partida.getPuntaje()
    unTablero = archivo_partida.getTablero()
    atril_jugador = archivo_partida.getAtril()
    atril_pc = archivo_partida.getAtrilPC()
    bolsa_fichas = archivo_partida.getBolsaFichas()
    preferencias = archivo_partida.getPreferencias()
    cant_cambiar = archivo_partida.getCantCambiar()
    puntaje_pc = archivo_partida.getPuntajePC()
    #La partida sólo se puede guardar en el turno del jugador. Al cargarla,
    #continuará siendo su turno
    turno_jugador = True
    #Construye la interfaz
    interfaz = Dibujar(unTablero, preferencias, atril_jugador)
    #Si se habían agotado las oportunidades para cambiar las fichas...
    if (cant_cambiar == 0):
        #... el botón permite finalizar el juego
        interfaz.habilitarFinalizacion()
    #Solicita el tiempo que faltaba para finalizar la partida, lo convierte a
    #segundos y lo envía al timer
    interfaz.setTimer(archivo_partida.getTiempoRestante() / 60)
    interfaz.actualizarPuntajePC(puntaje_pc)
    interfaz.actualizarPuntaje(puntaje)
else:
    #Si no había ninguna partida para cargar, crea nuevos atriles
    atril_jugador = Atril (bolsa_fichas, 7)
    atril_pc = Atril(bolsa_fichas, 7)
    #El primer turno se decide al azar
    turno_jugador = random.choice([True, False])
    #Asigna la cantidad de veces que se pueden cambiar las fichas
    cant_cambiar = 3
    puntaje = 0
    puntaje_pc = 0
    interfaz = Dibujar(unTablero, preferencias, atril_jugador)
    #El tiempo de la partida se determina según el nivel de dificultad
    interfaz.setTimer(tiempo_partida)

#Lazo principal del juego
jugar = True
while jugar:

    #Turno del jugador
    if (turno_jugador):
        event, value = interfaz.leer()

        #Si se acabo el tiempo o se cerró la ventana, se termina el juego
        if (interfaz.terminoTimer()) or (event == None):
            break

        #-----EVENTO: Clickear en una ficha del atril-----
        if ('ficha' in event):
            #Se obtiene el índice de la ficha seleccionada a partir de la "key"
            #del boton y se agrega a una lista
            fichas_seleccionadas = []
            fichas_seleccionadas.append(int(event.split(" ")[1]))

            #En el siguiente string se irá formando la palabra
            palabra = ''
            #Le pide al atril la ficha que se corresponde con el botón que se clickeó
            palabra += list(atril_jugador.get_ficha(int(event.split(" ")[1])).keys())[0]

            #Muestra la palabra que se va formando; inhabilita la ficha clickeada,
            #el botón de guardado y el de cambiar
            interfaz.actualizarTexto(palabra)
            interfaz.inhabilitarElemento(event)
            interfaz.inhabilitarElemento('guardar')
            interfaz.inhabilitarElemento('cambiar')

            #-----EVENTO: Clickear en otra ficha o en el botón "Validar"-----
            click_validar = False
            while (not click_validar):
                event, value = interfaz.leer()

                #Circunstancias que cierran el lazo
                if (interfaz.terminoTimer()) or (event == None):
                    jugar = False
                    break
                if (event == 'validar'):
                    click_validar = True

                if ('ficha' in event):
                    #Cada vez que se clickea en una ficha, agrega el índice (la key) a
                    #"fichas_seleccionadas", inhabilita el botón correspondiente y
                    #añade la letra a la palabra
                    fichas_seleccionadas.append(int(event.split(" ")[1]))
                    interfaz.inhabilitarElemento(event)
                    palabra += list(atril_jugador.get_ficha(int(event.split()[1])).keys())[0]
                    #Muestra la palabra que se está formando en la interfaz
                    interfaz.actualizarTexto(palabra)

                #El timer debe actualizarse obligatoriamente dentro de cada evento
                interfaz.actualizarTimer()

            #Si clickeó validar (no se terminó el tiempo ni se cerró la ventana)...
            if (click_validar):
                #Valida la palabra y, si existe, permite que se decida la posición en el tablero
                if(cp.check_jugador(palabra, preferencias.getNivel())):
                    interfaz.actualizarTexto('SELECCIONE DÓNDE INSERTAR', tamaño=12, color='green', fondo='white')

                    #-----EVENTO: Clickear en el tablero para elegir la posición-----
                    elegir_posicion = True
                    cambio_posicion = False
                    while elegir_posicion:
                        #La primera vez, se esperará que decida donde insertarla
                        if not (cambio_posicion):
                            event, value = interfaz.leer()
                        if (interfaz.terminoTimer()) or (event == None):
                            jugar = False
                            break

                        if 'tablero' in event:
                            #Muestra los botones de selección de orientación
                            interfaz.seleccionarOrientacion(event.split()[1], preferencias)

                            #Guarda la coordenada de ese botón según sus keys
                            fila = event.split(" ")[1].split(',')[0]
                            columna = event.split(" ")[1].split(',')[1]

                            #Calcula las coordenadas que estan debajo y a la derecha
                            #de la que escogió. Se utilizarán para decidir el sentido
                            coord_derecha = fila + ',' + str(int(columna) + 1)
                            coord_inferior = str(int(fila) + 1) + ',' + columna

                            #-----EVENTO: Decidir sentido-----
                            while True:
                                event, value = interfaz.leer()
                                if (interfaz.terminoTimer()) or (event == None):
                                    jugar = False
                                    break

                                #Si seleccionó la coordenada que está a la derecha (insertar horizontal)
                                #o la que está debajo (insertar vertical)...
                                if (event == f'tablero {coord_derecha}') or (event == f'tablero {coord_inferior}'):

                                    #Las fichas se guardarán en esta lista
                                    lista_insercion = []
                                    for f in fichas_seleccionadas:
                                        #Usa la lista de índices para pedirle al atril las fichas necesarias
                                        lista_insercion.append(atril_jugador.get_ficha(f))

                                    #Le pide al tablero que intente agregarlas
                                    puntaje_palabra = unTablero.insertarPalabra(lista_insercion, (int(fila),int(columna)), 'h' if event == f'tablero {coord_derecha}' else 'v')

                                    #Si el tablero devuelve puntaje negativo, significa que no hubo espacio
                                    if puntaje_palabra == -1:
                                        interfaz.actualizarTexto('NO HAY ESPACIO', color='red', fondo='white', tamaño=12)
                                    else:
                                        #Las fichas se eliminan del atril en orden descendente, para evitar excepciones
                                        fichas_seleccionadas.sort(reverse=True)
                                        for f in fichas_seleccionadas:
                                            atril_jugador.usar_ficha(f)

                                        #Se completan los espacios que vacios en el atril
                                        atril_jugador.llenar_atril(bolsa_fichas)

                                        #Se incremente el puntaje del jugador y actualizan en la interfaz
                                        puntaje += puntaje_palabra
                                        interfaz.actualizarPuntaje(puntaje)
                                        interfaz.textoEstandar()
                                        turno_jugador = False

                                    interfaz.actualizarAtril(atril_jugador)
                                    interfaz.actualizarTablero(unTablero)
                                    elegir_posicion = False
                                    break

                                #Si se clickeó más allá de los botones de sentido, designa ese lugar como la nueva
                                #ubicación para la palabra
                                elif ('tablero' in event):
                                    cambio_posicion = True
                                    interfaz.reestablecerOrientacion(fila+','+columna, unTablero, preferencias)
                                    break
                                interfaz.actualizarTimer()
                        interfaz.actualizarTimer()

                #Si el módulo que resuelve la validez de la palabra devolvió False..
                else:
                    interfaz.actualizarTexto('PALABRA NO VÁLIDA ¡PRUEBA DE NUEVO!', tamaño=10, color='red', fondo='white')
                    interfaz.actualizarAtril(atril_jugador)

                #Antes de continuar esperando eventos y habilitar los botones,
                #se comprueba que no se haya cerrado la ventana
                if (event != None):
                    interfaz.habilitarElemento('guardar')
                    interfaz.habilitarElemento('cambiar')

        #-----EVENTO: Botón para cambiar fichas-----
        if (event == 'cambiar'):
            if (cant_cambiar > 0):
                cant_cambiar = cant_cambiar - 1
                atril_jugador.cambiar_fichas(bolsa_fichas)
                interfaz.actualizarAtril(atril_jugador)
                #Si se alcanzó la cantidad máxima de cambios permitida, "cambiar"
                #se convierte en "Finalizar juego"
                if (cant_cambiar == 0):
                    interfaz.habilitarFinalizacion()
                turno_jugador = False
            else:
                #Si se clickea "Finalizar juego", se termina la ronda
                jugar = False

        #-----EVENTO: Guardar partida-----
        if event == 'guardar':
            #Paraliza el timer y muestra un pop de confirmación
            instante = time.time()
            eleccion = interfaz.popUpOkCancel('¿Estas seguro que deseas guardar la partida?')
            interfaz.paralizarTimer(instante)
            if eleccion == 'OK':
                archivo_partida = Juego_Guardado(ruta_guardado, unTablero, 'NombreUsuario', atril_jugador, atril_pc, bolsa_fichas, puntaje, puntaje_pc, interfaz.getTiempoRestante(), preferencias, cant_cambiar)
                archivo_partida.crear_guardado()
                jugar = False
        interfaz.actualizarTimer()

    #Turno de la PC
    else:
        if (interfaz.terminoTimer()):
            break

        #Busca una palabra y un lugar en el tablero
        mejor_opcion = cp.check_compu(atril_pc, unTablero, preferencias.getNivel())

        #Si encontró al menos una opcíón, la inserta y actualiza la información
        if len(mejor_opcion) != 0:
            puntaje_pc += unTablero.insertarPalabra(mejor_opcion['fichas'], mejor_opcion['coordenada'], mejor_opcion['sentido'])
            for ficha in mejor_opcion['fichas']:
                indice = atril_pc.ver_atril().index(ficha)
                atril_pc.usar_ficha(indice)
            atril_pc.llenar_atril(bolsa_fichas)
            interfaz.actualizarTablero(unTablero)
            interfaz.actualizarPuntajePC(puntaje_pc)
            interfaz.actualizarTexto(random.choice(['PC: ¡A ver cómo contrarrestas eso!', 'PC: ¿Te quedaste sin ideas?', 'PC: Podés hacerlo mejor...',
                                                        'PC: ¡Tu turno!', 'PC: He tenido retos más difíciles.', 'PC: El tiempo se acaba, amiguito.', 'PC: Jamás me han derrotado.',
                                                        'PC: Hoy estas con poca imaginación.', 'PC: Quizás deberías volver al buscaminas.', 'PC: Mis núcleos son más rápidos que tu cerebro.',
                                                        'PC: 100101110, que en binario es "perdedor"', 'PC: El código fuente no está de tu lado :(', 'PC: ¿Mala? ¿Yo?',
                                                        f'PC: Tu turno, {nombre_usuario}', 'PC: *bosteza*']), tamaño=12, color='#EBDEB6', fondo=random.choice(['#D10E49', '#12870D', '#80870D']), pc=True)
            #Si la bolsa de fichas se vació, advierte al jugador
            if len(bolsa_fichas) == 0:
                interfaz.textoEstandar(pc=True)
                interfaz.actualizarTexto('PC: La bolsa de fichas se vació :(', tamaño=14, color='#EBDEB6', fondo='#A9084F')
                cant_cambiar = 0
                interfaz.habilitarFinalizacion()
        turno_jugador = True
