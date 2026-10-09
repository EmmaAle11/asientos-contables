"""
ejercicios_seed.py
==================
Ejercicios contables de EJEMPLO ("seed") ya resueltos y cuadrados.

Sirven para dos cosas:
  1. Que la interfaz arranque con contenido de muestra (correcta función).
  2. Que el estudiante vea asientos bien hechos como referencia.

Todos usan cuentas del catálogo del SAT (cuentas_sat.py) y respetan la
partida doble (total de cargos == total de abonos).
"""

from ..dominio.modelo import Asiento, Movimiento
from ..dominio.puertos import RepositorioEjercicios

# Fecha de ejemplo usada en los seeds (puedes cambiarla en la interfaz).
FECHA = "2026-07-25"


def _apertura() -> Asiento:
    """Asiento 1: Apertura del negocio con aportación de los socios."""
    a = Asiento("1) Apertura - Aportación de capital")
    a.agregar(Movimiento(FECHA, "102.01", cargo=200000, descripcion="Depósito inicial en banco"))
    a.agregar(Movimiento(FECHA, "101.01", cargo=50000,  descripcion="Efectivo en caja"))
    a.agregar(Movimiento(FECHA, "301.01", abono=250000, descripcion="Aportación de los socios"))
    return a


def _compra_credito() -> Asiento:
    """Asiento 2: Compra de mercancía a crédito con IVA (16%)."""
    a = Asiento("2) Compra de mercancía a crédito (IVA 16%)")
    a.agregar(Movimiento(FECHA, "115.01", cargo=100000, descripcion="Mercancía adquirida"))
    a.agregar(Movimiento(FECHA, "118.01", cargo=16000,  descripcion="IVA acreditable (16%)"))
    a.agregar(Movimiento(FECHA, "201.01", abono=116000, descripcion="Adeudo al proveedor"))
    return a


def _venta_contado() -> Asiento:
    """Asiento 3: Venta de mercancía de contado con IVA (16%)."""
    a = Asiento("3) Venta de contado (IVA 16%)")
    a.agregar(Movimiento(FECHA, "102.01", cargo=69600,  descripcion="Cobro en banco"))
    a.agregar(Movimiento(FECHA, "401.01", abono=60000,  descripcion="Ingreso por ventas"))
    a.agregar(Movimiento(FECHA, "213.01", abono=9600,   descripcion="IVA trasladado (16%)"))
    return a


def _pago_renta() -> Asiento:
    """Asiento 4: Pago de la renta del local con cheque/transferencia."""
    a = Asiento("4) Pago de renta del local (IVA 16%)")
    a.agregar(Movimiento(FECHA, "601.06", cargo=15000, descripcion="Renta del mes"))
    a.agregar(Movimiento(FECHA, "118.01", cargo=2400,  descripcion="IVA acreditable (16%)"))
    a.agregar(Movimiento(FECHA, "102.01", abono=17400, descripcion="Pago desde banco"))
    return a


def _pago_proveedor() -> Asiento:
    """Asiento 5: Pago total de la deuda al proveedor."""
    a = Asiento("5) Pago a proveedor")
    a.agregar(Movimiento(FECHA, "201.01", cargo=116000, descripcion="Liquidación de adeudo"))
    a.agregar(Movimiento(FECHA, "102.01", abono=116000, descripcion="Salida de banco"))
    return a


def cargar_seeds() -> list[Asiento]:
    """Devuelve la lista de todos los ejercicios de ejemplo, ya cuadrados."""
    return [
        _apertura(),
        _compra_credito(),
        _venta_contado(),
        _pago_renta(),
        _pago_proveedor(),
    ]


class RepositorioSeed(RepositorioEjercicios):
    """
    ADAPTADOR del puerto RepositorioEjercicios.

    Sirve los ejercicios de ejemplo escritos arriba. El dia que se guarden en
    disco o en una base de datos, basta escribir otro adaptador que implemente
    el mismo puerto; ni el dominio ni los casos de uso cambian.
    """

    def cargar(self) -> list[Asiento]:
        return cargar_seeds()
