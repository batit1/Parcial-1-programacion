El programa lanza dos hilos en paralelo:

El Receptor que seria el producer: simula la llegada de imágenes a ritmo variable.
Cada imagen se mete en la cola inmediatamente para no perderla.

El Procesador (consumer): saca imágenes de la cola y las analiza una a una.
Si la cola está vacía, espera sin consumir CPU.

La queue.Queue actúa como buffer entre los dos hilos. Es thread-safe por
diseño, por lo que no hace falta sincronización manual.


El hilo Receptor encola cada imagen nada más recibirla (cola.put()).
Como la cola es ilimitada (maxsize=0), nunca se pierde ninguna imagen,
aunque lleguen en ráfagas muy rápidas.


Es thread-safe(no hace falta Lock manual).
Mantiene el orden FIFO (primera en llegar, primera en procesarse).
get() es bloqueante: el procesador duerme hasta que haya trabajo,
  sin malgastar CPU.

Sin buffer - Las imágenes que llegan mientras se procesa otra se pierden
Lista sin Lock - Dos hilos modificándola a la vez corrompería los datos 
Bucle de espera activo - El procesador consumiría el 100% de CPU esperando 

Los dos hilos arrancan a la vez con .start() y corren de forma independiente. El Receptor no espera al Procesador y viceversa. 
Al terminar todas las imágenes, el Receptor mete un None en la cola como señal de parada para que el Procesador acabe de forma ordenada.
Finalmente, .join() espera a que ambos hilos terminen antes de mostrar el resumen.
