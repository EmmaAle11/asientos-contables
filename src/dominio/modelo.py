"""
DOMINIO :: Modelo
=================
Corazón del negocio contable.

Define dos estructuras principales:
  - Movimiento : una línea de un asiento (fecha, cuenta, cargo, abono, descripción).
  - Asiento    : un ejercicio contable completo = conjunto de movimientos que,
                 por partida doble, deben CUADRAR (total cargos == total abonos).

Esta capa no importa tkinter, ni openpyxl, ni nada de fuera: solo reglas
contables. Por eso se puede probar sin abrir una ventana ni escribir un Excel.
"""

from dataclasses import dataclass, field

from .catalogo_sat import obtener_cuenta
from .errores import CuentaInexistente, MovimientoInvalido


@dataclass
class Movimiento:
    """
    Una línea (renglón) de un asiento contable.

    Atributos:
        fecha       : fecha del movimiento (texto 'AAAA-MM-DD').
        codigo      : código agrupador del SAT de la cuenta (ej. '101.01').
        cargo       : importe al DEBE (>= 0).
        abono       : importe al HABER (>= 0).
        descripcion : concepto/glosa del movimiento.
    """
    fecha: str
    codigo: str
    cargo: float = 0.0
    abono: float = 0.0
    descripcion: str = ""

    @property
    def nombre_cuenta(self) -> str:
        """Nombre de la cuenta según el catálogo del SAT."""
        cuenta = obtener_cuenta(self.codigo)
        return cuenta.nombre if cuenta else "(cuenta desconocida)"

    def validar(self) -> None:
        """
        Verifica que el movimiento sea coherente.
        Lanza ValueError con un mensaje claro si algo está mal.
        """
        if obtener_cuenta(self.codigo) is None:
            raise CuentaInexistente(f"La cuenta '{self.codigo}' no existe en el catálogo SAT.")
        if self.cargo < 0 or self.abono < 0:
            raise MovimientoInvalido("Cargo y abono no pueden ser negativos.")
        if self.cargo > 0 and self.abono > 0:
            raise MovimientoInvalido("Un movimiento no puede tener cargo Y abono a la vez.")
        if self.cargo == 0 and self.abono == 0:
            raise MovimientoInvalido("El movimiento debe tener un cargo o un abono.")


@dataclass
class Asiento:
    """
    Un ejercicio/asiento contable completo.

    Atributos:
        nombre      : título del ejercicio (ej. 'Compra de mercancía a crédito').
        movimientos : lista de Movimiento que lo componen.
    """
    nombre: str
    movimientos: list[Movimiento] = field(default_factory=list)

    # ---- subrutinas de cálculo ----
    def total_cargos(self) -> float:
        """Suma de todos los cargos (DEBE)."""
        return round(sum(m.cargo for m in self.movimientos), 2)

    def total_abonos(self) -> float:
        """Suma de todos los abonos (HABER)."""
        return round(sum(m.abono for m in self.movimientos), 2)

    def diferencia(self) -> float:
        """Diferencia cargos - abonos (0 => el asiento cuadra)."""
        return round(self.total_cargos() - self.total_abonos(), 2)

    def esta_cuadrado(self) -> bool:
        """True si cumple la partida doble (cargos == abonos y hay movimientos)."""
        return bool(self.movimientos) and self.diferencia() == 0.0

    # ---- subrutinas de edición ----
    def agregar(self, movimiento: Movimiento) -> None:
        """Valida y agrega un movimiento al asiento."""
        movimiento.validar()
        self.movimientos.append(movimiento)

    def limpiar(self) -> None:
        """Elimina todos los movimientos (para empezar un ejercicio nuevo)."""
        self.movimientos.clear()
