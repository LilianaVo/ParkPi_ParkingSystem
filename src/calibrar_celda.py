import time
import sys
from celda_carga import CeldaDeCarga 

# --- CONFIGURACIÓN ---
PINES_CELDA_1_DT = 17   # Conectado a GPIO 17 (Pin 11)
PINES_CELDA_1_SCK = 27  # Conectado a GPIO 27 (Pin 13)

celda = None

try:
    print("\n--- Herramienta de Calibración de Celdas de Carga (HX711) ---")

    # 1. Inicializar la celda
    print(f"Inicializando celda en DT={PINES_CELDA_1_DT} y SCK={PINES_CELDA_1_SCK}...")
    celda = CeldaDeCarga(pin_dt=PINES_CELDA_1_DT, pin_sck=PINES_CELDA_1_SCK)
    
    if celda.h is None:
        raise Exception("Falló la inicialización de la celda (self.h es None).")
        
    print("Celda inicializada con éxito.")

    # 2. Proceso de Tara (Calibración a Cero)
    print("\n--- PASO 1: CALIBRACIÓN (TARA) ---")
    print("¡IMPORTANTE! Asegúrate de que no haya NADA de peso sobre la celda.")
    input("Presiona ENTER cuando estés listo para poner la balanza a cero...")

    celda.calibrar() 
    lectura_sin_peso = celda.obtener_lectura_cruda()
    print(f"Lectura en crudo (sin peso): {lectura_sin_peso}")

    # 3. Proceso de Medición de Factor
    print("\n--- PASO 2: ENCONTRAR EL FACTOR DE ESCALA ---")
    print("¡IMPORTANTE! Coloca un objeto de PESO CONOCIDO sobre la celda.")

    peso_conocido_str = ""
    while not peso_conocido_str.isdigit():
        peso_conocido_str = input("\nEscribe el peso conocido en GRAMOS (ej. 1000) y presiona ENTER: ")

    peso_conocido = float(peso_conocido_str)
    if peso_conocido <= 0:
        print("El peso debe ser mayor a 0.")
        sys.exit()

    print(f"Tomando lectura con {peso_conocido}g. Por favor espera...")
    time.sleep(2) 

    lectura_con_peso = celda.obtener_lectura_cruda()
    print(f"Lectura en crudo (con peso): {lectura_con_peso}")

    # 4. Cálculo
    
    lectura_neta = abs(lectura_con_peso - lectura_sin_peso)
    if lectura_neta == 0:
        print("[ERROR] La lectura con peso y sin peso es idéntica. Verifica la celda.")
        sys.exit()
        
    factor_de_escala = lectura_neta / peso_conocido
    
    print("\n--- ¡CÁLCULO COMPLETADO! ---")
    print(f"Tu FACTOR DE ESCALA (Ratio) es: {factor_de_escala}")
    print("\n¡GUARDA ESTE NÚMERO! Lo necesitarás en tu script 'main.py'.\n")

    # 5. Verificación
    print("--- PASO 3: VERIFICACIÓN ---")
    print(f"Aplicando el factor {factor_de_escala} a la celda...")
    celda.establecer_factor_escala(factor_de_escala)

    print("\nAhora mostraré el peso medido en tiempo real.")
    print("Verifica que la lectura sea cercana a los gramos que pusiste.")
    print("Presiona Ctrl+C para salir.")
    
    while True:
        peso_medido = celda.obtener_peso()
        print(f"  Peso medido: {peso_medido:.2f} g")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n\nCerrando script de calibración. ¡Adiós!")
except Exception as e:
    print(f"\nOcurrió un error: {e}")
finally:
    if celda:
        celda.limpiar()