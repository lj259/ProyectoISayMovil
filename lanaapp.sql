<<<<<<< Updated upstream
-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 01-07-2025 a las 20:39:09
-- Versión del servidor: 8.0.30
-- Versión de PHP: 8.3.11

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `lanaapp`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

=======

-- Creación de la base de datos y selección
CREATE DATABASE IF NOT EXISTS `lanaapp`
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci;
USE `lanaapp`;

-- Tabla usuarios
DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id`                INT            NOT NULL AUTO_INCREMENT,
  `nombre_usuario`    VARCHAR(50)    NOT NULL,
  `correo`            VARCHAR(100)   NOT NULL,
  `contraseña`   VARCHAR(255)   NOT NULL,
  `telefono`          VARCHAR(20)    DEFAULT NULL,
  `esta_activo`       TINYINT(1)     DEFAULT '1',
  `fecha_creacion`    TIMESTAMP      NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_usuario_nombre` (`nombre_usuario`),
  UNIQUE KEY `uq_usuario_correo` (`correo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


ALTER TABLE usuarios
  CHANGE COLUMN `contraseña` `contraseña` VARCHAR(255) NOT NULL;

-- Tabla categorías
DROP TABLE IF EXISTS `categorias`;
>>>>>>> Stashed changes
CREATE TABLE `categorias` (
  `id` int NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `tipo` enum('ingreso','gasto') NOT NULL,
  `usuario_id` int DEFAULT NULL,
  `es_predeterminada` tinyint(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

<<<<<<< Updated upstream
-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notificaciones`
--

=======
-- Tabla notificaciones
DROP TABLE IF EXISTS `notificaciones`;
>>>>>>> Stashed changes
CREATE TABLE `notificaciones` (
  `id` int NOT NULL,
  `usuario_id` int NOT NULL,
  `tipo` enum('correo','sms') NOT NULL,
  `asunto` varchar(100) NOT NULL,
  `mensaje` text NOT NULL,
  `fue_enviada` tinyint(1) DEFAULT '0',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_programada` timestamp NULL DEFAULT NULL,
  `fecha_envio` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

<<<<<<< Updated upstream
-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pagos_fijos`
--

=======
-- Tabla pagos_fijos
DROP TABLE IF EXISTS `pagos_fijos`;
>>>>>>> Stashed changes
CREATE TABLE `pagos_fijos` (
  `id` int NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `monto` float DEFAULT NULL,
  `fecha` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

<<<<<<< Updated upstream
-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `presupuestos`
--

=======
-- Tabla presupuestos
DROP TABLE IF EXISTS `presupuestos`;
>>>>>>> Stashed changes
CREATE TABLE `presupuestos` (
  `id` int NOT NULL,
  `usuario_id` int NOT NULL,
  `categoria_id` int NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `ano` int NOT NULL,
  `mes` int NOT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

<<<<<<< Updated upstream
-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `transacciones`
--

=======
-- Tabla transacciones
DROP TABLE IF EXISTS `transacciones`;
>>>>>>> Stashed changes
CREATE TABLE `transacciones` (
  `id` int NOT NULL,
  `usuario_id` int NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `categoria_id` int NOT NULL,
  `tipo` enum('ingreso','gasto') NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `fecha` date NOT NULL,
  `es_recurrente` tinyint(1) DEFAULT '0',
  `id_recurrente` int DEFAULT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

<<<<<<< Updated upstream
-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int NOT NULL,
  `nombre_usuario` varchar(50) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `contraseña_hash` varchar(255) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `esta_activo` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `pagos_fijos`
--
ALTER TABLE `pagos_fijos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_pagos_fijos_descripcion` (`descripcion`),
  ADD KEY `ix_pagos_fijos_id` (`id`);

--
-- Indices de la tabla `presupuestos`
--
ALTER TABLE `presupuestos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `usuario_id` (`usuario_id`,`categoria_id`,`mes`),
  ADD KEY `categoria_id` (`categoria_id`);

--
-- Indices de la tabla `transacciones`
--
ALTER TABLE `transacciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `categoria_id` (`categoria_id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre_usuario` (`nombre_usuario`),
  ADD UNIQUE KEY `correo` (`correo`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `pagos_fijos`
--
ALTER TABLE `pagos_fijos`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `presupuestos`
--
ALTER TABLE `presupuestos`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `transacciones`
--
ALTER TABLE `transacciones`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD CONSTRAINT `categorias_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `presupuestos`
--
ALTER TABLE `presupuestos`
  ADD CONSTRAINT `presupuestos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  ADD CONSTRAINT `presupuestos_ibfk_2` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`);

--
-- Filtros para la tabla `transacciones`
--
ALTER TABLE `transacciones`
  ADD CONSTRAINT `transacciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  ADD CONSTRAINT `transacciones_ibfk_2` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
=======
-- Datos de ejemplo
INSERT INTO `usuarios` (`nombre_usuario`,`correo`,`contraseña_hash`,`telefono`,`esta_activo`)
VALUES
 ('juanperez','juan.perez@lanaapp.com','$2b$10$EjemploHash1','555-1234',1),
 ('mariagonzalez','maria.gonzalez@lanaapp.com','$2b$10$EjemploHash2','555-5678',1);

INSERT INTO `categorias` (`nombre`,`tipo`,`usuario_id`,`es_predeterminada`)
VALUES
 ('Salario','ingreso',1,1),
 ('Freelance','ingreso',1,0),
 ('Alquiler','gasto',1,1),
 ('Compras','gasto',1,0),
 ('Beca','ingreso',2,1),
 ('Transporte','gasto',2,1);

INSERT INTO `notificaciones` (`usuario_id`,`tipo`,`asunto`,`mensaje`,`fue_enviada`,`fecha_programada`)
VALUES
 (1,'correo','Recordatorio presupuesto','Tu presupuesto mensual está por vencer.',0,'2025-07-05 09:00:00'),
 (2,'sms','Pago fijo próximo','No olvides tu pago fijo de suscripción.',0,'2025-07-10 18:00:00');

INSERT INTO `pagos_fijos` (`descripcion`,`monto`,`fecha`,`usuario_id`)
VALUES
 ('Netflix',159.00,'2025-07-15',1),
 ('Spotify',79.99,'2025-07-20',1),
 ('Suscripción gimnasio',299.50,'2025-07-05',2);

INSERT INTO `presupuestos` (`usuario_id`,`categoria_id`,`monto`,`ano`,`mes`)
VALUES
 (1,3,1200.00,2025,7),
 (1,4,500.00,2025,7),
 (2,6,300.00,2025,7);

INSERT INTO `transacciones` (`usuario_id`,`monto`,`categoria_id`,`tipo`,`descripcion`,`fecha`,`es_recurrente`)
VALUES
 (1,2500.00,1,'ingreso','Pago de nómina julio','2025-07-01',0),
 (1,75.50,4,'gasto','Supermercado','2025-07-03',0),
 (1,159.00,2,'gasto','Netflix','2025-07-15',1),
 (2,300.00,1,'gasto','Taxi mensual','2025-07-02',1);
>>>>>>> Stashed changes
