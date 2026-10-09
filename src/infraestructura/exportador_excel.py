"""
exportar_excel.py
=================
Exportación de asientos contables a un archivo .xlsx (Excel).

Cada ejercicio (Asiento) se escribe en su PROPIA hoja de cálculo, con las
columnas solicitadas: Fecha | Cuenta SAT | Nombre de la cuenta | Cargo |
Abono | Descripción, más una fila de TOTALES.

Se agrega además una hoja "Resumen" con el estado (cuadrado o no) de cada
ejercicio.

Usa la librería openpyxl.  Instalar con:  pip install openpyxl
"""

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from ..dominio.modelo import Asiento
from ..dominio.puertos import ExportadorDeAsientos

# --- estilos reutilizables ---
_AZUL = "1F4E78"
_GRIS = "D9E1F2"
_ENCABEZADO = Font(bold=True, color="FFFFFF", size=11)
_TITULO = Font(bold=True, color=_AZUL, size=13)
_RELLENO_ENC = PatternFill("solid", fgColor=_AZUL)
_RELLENO_TOT = PatternFill("solid", fgColor=_GRIS)
_NEGRITA = Font(bold=True)
_DINERO = "#,##0.00"
_BORDE = Border(*(Side(style="thin", color="BFBFBF"),) * 4)

_COLUMNAS = ["Fecha", "Cuenta SAT", "Nombre de la cuenta", "Cargo", "Abono", "Descripción"]


def _nombre_hoja_valido(nombre: str, usados: set[str]) -> str:
    """
    Excel limita los nombres de hoja a 31 caracteres y prohíbe : \\ / ? * [ ].
    Además no pueden repetirse. Esta subrutina genera uno válido y único.
    """
    prohibidos = ':\\/?*[]'
    limpio = "".join("-" if c in prohibidos else c for c in nombre)[:31].strip()
    if not limpio:
        limpio = "Hoja"
    base, i = limpio, 1
    while limpio in usados:
        sufijo = f" ({i})"
        limpio = base[:31 - len(sufijo)] + sufijo
        i += 1
    usados.add(limpio)
    return limpio


def _escribir_hoja(wb: Workbook, asiento: Asiento, usados: set[str]) -> None:
    """Crea y llena una hoja con un asiento contable."""
    ws = wb.create_sheet(_nombre_hoja_valido(asiento.nombre, usados))

    # Título del ejercicio (fila 1)
    ws.merge_cells("A1:F1")
    celda_titulo = ws["A1"]
    celda_titulo.value = asiento.nombre
    celda_titulo.font = _TITULO
    celda_titulo.alignment = Alignment(horizontal="left")

    # Encabezados (fila 3)
    fila_enc = 3
    for col, texto in enumerate(_COLUMNAS, start=1):
        c = ws.cell(row=fila_enc, column=col, value=texto)
        c.font = _ENCABEZADO
        c.fill = _RELLENO_ENC
        c.alignment = Alignment(horizontal="center")
        c.border = _BORDE

    # Movimientos
    fila = fila_enc + 1
    for m in asiento.movimientos:
        valores = [m.fecha, m.codigo, m.nombre_cuenta, m.cargo, m.abono, m.descripcion]
        for col, val in enumerate(valores, start=1):
            c = ws.cell(row=fila, column=col, value=val)
            c.border = _BORDE
            if col in (4, 5):  # cargo / abono con formato de dinero
                c.number_format = _DINERO
        fila += 1

    # Fila de totales
    ws.cell(row=fila, column=3, value="TOTALES").font = _NEGRITA
    tc = ws.cell(row=fila, column=4, value=asiento.total_cargos())
    ta = ws.cell(row=fila, column=5, value=asiento.total_abonos())
    for c in (tc, ta):
        c.font = _NEGRITA
        c.number_format = _DINERO
    for col in range(1, 7):
        ws.cell(row=fila, column=col).fill = _RELLENO_TOT
        ws.cell(row=fila, column=col).border = _BORDE

    # Estado (cuadra / no cuadra)
    estado = "CUADRADO ✔" if asiento.esta_cuadrado() else f"DESCUADRE: {asiento.diferencia():+,.2f}"
    ws.cell(row=fila + 1, column=3, value=estado).font = Font(
        bold=True, color="1E7E34" if asiento.esta_cuadrado() else "C00000")

    _ajustar_columnas(ws)


def _ajustar_columnas(ws) -> None:
    """Ajusta el ancho de las columnas al contenido más largo."""
    anchos = [12, 12, 34, 14, 14, 40]
    for i, ancho in enumerate(anchos, start=1):
        ws.column_dimensions[get_column_letter(i)].width = ancho


def _escribir_resumen(wb: Workbook, asientos: list[Asiento]) -> None:
    """Hoja inicial con el estado de todos los ejercicios."""
    ws = wb.create_sheet("Resumen", 0)  # 0 => la pone primera
    ws["A1"] = "Resumen de ejercicios contables"
    ws["A1"].font = _TITULO

    encabezados = ["#", "Ejercicio", "Total cargos", "Total abonos", "Estado"]
    for col, texto in enumerate(encabezados, start=1):
        c = ws.cell(row=3, column=col, value=texto)
        c.font = _ENCABEZADO
        c.fill = _RELLENO_ENC
        c.alignment = Alignment(horizontal="center")

    for i, a in enumerate(asientos, start=1):
        fila = 3 + i
        ws.cell(row=fila, column=1, value=i)
        ws.cell(row=fila, column=2, value=a.nombre)
        ws.cell(row=fila, column=3, value=a.total_cargos()).number_format = _DINERO
        ws.cell(row=fila, column=4, value=a.total_abonos()).number_format = _DINERO
        ws.cell(row=fila, column=5,
                value="Cuadrado" if a.esta_cuadrado() else "Descuadrado")

    for col, ancho in enumerate([5, 40, 16, 16, 16], start=1):
        ws.column_dimensions[get_column_letter(col)].width = ancho


def exportar(asientos: list[Asiento], ruta: str) -> str:
    """
    Exporta la lista de asientos a un archivo .xlsx.

    Args:
        asientos: lista de ejercicios (Asiento) a guardar.
        ruta    : ruta completa del archivo destino (…/archivo.xlsx).

    Returns:
        La ruta del archivo generado.
    """
    wb = Workbook()
    wb.remove(wb.active)  # quita la hoja vacía por defecto

    usados: set[str] = set()
    for asiento in asientos:
        _escribir_hoja(wb, asiento, usados)

    _escribir_resumen(wb, asientos)

    if not ruta.lower().endswith(".xlsx"):
        ruta += ".xlsx"
    wb.save(ruta)
    return ruta


class ExportadorExcel(ExportadorDeAsientos):
    """
    ADAPTADOR del puerto ExportadorDeAsientos.

    Envuelve la subrutina `exportar` de arriba. openpyxl solo se conoce en este
    archivo: la aplicacion pide "exporta" y no sabe si el resultado es .xlsx,
    .csv o un PDF.
    """

    def exportar(self, asientos: list[Asiento], destino: str) -> str:
        return exportar(asientos, destino)
