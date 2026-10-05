"""Panel de gestión con catálogo CRUD y consulta de usuarios."""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from modelos.usuario import ADMINISTRADOR, CLIENTE, EMPLEADO, ROLES
from ui.venta_view import VentaView


class MainView(tk.Frame):
    """Panel principal que presenta productos y usuarios del restaurante."""

    def __init__(
        self, master, restaurante_servicio, venta_servicio, al_cerrar_sesion
    ) -> None:
        super().__init__(master, padx=22, pady=22)
        self._restaurante_servicio = restaurante_servicio
        self._venta_servicio = venta_servicio
        self._al_cerrar_sesion = al_cerrar_sesion
        self._codigo_original = None
        self._campos = {}
        self._usuario_actual = None
        self._identificacion_usuario_original = None
        self._campos_usuario = {}
        self._rol_usuario_var = tk.StringVar(value=CLIENTE)
        self._logo_image = None
        self._construir_widgets()

    def _construir_widgets(self) -> None:
        encabezado = ttk.Frame(self)
        encabezado.pack(fill="x", pady=(0, 14))

        ruta_logo = Path(__file__).resolve().parent.parent / "assets" / "restaurante_logo.ppm"
        try:
            self._logo_image = tk.PhotoImage(file=str(ruta_logo)).subsample(5, 5)
            ttk.Label(encabezado, image=self._logo_image).pack(side="left", padx=(0, 10))
        except tk.TclError:
            # Muestra el título si el recurso gráfico no puede cargarse.
            ttk.Label(encabezado, text="🍽", font=("Segoe UI Emoji", 20)).pack(side="left", padx=(0, 10))
        ttk.Label(
            encabezado, text="Gestión del restaurante", font=("Segoe UI", 17, "bold")
        ).pack(side="left")

        self._label_bienvenida = ttk.Label(encabezado, text="Bienvenido")
        self._label_bienvenida.pack(side="left", padx=(18, 0))

        ttk.Button(
            encabezado, text="Cerrar sesión", command=self._al_cerrar_sesion
        ).pack(side="right")

        resumen = ttk.Frame(self)
        resumen.pack(fill="x", pady=(0, 14))
        self._label_resumen = ttk.Label(resumen, text="")
        self._label_resumen.pack(side="left")

        self._pestañas = ttk.Notebook(self)
        self._pestañas.pack(fill="both", expand=True)
        self._pestañas.bind("<<NotebookTabChanged>>", self._al_cambiar_pestaña)
        self._construir_pestaña_productos()
        self._construir_pestaña_usuarios()
        self._construir_pestaña_ventas()

    def _construir_pestaña_productos(self) -> None:
        pestaña = ttk.Frame(self._pestañas, padding=12)
        pestaña.columnconfigure(0, weight=1)
        pestaña.rowconfigure(1, weight=1)
        self._pestañas.add(pestaña, text="🍲 Productos")

        formulario = ttk.LabelFrame(pestaña, text="Datos del producto", padding=12)
        formulario.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for columna in range(5):
            formulario.columnconfigure(columna, weight=1)

        etiquetas = (
            ("Código", "codigo"),
            ("Nombre", "nombre"),
            ("Categoría", "categoria"),
            ("Precio", "precio"),
            ("Stock", "stock"),
        )
        anchos = {"codigo": 14, "nombre": 24, "categoria": 19, "precio": 12, "stock": 10}
        for columna, (titulo, clave) in enumerate(etiquetas):
            ttk.Label(formulario, text=titulo).grid(
                row=0, column=columna, sticky="w", padx=5, pady=(0, 4)
            )
            entrada = ttk.Entry(formulario, width=anchos[clave])
            entrada.grid(row=1, column=columna, sticky="ew", padx=5, pady=(0, 10))
            self._campos[clave] = entrada

        acciones = ttk.Frame(formulario)
        acciones.grid(row=2, column=0, columnspan=5, sticky="w", padx=3)
        ttk.Button(acciones, text="Buscar", command=self._buscar_producto).pack(
            side="left", padx=(0, 7)
        )
        ttk.Button(acciones, text="Registrar", command=self._registrar_producto).pack(
            side="left", padx=7
        )
        ttk.Button(acciones, text="Actualizar", command=self._actualizar_producto).pack(
            side="left", padx=7
        )
        ttk.Button(acciones, text="Eliminar", command=self._eliminar_producto).pack(
            side="left", padx=7
        )
        ttk.Button(acciones, text="Limpiar", command=self._limpiar_formulario).pack(
            side="left", padx=7
        )

        tabla_marco = ttk.LabelFrame(pestaña, text="Productos registrados", padding=8)
        tabla_marco.grid(row=1, column=0, sticky="nsew")
        tabla_marco.columnconfigure(0, weight=1)
        tabla_marco.rowconfigure(0, weight=1)

        columnas = ("codigo", "nombre", "categoria", "precio", "stock", "disponible")
        self._tabla_productos = ttk.Treeview(
            tabla_marco, columns=columnas, show="headings", selectmode="browse"
        )
        encabezados = {
            "codigo": ("Código", 90),
            "nombre": ("Nombre", 220),
            "categoria": ("Categoría", 150),
            "precio": ("Precio", 100),
            "stock": ("Stock", 80),
            "disponible": ("Disponibilidad", 125),
        }
        for clave, (titulo, ancho) in encabezados.items():
            self._tabla_productos.heading(clave, text=titulo)
            self._tabla_productos.column(clave, anchor="center", width=ancho)
        scrollbar = ttk.Scrollbar(
            tabla_marco, orient="vertical", command=self._tabla_productos.yview
        )
        self._tabla_productos.configure(yscrollcommand=scrollbar.set)
        self._tabla_productos.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._tabla_productos.bind("<<TreeviewSelect>>", self._al_seleccionar_producto)

        self._estado_productos = ttk.Label(pestaña, text="Selecciona una fila o busca por código.")
        self._estado_productos.grid(row=2, column=0, sticky="w", pady=(8, 0))

    def _construir_pestaña_usuarios(self) -> None:
        pestaña = ttk.Frame(self._pestañas, padding=12)
        self._pestaña_usuarios = pestaña
        pestaña.columnconfigure(0, weight=1)
        pestaña.rowconfigure(2, weight=1)
        self._pestañas.add(pestaña, text="👥 Usuarios")

        formulario = ttk.LabelFrame(pestaña, text="Datos del usuario", padding=10)
        formulario.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for columna in range(5):
            formulario.columnconfigure(columna, weight=1)

        campos = (
            ("Identificación", "identificacion", 14),
            ("Nombre", "nombre", 24),
            ("Usuario", "usuario", 18),
            ("Contraseña", "contraseña", 16),
        )
        for columna, (titulo, clave, ancho) in enumerate(campos):
            ttk.Label(formulario, text=titulo).grid(
                row=0, column=columna, sticky="w", padx=4, pady=(0, 4)
            )
            entrada = ttk.Entry(
                formulario,
                width=ancho,
                show="•" if clave == "contraseña" else "",
            )
            entrada.grid(row=1, column=columna, sticky="ew", padx=4, pady=(0, 8))
            self._campos_usuario[clave] = entrada

        ttk.Label(formulario, text="Rol").grid(
            row=0, column=4, sticky="w", padx=4, pady=(0, 4)
        )
        self._combo_rol_usuario = ttk.Combobox(
            formulario,
            textvariable=self._rol_usuario_var,
            values=ROLES,
            state="readonly",
            width=18,
        )
        self._combo_rol_usuario.grid(row=1, column=4, sticky="ew", padx=4, pady=(0, 8))
        self._combo_rol_usuario.bind(
            "<<ComboboxSelected>>", self._al_cambiar_rol_usuario
        )

        acciones = ttk.Frame(formulario)
        acciones.grid(row=2, column=0, columnspan=5, sticky="w", padx=2)
        ttk.Button(
            acciones, text="Registrar", command=self._registrar_usuario
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            acciones, text="Actualizar", command=self._actualizar_usuario
        ).pack(side="left", padx=6)
        ttk.Button(
            acciones, text="Eliminar", command=self._eliminar_usuario
        ).pack(side="left", padx=6)
        ttk.Button(
            acciones, text="Limpiar", command=self._limpiar_formulario_usuario
        ).pack(side="left", padx=6)

        self._ayuda_rol = ttk.Label(
            pestaña,
            text="Cliente: cuenta sin acceso a la gestión administrativa de usuarios.",
        )
        self._ayuda_rol.grid(row=1, column=0, sticky="w", pady=(0, 8))
        self._estado_usuarios = ttk.Label(
            pestaña, text="Selecciona un usuario o registra uno nuevo."
        )
        self._estado_usuarios.grid(row=3, column=0, sticky="w", pady=(8, 0))

        tabla_marco = ttk.LabelFrame(pestaña, text="Usuarios registrados", padding=8)
        tabla_marco.grid(row=2, column=0, sticky="nsew")
        tabla_marco.columnconfigure(0, weight=1)
        tabla_marco.rowconfigure(0, weight=1)

        columnas = ("identificacion", "nombre", "usuario", "rol")
        self._tabla_usuarios = ttk.Treeview(
            tabla_marco, columns=columnas, show="headings", selectmode="browse"
        )
        encabezados = {
            "identificacion": ("Identificación", 140),
            "nombre": ("Nombre", 260),
            "usuario": ("Usuario", 200),
            "rol": ("Rol", 160),
        }
        for clave, (titulo, ancho) in encabezados.items():
            self._tabla_usuarios.heading(clave, text=titulo)
            self._tabla_usuarios.column(clave, anchor="center", width=ancho)
        scrollbar = ttk.Scrollbar(
            tabla_marco, orient="vertical", command=self._tabla_usuarios.yview
        )
        self._tabla_usuarios.configure(yscrollcommand=scrollbar.set)
        self._tabla_usuarios.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self._tabla_usuarios.bind(
            "<<TreeviewSelect>>", self._al_seleccionar_usuario
        )

        for entrada in self._campos_usuario.values():
            entrada.bind("<Return>", lambda _evento: self._registrar_usuario())
            entrada.bind("<Escape>", self._al_presionar_escape_usuario)
        self._combo_rol_usuario.bind(
            "<Return>", lambda _evento: self._registrar_usuario()
        )
        self._combo_rol_usuario.bind(
            "<Escape>", self._al_presionar_escape_usuario
        )
        self._tabla_usuarios.bind(
            "<Escape>", self._al_presionar_escape_usuario
        )

    def _construir_pestaña_ventas(self) -> None:
        pestaña = ttk.Frame(self._pestañas, padding=18)
        self._pestañas.add(pestaña, text="🧾 Ventas")
        self._vista_ventas = VentaView(
            pestaña,
            venta_servicio=self._venta_servicio,
            restaurante_servicio=self._restaurante_servicio,
            al_registrar_venta=self._al_registrar_venta,
        )
        self._vista_ventas.pack(fill="both", expand=True)

    def actualizar(self, usuario_autenticado) -> None:
        self._usuario_actual = usuario_autenticado
        self._label_bienvenida.config(
            text=f"Bienvenido, {usuario_autenticado.nombre} · {usuario_autenticado.rol}"
        )
        self._actualizar_acceso_usuarios()
        self._refrescar_tabla_productos()
        self._actualizar_resumen()
        self._vista_ventas.actualizar(usuario_autenticado)

    def _actualizar_acceso_usuarios(self) -> None:
        pestaña = str(self._pestaña_usuarios)
        visibles = self._pestañas.tabs()
        es_administrador = (
            self._usuario_actual is not None
            and self._usuario_actual.rol == ADMINISTRADOR
        )
        if es_administrador:
            if pestaña not in visibles:
                self._pestañas.insert(1, self._pestaña_usuarios, text="👥 Usuarios")
            self._refrescar_tabla_usuarios()
        else:
            if pestaña in visibles:
                self._pestañas.forget(self._pestaña_usuarios)
            self._tabla_usuarios.delete(*self._tabla_usuarios.get_children())
            self._identificacion_usuario_original = None
            for entrada in self._campos_usuario.values():
                entrada.delete(0, tk.END)
            self._rol_usuario_var.set(CLIENTE)

    def _puede_gestionar_usuarios(self) -> bool:
        if self._usuario_actual is None or self._usuario_actual.rol != ADMINISTRADOR:
            self._mostrar_estado_usuario(
                "Solo un Administrador puede gestionar usuarios.", error=True
            )
            return False
        return True

    def _leer_formulario_usuario(self) -> dict:
        return {
            "identificacion": self._campos_usuario["identificacion"].get(),
            "nombre": self._campos_usuario["nombre"].get(),
            "usuario": self._campos_usuario["usuario"].get(),
            "contraseña": self._campos_usuario["contraseña"].get(),
            "rol": self._rol_usuario_var.get(),
        }

    def _al_seleccionar_usuario(self, _evento=None) -> None:
        seleccion = self._tabla_usuarios.selection()
        if not seleccion:
            return
        valores = self._tabla_usuarios.item(seleccion[0], "values")
        usuario = self._restaurante_servicio.buscar_usuario(valores[0])
        if usuario is None:
            self._mostrar_estado_usuario("No se encontró el usuario seleccionado.", error=True)
            return
        self._identificacion_usuario_original = usuario.identificacion
        for clave, entrada in self._campos_usuario.items():
            entrada.delete(0, tk.END)
            entrada.insert(0, str(getattr(usuario, clave)))
        self._rol_usuario_var.set(usuario.rol)
        self._actualizar_ayuda_rol(usuario.rol)
        self._mostrar_estado_usuario(
            f"Usuario {usuario.identificacion} cargado para consulta o edición."
        )

    def _registrar_usuario(self) -> None:
        if not self._puede_gestionar_usuarios():
            return
        try:
            usuario = self._restaurante_servicio.registrar_usuario(
                **self._leer_formulario_usuario()
            )
        except (ValueError, OSError) as error:
            self._mostrar_estado_usuario(str(error), error=True)
            return
        self._refrescar_tabla_usuarios()
        self._limpiar_formulario_usuario(mostrar_mensaje=False)
        self._mostrar_estado_usuario(
            f"Usuario {usuario.nombre} registrado y guardado."
        )

    def _actualizar_usuario(self) -> None:
        if not self._puede_gestionar_usuarios():
            return
        if self._identificacion_usuario_original is None:
            self._mostrar_estado_usuario(
                "Selecciona un usuario antes de actualizar.", error=True
            )
            return
        try:
            usuario = self._restaurante_servicio.actualizar_usuario(
                self._identificacion_usuario_original,
                **self._leer_formulario_usuario(),
            )
        except (ValueError, OSError) as error:
            self._mostrar_estado_usuario(str(error), error=True)
            return
        self._refrescar_tabla_usuarios()
        self._limpiar_formulario_usuario(mostrar_mensaje=False)
        self._mostrar_estado_usuario(
            f"Usuario {usuario.nombre} actualizado y guardado."
        )

    def _eliminar_usuario(self) -> None:
        if not self._puede_gestionar_usuarios():
            return
        if self._identificacion_usuario_original is None:
            self._mostrar_estado_usuario(
                "Selecciona un usuario antes de eliminar.", error=True
            )
            return
        usuario = self._restaurante_servicio.buscar_usuario(
            self._identificacion_usuario_original
        )
        if usuario is None:
            self._mostrar_estado_usuario("No se encontró el usuario seleccionado.", error=True)
            return
        confirmado = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Deseas eliminar al usuario {usuario.nombre}?",
            parent=self,
        )
        if not confirmado:
            return
        try:
            self._restaurante_servicio.eliminar_usuario(usuario.identificacion)
        except (ValueError, OSError) as error:
            self._mostrar_estado_usuario(str(error), error=True)
            return
        self._refrescar_tabla_usuarios()
        self._limpiar_formulario_usuario(mostrar_mensaje=False)
        self._mostrar_estado_usuario(f"Usuario {usuario.nombre} eliminado.")

    def _limpiar_formulario_usuario(self, _evento=None, mostrar_mensaje=True):
        for entrada in self._campos_usuario.values():
            entrada.delete(0, tk.END)
        self._rol_usuario_var.set(CLIENTE)
        self._identificacion_usuario_original = None
        seleccion = self._tabla_usuarios.selection()
        if seleccion:
            self._tabla_usuarios.selection_remove(*seleccion)
        self._actualizar_ayuda_rol(CLIENTE)
        if mostrar_mensaje:
            self._mostrar_estado_usuario("Formulario listo para un usuario nuevo.")
        self._campos_usuario["identificacion"].focus_set()
        return "break" if _evento is not None else None

    def _al_presionar_escape_usuario(self, _evento=None):
        return self._limpiar_formulario_usuario(_evento)

    def _al_cambiar_rol_usuario(self, _evento=None) -> None:
        rol = self._rol_usuario_var.get()
        self._actualizar_ayuda_rol(rol)

    def _actualizar_ayuda_rol(self, rol: str) -> None:
        descripciones = {
            ADMINISTRADOR: "Administrador: puede gestionar las cuentas de usuarios.",
            EMPLEADO: "Empleado: conserva el acceso operativo a productos y ventas.",
            CLIENTE: "Cliente: cuenta sin acceso a la gestión administrativa de usuarios.",
        }
        self._ayuda_rol.config(text=descripciones.get(rol, "Selecciona un rol."))

    def _mostrar_estado_usuario(self, mensaje: str, error: bool = False) -> None:
        self._estado_usuarios.config(
            text=mensaje,
            foreground="#a12622" if error else "#25643b",
        )

    def _al_registrar_venta(self, _venta, _producto) -> None:
        """Refresca el catálogo y el resumen luego de completar una venta."""
        self._refrescar_tabla_productos()
        self._actualizar_resumen()

    def _al_cambiar_pestaña(self, _evento=None) -> None:
        """Refresca las opciones al volver a Ventas después de editar productos."""
        if self._pestañas.select() == str(self._vista_ventas.master):
            self._vista_ventas.actualizar()

    def _leer_formulario(self) -> dict:
        return {clave: entrada.get() for clave, entrada in self._campos.items()}

    def _buscar_producto(self) -> None:
        codigo = self._campos["codigo"].get()
        producto = self._restaurante_servicio.buscar_producto(codigo)
        if producto is None:
            self._mostrar_estado("No se encontró un producto con ese código.", error=True)
            return
        self._cargar_formulario(producto)
        self._mostrar_estado(f"Producto {producto.codigo} cargado para consulta o edición.")

    def _al_seleccionar_producto(self, _evento=None) -> None:
        seleccion = self._tabla_productos.selection()
        if not seleccion:
            return
        valores = self._tabla_productos.item(seleccion[0], "values")
        producto = self._restaurante_servicio.buscar_producto(str(valores[0]))
        if producto is not None:
            self._cargar_formulario(producto)

    def _cargar_formulario(self, producto) -> None:
        for clave, entrada in self._campos.items():
            entrada.delete(0, tk.END)
            entrada.insert(0, str(getattr(producto, clave)))
        self._codigo_original = producto.codigo

    def _registrar_producto(self) -> None:
        try:
            producto = self._restaurante_servicio.registrar_producto(
                **self._leer_formulario()
            )
        except (ValueError, OSError) as error:
            self._mostrar_estado(str(error), error=True)
            return
        self._refrescar_tabla_productos()
        self._actualizar_resumen()
        self._seleccionar_fila(producto.codigo)
        self._mostrar_estado(f"Producto {producto.codigo} registrado y guardado.")

    def _actualizar_producto(self) -> None:
        if self._codigo_original is None:
            self._mostrar_estado("Busca o selecciona un producto antes de actualizar.", error=True)
            return
        try:
            producto = self._restaurante_servicio.actualizar_producto(
                self._codigo_original, **self._leer_formulario()
            )
        except (ValueError, OSError) as error:
            self._mostrar_estado(str(error), error=True)
            return
        self._refrescar_tabla_productos()
        self._actualizar_resumen()
        self._seleccionar_fila(producto.codigo)
        self._mostrar_estado(f"Producto {producto.codigo} actualizado y guardado.")

    def _eliminar_producto(self) -> None:
        if self._codigo_original is None:
            self._mostrar_estado("Busca o selecciona un producto antes de eliminar.", error=True)
            return
        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Deseas eliminar el producto {self._codigo_original}?",
            parent=self,
        ):
            return
        codigo = self._codigo_original
        try:
            self._restaurante_servicio.eliminar_producto(codigo)
        except (ValueError, OSError) as error:
            self._mostrar_estado(str(error), error=True)
            return
        self._refrescar_tabla_productos()
        self._actualizar_resumen()
        self._limpiar_formulario()
        self._mostrar_estado(f"Producto {codigo} eliminado.")

    def _limpiar_formulario(self) -> None:
        for entrada in self._campos.values():
            entrada.delete(0, tk.END)
        self._codigo_original = None
        seleccion = self._tabla_productos.selection()
        if seleccion:
            self._tabla_productos.selection_remove(*seleccion)
        self._mostrar_estado("Formulario listo para un producto nuevo.")
        self._campos["codigo"].focus_set()

    def _refrescar_tabla_productos(self) -> None:
        self._tabla_productos.delete(*self._tabla_productos.get_children())
        for indice, producto in enumerate(self._restaurante_servicio.listar_productos()):
            self._tabla_productos.insert(
                "",
                tk.END,
                iid=f"producto-{indice}",
                values=(
                    producto.codigo,
                    producto.nombre,
                    producto.categoria,
                    f"$ {producto.precio:.2f}",
                    producto.stock,
                    "Disponible" if producto.disponible else "Agotado",
                ),
            )

    def _seleccionar_fila(self, codigo: str) -> None:
        for fila in self._tabla_productos.get_children():
            valores = self._tabla_productos.item(fila, "values")
            if str(valores[0]).casefold() == codigo.casefold():
                self._tabla_productos.selection_set(fila)
                self._tabla_productos.focus(fila)
                self._tabla_productos.see(fila)
                break

    def _refrescar_tabla_usuarios(self) -> None:
        self._tabla_usuarios.delete(*self._tabla_usuarios.get_children())
        for usuario in self._restaurante_servicio.listar_usuarios():
            self._tabla_usuarios.insert(
                "",
                tk.END,
                iid=f"usuario-{usuario.identificacion}",
                values=(
                    usuario.identificacion,
                    usuario.nombre,
                    usuario.usuario,
                    usuario.rol,
                ),
            )

    def _actualizar_resumen(self) -> None:
        self._label_resumen.config(
            text=(
                f"{self._restaurante_servicio.total_productos()} productos"
                f"   ·   {self._restaurante_servicio.total_usuarios()} usuarios"
            )
        )

    def _mostrar_estado(self, mensaje: str, error: bool = False) -> None:
        self._estado_productos.config(
            text=mensaje,
            foreground="#a12622" if error else "#25643b",
        )
