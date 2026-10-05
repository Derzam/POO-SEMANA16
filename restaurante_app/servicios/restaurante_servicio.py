"""Reglas de negocio y operaciones de consulta y CRUD del restaurante."""

from typing import List, Optional

from modelos.producto import Producto
from modelos.usuario import Usuario
from servicios.archivo_servicio import ArchivoServicio


class RestauranteServicio:
    """Coordina acceso, consulta de datos y mantenimiento de productos."""

    def __init__(self, archivo_servicio: ArchivoServicio) -> None:
        self._archivo_servicio = archivo_servicio
        self._productos: List[Producto] = []
        self._usuarios: List[Usuario] = []

    def cargar_datos(self) -> None:
        self._productos = self._archivo_servicio.cargar_productos()
        self._usuarios = self._archivo_servicio.cargar_usuarios()

    def validar_acceso(self, usuario: str, contraseña: str) -> Optional[Usuario]:
        usuario_normalizado = usuario.strip()
        for candidato in self._usuarios:
            if candidato.usuario == usuario_normalizado and candidato.contraseña == contraseña:
                return candidato
        return None

    def listar_productos(self) -> List[Producto]:
        """Devuelve una copia de la lista para proteger la colección interna."""
        return list(self._productos)

    def listar_usuarios(self) -> List[Usuario]:
        return list(self._usuarios)

    def buscar_usuario(self, identificacion: int) -> Optional[Usuario]:
        """Busca un usuario por identificador sin exponer la lista interna."""
        try:
            identificacion_validada = Usuario.validar_identificacion(identificacion)
        except ValueError:
            return None
        return next(
            (
                usuario
                for usuario in self._usuarios
                if usuario.identificacion == identificacion_validada
            ),
            None,
        )

    def registrar_usuario(
        self, identificacion: int, nombre: str, usuario: str, contraseña: str, rol: str
    ) -> Usuario:
        nuevo = Usuario(identificacion, nombre, usuario, contraseña, rol)
        self._verificar_usuario_disponible(nuevo)
        nuevos_usuarios = self.listar_usuarios()
        nuevos_usuarios.append(nuevo)
        self._guardar_y_actualizar_usuarios(nuevos_usuarios)
        return nuevo

    def actualizar_usuario(
        self,
        identificacion_original: int,
        identificacion: int,
        nombre: str,
        usuario: str,
        contraseña: str,
        rol: str,
    ) -> Usuario:
        indice = self._indice_usuario(identificacion_original)
        actualizado = Usuario(identificacion, nombre, usuario, contraseña, rol)
        self._verificar_usuario_disponible(actualizado, excluir_indice=indice)
        nuevos_usuarios = self.listar_usuarios()
        nuevos_usuarios[indice] = actualizado
        self._guardar_y_actualizar_usuarios(nuevos_usuarios)
        return actualizado

    def eliminar_usuario(self, identificacion: int) -> Usuario:
        indice = self._indice_usuario(identificacion)
        nuevos_usuarios = self.listar_usuarios()
        eliminado = nuevos_usuarios.pop(indice)
        self._guardar_y_actualizar_usuarios(nuevos_usuarios)
        return eliminado

    def buscar_producto(self, codigo: str) -> Optional[Producto]:
        if not isinstance(codigo, str):
            return None
        codigo_normalizado = codigo.strip().casefold()
        if not codigo_normalizado:
            return None
        return next(
            (p for p in self._productos if p.codigo.casefold() == codigo_normalizado),
            None,
        )

    def registrar_producto(
        self, codigo: str, nombre: str, categoria: str, precio: float, stock: int
    ) -> Producto:
        producto = Producto(codigo, nombre, categoria, precio, stock)
        self._verificar_codigo_disponible(producto.codigo)
        nuevos_productos = self.listar_productos()
        nuevos_productos.append(producto)
        self._guardar_y_actualizar(nuevos_productos)
        return producto

    def actualizar_producto(
        self,
        codigo_original: str,
        codigo: str,
        nombre: str,
        categoria: str,
        precio: float,
        stock: int,
    ) -> Producto:
        indice = self._indice_producto(codigo_original)
        actualizado = Producto(codigo, nombre, categoria, precio, stock)
        self._verificar_codigo_disponible(actualizado.codigo, excluir_indice=indice)
        nuevos_productos = self.listar_productos()
        nuevos_productos[indice] = actualizado
        self._guardar_y_actualizar(nuevos_productos)
        return actualizado

    def eliminar_producto(self, codigo: str) -> Producto:
        indice = self._indice_producto(codigo)
        eliminados = self.listar_productos()
        producto = eliminados.pop(indice)
        self._guardar_y_actualizar(eliminados)
        return producto

    def total_productos(self) -> int:
        return len(self._productos)

    def total_usuarios(self) -> int:
        return len(self._usuarios)

    def _indice_usuario(self, identificacion: int) -> int:
        usuario = self.buscar_usuario(identificacion)
        if usuario is None:
            raise ValueError("No se encontró un usuario con esa identificación.")
        return self._usuarios.index(usuario)

    def _verificar_usuario_disponible(
        self, nuevo: Usuario, excluir_indice: Optional[int] = None
    ) -> None:
        for indice, existente in enumerate(self._usuarios):
            if indice == excluir_indice:
                continue
            if existente.identificacion == nuevo.identificacion:
                raise ValueError("Ya existe un usuario con esa identificación.")
            if existente.usuario.casefold() == nuevo.usuario.casefold():
                raise ValueError("Ya existe una cuenta con ese nombre de usuario.")

    def _guardar_y_actualizar_usuarios(self, usuarios: List[Usuario]) -> None:
        # Primero se persiste; si falla, la colección en memoria no cambia.
        self._archivo_servicio.guardar_usuarios(usuarios)
        self._usuarios = usuarios

    def _indice_producto(self, codigo: str) -> int:
        producto = self.buscar_producto(codigo)
        if producto is None:
            raise ValueError("No se encontró un producto con ese código.")
        return self._productos.index(producto)

    def _verificar_codigo_disponible(
        self, codigo: str, excluir_indice: Optional[int] = None
    ) -> None:
        for indice, producto in enumerate(self._productos):
            if indice != excluir_indice and producto.codigo.casefold() == codigo.casefold():
                raise ValueError("Ya existe un producto con ese código.")

    def _guardar_y_actualizar(self, productos: List[Producto]) -> None:
        # Primero se persiste; si el archivo falla, la colección en memoria sigue igual.
        self._archivo_servicio.guardar_productos(productos)
        self._productos = productos
