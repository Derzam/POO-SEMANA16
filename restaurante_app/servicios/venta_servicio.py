"""Reglas de negocio de ventas y coordinación con el inventario."""

from datetime import datetime
from typing import List, Tuple

from modelos.venta import Venta
from servicios.archivo_servicio import ArchivoServicio
from servicios.restaurante_servicio import RestauranteServicio


class VentaServicio:
    """Valida ventas, descuenta existencias y persiste el historial."""

    def __init__(
        self,
        archivo_servicio: ArchivoServicio,
        restaurante_servicio: RestauranteServicio,
    ) -> None:
        self._archivo_servicio = archivo_servicio
        self._restaurante_servicio = restaurante_servicio
        self._ventas: List[Venta] = []

    def cargar_ventas(self) -> None:
        self._ventas = self._archivo_servicio.cargar_ventas()

    def listar_ventas(self) -> List[Venta]:
        return list(self._ventas)

    def total_ventas(self) -> int:
        return len(self._ventas)

    def registrar_venta(
        self, identificacion_usuario: int, codigo_producto: str, cantidad
    ) -> Tuple[Venta, object]:
        cantidad_validada = Venta.validar_cantidad(cantidad)
        try:
            identificacion = Venta.validar_identificacion(identificacion_usuario)
        except ValueError:
            raise ValueError("Selecciona un usuario registrado.") from None
        usuario = next(
            (
                candidato
                for candidato in self._restaurante_servicio.listar_usuarios()
                if candidato.identificacion == identificacion
            ),
            None,
        )
        if usuario is None:
            raise ValueError("El usuario seleccionado no está registrado.")

        producto = self._restaurante_servicio.buscar_producto(codigo_producto)
        if producto is None:
            raise ValueError("Selecciona un producto registrado.")
        if producto.stock <= 0:
            raise ValueError("El producto no tiene existencias disponibles.")
        if cantidad_validada > producto.stock:
            raise ValueError(
                f"Stock insuficiente. Hay {producto.stock} unidades disponibles."
            )

        venta = Venta(
            codigo_venta=self._nuevo_codigo(),
            fecha=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            identificacion_usuario=usuario.identificacion,
            nombre_usuario=usuario.nombre,
            codigo_producto=producto.codigo,
            nombre_producto=producto.nombre,
            cantidad=cantidad_validada,
            precio_unitario=producto.precio,
        )
        producto_actualizado = self._restaurante_servicio.actualizar_producto(
            codigo_original=producto.codigo,
            codigo=producto.codigo,
            nombre=producto.nombre,
            categoria=producto.categoria,
            precio=producto.precio,
            stock=producto.stock - cantidad_validada,
        )
        nuevas_ventas = self.listar_ventas()
        nuevas_ventas.append(venta)
        try:
            self._archivo_servicio.guardar_ventas(nuevas_ventas)
        except OSError as error:
            try:
                self._restaurante_servicio.actualizar_producto(
                    codigo_original=producto_actualizado.codigo,
                    codigo=producto.codigo,
                    nombre=producto.nombre,
                    categoria=producto.categoria,
                    precio=producto.precio,
                    stock=producto.stock,
                )
            except (ValueError, OSError) as error_reversion:
                raise OSError(
                    "No se pudo guardar la venta ni restaurar el stock. "
                    "Revisa los archivos de datos antes de continuar."
                ) from error_reversion
            raise OSError(
                "No se pudo guardar la venta; el stock anterior fue restaurado."
            ) from error

        self._ventas = nuevas_ventas
        return venta, producto_actualizado

    def _nuevo_codigo(self) -> str:
        existentes = {venta.codigo_venta for venta in self._ventas}
        consecutivo = 1
        while f"V-{consecutivo:04d}" in existentes:
            consecutivo += 1
        return f"V-{consecutivo:04d}"
