"""
APLICACION :: Casos de uso
==========================
Lo que el usuario puede HACER con los asientos, sin saber que hay una ventana
Tkinter delante ni un archivo Excel detras.

`LibroDeEjercicios` es el caso de uso central: mantiene la coleccion de
ejercicios y el que esta seleccionado. La UI le pide acciones y le consulta
estado, pero no manipula las listas por su cuenta.
"""

from ..dominio.errores import ErrorContable
from ..dominio.modelo import Asiento, Movimiento
from ..dominio.puertos import ExportadorDeAsientos, RepositorioEjercicios


class LibroDeEjercicios:
    """
    Coordina la coleccion de ejercicios contables.

    Recibe el repositorio y el exportador por constructor: cambiar Excel por CSV
    o los seeds por una base de datos no obliga a tocar esta clase.
    """

    def __init__(self, repositorio: RepositorioEjercicios, exportador: ExportadorDeAsientos):
        self._repositorio = repositorio
        self._exportador = exportador
        self.ejercicios: list[Asiento] = repositorio.cargar()
        self.indice_actual: int = 0

    # ---- consultas ----
    @property
    def actual(self) -> Asiento:
        return self.ejercicios[self.indice_actual]

    def nombres(self) -> list[str]:
        """Etiquetas numeradas para el selector de la interfaz."""
        return [f"{i + 1}. {a.nombre}" for i, a in enumerate(self.ejercicios)]

    # ---- acciones ----
    def seleccionar(self, indice: int) -> None:
        if 0 <= indice < len(self.ejercicios):
            self.indice_actual = indice

    def crear_ejercicio(self) -> None:
        """Agrega un ejercicio en blanco y lo deja seleccionado."""
        self.ejercicios.append(Asiento(f"Ejercicio nuevo {len(self.ejercicios) + 1}"))
        self.indice_actual = len(self.ejercicios) - 1

    def recargar_ejemplos(self) -> None:
        """Descarta todo y vuelve a los ejercicios del repositorio."""
        self.ejercicios = self._repositorio.cargar()
        self.indice_actual = 0

    def agregar_movimiento(self, movimiento: Movimiento) -> None:
        """
        Agrega un movimiento al ejercicio actual.

        La validacion la hace el dominio (Asiento.agregar); aqui solo se
        propaga el ErrorContable para que el adaptador decida como mostrarlo.
        """
        self.actual.agregar(movimiento)

    def eliminar_movimiento(self, indice: int) -> None:
        if not 0 <= indice < len(self.actual.movimientos):
            raise ErrorContable("No existe ese movimiento en el asiento.")
        del self.actual.movimientos[indice]

    def exportar(self, destino: str) -> str:
        """Vuelca TODOS los ejercicios al destino indicado."""
        return self._exportador.exportar(self.ejercicios, destino)
