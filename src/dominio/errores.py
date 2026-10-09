"""
DOMINIO :: Errores
==================
Fallos contables expresados en lenguaje del negocio.

Antes todo se lanzaba como ValueError generico; distinguirlos permite que cada
adaptador reaccione distinto (la UI muestra un dialogo, una API devolveria 400).
Todos heredan de ValueError para no romper el codigo que ya los capturaba asi.
"""


class ErrorContable(ValueError):
    """Raiz de los errores del dominio contable."""


class CuentaInexistente(ErrorContable):
    """El codigo agrupador no esta en el catalogo del SAT."""


class MovimientoInvalido(ErrorContable):
    """El movimiento viola las reglas de la partida doble."""


class AsientoDescuadrado(ErrorContable):
    """Los cargos no igualan a los abonos."""
