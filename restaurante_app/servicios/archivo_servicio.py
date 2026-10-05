"""Lectura y persistencia de productos, usuarios y ventas en archivos JSON."""

import json
import os
from pathlib import Path
import tempfile
from typing import Callable, List, TypeVar

from modelos.producto import Producto
from modelos.usuario import Usuario
from modelos.venta import Venta

RUTA_DATOS = Path(__file__).resolve().parent.parent / "datos"
T = TypeVar("T")


class ArchivoServicio:
    """Lee los JSON de datos y persiste las modificaciones de productos."""

    def __init__(
        self,
        ruta_productos: Path = RUTA_DATOS / "productos.json",
        ruta_usuarios: Path = RUTA_DATOS / "usuarios.json",
        ruta_ventas: Path = RUTA_DATOS / "ventas.json",
    ) -> None:
        self._ruta_productos = Path(ruta_productos)
        self._ruta_usuarios = Path(ruta_usuarios)
        self._ruta_ventas = Path(ruta_ventas)

    def cargar_productos(self) -> List[Producto]:
        return self._cargar(self._ruta_productos, Producto.from_dict, "productos")

    def cargar_usuarios(self) -> List[Usuario]:
        return self._cargar(self._ruta_usuarios, Usuario.from_dict, "usuarios")

    def cargar_ventas(self) -> List[Venta]:
        return self._cargar(self._ruta_ventas, Venta.from_dict, "ventas")

    def guardar_productos(self, productos: List[Producto]) -> None:
        """Guarda el catálogo completo en el JSON de productos."""
        self._guardar_json(
            self._ruta_productos, [producto.to_dict() for producto in productos]
        )

    def guardar_usuarios(self, usuarios: List[Usuario]) -> None:
        """Guarda el listado de usuarios en su archivo JSON."""
        self._guardar_json(
            self._ruta_usuarios, [usuario.to_dict() for usuario in usuarios]
        )

    def guardar_ventas(self, ventas: List[Venta]) -> None:
        """Guarda el historial completo de ventas en su archivo JSON."""
        self._guardar_json(self._ruta_ventas, [venta.to_dict() for venta in ventas])

    @staticmethod
    def _guardar_json(ruta: Path, datos: list) -> None:
        """Reemplaza el JSON de forma atómica para conservar el archivo previo."""
        ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=str(ruta.parent),
                prefix=f".{ruta.stem}-",
                suffix=".tmp",
                delete=False,
            ) as archivo:
                temporal = Path(archivo.name)
                json.dump(datos, archivo, ensure_ascii=False, indent=4)
                archivo.write("\n")
                archivo.flush()
                os.fsync(archivo.fileno())
            os.replace(str(temporal), str(ruta))
        except Exception:
            if temporal is not None and temporal.exists():
                try:
                    temporal.unlink()
                except OSError:
                    pass
            raise

    @staticmethod
    def _cargar(ruta: Path, convertir: Callable[[dict], T], etiqueta: str) -> List[T]:
        try:
            with ruta.open("r", encoding="utf-8") as archivo:
                datos_crudos = json.load(archivo)
        except FileNotFoundError:
            print(f"Aviso: No se encontró el archivo de {etiqueta} ({ruta}).")
            return []
        except json.JSONDecodeError:
            print(f"Aviso: El archivo de {etiqueta} ({ruta}) no contiene JSON válido.")
            return []
        except OSError as error:
            print(f"Aviso: No se pudo leer el archivo de {etiqueta} ({ruta}): {error}")
            return []

        if not isinstance(datos_crudos, list):
            print(f"Aviso: El archivo de {etiqueta} debe contener una lista JSON.")
            return []

        objetos: List[T] = []
        for indice, entrada in enumerate(datos_crudos, start=1):
            try:
                if not isinstance(entrada, dict):
                    raise ValueError("el registro debe ser un objeto JSON")
                objetos.append(convertir(entrada))
            except (KeyError, TypeError, ValueError) as error:
                print(f"Aviso: Se omitió el registro {indice} de {etiqueta}: {error}")
        return objetos
