-- Base de datos para la API de Reservas
DROP DATABASE IF EXISTS reservas_db;
CREATE DATABASE reservas_db;
USE reservas_db;

-- NUEVA TABLA: Define los roles de la aplicación
CREATE TABLE roles (
    id INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

INSERT INTO roles (id, nombre) VALUES
(1, 'Admin'),
(2, 'Cliente');

-- TABLA MODIFICADA: Ahora incluye una columna 'rol_id'
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- NUEVA COLUMNA: Por defecto es 2 (Cliente)
    rol_id INT NOT NULL DEFAULT 2, 
    
    -- NUEVA LLAVE FORÁNEA: Conecta usuarios con roles
    FOREIGN KEY (rol_id) REFERENCES roles(id)
);

-- Tabla para almacenar las reservas (sin cambios)
CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tour_id INT NOT NULL, 
    usuario_id INT,
    fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cantidad_personas INT NOT NULL,
    costo_total DECIMAL(10, 2) NOT NULL,
    estado ENUM('Pendiente', 'Confirmada', 'Cancelada') NOT NULL DEFAULT 'Pendiente',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

INSERT INTO usuarios (id, nombre, email, password) VALUES
(101, 'Ana Pérez', 'ana.perez@email.com', '$2b$12$0TPh9qxvO5hO1wVjVHZ.beiYi8AkScl2UOEdGf7xqYlZghWhq7NHW'),
(102, 'Juan Rodríguez', 'juan.rodriguez@email.com', '$2b$12$wHHKAhXLbDtSBqTkDgGuFujk8OjGHEGnEsF1kTQ11MwUZTBzgCHsm'),
(103, 'Lucía Gómez', 'lucia.gomez@email.com', '$2b$12$46VNCjur9AUrVEsBOFK98eW0xeZj51UzMycXGSHcy97gYO6i22HD2'),
(104, 'Manuel Fernandez', 'mf@email.com', '$2b$12$Nw4DS/O2gygau6nA6.hVq.iBb92wk4m1KRY/gDuKydT52nPt62M52'),
(105, 'Jose Montenegro', 'jm@email.com', '$2b$12$nKqWAcjelSXRZ9UJDsev7.w21/J1LDU0xwjbVrmJ0510BAMC1Qv6a');

INSERT INTO reservas (tour_id, usuario_id, cantidad_personas, costo_total, estado) VALUES
(1, 101, 2, 300000.00, 'Confirmada'),
(3, 102, 1, 350000.00, 'Confirmada'),
(2, 101, 4, 380000.00, 'Pendiente'),
(7, 103, 2, 500000.00, 'Confirmada'),
(10, 102, 3, 360000.00, 'Cancelada'),
(5, 104, 1, 1400000.00, 'Confirmada'),
(8, 105, 3, 330000.00, 'Confirmada'),
(11, 101, 2, 180000.00, 'Confirmada'),
(15, 104, 4, 240000.00, 'Pendiente'),
(6, 102, 2, 150000.00, 'Confirmada'),
(14, 103, 2, 200000.00, 'Cancelada'),   
(1, 105, 1, 150000.00, 'Confirmada');