"""
COMPOSITION ROOT :: Asientos Contables
======================================
Único punto donde se decide qué implementación concreta usa cada puerto.

Aquí se arma el hexágono: se crean los adaptadores (seeds, Excel), se inyectan
en el caso de uso, y este en la interfaz. Ningún otro archivo conoce a la vez el
dominio y la infraestructura.

Ejecuta:
    python3 main.py

Requisitos:
    - Python 3.10+  (usa tkinter, incluido en Python)
    - openpyxl      ->  pip install -r requirements.txt
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.aplicacion.casos_uso import LibroDeEjercicios
from src.infraestructura.exportador_excel import ExportadorExcel
from src.infraestructura.repositorio_seed import RepositorioSeed
from src.infraestructura.ui_tkinter import iniciar


def construir_libro() -> LibroDeEjercicios:
    """Cablea las dependencias. Aislado para poder reusarlo en pruebas."""
    return LibroDeEjercicios(
        repositorio=RepositorioSeed(),
        exportador=ExportadorExcel(),
    )


if __name__ == "__main__":
    iniciar(construir_libro())
