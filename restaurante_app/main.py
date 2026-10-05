"""Punto de entrada y navegación de la aplicación Tkinter."""

import tkinter as tk

from servicios.archivo_servicio import ArchivoServicio
from servicios.restaurante_servicio import RestauranteServicio
from servicios.venta_servicio import VentaServicio
from ui.login_view import LoginView
from ui.main_view import MainView


class Aplicacion:
    """Prepara los servicios y cambia entre el login y el panel principal."""

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._root.title("Sistema de Gestión de Restaurante")
        self._root.geometry("1040x680")
        self._root.minsize(880, 590)

        archivo_servicio = ArchivoServicio()
        self._restaurante_servicio = RestauranteServicio(archivo_servicio)
        self._restaurante_servicio.cargar_datos()
        self._venta_servicio = VentaServicio(archivo_servicio, self._restaurante_servicio)
        self._venta_servicio.cargar_ventas()

        self._contenedor = tk.Frame(self._root)
        self._contenedor.pack(fill="both", expand=True)
        self._contenedor.rowconfigure(0, weight=1)
        self._contenedor.columnconfigure(0, weight=1)

        self._login_view = LoginView(
            self._contenedor,
            restaurante_servicio=self._restaurante_servicio,
            al_iniciar_sesion=self._mostrar_main_view,
        )
        self._main_view = MainView(
            self._contenedor,
            restaurante_servicio=self._restaurante_servicio,
            venta_servicio=self._venta_servicio,
            al_cerrar_sesion=self._cerrar_sesion,
        )

        for vista in (self._login_view, self._main_view):
            vista.grid(row=0, column=0, sticky="nsew")

        self._mostrar_login_view()

    def _mostrar_login_view(self) -> None:
        self._login_view.tkraise()

    def _mostrar_main_view(self, usuario_autenticado) -> None:
        self._main_view.actualizar(usuario_autenticado)
        self._main_view.tkraise()

    def _cerrar_sesion(self) -> None:
        self._login_view.limpiar()
        self._mostrar_login_view()


def main() -> None:
    root = tk.Tk()
    Aplicacion(root)
    root.mainloop()


if __name__ == "__main__":
    main()
