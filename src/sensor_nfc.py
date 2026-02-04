import time
import board
import busio
import sys
from adafruit_pn532.i2c import PN532_I2C

class SensorNFC:
    """
    Clase para manejar la lógica del lector NFC PN532
    y la validación de tarjetas.
    """
    
    def __init__(self):
        """
        Inicializa la conexión I2C con el lector PN532.
        """
        self.pn532 = None
        self.valid_uids = set() # Un 'set' para búsquedas rápidas (O(1))

        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.pn532 = PN532_I2C(i2c, debug=False)

            # Comprobar la conexión leyendo la versión del firmware
            versiondata = self.pn532.firmware_version
            print(f"[NFC] Lector PN532 encontrado. Firmware: {versiondata[0]}.{versiondata[1]}")

            # Configurar el lector para escuchar
            self.pn532.SAM_configuration()
            print("[NFC] Lector configurado y esperando tarjetas...")

        except Exception as e:
            print(f"[ERROR FATAL] No se pudo inicializar el SensorNFC.")
            print(f"Detalle: {e}")
            print("Verifica la conexión I2C (SCL/SDA) y que I2C esté habilitado.")
            self.pn532 = None

    def cargar_uids_validos(self, archivo="valid_uids.txt"):
        """
        Lee el archivo de texto (generado por registrar_tarjeta.py)
        y carga los UIDs en el 'set' en memoria.
        """
        if self.pn532 is None:
            return False
            
        try:
            with open(archivo, 'r') as f:
                for linea in f:
                    uid_limpio = linea.strip()
                    if uid_limpio:
                        self.valid_uids.add(uid_limpio)
            print(f"[NFC] Se cargaron {len(self.valid_uids)} UIDs válidos desde {archivo}.")
            return True
        except FileNotFoundError:
            print(f"[ERROR] No se encontró el archivo de UIDs: {archivo}")
            return False
        except Exception as e:
            print(f"[ERROR] No se pudo leer el archivo de UIDs: {e}")
            return False

    def es_valido(self, uid_string):
        """
        Comprueba si un UID (string) está en el set de UIDs válidos.
        """
        return uid_string in self.valid_uids

    def esperar_y_leer_uid(self, timeout=0.5):
        """
        Intenta leer una tarjeta. No es bloqueante.
        Devuelve el UID como string si encuentra una, o None si no.
        """
        if self.pn532 is None:
            return None
            
        try:
            # 'timeout=0.5' significa que solo espera 0.5s
            uid = self.pn532.read_passive_target(timeout=timeout)
            
            if uid is None:
                return None
            
            # Convertimos el bytearray a string hexadecimal
            return uid.hex()
            
        except Exception as e:
            # Esto puede pasar si la tarjeta se retira muy rápido
            # print(f"Error de lectura NFC: {e}")
            return None