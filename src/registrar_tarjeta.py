import time
import board
import busio
import sys
from adafruit_pn532.i2c import PN532_I2C

# Nombre del archivo donde se guardarán los UIDs válidos
UID_FILE = 'valid_uids.txt'

# --- Inicialización del Lector I2C ---
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C(i2c, debug=False) #debug false no imprime inforrmación de debug

    # --- Comprobar Conexión ---
    # Lee la versión del firmware para confirmar que se podrá establecer comunicación
    versiondata = pn532.firmware_version
    print(f"\n¡Lector PN532 encontrado!")
    print(f"Versión de Firmware: {versiondata[0]}.{versiondata[1]}")

    # Configura el lector para escuchar tarjetas
    pn532.SAM_configuration()

except Exception as e:
    print(f"\n[ERROR FATAL] No se pudo inicializar el PN532.")
    print(f"Detalle: {e}")
    print("\nPor favor, verifica lo siguiente:")
    print("  1. Que el PN532 esté correctamente conectado (SCL a SCL, SDA a SDA).")
    print("  2. Que la interfaz I2C esté habilitada en 'sudo raspi-config'.")
    sys.exit()

print("\n--- Registro de Tarjetas NFC ---")
print(f"Los UIDs válidos se guardarán en: {UID_FILE}")

try:
    while True:
        print(f"\n[ESPERANDO] Acerca una tarjeta para registrarla (Ctrl+C para salir)...")
        
        # El lector espera a que una tarjeta pasiva sea detectada
        uid = pn532.read_passive_target(timeout=10.0)
        
        # Si no se encontró tarjeta, el bucle 'while' simplemente reinicia
        if uid is None:
            continue

        # --- Tarjeta Encontrada ---
        # El 'uid' es un bytearray que se convierte en decimal para el código
        uid_string = uid.hex()
        
        print(f"\n¡Tarjeta detectada!")
        print(f"  UID (hex): {uid_string}")
        print(f"  UID (len): {len(uid)} bytes")

        # --- Confirmación del Usuario ---
        respuesta = ""
        while respuesta not in ['s', 'n']:
            respuesta = input(f"¿Deseas guardar este UID? (s/n): ").strip().lower()

        # --- Guardado en Archivo ---
        if respuesta == 's':
            try:
                # 'a' significa 'append' (añadir al final del archivo)
                with open(UID_FILE, 'a') as f:
                    f.write(uid_string + "\n")
                print(f"[ÉXITO] UID {uid_string} guardado en {UID_FILE}")
            except Exception as e:
                print(f"[ERROR] No se pudo escribir en el archivo: {e}")
        else:
            print("[INFO] Operación cancelada. UID no guardado.")

        # --- Esperar a que se retire la tarjeta ---
        # Esto es importante para no volver a leer la misma tarjeta 100 veces.
        print("\n[INFO] Por favor, retira la tarjeta del lector...")
        
        # Espera en un bucle mientras la tarjeta SIGA presente
        while pn532.read_passive_target(timeout=0.1) is not None:
            time.sleep(0.2) # Pequeña pausa para no saturar el bus I2C
            
        print("[INFO] Tarjeta retirada. Listo para la siguiente.")

except KeyboardInterrupt:
    print("\n\nCerrando el script de registro. ¡Adiós!")
    sys.exit()