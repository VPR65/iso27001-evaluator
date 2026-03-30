-- Inicialización de Base de Datos PostgreSQL
-- Se ejecuta automáticamente al crear el contenedor

-- Extensión para UUID (si se necesita)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Nota: Las tablas se crean automáticamente por la aplicación
-- Este script es para configuraciones iniciales de la BD

-- Configurar timezone
ALTER DATABASE iso27001 SET TIMEZONE TO 'UTC';

-- Comentario para el DBA
-- Las tablas se crean via SQLModel/SQLAlchemy al iniciar la app
-- No es necesario crear tablas manualmente aquí
