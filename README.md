# Sistema de Gestión de Restaurante — Semana 16
Autor : Derly Zambrano

Esta versión continúa la aplicación de Semana 15. Conserva inicio de sesión, productos y ventas, y añade la gestión de usuarios con roles `Administrador`, `Empleado` y `Cliente`.

## Estructura

```text
POO-SEMANA-16/
├── README.md
└── restaurante_app/
    ├── assets/ (logotipo, ilustración viche_manabita.png e iconos SVG)
    ├── datos/ (productos.json, usuarios.json, ventas.json)
    ├── modelos/ (producto.py, usuario.py, venta.py)
    ├── servicios/ (archivo_servicio.py, restaurante_servicio.py, venta_servicio.py)
    ├── ui/ (login_view.py, main_view.py, venta_view.py)
    └── main.py
```

## Usuarios y eventos

La pestaña Usuarios aparece únicamente cuando inicia sesión una cuenta con rol Administrador. Desde el formulario puede registrar, consultar, actualizar y eliminar usuarios. La tabla muestra identificación, nombre, usuario y rol; no presenta contraseñas. Al seleccionar una fila, `<<TreeviewSelect>>` obtiene el identificador y consulta el objeto mediante `RestauranteServicio` para cargarlo en el formulario.

El `Combobox` ofrece los tres roles y `<<ComboboxSelected>>` actualiza su descripción. `Return` reutiliza el callback de registro y `Escape` limpia el formulario y la selección. Los botones mantienen `command=`. La interfaz responde a los eventos y delega validaciones, CRUD y persistencia a los servicios; no manipula archivos JSON directamente.

## Roles y persistencia

`Usuario` incorpora y valida el rol. `RestauranteServicio` valida identificadores y nombres de usuario únicos y coordina el CRUD; `ArchivoServicio` persiste el listado en `datos/usuarios.json` mediante reemplazo atómico. Los datos de productos, ventas e inventario conservan su flujo de Semana 15. Los archivos de datos incluidos sirven para demostración y guardan contraseñas en texto plano; no deben contener credenciales reales.

La interfaz conserva el logotipo Sazón Manaba de `assets/` y las pestañas Productos y Ventas. Los roles Empleado y Cliente no ven la pestaña administrativa de Usuarios.

## Ejecución

Requisitos: Python 3.7 o posterior con Tkinter. Desde la carpeta del repositorio:

```powershell
cd restaurante_app
python main.py
```

Cuentas de prueba de `restaurante_app/datos/usuarios.json`:

| Usuario | Contraseña | Rol |
| --- | --- | --- |
| derly | admin123 | Administrador |
| prueba | 1234 | Empleado |
| cliente | cliente123 | Cliente |

## Recursos visuales

`restaurante_app/assets/viche_manabita.png` es una ilustración original para la pantalla de acceso. El logotipo existente se conserva. La carpeta `restaurante_app/assets/iconos/` incluye pictogramas SVG escalables para productos, usuarios, ventas y acciones de agregar, editar, eliminar y limpiar; las pestañas muestran pictogramas para identificar las secciones.
