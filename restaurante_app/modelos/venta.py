"""Modelo de una venta básica del restaurante."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Venta:
    codigo_venta: str
    fecha: str
    identificacion_usuario: int
    nombre_usuario: str
    codigo_producto: str
    nombre_producto: str
    cantidad: int
    precio_unitario: float

    def __post_init__(self) -> None:
        for campo in ("codigo_venta", "fecha", "nombre_usuario", "codigo_producto", "nombre_producto"):
            valor = getattr(self, campo)
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"El campo {campo} no puede estar vacío.")
            object.__setattr__(self, campo, valor.strip())

        object.__setattr__(
            self,
            "identificacion_usuario",
            self.validar_identificacion(self.identificacion_usuario),
        )
        object.__setattr__(self, "cantidad", self.validar_cantidad(self.cantidad))

        if isinstance(self.precio_unitario, bool):
            raise ValueError("El precio unitario debe ser mayor que cero.")
        try:
            precio = float(self.precio_unitario)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("El precio unitario debe ser numérico.") from None
        if not math.isfinite(precio) or precio <= 0:
            raise ValueError("El precio unitario debe ser finito y mayor que cero.")
        object.__setattr__(self, "precio_unitario", precio)

    @staticmethod
    def validar_cantidad(valor) -> int:
        if isinstance(valor, bool):
            raise ValueError("La cantidad debe ser un entero mayor que cero.")
        try:
            cantidad = float(valor)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("La cantidad debe ser un número entero.") from None
        if not math.isfinite(cantidad) or not cantidad.is_integer() or cantidad <= 0:
            raise ValueError("La cantidad debe ser un entero mayor que cero.")
        return int(cantidad)

    @staticmethod
    def validar_identificacion(valor) -> int:
        if isinstance(valor, bool):
            raise ValueError("La identificación del usuario debe ser un entero positivo.")
        try:
            identificacion = int(valor)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("La identificación del usuario debe ser un entero positivo.") from None
        if isinstance(valor, float):
            if not math.isfinite(valor) or not valor.is_integer():
                raise ValueError("La identificación del usuario debe ser un entero positivo.")
        elif not isinstance(valor, (int, str)):
            raise ValueError("La identificación del usuario debe ser un entero positivo.")
        if isinstance(valor, str) and str(identificacion) != valor.strip():
            raise ValueError("La identificación del usuario debe ser un entero positivo.")
        if identificacion <= 0:
            raise ValueError("La identificación del usuario debe ser un entero positivo.")
        return identificacion

    @property
    def total(self) -> float:
        return round(self.precio_unitario * self.cantidad, 2)

    def to_dict(self) -> dict:
        return {
            "codigo_venta": self.codigo_venta,
            "fecha": self.fecha,
            "identificacion_usuario": self.identificacion_usuario,
            "nombre_usuario": self.nombre_usuario,
            "codigo_producto": self.codigo_producto,
            "nombre_producto": self.nombre_producto,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario,
            "total": self.total,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Venta":
        if not isinstance(datos, dict):
            raise ValueError("Cada venta debe ser un objeto JSON.")
        try:
            return cls(
                codigo_venta=datos["codigo_venta"],
                fecha=datos["fecha"],
                identificacion_usuario=datos["identificacion_usuario"],
                nombre_usuario=datos["nombre_usuario"],
                codigo_producto=datos["codigo_producto"],
                nombre_producto=datos["nombre_producto"],
                cantidad=datos["cantidad"],
                precio_unitario=datos["precio_unitario"],
            )
        except KeyError as error:
            raise ValueError(f"Falta el campo obligatorio {error.args[0]}.") from None
