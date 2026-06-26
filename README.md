
EV CHARGE — GUÍA DE NAVEGACIÓN Y MANUAL DE USUARIO


¡Bienvenido a EV Charge! Esta guía te explicará paso a paso cómo 
moverte por la aplicación, qué encontrarás en cada pantalla y 
cómo usar todas las funcionalidades.


1. ACCESO A LA APLICACIÓN

Abre tu navegador y ve a: http://127.0.0.1:8000

Aquí encontrarás la "Landing Page" (página de inicio) de EV Charge. 
Desde aquí puedes conocer el proyecto y acceder a las herramientas 
principales.


2. NAVEGACIÓN POR LA LANDING PAGE (Index)

En la barra de navegación superior (navbar) encontrarás:

- INICIO: Te lleva al banner principal con el eslogan del proyecto.
- SERVICIOS: Una sección con 6 tarjetas que explican las funcionalidades clave 
  de la aplicación (Mapa, Filtro, Planificador, Comunidad, Historial y Reservas).
- QUIÉNES SOMOS: Información sobre el origen del proyecto (SENA ADSO).
- EN NÚMEROS: Estadísticas visuales del proyecto.
- CONTACTO: Un formulario para enviar mensajes.

BOTONES IMPORTANTES EN EL NAVBAR:
- "Abrir mapa →": Este es el botón más importante. Te lleva al 
  DASHBOARD DEL USUARIO.
- "Iniciar sesión" / "Registrarse": Si no tienes cuenta, haz clic aquí. 
  Se abrirá una ventana modal para que te loguees o crees tu usuario.


3. EL DASHBOARD DEL USUARIO (mapa.html)

Cuando haces clic en "Abrir mapa", entras al centro de operaciones. 
A la izquierda tienes un menú lateral (Sidebar) y a la derecha el mapa.

SECCIÓN SUPERIOR (Topbar):
- Botón "← Inicio": Para volver a la Landing Page.
- Logo de EV Charge.
- Información de usuario y botones de "Iniciar sesión / Cerrar sesión".

EL MAPA (Centro):
- Puedes hacer zoom y moverte por el mapa de Bogotá.
- Los puntos verdes son ESTACIONES DE CARGA.
- Haz clic en cualquier punto verde para ver la información de esa estación 
  (nombre, dirección, conectores disponibles, si está libre o reservada).

EL MENÚ LATERAL (Sidebar - Navegación entre pestañas):
El menú lateral tiene varias pestañas. Para cambiar de funcionalidad, 
solo haz clic en el nombre de la pestaña en la parte superior del menú.


4. CÓMO USAR CADA PESTAÑA DEL MENÚ LATERAL


PESTAÑA: 🗺 MAPA
Cuando seleccionas una estación en el mapa, aquí se despliega su información.
- Verás su estado (Disponible, Reservada, o En mantenimiento).
- Podrás ver sus conectores, calificaciones de otros usuarios y reportes activos.
- Botones clave: 
  * "⭐ Calificar esta estación": Te permite dejar una puntuación.
  * "📢 Reportar problema": Para reportar averías.
  * "🚀 Cómo llegar desde aquí": Calcula la ruta desde tu ubicación actual hasta la estación.

PESTAÑA: 🚗 AUTO (Vehículos)
- Aquí puedes gestionar tus vehículos eléctricos.
- Para agregar un vehículo: Completa los datos (Marca, Modelo, Autonomía, Conector) 
  y haz clic en "Guardar vehículo".
- El sistema usará el conector de tu vehículo activo para filtrar estaciones automáticamente.

PESTAÑA: 📋 CARGAS (Historial)
- Aquí verás las estadísticas de tus recargas (sesiones totales, kWh, costos).
- El sistema AGREGARÁ AUTOMÁTICAMENTE una carga cada vez que hagas una 
  reserva exitosa, simulando una recarga real.

PESTAÑA: 💳 PAGOS (Métodos de Pago)
- Puedes guardar tus tarjetas o métodos de pago para futuras transacciones.
- Para agregar: Elige el tipo (Visa, Mastercard, etc.), escribe el número enmascarado 
  (ej: **** **** **** 1234) y haz clic en "Guardar método".

PESTAÑA: 📅 RESERVAS (Mis Reservas)
- Aquí gestionas todas tus reservas de estaciones.
- Para hacer una nueva reserva:
  1. Escribe el ID o nombre de la estación.
  2. Selecciona la fecha y hora de INICIO.
  3. Selecciona la fecha y hora de FIN.
  4. Haz clic en "Crear reserva".
- Las reservas activas aparecerán listadas aquí, y podrás cancelarlas si lo deseas.

PESTAÑA: 👤 PERFIL
- Aquí ves un resumen de tu cuenta: total de cargas realizadas y kWh consumidos.
- También verás un resumen de tus reservas activas.

5. EL DASHBOARD DEL ADMINISTRADOR (admin.html)

Si inicias sesión con la cuenta de administrador, aparecerá un enlace 
"⚙ Admin" en el menú lateral del Mapa. Al hacer clic, entrarás al panel 
de control de Terpel.

CREDENCIALES DEL ADMIN:
- Usuario: terpel@evcharge.co
- Contraseña: 123456

Dentro del Admin Dashboard encontrarás estas secciones en el menú de la izquierda:

- 📊 RESUMEN: Vista rápida de cuántos usuarios, reportes y calificaciones hay en el sistema.
- 👤 USUARIOS: Lista de todos los usuarios registrados. Puedes buscar por nombre o correo.
- 📢 REPORTES: Lista de problemas reportados por la comunidad. Puedes filtrar por "Pendientes" o 
  "Resueltos". Si un reporte está solucionado, haces clic en "Resolver" y desaparece de la lista.
- 📍 ESTACIONES: Aquí el Admin puede agregar estaciones propias (ej: estaciones de Terpel). 
  Llenas el formulario (Nombre, ubicación, conector, potencia) y haces clic en "Guardar estación".
  También puedes cambiar el estado de una estación (Disponible / Mantenimiento).
- 📋 GESTIÓN DE RESERVAS: El Admin ve TODAS las reservas de todos los usuarios. 
  Puede filtrarlas por estado (Activas/Canceladas) y cancelar o eliminar cualquier reserva.


6. FUNCIONALIDADES 

- FILTRO AUTOMÁTICO: Registra un vehículo con conector "CCS" en la pestaña "Auto". 
  Ve al mapa y mira cómo el filtro se selecciona solo y te muestra estaciones compatibles.

- CREAR RESERVA Y CARGA AUTOMÁTICA: Ve a la pestaña "Reservas", crea una reserva. 
  Luego ve a la pestaña "Cargas" y verás que el sistema ha generado automáticamente 
  una entrada con kWh aleatorios y un costo estimado.

- PLANIFICADOR DE VIAJE: En el mapa, usa el botón "🧭 Planificador". Pon las coordenadas 
  de origen y destino (puedes usar la ubicación actual con el botón "Usar mi ubicación"). 
  El sistema calculará la ruta y te mostrará las paradas de carga necesarias en el mapa.

------------------------------------------------------------
7. CIERRE DE SESIÓN
------------------------------------------------------------
Para salir de la aplicación, busca el botón "Salir" o "Cerrar sesión" en la 
parte superior derecha de la pantalla (en el Topbar) o en la parte inferior 
del menú lateral en el caso del Admin.
