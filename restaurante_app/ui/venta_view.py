"""Formulario de ventas e historial visual."""

import tkinter as tk
from tkinter import ttk


class VentaView(ttk.Frame):
    """Permite elegir usuario y producto y consultar las ventas."""

    def __init__(self, master, venta_servicio, restaurante_servicio, al_registrar_venta):
        super().__init__(master, padding=12)
        self._venta_servicio = venta_servicio
        self._restaurante_servicio = restaurante_servicio
        self._al_registrar_venta = al_registrar_venta
        self._usuarios_por_opcion = {}
        self._productos_por_opcion = {}
        self._construir_widgets()
        self.actualizar()

    def _construir_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        formulario = ttk.LabelFrame(self, text="Registrar una venta", padding=14)
        formulario.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        formulario.columnconfigure(1, weight=1)
        formulario.columnconfigure(3, weight=1)

        ttk.Label(formulario, text="Usuario").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=5)
        self._usuario_var = tk.StringVar()
        self._combo_usuarios = ttk.Combobox(
            formulario, textvariable=self._usuario_var, state="readonly", width=31
        )
        self._combo_usuarios.grid(row=0, column=1, sticky="ew", padx=(0, 18), pady=5)

        ttk.Label(formulario, text="Producto disponible").grid(
            row=0, column=2, sticky="w", padx=(0, 8), pady=5
        )
        self._producto_var = tk.StringVar()
        self._combo_productos = ttk.Combobox(
            formulario, textvariable=self._producto_var, state="readonly", width=37
        )
        self._combo_productos.grid(row=0, column=3, sticky="ew", pady=5)
        self._combo_productos.bind(
            "<<ComboboxSelected>>", lambda _evento: self._actualizar_total_estimado()
        )

        ttk.Label(formulario, text="Cantidad").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=5)
        self._cantidad_var = tk.StringVar(value="1")
        self._entrada_cantidad = ttk.Entry(formulario, textvariable=self._cantidad_var, width=12)
        self._entrada_cantidad.grid(row=1, column=1, sticky="w", pady=5)
        self._entrada_cantidad.bind(
            "<KeyRelease>", lambda _evento: self._actualizar_total_estimado()
        )
        self._total_estimado = ttk.Label(formulario, text="Total estimado: $0.00")
        self._total_estimado.grid(row=1, column=2, columnspan=2, sticky="e", pady=5)

        acciones = ttk.Frame(formulario)
        acciones.grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 2))
        ttk.Button(
            acciones,
            text="Registrar venta",
            style="Accent.TButton",
            command=self._registrar_venta,
        ).pack(side="left")
        ttk.Label(acciones, text="El stock se valida antes de guardar.").pack(
            side="left", padx=12
        )

        historial = ttk.LabelFrame(self, text="Historial de ventas", padding=8)
        historial.grid(row=1, column=0, sticky="nsew")
        historial.columnconfigure(0, weight=1)
        historial.rowconfigure(0, weight=1)
        columnas = ("codigo", "fecha", "usuario", "producto", "cantidad", "unitario", "total")
        self._tabla_ventas = ttk.Treeview(
            historial, columns=columnas, show="headings", selectmode="browse"
        )
        encabezados = {
            "codigo": ("N.º venta", 90),
            "fecha": ("Fecha y hora", 150),
            "usuario": ("Usuario", 170),
            "producto": ("Producto", 230),
            "cantidad": ("Cantidad", 80),
            "unitario": ("Precio unitario", 110),
            "total": ("Total", 100),
        }
        for clave, (titulo, ancho) in encabezados.items():
            self._tabla_ventas.heading(clave, text=titulo)
            self._tabla_ventas.column(clave, anchor="center", width=ancho)
        barra_vertical = ttk.Scrollbar(
            historial, orient="vertical", command=self._tabla_ventas.yview
        )
        barra_horizontal = ttk.Scrollbar(
            historial, orient="horizontal", command=self._tabla_ventas.xview
        )
        self._tabla_ventas.configure(
            yscrollcommand=barra_vertical.set, xscrollcommand=barra_horizontal.set
        )
        self._tabla_ventas.grid(row=0, column=0, sticky="nsew")
        barra_vertical.grid(row=0, column=1, sticky="ns")
        barra_horizontal.grid(row=1, column=0, sticky="ew")

        self._estado = ttk.Label(self, text="Selecciona un usuario y un producto.")
        self._estado.grid(row=2, column=0, sticky="w", pady=(8, 0))

    def actualizar(self, usuario_autenticado=None):
        usuario_anterior = self._usuarios_por_opcion.get(self._usuario_var.get())
        producto_anterior = self._productos_por_opcion.get(self._producto_var.get())
        self._usuarios_por_opcion = {}
        opciones_usuarios = []
        for usuario in self._restaurante_servicio.listar_usuarios():
            opcion = f"{usuario.nombre} · {usuario.usuario} (ID {usuario.identificacion})"
            opciones_usuarios.append(opcion)
            self._usuarios_por_opcion[opcion] = usuario.identificacion
        self._combo_usuarios["values"] = opciones_usuarios
        if usuario_autenticado is not None:
            usuario_anterior = usuario_autenticado.identificacion
        opcion_usuario = next(
            (op for op, uid in self._usuarios_por_opcion.items() if uid == usuario_anterior),
            opciones_usuarios[0] if opciones_usuarios else "",
        )
        self._usuario_var.set(opcion_usuario)

        self._productos_por_opcion = {}
        opciones_productos = []
        for producto in self._restaurante_servicio.listar_productos():
            if producto.stock <= 0:
                continue
            opcion = f"{producto.codigo} · {producto.nombre} (stock: {producto.stock})"
            opciones_productos.append(opcion)
            self._productos_por_opcion[opcion] = producto.codigo
        self._combo_productos["values"] = opciones_productos
        opcion_producto = next(
            (op for op, codigo in self._productos_por_opcion.items() if codigo == producto_anterior),
            opciones_productos[0] if opciones_productos else "",
        )
        self._producto_var.set(opcion_producto)
        self._refrescar_tabla_ventas()
        self._actualizar_total_estimado()

    def _actualizar_total_estimado(self):
        codigo = self._productos_por_opcion.get(self._producto_var.get())
        producto = self._restaurante_servicio.buscar_producto(codigo) if codigo else None
        try:
            cantidad = int(self._cantidad_var.get())
            if cantidad <= 0:
                raise ValueError
        except (TypeError, ValueError):
            cantidad = 0
        total = producto.precio * cantidad if producto is not None else 0
        self._total_estimado.config(text=f"Total estimado: $ {total:.2f}")

    def _registrar_venta(self):
        identificacion = self._usuarios_por_opcion.get(self._usuario_var.get())
        codigo_producto = self._productos_por_opcion.get(self._producto_var.get())
        if identificacion is None:
            self._mostrar_estado("Selecciona un usuario registrado.", error=True)
            return
        if codigo_producto is None:
            self._mostrar_estado("Selecciona un producto con existencias.", error=True)
            return
        try:
            venta, producto = self._venta_servicio.registrar_venta(
                identificacion, codigo_producto, self._cantidad_var.get()
            )
        except (ValueError, OSError) as error:
            self._mostrar_estado(str(error), error=True)
            return
        self._cantidad_var.set("1")
        self.actualizar()
        self._al_registrar_venta(venta, producto)
        self._mostrar_estado(f"Venta {venta.codigo_venta} registrada por $ {venta.total:.2f}.")

    def _refrescar_tabla_ventas(self):
        self._tabla_ventas.delete(*self._tabla_ventas.get_children())
        for indice, venta in enumerate(self._venta_servicio.listar_ventas()):
            self._tabla_ventas.insert(
                "",
                tk.END,
                iid=f"venta-{indice}",
                values=(
                    venta.codigo_venta,
                    venta.fecha,
                    venta.nombre_usuario,
                    f"{venta.codigo_producto} · {venta.nombre_producto}",
                    venta.cantidad,
                    f"$ {venta.precio_unitario:.2f}",
                    f"$ {venta.total:.2f}",
                ),
            )
        filas = self._tabla_ventas.get_children()
        if filas:
            self._tabla_ventas.see(filas[-1])

    def _mostrar_estado(self, mensaje, error=False):
        self._estado.config(
            text=mensaje,
            foreground="#a12622" if error else "#25643b",
        )

