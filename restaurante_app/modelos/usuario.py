"""Modelo de un usuario del sistema del restaurante."""

from dataclasses import dataclass
import math


ADMINISTRADOR = "Administrador"
EMPLEADO = "Empleado"
CLIENTE = "Cliente"
ROLES = (ADMINISTRADOR, EMPLEADO, CLIENTE)


@dataclass
class Usuario:
    """Representa una cuenta y su rol dentro de la aplicación."""

    identificacion: int
    nombre: str
    usuario: str
    contraseña: str
    rol: str = CLIENTE

    def __post_init__(self) -> None:
        self.identificacion = self.validar_identificacion(self.identificacion)

        if not isinstance(self.nombre, str) or not self.nombre.strip():
            raise ValueError("El nombre del usuario no puede estar vacío.")
        self.nombre = self.nombre.strip()

        if not isinstance(self.usuario, str) or not self.usuario.strip():
            raise ValueError("El nombre de usuario no puede estar vacío.")
        self.usuario = self.usuario.strip()

        if not isinstance(self.contraseña, str) or not self.contraseña.strip():
            raise ValueError("La contraseña no puede estar vacía.")

        if not isinstance(self.rol, str) or self.rol.strip() not in ROLES:
            raise ValueError("Selecciona un rol válido: Administrador, Empleado o Cliente.")
        self.rol = self.rol.strip()

    @staticmethod
    def validar_identificacion(valor) -> int:
        if isinstance(valor, bool):
            raise ValueError("La identificación debe ser un entero positivo.")
        try:
            identificacion = int(valor)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("La identificación debe ser un entero positivo.") from None

        if isinstance(valor, float):
            if not math.isfinite(valor) or not valor.is_integer():
                raise ValueError("La identificación debe ser un entero positivo.")
        elif isinstance(valor, str):
            if str(identificacion) != valor.strip():
                raise ValueError("La identificación debe ser un entero positivo.")
        elif not isinstance(valor, int):
            raise ValueError("La identificación debe ser un entero positivo.")

        if identificacion <= 0:
            raise ValueError("La identificación debe ser un entero positivo.")
        return identificacion

    def __str__(self) -> str:
        return (
            f"[ID {self.identificacion}] {self.nombre} — "
            f"usuario: {self.usuario} — rol: {self.rol}"
        )

    def to_dict(self) -> dict:
        """Convierte el usuario al formato persistido en JSON."""
        return {
            "identificacion": self.identificacion,
            "nombre": self.nombre,
            "usuario": self.usuario,
            "contraseña": self.contraseña,
            "rol": self.rol,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Usuario":
        if not isinstance(datos, dict):
            raise ValueError("Cada usuario debe estar representado por un objeto JSON.")
        try:
            return cls(
                identificacion=datos["identificacion"],
                nombre=datos["nombre"],
                usuario=datos["usuario"],
                contraseña=datos["contraseña"],
                # Permite cargar los usuarios de Semana 15 sin perder compatibilidad.
                rol=datos.get("rol", CLIENTE),
            )
        except KeyError as error:
            raise ValueError(f"Falta el campo obligatorio {error.args[0]}.") from None
