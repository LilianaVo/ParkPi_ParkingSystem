import time
import threading
import sys
from gpiozero import LED, Servo
from celda_carga import CeldaDeCarga  # Nuestra clase V22
from sensor_nfc import SensorNFC

# --- 1. CONFIGURACIÓN DE HARDWARE ---

# Pines Celdas
PINES_CELDA_1 = {'dt': 17, 'sck': 27}
PINES_CELDA_2 = {'dt': 5,  'sck': 6}
PINES_CELDA_3 = {'dt': 13, 'sck': 19}

# Factores de Escala
FACTOR_CELDA_1 = 215.23999999999901
FACTOR_CELDA_2 = 92.57142857142857
FACTOR_CELDA_3 = 33.268571428572095

# --- NUEVO (V21): Hysteresis (Histéresis) ---
# Ya no usamos un solo umbral, usamos dos.
UMBRAL_PARA_OCUPAR = 35.0  # Debe subir de 35g para marcar OCUPADO
UMBRAL_PARA_LIBERAR = 25.0 # Debe bajar de 25g para marcar LIBRE
# (Tu 'ruido' entre 29g y 31g ahora caerá en esta 'zona muerta' y no causará flickering)

# Pines LEDs y Servo
PIN_LED_1 = 22
PIN_LED_2 = 23
PIN_LED_3 = 24
PIN_SERVO = 4 

# --- 2. VARIABLES GLOBALES COMPARTIDAS ---

estado_cajones = ['LIBRE', 'LIBRE', 'LIBRE']
lock_estado = threading.Lock()
gpio_lock = threading.Lock()

# --- NUEVO (V21): Evento para detener el hilo de forma segura ---
app_running = threading.Event()

# --- 3. HILO 1: GESTOR DE PESO Y LEDS (FONDO) ---

# --- 3. HILO 1: GESTOR DE PESO Y LEDS (FONDO) ---

def gestor_peso_y_leds(celdas, leds):
    """
    (VERSIÓN 25 - Usa gpio_lock para ser 'thread-safe')
    """
    current_celda_index = 0
    
    while app_running.is_set():
        try:
            i = current_celda_index
            celda = celdas[i]
            led = leds[i]
            
            # --- MODIFICADO (V25): Adquirimos el candado de hardware ---
            with gpio_lock:
                # Todo el trabajo de GPIO (leer celda Y prender LED)
                # ocurre dentro del candado.
                
                peso = celda.obtener_peso() # V22 ahora promedia 5 lecturas
                
                # --- Lógica de Hysteresis (Sin cambios) ---
                estado_actual = estado_cajones[i]
                nuevo_estado = estado_actual 
                if estado_actual == 'LIBRE' and peso > UMBRAL_PARA_OCUPAR:
                    nuevo_estado = 'OCUPADO'
                elif estado_actual == 'OCUPADO' and peso < UMBRAL_PARA_LIBERAR:
                    nuevo_estado = 'LIBRE'
                
                # Actualizamos el LED
                if nuevo_estado == 'LIBRE':
                    led.on() # Led verde encendido = LIBRE
                else:
                    led.off() # Led verde apagado = OCUPADO
            # --- MODIFICADO (V25): Liberamos el candado de hardware ---
            
            # El estado global se actualiza fuera del candado de GPIO
            with lock_estado:
                if estado_cajones[i] != nuevo_estado:
                    print(f"[Peso] Cajón {i+1} cambió a: {nuevo_estado} (Peso: {peso:.2f}g)")
                estado_cajones[i] = nuevo_estado
            
            current_celda_index = (current_celda_index + 1) % len(celdas) 
            time.sleep(0.2) 
            
        except Exception as e:
            if app_running.is_set(): 
                print(f"[Error Hilo Peso] {e}")
                time.sleep(1)

# --- 4. HILO 2: GESTOR DE ACCESO NFC (PRINCIPAL) ---

def gestor_acceso_nfc(sensor_nfc, servo):
    """
    Función que se ejecuta en el hilo principal.
    (Sin cambios significativos, sigue simulado)
    """
    print("[NFC] Gestor de acceso iniciado. Esperando tarjetas...")
    
    # --- MODIFICADO (V21): El bucle depende del evento ---
    while app_running.is_set():
        # 1. Esperar tarjeta
        uid_string = sensor_nfc.esperar_y_leer_uid(timeout=0.1)
        
        if uid_string:
            print(f"[NFC] Tarjeta detectada: {uid_string}")
            
            # 2. Verificar si es válida
            if sensor_nfc.es_valido(uid_string):
                print("[Acceso] UID Válido.")
                
                # 3. Consultar disponibilidad
                lugares_disponibles = False
                with lock_estado:
                    estado_actual = estado_cajones.copy()
                
                if 'LIBRE' in estado_actual:
                    lugares_disponibles = True
                    
                # 4. Actuar
                if lugares_disponibles:
                    print("[Acceso] ¡Acceso Concedido! Abriendo barrera...")
                    try:
                        # --- MODIFICADO (V25): Adquirimos el candado de hardware ---
                        with gpio_lock:
                            print("[Acceso] Barrera Abriendo (a 90 grados)...")
                            servo.mid() 
                        # Liberamos el candado (para que el hilo de peso pueda correr)
                        
                        print("[Acceso] Barrera abierta por 10 segundos...")
                        time.sleep(10) # El sleep largo OCURRE FUERA del candado
                        
                        # --- MODIFICADO (V25): Adquirimos el candado de nuevo ---
                        with gpio_lock:
                            print("[Acceso] Barrera Cerrando (a 0 grados)...")
                            servo.min() 
                        # Liberamos el candado
                        
                        print("[Acceso] Barrera cerrada.")
                    except Exception as e:
                        print(f"[Error Servo] {e}")
                else:
                    print("[Acceso] Acceso Denegado: Estacionamiento LLENO.")
                    
            else:
                print("[Acceso] Acceso Denegado: UID Inválido.")
            
            print("[NFC] Esperando 3s para retirar la tarjeta...")
            time.sleep(3)
        
        # Pequeña pausa si no se detectó nada
        # (Importante: time.sleep() cede control a otros hilos)
        time.sleep(0.1)


# --- 5. BLOQUE DE INICIO ---

if __name__ == "__main__":
    
    celdas = []
    leds = []
    servo = None
    hilo_peso = None
    
    try:
        # --- Inicializar Hardware ---
        print("Inicializando hardware...")
        
        # --- NUEVO (V21): Establecer el evento ---
        app_running.set()
        
        leds = [LED(PIN_LED_1), LED(PIN_LED_2), LED(PIN_LED_3)]
        print(f"LEDs (3) inicializados en pines: {PIN_LED_1}, {PIN_LED_2}, {PIN_LED_3}")
        
        # --- CÓDIGO REAL DEL SERVO (V24) ---
        # (Ajustamos el pulso para el MG90S)
        servo = Servo(PIN_SERVO, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
        # Asumimos que .min() es 0 grados (CERRADO)
        servo.min() 
        print(f"Servo inicializado en pin: {PIN_SERVO}")

        sensor_nfc = SensorNFC()
        if sensor_nfc.pn532 is None: # (Corregido a pn523 de la clase)
             raise Exception("No se pudo inicializar el lector NFC.")
        if not sensor_nfc.cargar_uids_validos("valid_uids.txt"):
             print("[Advertencia] No se cargaron UIDs. Nadie podrá entrar.")
        
        print("Inicializando celdas de carga (esto tarda)...")
        celda1 = CeldaDeCarga(pin_dt=PINES_CELDA_1['dt'], pin_sck=PINES_CELDA_1['sck'])
        celda1.establecer_factor_escala(FACTOR_CELDA_1)
        
        celda2 = CeldaDeCarga(pin_dt=PINES_CELDA_2['dt'], pin_sck=PINES_CELDA_2['sck'])
        celda2.establecer_factor_escala(FACTOR_CELDA_2)
        
        celda3 = CeldaDeCarga(pin_dt=PINES_CELDA_3['dt'], pin_sck=PINES_CELDA_3['sck'])
        celda3.establecer_factor_escala(FACTOR_CELDA_3)
        
        celdas = [celda1, celda2, celda3]
        if None in [c.h for c in celdas]: # Verificamos si alguna celda falló
            raise Exception("Una o más celdas no se inicializaron (self.h es None).")
            
        print("¡Todas las celdas calibradas y listas!")
        
        # --- Iniciar Hilo de Fondo ---
        print("Iniciando hilo de monitoreo de peso...")
        hilo_peso = threading.Thread(
            target=gestor_peso_y_leds, 
            args=(celdas, leds),
            daemon=True
        )
        hilo_peso.start()
        
        # --- Iniciar Hilo Principal (NFC) ---
        gestor_acceso_nfc(sensor_nfc, servo)
        
    except KeyboardInterrupt:
        print("\nCerrando el programa (Ctrl+C detectado)...")
    except Exception as e:
        print(f"\n[ERROR FATAL EN MAIN] {e}")
    finally:
        # --- MODIFICADO (V21): Limpieza Segura ---
        print("Iniciando secuencia de apagado...")
        
        # 1. Detener los hilos
        app_running.clear() # Le dice a los hilos que dejen de ejecutarse
        
        # 2. Esperar a que el hilo de peso termine (importante)
        if hilo_peso:
            print("Esperando al hilo de peso...")
            hilo_peso.join() # Espera a que el bucle 'while' termine
            print("Hilo de peso detenido.")
        
        # 3. Ahora SÍ es seguro limpiar el hardware
        print("Limpiando hardware...")
        if leds:
            for led in leds:
                led.off()
        if celdas:
            for celda in celdas:
                celda.limpiar() # ¡Vital para liberar pines lgpio!
        
        print("Programa terminado.")
        sys.exit()