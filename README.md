# 📒 Generador de Asientos Contables (Cuentas SAT)

Aplicación de escritorio en **Python** con interfaz gráfica (UI/UX) para
crear, registrar y exportar **asientos contables** usando el **código
agrupador de cuentas del SAT**.

---

## ✨ Qué hace

- Interfaz visual (Tkinter) para capturar asientos con:
  **Fecha · Cuenta SAT · Cargo · Abono · Descripción**.
- Trae **5 ejercicios de ejemplo (seed)** ya resueltos y cuadrados.
- Permite crear **ejercicios nuevos** en blanco.
- Muestra en vivo el total de **cargos**, **abonos** y si el asiento
  **cuadra** (partida doble).
- **Exporta todo a Excel (.xlsx)** desde la misma interfaz: una hoja de
  cálculo por ejercicio + una hoja **Resumen**.

---

## 🗂️ Estructura del proyecto (DDD + Hexagonal)

```
asientos-contables/
├── main.py                     COMPOSITION ROOT: cablea todo
├── certs/                      Certificado SSL de este proyecto
└── src/
    ├── dominio/                Reglas contables. No importa tkinter ni openpyxl.
    │   ├── modelo.py           Movimiento · Asiento (partida doble)
    │   ├── catalogo_sat.py     Cuentas del código agrupador del SAT
    │   ├── puertos.py          ExportadorDeAsientos · RepositorioEjercicios
    │   └── errores.py          CuentaInexistente · MovimientoInvalido…
    ├── aplicacion/
    │   └── casos_uso.py        LibroDeEjercicios (crear, agregar, exportar)
    └── infraestructura/        Adaptadores (lo intercambiable)
        ├── ui_tkinter.py       La ventana; no contiene ni una regla contable
        ├── exportador_excel.py Único archivo que importa openpyxl
        └── repositorio_seed.py Los 5 ejercicios de ejemplo
```

### Por qué el catálogo del SAT está en el dominio y Excel no

Los códigos agrupadores del SAT son **conocimiento del negocio contable** (Anexo
24 de la RMF): no son un detalle técnico que uno cambie por otro. Por eso viven
dentro del dominio.

Excel sí es un detalle: mañana podría ser CSV, PDF o una base de datos sin que
cambie una sola regla de partida doble. Por eso es un **puerto** con su adaptador.

### La ventana no sabe de contabilidad

`ui_tkinter.py` no suma, no valida y no decide si un asiento cuadra. Traduce
clics a llamadas de caso de uso y pinta lo que el dominio le responde:

```python
self.libro.agregar_movimiento(movimiento)   # el dominio valida y lanza si algo falla
```

Cada módulo está **documentado** (docstrings) y dividido en **subrutinas**
pequeñas con una sola responsabilidad.

---

## ▶️ Cómo ejecutarlo

**1. Instalar la dependencia (solo la primera vez):**

```bash
pip3 install -r requirements.txt
```

*(Tkinter ya viene incluido con Python, no hay que instalarlo.)*

**2. Ejecutar la aplicación:**

```bash
cd asientos-contables
python3 main.py
```

Se abrirá la ventana de la aplicación.

---

## 🖱️ Cómo se usa

1. Al abrir, verás el **Ejercicio 1** (los ejemplos ya cargados). Cambia
   entre ejercicios con el menú **"Ejercicio:"** de arriba.
2. Para uno nuevo: botón **➕ Nuevo ejercicio** (queda en blanco).
3. Para agregar un renglón, en **"Agregar movimiento"**:
   - Escribe la **Fecha** (AAAA-MM-DD).
   - Elige la **Cuenta SAT** del menú (muestra `código - nombre`).
   - Escribe el importe en **Cargo** *o* en **Abono** (no en ambos).
   - Escribe la **Descripción**.
   - Pulsa **➕ Agregar al asiento**.
4. Abajo verás si el asiento **✔ CUADRA** o el **⚠ Descuadre**.
5. Para guardar: **📤 Exportar TODO a Excel (.xlsx)** → elige dónde guardar.

---

## 🧾 Sobre las cuentas del SAT

Las cuentas usan el **código agrupador del Anexo 24** del SAT
(Contabilidad Electrónica). Ejemplos incluidos:

| Código   | Cuenta                              | Naturaleza |
|----------|-------------------------------------|------------|
| 101.01   | Caja                                | Deudora    |
| 102.01   | Bancos nacionales                   | Deudora    |
| 105.01   | Clientes nacionales                 | Deudora    |
| 115.01   | Inventario / Almacén                | Deudora    |
| 118.01   | IVA acreditable pagado              | Deudora    |
| 201.01   | Proveedores nacionales              | Acreedora  |
| 213.01   | IVA trasladado cobrado (por pagar)  | Acreedora  |
| 301.01   | Capital social                      | Acreedora  |
| 401.01   | Ventas y/o servicios (tasa general) | Acreedora  |
| 601.06   | Renta / Arrendamiento               | Deudora    |

*(El catálogo completo está en `src/dominio/catalogo_sat.py`.)*

---

## 💡 Recordatorio de partida doble

Todo asiento debe cumplir: **suma de cargos = suma de abonos**.
La aplicación lo verifica automáticamente y no te deja capturar un
movimiento con cargo y abono al mismo tiempo, ni con importes negativos.
