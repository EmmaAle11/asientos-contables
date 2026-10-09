"""
DOMINIO :: Puertos
==================
Contratos que la aplicacion necesita del exterior.

Nota de diseno: el catalogo del SAT NO es un puerto. Los codigos agrupadores son
conocimiento del negocio contable (Anexo 24 de la RMF), no un detalle tecnico
intercambiable, asi que vive dentro del dominio (catalogo_sat.py).

Excel y el origen de los ejercicios si son detalles: podrian ser CSV, PDF o una
base de datos sin que cambie ni una regla contable. Por eso son puertos.
"""

from abc import ABC, abstractmethod

from .modelo import Asiento


class ExportadorDeAsientos(ABC):
    """Puerto de salida: a donde se vuelcan los ejercicios."""

    @abstractmethod
    def exportar(self, asientos: list[Asiento], destino: str) -> str:
        """Escribe los asientos en `destino` y devuelve la ruta final."""


class RepositorioEjercicios(ABC):
    """Puerto de salida: de donde salen los ejercicios iniciales."""

    @abstractmethod
    def cargar(self) -> list[Asiento]:
        """Devuelve los ejercicios disponibles al arrancar."""
