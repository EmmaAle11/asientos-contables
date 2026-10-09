"""
INFRAESTRUCTURA :: Adaptador de entrada (Tkinter)
=================================================
Interfaz gráfica (UI/UX) del generador de asientos contables, hecha con
Tkinter (incluido en Python, no requiere instalar nada).

Permite:
  - Ver y navegar entre ejercicios (los de ejemplo/seed y los nuevos).
  - Crear ejercicios NUEVOS en blanco.
  - Agregar movimientos con: Fecha, Cuenta SAT, Cargo, Abono y Descripción.
  - Ver en vivo el total de cargos, abonos y si el asiento CUADRA.
  - Exportar todos los ejercicios a un archivo .xlsx (una hoja por ejercicio).

Es un ADAPTADOR: traduce clics y teclas a llamadas de casos de uso. No contiene
ni una regla contable — no suma, no valida partida doble, no decide si un asiento
cuadra. Todo eso lo pregunta al dominio a través de LibroDeEjercicios.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from ..aplicacion.casos_uso import LibroDeEjercicios
from ..dominio import catalogo_sat
from ..dominio.errores import ErrorContable
from ..dominio.modelo import Asiento, Movimiento
from .repositorio_seed import FECHA

# Paleta de colores para una UI limpia.
COLOR_FONDO = "#F4F6FB"
COLOR_AZUL = "#1F4E78"
COLOR_VERDE = "#1E7E34"
COLOR_ROJO = "#C00000"


class AppAsientos(tk.Tk):
    """Ventana principal de la aplicación."""

    def __init__(self, libro: LibroDeEjercicios):
        super().__init__()
        # El caso de uso llega ya construido desde main.py (inyeccion de
        # dependencias): la ventana no decide de donde salen los ejercicios.
        self.libro = libro
        self.title("Generador de Asientos Contables — Cuentas SAT")
        self.geometry("980x680")
        self.configure(bg=COLOR_FONDO)

        self._configurar_estilos()
        self._construir_encabezado()
        self._construir_barra_ejercicios()
        self._construir_tabla()
        self._construir_totales()
        self._construir_formulario()
        self._construir_barra_inferior()

        self._refrescar_todo()

    # ------------------------------------------------------------------ #
    #  Construcción de la interfaz (subrutinas de armado)                 #
    # ------------------------------------------------------------------ #
    def _configurar_estilos(self):
        """Estilos ttk para dar una apariencia moderna."""
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=26, font=("Helvetica", 10))
        estilo.configure("Treeview.Heading", font=("Helvetica", 10, "bold"),
                         background=COLOR_AZUL, foreground="white")
        estilo.configure("TButton", font=("Helvetica", 10), padding=6)
        estilo.configure("Azul.TButton", foreground="white", background=COLOR_AZUL)
        estilo.map("Azul.TButton", background=[("active", "#2E6DA4")])

    def _construir_encabezado(self):
        """Barra de título superior."""
        cabecera = tk.Frame(self, bg=COLOR_AZUL, height=64)
        cabecera.pack(fill="x")
        tk.Label(cabecera, text="📒  Asientos Contables",
                 bg=COLOR_AZUL, fg="white",
                 font=("Helvetica", 20, "bold")).pack(side="left", padx=20, pady=12)
        tk.Label(cabecera, text="Cuentas con código agrupador del SAT",
                 bg=COLOR_AZUL, fg="#CFE0F5",
                 font=("Helvetica", 11)).pack(side="left", pady=18)

    def _construir_barra_ejercicios(self):
        """Selector de ejercicio + botones para crear y cargar ejemplos."""
        barra = tk.Frame(self, bg=COLOR_FONDO)
        barra.pack(fill="x", padx=20, pady=(14, 4))

        tk.Label(barra, text="Ejercicio:", bg=COLOR_FONDO,
                 font=("Helvetica", 11, "bold")).pack(side="left")

        self.combo_ejercicios = ttk.Combobox(barra, state="readonly", width=48)
        self.combo_ejercicios.pack(side="left", padx=8)
        self.combo_ejercicios.bind("<<ComboboxSelected>>", self._cambiar_ejercicio)

        ttk.Button(barra, text="➕ Nuevo ejercicio",
                   command=self._nuevo_ejercicio).pack(side="left", padx=4)
        ttk.Button(barra, text="📚 Recargar ejemplos (seed)",
                   command=self._recargar_seeds).pack(side="left", padx=4)

    def _construir_tabla(self):
        """Tabla (Treeview) con los movimientos del ejercicio actual."""
        marco = tk.Frame(self, bg=COLOR_FONDO)
        marco.pack(fill="both", expand=True, padx=20, pady=6)

        columnas = ("fecha", "cuenta", "nombre", "cargo", "abono", "descripcion")
        self.tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=10)
        encabezados = {
            "fecha": ("Fecha", 90),
            "cuenta": ("Cuenta SAT", 90),
            "nombre": ("Nombre de la cuenta", 230),
            "cargo": ("Cargo", 110),
            "abono": ("Abono", 110),
            "descripcion": ("Descripción", 250),
        }
        for col, (titulo, ancho) in encabezados.items():
            self.tabla.heading(col, text=titulo)
            anchor = "e" if col in ("cargo", "abono") else "w"
            self.tabla.column(col, width=ancho, anchor=anchor)

        scroll = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Botón para borrar el movimiento seleccionado.
        ttk.Button(self, text="🗑  Eliminar movimiento seleccionado",
                   command=self._eliminar_movimiento).pack(anchor="e", padx=20)

    def _construir_totales(self):
        """Etiquetas con totales y estado de cuadre."""
        marco = tk.Frame(self, bg=COLOR_FONDO)
        marco.pack(fill="x", padx=20, pady=(8, 2))

        self.lbl_cargos = tk.Label(marco, text="Cargos: 0.00", bg=COLOR_FONDO,
                                   font=("Helvetica", 11, "bold"))
        self.lbl_cargos.pack(side="left", padx=(0, 20))
        self.lbl_abonos = tk.Label(marco, text="Abonos: 0.00", bg=COLOR_FONDO,
                                   font=("Helvetica", 11, "bold"))
        self.lbl_abonos.pack(side="left", padx=(0, 20))
        self.lbl_estado = tk.Label(marco, text="", bg=COLOR_FONDO,
                                   font=("Helvetica", 11, "bold"))
        self.lbl_estado.pack(side="left")

    def _construir_formulario(self):
        """Formulario para capturar un nuevo movimiento."""
        marco = tk.LabelFrame(self, text="  Agregar movimiento  ",
                              bg=COLOR_FONDO, font=("Helvetica", 11, "bold"),
                              fg=COLOR_AZUL, padx=12, pady=10)
        marco.pack(fill="x", padx=20, pady=8)

        # Fila 1: Fecha y Cuenta
        tk.Label(marco, text="Fecha (AAAA-MM-DD):", bg=COLOR_FONDO).grid(row=0, column=0, sticky="w")
        self.ent_fecha = tk.Entry(marco, width=16)
        self.ent_fecha.insert(0, FECHA)
        self.ent_fecha.grid(row=0, column=1, padx=6, pady=4, sticky="w")

        tk.Label(marco, text="Cuenta SAT:", bg=COLOR_FONDO).grid(row=0, column=2, sticky="w")
        self.combo_cuenta = ttk.Combobox(marco, state="readonly", width=42,
                                         values=catalogo_sat.lista_etiquetas())
        self.combo_cuenta.grid(row=0, column=3, padx=6, pady=4, sticky="w")
        self.combo_cuenta.current(0)

        # Fila 2: Cargo, Abono, Descripción
        tk.Label(marco, text="Cargo:", bg=COLOR_FONDO).grid(row=1, column=0, sticky="w")
        self.ent_cargo = tk.Entry(marco, width=16)
        self.ent_cargo.grid(row=1, column=1, padx=6, pady=4, sticky="w")

        tk.Label(marco, text="Abono:", bg=COLOR_FONDO).grid(row=1, column=2, sticky="w")
        self.ent_abono = tk.Entry(marco, width=16)
        self.ent_abono.grid(row=1, column=3, padx=6, pady=4, sticky="w")

        tk.Label(marco, text="Descripción:", bg=COLOR_FONDO).grid(row=2, column=0, sticky="w")
        self.ent_desc = tk.Entry(marco, width=70)
        self.ent_desc.grid(row=2, column=1, columnspan=3, padx=6, pady=4, sticky="w")

        ttk.Button(marco, text="➕ Agregar al asiento", style="Azul.TButton",
                   command=self._agregar_movimiento).grid(row=0, column=4, rowspan=2, padx=12)

    def _construir_barra_inferior(self):
        """Botón de exportación a Excel."""
        barra = tk.Frame(self, bg=COLOR_FONDO)
        barra.pack(fill="x", padx=20, pady=(4, 16))
        ttk.Button(barra, text="📤 Exportar TODO a Excel (.xlsx)",
                   style="Azul.TButton",
                   command=self._exportar_excel).pack(side="right")

    # ------------------------------------------------------------------ #
    #  Lógica de la interfaz (manejo de eventos)                         #
    # ------------------------------------------------------------------ #
    @property
    def ejercicio_actual(self) -> Asiento:
        """El Asiento actualmente seleccionado (lo decide el caso de uso)."""
        return self.libro.actual

    def _refrescar_todo(self):
        """Vuelve a pintar el selector, la tabla y los totales."""
        self._refrescar_combo()
        self._refrescar_tabla()
        self._refrescar_totales()

    def _refrescar_combo(self):
        nombres = self.libro.nombres()
        self.combo_ejercicios["values"] = nombres
        if nombres:
            self.combo_ejercicios.current(self.libro.indice_actual)

    def _refrescar_tabla(self):
        """Llena la tabla con los movimientos del ejercicio actual."""
        self.tabla.delete(*self.tabla.get_children())
        for m in self.ejercicio_actual.movimientos:
            self.tabla.insert("", "end", values=(
                m.fecha, m.codigo, m.nombre_cuenta,
                f"{m.cargo:,.2f}" if m.cargo else "",
                f"{m.abono:,.2f}" if m.abono else "",
                m.descripcion,
            ))

    def _refrescar_totales(self):
        """Actualiza las etiquetas de totales y el indicador de cuadre."""
        a = self.ejercicio_actual
        self.lbl_cargos.config(text=f"Cargos: {a.total_cargos():,.2f}")
        self.lbl_abonos.config(text=f"Abonos: {a.total_abonos():,.2f}")
        if a.esta_cuadrado():
            self.lbl_estado.config(text="✔ El asiento CUADRA", fg=COLOR_VERDE)
        else:
            self.lbl_estado.config(
                text=f"⚠ Descuadre: {a.diferencia():+,.2f}", fg=COLOR_ROJO)

    # ---- eventos ----
    def _cambiar_ejercicio(self, _evento=None):
        self.libro.seleccionar(self.combo_ejercicios.current())
        self._refrescar_tabla()
        self._refrescar_totales()

    def _nuevo_ejercicio(self):
        """Crea un ejercicio en blanco y lo selecciona."""
        self.libro.crear_ejercicio()
        self._refrescar_todo()

    def _recargar_seeds(self):
        """Restaura los ejercicios de ejemplo (con confirmación)."""
        if messagebox.askyesno("Recargar ejemplos",
                               "Esto reemplazará TODOS los ejercicios por los de "
                               "ejemplo. ¿Continuar?"):
            self.libro.recargar_ejemplos()
            self._refrescar_todo()

    def _leer_importe(self, entrada: tk.Entry) -> float:
        """Convierte el texto de una caja a número (vacío = 0)."""
        texto = entrada.get().strip().replace(",", "")
        return float(texto) if texto else 0.0

    def _agregar_movimiento(self):
        """Valida el formulario y agrega el movimiento al asiento actual."""
        try:
            codigo = catalogo_sat.codigo_desde_etiqueta(self.combo_cuenta.get())
            movimiento = Movimiento(
                fecha=self.ent_fecha.get().strip(),
                codigo=codigo,
                cargo=self._leer_importe(self.ent_cargo),
                abono=self._leer_importe(self.ent_abono),
                descripcion=self.ent_desc.get().strip(),
            )
            self.libro.agregar_movimiento(movimiento)  # el dominio valida
        except (ErrorContable, ValueError) as e:
            messagebox.showerror("Dato inválido", str(e))
            return

        # limpiar cajas de importe/descripción y refrescar
        self.ent_cargo.delete(0, "end")
        self.ent_abono.delete(0, "end")
        self.ent_desc.delete(0, "end")
        self._refrescar_tabla()
        self._refrescar_totales()

    def _eliminar_movimiento(self):
        """Borra el movimiento seleccionado en la tabla."""
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Eliminar", "Selecciona un movimiento en la tabla.")
            return
        self.libro.eliminar_movimiento(self.tabla.index(seleccion[0]))
        self._refrescar_tabla()
        self._refrescar_totales()

    def _exportar_excel(self):
        """Abre un diálogo y exporta todos los ejercicios a un .xlsx."""
        from tkinter import filedialog

        ruta = filedialog.asksaveasfilename(
            title="Guardar asientos como…",
            defaultextension=".xlsx",
            initialfile="asientos_contables.xlsx",
            filetypes=[("Libro de Excel", "*.xlsx")],
        )
        if not ruta:
            return
        try:
            destino = self.libro.exportar(ruta)
            messagebox.showinfo("Exportación exitosa",
                                f"Se guardó el archivo:\n{destino}")
        except Exception as e:  # noqa: BLE001  (mostrar cualquier error al usuario)
            messagebox.showerror("Error al exportar", str(e))


def iniciar(libro: LibroDeEjercicios):
    """Arranca la ventana con el caso de uso ya cableado."""
    AppAsientos(libro).mainloop()
