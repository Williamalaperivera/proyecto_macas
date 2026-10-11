def procesar_sensores_aoa(aoa_1, aoa_2):
    """
    Simula la lógica de validación de los sensores del Ángulo de Ataque (AoA).
    Retorna una respuesta basada en las reglas de seguridad de redundancia.
    """
    # 1. Validación de datos nulos
    if aoa_1 is None or aoa_2 is None:
        raise ValueError("Error crítico: Un sensor no está enviando información (NULL).")
        
    # 2. Validación de formatos correctos
    if not isinstance(aoa_1, (int, float)) or not isinstance(aoa_2, (int, float)):
        raise TypeError("Error de formato: Los datos del sensor deben ser numéricos.")
        
    # 3. Validación de valores fuera de rango físico razonable
    if aoa_1 < -90 or aoa_1 > 90 or aoa_2 < -90 or aoa_2 > 90:
        raise ValueError("Error de lectura: Valor de sensor inválido o fuera de rango.")

    # 4. Validación cruzada de redundancia (Doble Sensor)
    diferencia = abs(aoa_1 - aoa_2)
    
    # 5. Lógica de decisión segura
    if diferencia <= 3:
        return "Procesamiento normal. Sistemas sincronizados."
    elif 3 < diferencia <= 10:
        return "Alerta menor: Identificar diferencia y continuar según reglas definidas."
    else:
        return "Alerta crítica (AOA Disagree): Inconsistencia grave entre sensores. Desactivando MCAS automático."