"""
cuentas_sat.py
==============
Catálogo de cuentas contables basado en el **Código Agrupador del SAT**
(Anexo 24 de la Resolución Miscelánea Fiscal, "Contabilidad Electrónica").

Cada cuenta tiene:
  - codigo      : número agrupador designado por el SAT (ej. "101.01").
  - nombre      : nombre estándar de la cuenta.
  - naturaleza  : "deudora" o "acreedora" (indica de qué lado aumenta).
  - tipo        : clasificación general (Activo, Pasivo, Capital, Ingreso,
                  Costo, Gasto).

Este módulo NO tiene lógica de interfaz: solo son datos reutilizables.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CuentaSAT:
    """Representa una cuenta del catálogo del SAT (código agrupador)."""
    codigo: str
    nombre: str
    naturaleza: str   # "deudora" | "acreedora"
    tipo: str         # Activo | Pasivo | Capital | Ingreso | Costo | Gasto


# ---------------------------------------------------------------------------
# Catálogo (subconjunto de las cuentas más usadas del Anexo 24 del SAT).
# ---------------------------------------------------------------------------
CATALOGO = [
    # ---- ACTIVO (naturaleza deudora) ----
    CuentaSAT("101.01", "Caja",                          "deudora",   "Activo"),
    CuentaSAT("102.01", "Bancos nacionales",             "deudora",   "Activo"),
    CuentaSAT("103.01", "Inversiones temporales",        "deudora",   "Activo"),
    CuentaSAT("105.01", "Clientes nacionales",           "deudora",   "Activo"),
    CuentaSAT("107.01", "Cuentas por cobrar",            "deudora",   "Activo"),
    CuentaSAT("108.01", "Deudores diversos",             "deudora",   "Activo"),
    CuentaSAT("115.01", "Inventario / Almacén",          "deudora",   "Activo"),
    CuentaSAT("118.01", "IVA acreditable pagado",        "deudora",   "Activo"),
    CuentaSAT("118.02", "IVA acreditable pendiente de pago", "deudora", "Activo"),
    CuentaSAT("120.01", "Anticipo a proveedores",        "deudora",   "Activo"),
    CuentaSAT("151.01", "Terrenos",                      "deudora",   "Activo"),
    CuentaSAT("152.01", "Edificios",                     "deudora",   "Activo"),
    CuentaSAT("155.01", "Mobiliario y equipo de oficina","deudora",   "Activo"),
    CuentaSAT("156.01", "Equipo de transporte",          "deudora",   "Activo"),
    CuentaSAT("157.01", "Equipo de cómputo",             "deudora",   "Activo"),

    # ---- PASIVO (naturaleza acreedora) ----
    CuentaSAT("201.01", "Proveedores nacionales",        "acreedora", "Pasivo"),
    CuentaSAT("205.01", "Documentos por pagar a corto plazo", "acreedora", "Pasivo"),
    CuentaSAT("206.01", "Acreedores diversos",           "acreedora", "Pasivo"),
    CuentaSAT("208.01", "Anticipo de clientes",          "acreedora", "Pasivo"),
    CuentaSAT("213.01", "IVA trasladado cobrado (por pagar)",   "acreedora", "Pasivo"),
    CuentaSAT("213.02", "IVA trasladado no cobrado (pendiente)","acreedora", "Pasivo"),
    CuentaSAT("214.01", "ISR retenido por salarios",     "acreedora", "Pasivo"),
    CuentaSAT("216.01", "Impuestos y derechos por pagar","acreedora", "Pasivo"),

    # ---- CAPITAL (naturaleza acreedora) ----
    CuentaSAT("301.01", "Capital social",                "acreedora", "Capital"),
    CuentaSAT("305.01", "Resultado de ejercicios anteriores", "acreedora", "Capital"),
    CuentaSAT("320.01", "Resultado del ejercicio",       "acreedora", "Capital"),

    # ---- INGRESOS (naturaleza acreedora) ----
    CuentaSAT("401.01", "Ventas y/o servicios gravados a la tasa general", "acreedora", "Ingreso"),
    CuentaSAT("402.01", "Devoluciones y descuentos sobre ventas", "deudora", "Ingreso"),
    CuentaSAT("702.01", "Productos financieros (intereses ganados)", "acreedora", "Ingreso"),

    # ---- COSTOS (naturaleza deudora) ----
    CuentaSAT("501.01", "Costo de venta",                "deudora",   "Costo"),
    CuentaSAT("502.01", "Compras",                       "deudora",   "Costo"),

    # ---- GASTOS (naturaleza deudora) ----
    CuentaSAT("601.01", "Sueldos y salarios",            "deudora",   "Gasto"),
    CuentaSAT("601.06", "Renta / Arrendamiento",         "deudora",   "Gasto"),
    CuentaSAT("601.10", "Luz, agua y teléfono (servicios)", "deudora","Gasto"),
    CuentaSAT("601.53", "Papelería y artículos de oficina", "deudora","Gasto"),
    CuentaSAT("602.01", "Gastos de venta",               "deudora",   "Gasto"),
    CuentaSAT("603.01", "Gastos de administración",      "deudora",   "Gasto"),
    CuentaSAT("701.01", "Gastos financieros (intereses pagados)", "deudora", "Gasto"),
]

# Índice rápido por código, para búsquedas O(1).
_INDICE = {c.codigo: c for c in CATALOGO}


# ---------------------------------------------------------------------------
# Subrutinas de consulta
# ---------------------------------------------------------------------------
def obtener_cuenta(codigo: str) -> CuentaSAT | None:
    """Devuelve la CuentaSAT con ese código, o None si no existe."""
    return _INDICE.get(codigo)


def etiqueta(cuenta: CuentaSAT) -> str:
    """Texto legible para mostrar en menús: '101.01 - Caja'."""
    return f"{cuenta.codigo} - {cuenta.nombre}"


def lista_etiquetas() -> list[str]:
    """Lista de todas las cuentas en formato 'codigo - nombre' (para menús)."""
    return [etiqueta(c) for c in CATALOGO]


def codigo_desde_etiqueta(texto: str) -> str:
    """De 'que 101.01 - Caja' extrae el código '101.01'."""
    return texto.split(" - ", 1)[0].strip()
