import time
import lgpio
import sys

class CeldaDeCarga:
    """
    Clase para interactuar con el sensor HX711.
    (VERSIÓN 21.0 - Limpieza de GPIO más robusta)
    """
    
    def __init__(self, pin_dt, pin_sck):
        self.pin_dt = pin_dt
        self.pin_sck = pin_sck
        self.offset = 0
        self.factor_escala = 1.0
        self.h = None # Handle para la biblioteca lgpio
        
        # Banderas para rastrear qué pines logramos reclamar
        self._dt_claimed = False
        self._sck_claimed = False
        # --------------------
        
        try:
            self.h = lgpio.gpiochip_open(0)
            
            lgpio.gpio_claim_input(self.h, self.pin_dt)
            self._dt_claimed = True # Marcamos como reclamado
            
            lgpio.gpio_claim_output(self.h, self.pin_sck)
            self._sck_claimed = True # Marcamos como reclamado
            
            print(f"Celda de Carga (DT={pin_dt}, SCK={pin_sck}) inicializada con lgpio.")
            self.calibrar()

        except Exception as e:
            print(f"Error inicializando CeldaDeCarga (DT={pin_dt}): {e}")
            self.limpiar() # Asegurarnos de limpiar si el __init__ falla
            self.h = None # Marcar como fallido

    def limpiar(self):
        """Libera los pines GPIO de forma segura."""
        if self.h:
            print("\nLimpiando y liberando pines GPIO...")
            try:
                if self._dt_claimed:
                    lgpio.gpio_free(self.h, self.pin_dt)
                if self._sck_claimed:
                    lgpio.gpio_free(self.h, self.pin_sck)
                # ------------------------
                    
                lgpio.gpiochip_close(self.h)
                self.h = None
                print("Pines liberados.")
            except Exception as e:
                print(f"Error durante la limpieza: {e}")
                self.h = None

    def __del__(self):
        self.limpiar()

    def _is_ready(self):
        return lgpio.gpio_read(self.h, self.pin_dt) == 0

    def _read_raw_value(self):
        while not self._is_ready():
            time.sleep(0.01)

        lectura_cruda = 0
        for i in range(24):
            lgpio.gpio_write(self.h, self.pin_sck, 1)
            lectura_cruda = (lectura_cruda << 1)
            if lgpio.gpio_read(self.h, self.pin_dt) == 1:
                lectura_cruda += 1
            lgpio.gpio_write(self.h, self.pin_sck, 0)
        
        lgpio.gpio_write(self.h, self.pin_sck, 1)
        lgpio.gpio_write(self.h, self.pin_sck, 0)

        if lectura_cruda & 0x800000:
            lectura_cruda |= ~0xFFFFFF
            
        return lectura_cruda

    def calibrar(self):
        if self.h is None: return
        try:
            print(f"Iniciando calibración (tara)...")
            # Leemos 5 veces para la tara
            lecturas = [self._read_raw_value() for _ in range(5)]
            self.offset = sum(lecturas) / len(lecturas)
            print(f"Calibración completada. Offset: {self.offset}")
            time.sleep(0.5) # Reducimos la espera
        except Exception as e:
            print(f"Error durante la calibración: {e}")

    def establecer_factor_escala(self, factor):
        self.factor_escala = factor
        print(f"Factor de escala establecido en: {factor}")

    def obtener_peso(self):
        """Devuelve el peso actual en gramos, promediando 5 lecturas."""
        if self.h is None: return 0.0
        try:
            lecturas = [self._read_raw_value() for _ in range(5)]
            lectura_neta = (sum(lecturas) / len(lecturas)) - self.offset
            
            if self.factor_escala == 0: return 0.0
            
            # --- MODIFICADO V23 ---
            # ¡Usamos abs() para ignorar la inversión!
            gramos = abs(lectura_neta / self.factor_escala)
            # ---------------------

            # La lógica de 'gramos < 0' ya no es fiable
            # Usamos un umbral pequeño de 'lectura_neta'
            if abs(lectura_neta) < (self.factor_escala * 0.5): # Si es menos de medio gramo
                 return 0.0
            
            return gramos
        except Exception as e:
            print(f"Error al leer el peso: {e}")
            return 0.0

    def obtener_lectura_cruda(self):
        """Devuelve la lectura cruda (promediada), menos el offset."""
        if self.h is None: return 0
        try:
            lecturas = [self._read_raw_value() for _ in range(5)]
            valor_neto = (sum(lecturas) / len(lecturas)) - self.offset
            
            # --- MODIFICADO V23 ---
            # ¡Usamos abs() para ignorar la inversión!
            return abs(valor_neto)
            # ---------------------
        except Exception as e:
            print(f"Error al leer valor en crudo: {e}")
            return 0