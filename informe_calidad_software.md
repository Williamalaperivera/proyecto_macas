# Informe de Evaluación y Calidad de Software: Proyecto MCAS

---

## 1. Introducción

### Objetivo
Evaluar la calidad del software mediante pruebas automatizadas y análisis estático del sistema, identificando problemas potenciales, validando el comportamiento ante fallas de sensores y proponiendo mejoras continuas en la robustez y confiabilidad del código.

### Herramienta(s) utilizada(s)
* **pytest 9.1.1** (Entorno de pruebas unitarias y aserciones)
* **Python 3.12.3** (Intérprete base, plataforma `win32`)
* **Librerías de soporte:** `pluggy 1.6.0`, `iniconfig 2.3.1`, `colorama 0.4.6`

### Alcance
Se analizaron los módulos principales del sistema de control y validación de redundancia de sensores de Ángulo de Ataque (**MCAS - Maneuvering Characteristics Augmentation System**), específicamente:
* Módulo lógico principal: `mcas_logic.py` (`procesar_sensores_aoa`)
* Suite de pruebas unitarias: `tests/test_mcas.py`

El análisis abarca aspectos críticos de:
1. **Seguridad y tolerancia a fallos:** Detección de discrepancias (`AOA Disagree`), entradas nulas (`NULL/None`) y valores físicamente inválidos.
2. **Rendimiento:** Tiempos de ejecución y sobrecarga de validación en tiempo de ejecución.
3. **Mantenibilidad:** Cobertura de ramas condicionales, legibilidad y adherencia a estándares de codificación PEP 8.

---

## 2. Metodología

### Proceso
1. **Configuración del entorno:** Instalación y aprovisionamiento de dependencias mediante `pip install pytest`.
2. **Ejecución del análisis y pruebas:** Ejecución de la suite completa con `pytest` en la raíz del proyecto.
3. **Revisión de resultados y reportes:** Inspección de los reportes generados en consola, análisis de cobertura de casos borde (edge cases) e inspección de patrones de codificación.

```
+---------------------+       +--------------------+       +-----------------------+
|  Entorno & Setup    | ----> |  Ejecución pytest  | ----> |  Revisión & Reportes  |
|  (Python 3.12, pip) |       |  (6 tests pasados) |       |  (Inspección técnica) |
+---------------------+       +--------------------+       +-----------------------+
```

### Criterios de evaluación
* **Normas de codificación:** Cumplimiento de estándares de estilo PEP 8, convenciones de tipado estático (*type hints*) y claridad en docstrings.
* **Vulnerabilidades y seguridad:** Manejo defensivo frente a inyecciones de tipos inválidos, valores nulos no controlados y desbordamiento de rangos físicos de los sensores (-90° a +90°).
* **Duplicidad de código:** Detección de validaciones redundantes o lógica de decisión repetitiva en el flujo de control.
* **Cobertura de pruebas:** Medición del alcance de las aserciones sobre cada caso de uso: sincronización normal, diferencias tolerables (<= 3°), advertencias intermedias (3° < diff <= 10°), inconsistencia severa (> 10°), y excepciones esperadas (`ValueError`, `TypeError`).

---

## 3. Resultados del análisis

### Resumen de Ejecución
La ejecución automatizada arrojó un resultado satisfactorio en la suite ejecutada:
* **Pruebas recolectadas:** 6
* **Pruebas aprobadas:** 6 (100% de éxito)
* **Tiempo total de ejecución:** 0.03 segundos

| Caso de Prueba (`tests/test_mcas.py`) | Entrada / Escenario | Resultado Obtenido | Estado |
| :--- | :--- | :--- | :---: |
| `test_valores_normales` | AoA1=15, AoA2=16 (diff: 1°) | Sincronización normal | **PASSED** |
| `test_diferencia_pequena` | AoA1=20, AoA2=22 (diff: 2°) | Sincronización normal | **PASSED** |
| `test_diferencia_grande` | AoA1=70, AoA2=15 (diff: 55°) | Alerta crítica (AOA Disagree) | **PASSED** |
| `test_sensor_sin_informacion` | AoA1=20, AoA2=None | `ValueError` (Sensor NULL) | **PASSED** |
| `test_valor_invalido` | AoA1=-200, AoA2=15 | `ValueError` (Fuera de rango) | **PASSED** |
| `test_formato_incorrecto` | AoA1="ABC", AoA2=15 | `TypeError` (Dato no numérico) | **PASSED** |

---

### Severidad y Tipos de Hallazgos

A partir del análisis estático y funcional complementario sobre la implementación actual, se identificaron los siguientes hallazgos:

| ID | Categoría | Severidad | Descripción del Hallazgo | Ubicación | Frecuencia |
| :---: | :--- | :---: | :--- | :--- | :---: |
| **H-01** | Cobertura de Pruebas | **Medio** | La rama condicional de advertencia intermedia (`3 < diff <= 10`) no tiene una prueba unitaria explícita asociada en `test_mcas.py`. | `mcas_logic.py:23` | 1 vez |
| **H-02** | Tipado y Codificación | **Bajo** | Ausencia de Type Annotations en la firma de `procesar_sensores_aoa(aoa_1: float, aoa_2: float) -> str`. | `mcas_logic.py:1` | Recurrente |
| **H-03** | Arquitectura / Mantenibilidad | **Medio** | El resultado se retorna como cadenas literales de texto (`str`) en lugar de enumeraciones (`Enum`) o estructuras de estado tipadas. | `mcas_logic.py:22-26` | 3 retornos |
| **H-04** | Rendimiento | **Bajo** | Tiempo de validación óptimo (< 1 ms por llamada), sin cuellos de botella detectados para ejecución sincrónica. | General | N/A |
| **H-05** | Seguridad / Integridad | **Bajo** | Las validaciones de rango físico están cableadas (*hardcoded*) en el código sin constantes reutilizables configurables. | `mcas_logic.py:15` | 1 vez |

---

### Estadísticas de Distribución de Hallazgos

#### Distribución por Severidad
```
Crítico:    [0]  (0%)
Alto:       [0]  (0%)
Medio:      [2]  (40%)  ████████████████
Bajo:       [3]  (60%)  ████████████████████████
Total:      5 hallazgos analizados
```

#### Distribución por Categoría
| Categoría | Cantidad | Porcentaje |
| :--- | :---: | :---: |
| Cobertura y Pruebas Unitarias | 1 | 20% |
| Mantenibilidad y Estructura | 2 | 40% |
| Calidad de Codificación (Typing/Estándares) | 1 | 20% |
| Seguridad e Integridad de Parámetros | 1 | 20% |

### Archivos de soporte
* **Consola de pytest:** `rootdir: C:\Users\willi\OneDrive\Desktop\proyecto_mcas`, `tests\test_mcas.py ...... [100%]`
* **Caché de pruebas:** `.pytest_cache/`
* **Módulos bajo análisis:** `mcas_logic.py` y `tests/test_mcas.py`

---

## 4. Análisis de impacto

### Impacto potencial
1. **Riesgos en seguridad y confiabilidad:** En sistemas críticos como MCAS, la falta de verificación automatizada sobre el rango de alerta menor (`3 < diff <= 10`) podría permitir regresiones desapercibidas en revisiones futuras.
2. **Degradación del rendimiento:** Actualmente inexistente debido a la simplicidad algorítmica; sin embargo, el procesamiento de cadenas de texto comparativas en clientes externos agrega sobrecarga innecesaria frente a códigos de estado numéricos o enumeraciones.
3. **Afectación de la funcionalidad:** Retornar cadenas de caracteres propicia errores por discrepancias tipográficas en integraciones con otros subsistemas o interfaces de cabina.
4. **Aumento de costos de mantenimiento:** La ausencia de *Type Annotations* reduce la efectividad del análisis estático automatizado (como `mypy` o `flake8`) y dificulta la incorporación de nuevos desarrolladores.

### Prioridad de resolución
1. **Prioridad Alta:** Incorporar el caso de prueba faltante para cubrir la rama intermedia (`3° < diferencia <= 10°`) garantizando el 100% de cobertura de ramas (*branch coverage*).
2. **Prioridad Media:** Reemplazar el retorno de cadenas de texto por enumeraciones (`Enum` / constantes de estado) para desacoplar lógica de presentación y lógica de control.
3. **Prioridad Baja:** Implementar tipado estático (*Type Hints*) en los parámetros de entrada y salida, y parametrizar las constantes de umbrales (-90, 90, 3, 10).

---

## 5. Recomendaciones

### Acciones correctivas
* **Completar suite de pruebas:** Agregar `test_alerta_menor()` en `tests/test_mcas.py` (ej. con valores de 10 y 15, diferencia de 5 grados).
* **Refactorización de tipos de retorno:** Definir una clase de estados:
  ```python
  from enum import Enum

  class EstadoMCAS(Enum):
      SINCRONIZADO = "Procesamiento normal. Sistemas sincronizados."
      ALERTA_MENOR = "Alerta menor: Identificar diferencia y continuar según reglas definidas."
      AOA_DISAGREE = "Alerta crítica (AOA Disagree): Inconsistencia grave entre sensores. Desactivando MCAS automático."
  ```
* **Introducción de constantes de umbral:** Declarar `UMBRAL_NORMAL = 3`, `UMBRAL_ALERTA = 10`, `RANGO_AOA_MIN = -90`, `RANGO_AOA_MAX = 90`.

### Mejoras de proceso
* **Integración de análisis estático continuo:** Incorporar herramientas de linter y tipado estático como `flake8`, `black` y `mypy` en el flujo de trabajo local y en CI/CD.
* **Medición de cobertura de código:** Integrar `pytest-cov` para auditar formalmente el porcentaje de cobertura de líneas y de ramas condicionales en cada commit.
* **Revisiones de código (Peer Review):** Exigir que cualquier modificación a las reglas de tolerancia del sistema incluya pruebas unitarias positivas y negativas asociadas.

---

## 6. Conclusiones

### Resumen
La evaluación realizada confirma que el módulo central de validación de redundancia de sensores (`mcas_logic.py`) cuenta con una sólida base de pruebas unitarias que superó con éxito las 6 aserciones ejecutadas bajo **pytest 9.1.1** en 0.03 segundos. Se valida correctamente el comportamiento defensivo ante datos `None`, datos de tipos inválidos y divergencias graves entre sensores.

No obstante, el análisis estático y de diseño pone de manifiesto oportunidades de mejora en la cobertura de ramas intermedias, la estandarización mediante tipos de datos fuertemente tipados y la desacoplación de cadenas de texto.

### Próximos pasos
1. Añadir la prueba unitaria para la condición `3 < diff <= 10`.
2. Refactorizar el módulo aplicando *Type Hints* y constantes/enumeraciones.
3. Automatizar la ejecución de `pytest` con reporte de cobertura mediante scripts o pipelines de integración continua.
