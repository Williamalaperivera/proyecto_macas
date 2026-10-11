import sys
import os
import pytest

# Permite que pytest encuentre el archivo mcas_logic en la carpeta anterior
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcas_logic import procesar_sensores_aoa

def test_valores_normales():
    # Prueba con valores de 15 y 16 (diferencia de 1 grado)
    resultado = procesar_sensores_aoa(15, 16)
    assert resultado == "Procesamiento normal. Sistemas sincronizados."

def test_diferencia_pequena():
    # Prueba con valores de 20 y 22 (diferencia de 2 grados)
    resultado = procesar_sensores_aoa(20, 22)
    assert resultado == "Procesamiento normal. Sistemas sincronizados."

def test_diferencia_grande():
    # Prueba con valores de 70 y 15 (diferencia de 55 grados)
    resultado = procesar_sensores_aoa(70, 15)
    assert resultado == "Alerta crítica (AOA Disagree): Inconsistencia grave entre sensores. Desactivando MCAS automático."

def test_sensor_sin_informacion():
    # Prueba con un sensor arrojando valor NULL (None en Python)
    with pytest.raises(ValueError, match="Un sensor no está enviando información"):
        procesar_sensores_aoa(20, None)

def test_valor_invalido():
    # Prueba con un valor físicamente imposible (-200)
    with pytest.raises(ValueError, match="Valor de sensor inválido o fuera de rango"):
        procesar_sensores_aoa(-200, 15)

def test_formato_incorrecto():
    # Prueba inyectando una cadena de texto en lugar de un número
    with pytest.raises(TypeError, match="Los datos del sensor deben ser numéricos"):
        procesar_sensores_aoa("ABC", 15)