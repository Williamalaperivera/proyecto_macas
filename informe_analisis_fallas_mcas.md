# Informe de Evaluación y Calidad de Software: Detección de Errores y Vulnerabilidades Críticas (MCAS)

---

## 1. Introducción

### Objetivo
Evaluar la calidad y confiabilidad del software mediante pruebas automatizadas y análisis de comportamiento frente a fallas, identificando vulnerabilidades críticas en la arquitectura de decisión, ausencia de validación defensiva y proponiendo las acciones correctivas inmediatas para mitigar riesgos operacionales y de seguridad.

### Herramienta(s) utilizada(s)
* **pytest 9.1.1** (Framework de pruebas automatizadas y aserciones)
* **Python 3.12.3** (Intérprete base, plataforma `win32`)
* **Librerías de soporte:** `pluggy 1.6.0`, `iniconfig 2.3.1`, `colorama 0.4.6`

### Alcance
Se sometió a prueba la implementación original vulnerable del módulo central de decisión del sistema de aumento de características de maniobra (**MCAS - Maneuvering Characteristics Augmentation System**):
* Módulo evaluado: `mcas_logic.py` (`procesar_sensores_aoa`)
* Suite de verificación de vulnerabilidades: `tests/test_mcas.py`

El alcance consideró los siguientes aspectos:
1. **Seguridad operacional y redundancia:** Comportamiento ante fallas asimétricas de un sensor (Single Point of Failure).
2. **Robustez ante entradas anómalas:** Manejo de datos nulos (`None`) e inyección de datos no numéricos (`str`).
3. **Mantenibilidad y tolerancia a fallos:** Estabilidad de la ejecución sin interrupciones abruptas no controladas por el intérprete.

---

## 2. Metodología

### Proceso
1. **Configuración y preparación:** Definición de escenarios de prueba diseñados para exponer fallas críticas de redundancia y validación de tipos.
2. **Ejecución del análisis dinámico:** Ejecución de la suite con el comando `pytest` en la raíz del proyecto.
3. **Revisión de reportes y trazas:** Análisis de las excepciones no controladas (`TypeError`), aserciones fallidas (`AssertionError`) y recolección de las discrepancias entre el comportamiento esperado y el comportamiento real.

```
+-----------------------------------+
| Definición de Escenarios Críticos |
| (Falla sensor, NULL, tipo String) |
+-----------------------------------+
                  │
                  ▼
+-----------------------------------+
|    Ejecución con pytest 9.1.1     | ──> [ 3 Fallas Detectadas (100% Fail) ]
+-----------------------------------+
                  │
                  ▼
+-----------------------------------+
| Diagnóstico de Causa Raíz (RCA)   |
| (Punto único de falla y no-valid) |
+-----------------------------------+
```

### Criterios de evaluación
* **Validación de redundancia cruzada:** El sistema no debe tomar decisiones críticas de control de vuelo basándose en un único sensor si existe discrepancia con el sensor secundario.
* **Manejo defensivo de excepciones:** Las entradas nulas o inválidas deben ser interceptadas y manejadas con mensajes de error de negocio controlados (`ValueError`), sin provocar colapsos no controlados del intérprete de Python.
* **Integridad de tipos:** Verificación estricta de formato numérico previo a cualquier operación de comparación lógica (`>=`).

---

## 3. Resultados del análisis

### Resumen de Ejecución
La ejecución de la suite de pruebas arrojó un **100% de fallas**, evidenciando la presencia de vulnerabilidades severas en el módulo evaluado:
* **Pruebas recolectadas:** 3
* **Pruebas aprobadas:** 0 (0%)
* **Pruebas fallidas:** 3 (100%)
* **Tiempo de ejecución:** 0.08 segundos

| Caso de Prueba (`tests/test_mcas.py`) | Escenario Evaluado | Resultado Esperado | Resultado Real Obtenido | Estado |
| :--- | :--- | :--- | :--- | :---: |
| `test_error_critico_falta_validacion_cruzada` | Sensor 1 defectuoso (80°), Sensor 2 normal (15°) | `Alerta crítica: Discrepancia de sensores.` | `"Activando MCAS: Bajando el morro del avión."` (`AssertionError`) | **FAILED** |
| `test_error_alto_datos_nulos_no_controlados` | Sensor principal desconectado (`None`, 15°) | `ValueError("Sensor desconectado")` | `TypeError: '>=' not supported between 'NoneType' and 'int'` | **FAILED** |
| `test_error_alto_formatos_invalidos` | Entrada de texto corrupto (`"Error"`, 15°) | `TypeError("Formato numérico requerido")` | Colapso del intérprete sin mensaje de dominio controlado | **FAILED** |

---

### Severidad y Tipos de Hallazgos

| ID | Tipo de Hallazgo | Severidad | Descripción del Problema | Ubicación | Frecuencia |
| :---: | :--- | :---: | :--- | :--- | :---: |
| **H-01** | **Seguridad / Arquitectura** | **Crítico** | **Punto Único de Falla (Single Point of Failure):** El algoritmo ignora por completo el sensor secundario (`aoa_2`) y activa el MCAS basándose únicamente en `aoa_1 >= 20`. | `mcas_logic.py:10` | Continua (100% de ejecuciones) |
| **H-02** | **Confiabilidad / Robustez** | **Alto** | **Ausencia de Validación de Nulos:** Comparación directa de `aoa_1` sin verificar si el valor es `None`, arrojando una excepción fatal no controlada. | `mcas_logic.py:10` | Cada vez que un sensor se desconecta |
| **H-03** | **Calidad de Código / Manejo de Tipos** | **Alto** | **Falta de Validación de Tipos:** No se verifica si los argumentos son de tipo numérico (`int`, `float`), provocando fallas del runtime al recibir cadenas o basura. | `mcas_logic.py:10` | Cada vez que se envían datos corruptos |
| **H-04** | **Mantenibilidad** | **Medio** | Falta de documentación de reglas de seguridad y ausencia de constantes para los umbrales de activación (valor 20 cableado). | `mcas_logic.py:10` | Estático en código |

---

### Estadísticas y Gráficos de Distribución

#### Distribución de Hallazgos por Severidad
```
Crítico:    [1]  (25%)  ████████████
Alto:       [2]  (50%)  ████████████████████████
Medio:      [1]  (25%)  ████████████
Bajo:       [0]  ( 0%)
Total:      4 hallazgos detectados
```

#### Distribución por Categoría de Problema
| Categoría | Cantidad | Porcentaje | Impacto Directo |
| :--- | :---: | :---: | :--- |
| Seguridad Crítica (Falla de Redundancia) | 1 | 25% | Activación errónea de actuadores |
| Robustez y Manejo de Excepciones | 2 | 50% | Caída/Bloqueo inesperado del servicio |
| Mantenibilidad y Parámetros Cableados | 1 | 25% | Dificultad de parametrización y auditoría |

### Archivos de soporte
* **Salida de consola de pytest:**
  ```
  FAILED tests/test_mcas.py::test_error_critico_falta_validacion_cruzada - AssertionError: ERROR CRÍTICO: El sistema ignoró el Sensor 2 y activó el MCAS basándose en un dato falso.
  FAILED tests/test_mcas.py::test_error_alto_datos_nulos_no_controlados - TypeError: '>=' not supported between instances of 'NoneType' and 'int'
  FAILED tests/test_mcas.py::test_error_alto_formatos_invalidos - AssertionError: Regex pattern did not match.
  ============================== 3 failed in 0.08s ==============================
  ```
* **Módulos auditados:** `mcas_logic.py` y `tests/test_mcas.py`.

---

## 4. Análisis de impacto

### Impacto potencial
1. **Riesgos catastróficos de seguridad:** Si un sensor físico de Ángulo de Ataque sufre avería o congelamiento y reporta un valor espurio (ej. 80°), el sistema ordenará bajar el morro de la aeronave de forma inadvertida e injustificada, aun cuando el segundo sensor indique condiciones de vuelo normales (15°).
2. **Denegación de servicio / Crash en ejecución:** Una pérdida de señal temporal o paquete corrupto (`None`, texto) interrumpe bruscamente el hilo de ejecución con `TypeError`, congelando el módulo de aviónica o el microservicio correspondiente.
3. **Degradación funcional y pérdida de control:** La ausencia de una alarma intermedia de discrepancia (`AOA Disagree`) priva a los operadores y sistemas superiores de la capacidad de deshabilitar la automatización a tiempo.
4. **Altos costos correctivos:** Mantener un diseño sin validación cruzada acarrea costos millonarios en rediseño, recertificación aeronáutica y daño reputacional.

### Prioridad de resolución
1. **Prioridad Inmediata (P1 - Crítico):** Implementar la validación cruzada y comparación diferencial de ambos sensores (`abs(aoa_1 - aoa_2)`); si la diferencia supera el umbral de tolerancia, desactivar la acción automática y disparar alerta.
2. **Prioridad Urgente (P2 - Alto):** Introducir validaciones de guarda al inicio de la función para descartar valores nulos (`is None`) y tipos no soportados antes de cualquier evaluación lógica.
3. **Prioridad Media (P3 - Medio):** Centralizar los umbrales de operación en constantes configurables y registrar eventos de auditoría (logs estructurados).

---

## 5. Recomendaciones

### Acciones correctivas
1. **Restablecer la lógica de redundancia y arquitectura segura:**
   ```python
   def procesar_sensores_aoa(aoa_1, aoa_2):
       # 1. Validación de desconexión / datos nulos
       if aoa_1 is None or aoa_2 is None:
           raise ValueError("Sensor desconectado o valor nulo.")

       # 2. Validación de formato de datos
       if not isinstance(aoa_1, (int, float)) or not isinstance(aoa_2, (int, float)):
           raise TypeError("Formato numérico requerido.")

       # 3. Validación de rango físico
       if not (-90 <= aoa_1 <= 90 and -90 <= aoa_2 <= 90):
           raise ValueError("Valor fuera de rango físico.")

       # 4. Validación cruzada de redundancia (Doble Sensor)
       diferencia = abs(aoa_1 - aoa_2)
       if diferencia > 10:
           return "Alerta crítica: Discrepancia de sensores."

       # 5. Decisión segura basada en ambos sensores concordantes
       if aoa_1 >= 20 and aoa_2 >= 20:
           return "Activando MCAS: Bajando el morro del avión."

       return "Procesamiento normal."
   ```
2. **Normalización de excepciones y contratos:** Asegurar que los mensajes de excepción coincidan con los contratos definidos en la especificación y en las pruebas unitarias.

### Mejoras de proceso
* **Pruebas de Inyección de Fallas (Fault Injection Testing):** Establecer como requisito mandatorio en el ciclo de vida de desarrollo la inclusión de pruebas negativas (sensores descalibrados, ruidos, desconexiones).
* **Bloqueo en Integración Continua (CI Quality Gates):** Impedir la integración de código a ramas principales si existe un fallo en las pruebas unitarias o si la cobertura cae por debajo del 100% en módulos de decisión crítica.
* **Análisis de Modos y Efectos de Falla (FMEA):** Revisar periódicamente la arquitectura para garantizar que ningún componente crítico dependa de una única fuente de datos.

---

## 6. Conclusiones

### Resumen
La nueva ejecución de pruebas automatizadas con **pytest 9.1.1** cumplió con éxito el propósito de evidenciar las debilidades intrínsecas de la lógica vulnerable. Las 3 pruebas fallidas demostraron empíricamente la existencia de un **punto único de falla crítico**, capaz de emitir comandos peligrosos ante sensores defectuosos, así como la vulnerabilidad del sistema ante caídas inesperadas por entradas nulas y datos corruptos.

### Próximos pasos
1. Aplicar de inmediato el parche correctivo con validación cruzada y guardas defensivas en `mcas_logic.py`.
2. Reejecutar `pytest` para certificar la aprobación total (3/3 passed).
3. Añadir pruebas de integración adicionales para validar los tiempos de respuesta y la resiliencia en escenarios de pérdida simultánea de telemetría.
