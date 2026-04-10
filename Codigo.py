import threading
import queue
import time
import random
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(order=True)
class ImagenSatelital:
    prioridad: int
    id: str = field(compare=False)
    satelite: str = field(compare=False)
    timestamp: datetime = field(compare=False, default_factory=datetime.now)
    resolucion_mb: float = field(compare=False, default=0.0)

    def __str__(self):
        return (
            f"Imagen(id={self.id}, satelite={self.satelite}, "
            f"prio={self.prioridad}, {self.resolucion_mb:.1f} MB)"
        )


class Estadisticas:
    def __init__(self):
        self._lock = threading.Lock()
        self.recibidas = 0
        self.procesadas = 0

    def registrar_recibida(self):
        with self._lock:
            self.recibidas += 1

    def registrar_procesada(self):
        with self._lock:
            self.procesadas += 1

    def resumen(self):
        with self._lock:
            return (
                f"  Recibidas : {self.recibidas}\n"
                f"  Procesadas: {self.procesadas}\n"
                f"  En cola   : {self.recibidas - self.procesadas}"
            )


class ReceptorImagenes(threading.Thread):

    SATELITES = ["Satelite-1", "Satelite-2", "Satelite-3", "Satelite-4", "Satelite-5"]

    def __init__(self, cola, stats, total_imagenes=15):
        super().__init__(name="Receptor", daemon=True)
        self.cola = cola
        self.stats = stats
        self.total = total_imagenes

    def run(self):
        print("[Receptor] Iniciado. Esperando imagenes de satelites...")

        for i in range(1, self.total + 1):
            pausa = random.choice([0.1, 0.1, 0.2, 0.5, 1.0, 1.5])
            time.sleep(pausa)

            imagen = ImagenSatelital(
                id=f"IMG-{i:04d}",
                satelite=random.choice(self.SATELITES),
                prioridad=random.randint(1, 3),
                resolucion_mb=round(random.uniform(50.0, 500.0), 1),
            )

            self.cola.put(imagen)
            self.stats.registrar_recibida()
            print(f"[Receptor] RECIBIDA  {imagen}  (cola: {self.cola.qsize()} pendientes)")

        self.cola.put(None)
        print(f"[Receptor] Finalizado. Total enviadas: {self.total}")


class ProcesadorImagenes(threading.Thread):
    """Extrae imágenes de la cola y las procesa una a una."""

    def __init__(self, cola, stats):
        super().__init__(name="Procesador", daemon=True)
        self.cola = cola
        self.stats = stats

    def analizar(self, imagen):
        duracion = random.uniform(0.5, 2.0)
        time.sleep(duracion)
        return {
            "cobertura_nubes_%": round(random.uniform(0, 100), 1),
            "ndvi": round(random.uniform(-1, 1), 3),
            "anomalias": random.randint(0, 5),
            "duracion_s": round(duracion, 2),
        }

    def run(self):
        print("[Procesador] Iniciado. Esperando imagenes en cola...")

        while True:
            imagen = self.cola.get()  
            if imagen is None:        
                print("[Procesador] Señal de parada recibida.")
                self.cola.task_done()
                break

            print(f"[Procesador] PROCESANDO {imagen}...")
            resultado = self.analizar(imagen)
            self.stats.registrar_procesada()
            self.cola.task_done()

            print(
                f"[Procesador] COMPLETADA {imagen} -> "
                f"nubes={resultado['cobertura_nubes_%']}%, "
                f"NDVI={resultado['ndvi']}, "
                f"anomalias={resultado['anomalias']}, "
                f"tiempo={resultado['duracion_s']}s"
            )

        print("[Procesador] Finalizado.")


def main(): 
    print("SISTEMA DE PROCESAMIENTO DE IMAGENES SATELITALES")
   

    cola = queue.Queue(maxsize=0)
    stats = Estadisticas()

    receptor = ReceptorImagenes(cola, stats, total_imagenes=15)
    procesador = ProcesadorImagenes(cola, stats)

    inicio = time.time()

    procesador.start()
    receptor.start()

    receptor.join()
    procesador.join()

    elapsed = time.time() - inicio
    print("  RESUMEN FINAL")
    print("-" * 60)
    print(stats.resumen())
    print(f"  Tiempo total: {elapsed:.1f} s")
    print("-" * 60)


if __name__ == "__main__":
    main()
