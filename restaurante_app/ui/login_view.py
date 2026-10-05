# ============================================================
# ui/login_view.py
# LoginView — presenta una pantalla de acceso simulada mediante
# componentes de Tkinter: campos de usuario y contraseña, un
# mensaje de estado y un botón de ingreso.
#
# LoginView NO valida nada por sí misma ni conoce productos.json
# ni usuarios.json: le pide la validación a RestauranteServicio
# y, si el acceso es correcto, avisa a main.py a través del
# callback `al_iniciar_sesion` para que este decida cuándo
# mostrar MainView. Así la vista solo se ocupa de la interfaz.
# ============================================================

from pathlib import Path
import tkinter as tk
from tkinter import ttk


class LoginView(tk.Frame):
    """Pantalla de acceso: solicita usuario y contraseña y delega la validación."""

    def __init__(self, master, restaurante_servicio, al_iniciar_sesion) -> None:
        super().__init__(master, padx=40, pady=40)
        self._restaurante_servicio = restaurante_servicio
        self._al_iniciar_sesion = al_iniciar_sesion  # callback(usuario_autenticado)

        self._construir_widgets()

    def _construir_widgets(self) -> None:
        ruta_assets = Path(__file__).resolve().parent.parent / "assets"
        marca = ttk.Frame(self)
        marca.grid(row=0, column=0, columnspan=2, pady=(0, 14))
        try:
            self._logo_image = tk.PhotoImage(
                file=str(ruta_assets / "restaurante_logo.ppm")
            ).subsample(2, 2)
            ttk.Label(marca, image=self._logo_image).pack(side="left", padx=(0, 12))
        except tk.TclError:
            self._logo_image = None
        try:
            self._banner_image = tk.PhotoImage(
                file=str(ruta_assets / "viche_manabita.png")
            ).subsample(8, 8)
            ttk.Label(marca, image=self._banner_image).pack(side="left")
        except tk.TclError:
            self._banner_image = None
        titulo = ttk.Label(
            self, text="Restaurante — Acceso al sistema", font=("Segoe UI", 14, "bold")
        )
        titulo.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(self, text="Usuario:").grid(row=2, column=0, sticky="e", pady=5)
        self._entrada_usuario = ttk.Entry(self, width=25)
        self._entrada_usuario.grid(row=2, column=1, pady=5)

        ttk.Label(self, text="Contraseña:").grid(row=3, column=0, sticky="e", pady=5)
        self._entrada_contraseña = ttk.Entry(self, width=25, show="•")
        self._entrada_contraseña.grid(row=3, column=1, pady=5)

        self._mensaje = ttk.Label(self, text="", foreground="red")
        self._mensaje.grid(row=4, column=0, columnspan=2, pady=(10, 0))

        boton_ingresar = ttk.Button(self, text="Ingresar", command=self._intentar_ingresar)
        boton_ingresar.grid(row=5, column=0, columnspan=2, pady=(15, 0))

        # Permitir presionar Enter en cualquiera de los dos campos.
        self._entrada_usuario.bind("<Return>", lambda evento: self._intentar_ingresar())
        self._entrada_contraseña.bind("<Return>", lambda evento: self._intentar_ingresar())

    def _intentar_ingresar(self) -> None:
        """Lee los campos, valida que no estén vacíos y delega el acceso a RestauranteServicio."""
        usuario = self._entrada_usuario.get()
        contraseña = self._entrada_contraseña.get()

        if not usuario.strip() or not contraseña:
            self._mensaje.config(text="Ingrese usuario y contraseña.")
            return

        usuario_autenticado = self._restaurante_servicio.validar_acceso(usuario, contraseña)
        if usuario_autenticado is None:
            self._mensaje.config(text="Usuario o contraseña incorrectos.")
            return

        self.limpiar()
        self._al_iniciar_sesion(usuario_autenticado)

    def limpiar(self) -> None:
        """Borra los campos y el mensaje de estado.

        main.py llama a este método antes de volver a mostrar LoginView
        (por ejemplo, tras cerrar sesión), para que no queden datos de
        la sesión anterior visibles en la pantalla de acceso.
        """
        self._entrada_usuario.delete(0, tk.END)
        self._entrada_contraseña.delete(0, tk.END)
        self._mensaje.config(text="")
