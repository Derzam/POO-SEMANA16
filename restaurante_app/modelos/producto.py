"""Modelo de los productos disponibles en el restaurante."""

import math


class Producto:
    """Representa un producto y valida sus campos al asignarlos."""

    def __init__(
        self,
        codigo: str,
        nombre: str,
        categoria: str,
        precio: float,
        stock: int,
    ) -> None:
        self.codigo = codigo
        self.nombre = nombre
        self.categoria = categoria
        self.precio = precio
        self.stock = stock

    @property
    def codigo(self) -> str:
        return self._codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        self._codigo = self._validar_texto(valor, "El código")

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = self._validar_texto(valor, "El nombre")

    @property
    def categoria(self) -> str:
        return self._categoria

    @categoria.setter
    def categoria(self, valor: str) -> None:
        self._categoria = self._validar_texto(valor, "La categoría")

    @staticmethod
    def _validar_texto(valor: str, etiqueta: str) -> str:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"{etiqueta} del producto no puede estar vacío.")
        return valor.strip()

    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, valor: float) -> None:
        if isinstance(valor, bool):
            raise ValueError("El precio debe ser un número mayor que cero.")
        try:
            precio = float(valor)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("El precio debe ser numérico.") from None
        if not math.isfinite(precio) or precio <= 0:
            raise ValueError("El precio debe ser un número finito mayor que cero.")
        self._precio = precio

    @property
    def stock(self) -> int:
        return self._stock

    @stock.setter
    def stock(self, valor: int) -> None:
        if isinstance(valor, bool):
            raise ValueError("El stock debe ser un número entero no negativo.")
        try:
            cantidad = float(valor)
        except (TypeError, ValueError, OverflowError):
            raise ValueError("El stock debe ser un número entero.") from None
        if not math.isfinite(cantidad) or not cantidad.is_integer() or cantidad < 0:
            raise ValueError("El stock debe ser un número entero no negativo.")
        self._stock = int(cantidad)

    @property
    def disponible(self) -> bool:
        return self._stock > 0

    def __str__(self) -> str:
        return f"{self.nombre} ($ {self.precio:.2f})"

    def to_dict(self) -> dict:
        """Convierte el producto al formato que se guarda en JSON."""
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "categoria": self.categoria,
            "precio": self.precio,
            "stock": self.stock,
        }

    @classmethod
    def from_dict(cls, datos: dict) -> "Producto":
        if not isinstance(datos, dict):
            raise ValueError("Cada producto debe estar representado por un objeto.")
        try:
            return cls(
                codigo=datos["codigo"],
                nombre=datos["nombre"],
                categoria=datos["categoria"],
                precio=datos["precio"],
                stock=datos["stock"],
            )
        except KeyError as error:
            raise ValueError(f"Falta el campo obligatorio {error.args[0]}.") from None

