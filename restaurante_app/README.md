# Restaurante — Semana 16

## Propósito

La aplicación conserva el login, productos y ventas de Semana 15. Añade CRUD de usuarios con roles Administrador, Empleado y Cliente, y evidencia eventos de selección, teclado y controles Tkinter.

## Estructura

```text
restaurante_app/
├── assets/ (restaurante_logo.svg, restaurante_logo.ppm, viche_manabita.png, iconos/*.svg)
├── datos/ (productos.json, usuarios.json, ventas.json)
├── modelos/ (producto.py, usuario.py, venta.py)
├── servicios/ (archivo_servicio.py, restaurante_servicio.py, venta_servicio.py)
├── ui/ (login_view.py, main_view.py, venta_view.py)
└── main.py
```

## Gestión de usuarios

Solo el Administrador ve la pestaña Usuarios. El formulario permite registrar, consultar, actualizar y eliminar cuentas, con identificación, nombre, usuario, contraseña y rol. El Treeview muestra identificación, nombre, usuario y rol; la contraseña no se incluye en sus filas.

Al seleccionar una fila, `<<TreeviewSelect>>` toma su identificador y llama a `RestauranteServicio.buscar_usuario` para cargar el usuario. El `Combobox` de rol responde a `<<ComboboxSelected>>`; `Return` ejecuta el método de registro existente y `Escape` limpia el formulario y la selección. Los botones usan `command=`. La interfaz coordina estos eventos y los servicios validan y guardan los cambios.

`Usuario` valida sus campos y el rol. `RestauranteServicio` evita identificadores y nombres de usuario duplicados y administra el CRUD. `ArchivoServicio` persiste los datos con reemplazo atómico. No se implementan permisos avanzados, bloqueo de cuentas ni recuperación de contraseñas.

## Ejecución

Requisitos: Python 3.7 o posterior con Tkinter. Ejecuta desde esta carpeta:

```powershell
python main.py
```

Usuarios de prueba definidos en `datos/usuarios.json`:

| Usuario | Contraseña | Rol |
| --- | --- | --- |
| derly | admin123 | Administrador |
| prueba | 1234 | Empleado |
| cliente | cliente123 | Cliente |

Las credenciales son solo para demostración y se guardan en texto plano; no uses contraseñas reales.

## Recursos visuales

La pantalla de acceso combina el logotipo original con `assets/viche_manabita.png`, una ilustración del viche manabita creada para el proyecto. `assets/iconos/` contiene pictogramas SVG escalables para Productos, Usuarios, Ventas y las acciones de agregar, editar, eliminar y limpiar. Las pestañas de la aplicación usan pictogramas junto a sus nombres.
