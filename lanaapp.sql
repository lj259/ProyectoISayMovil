-- --------------------------------------------------------
-- Dump corregido para LanaApp (01-07-2025)
-- --------------------------------------------------------

-- 1) Creación de la base de datos y selección
CREATE DATABASE IF NOT EXISTS lanaapp
  DEFAULT CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci;
USE lanaapp;

-- 2) Tabla usuarios
DROP TABLE IF EXISTS usuarios;
CREATE TABLE usuarios (
  id                INT            NOT NULL AUTO_INCREMENT,
  nombre_usuario    VARCHAR(50)    NOT NULL,
  correo            VARCHAR(100)   NOT NULL,
  contraseña   VARCHAR(255)   NOT NULL,
  telefono          VARCHAR(20)    DEFAULT NULL,
  esta_activo       TINYINT(1)     DEFAULT '1',
  fecha_creacion    TIMESTAMP      NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP    NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_usuario_nombre (nombre_usuario),
  UNIQUE KEY uq_usuario_correo (correo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


ALTER TABLE usuarios
  CHANGE COLUMN contraseña contraseña VARCHAR(255) NOT NULL;

-- 3) Tabla categorías
DROP TABLE IF EXISTS categorias;
CREATE TABLE categorias (
  id                INT            NOT NULL AUTO_INCREMENT,
  nombre            VARCHAR(50)    NOT NULL,
  tipo              ENUM('ingreso','gasto') NOT NULL,
  usuario_id        INT            DEFAULT NULL,
  es_predeterminada TINYINT(1)     DEFAULT '0',
  PRIMARY KEY (id),
  KEY idx_categorias_usuario (usuario_id),
  CONSTRAINT fk_categorias_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 4) Tabla notificaciones
DROP TABLE IF EXISTS notificaciones;
CREATE TABLE notificaciones (
  id               INT            NOT NULL AUTO_INCREMENT,
  usuario_id       INT            NOT NULL,
  tipo             ENUM('correo','sms') NOT NULL,
  asunto           VARCHAR(100)   NOT NULL,
  mensaje          TEXT           NOT NULL,
  fue_enviada      TINYINT(1)     DEFAULT '0',
  fecha_creacion   TIMESTAMP      NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_programada TIMESTAMP      NULL DEFAULT NULL,
  fecha_envio      TIMESTAMP      NULL DEFAULT NULL,
  PRIMARY KEY (id),
  KEY idx_notif_usuario (usuario_id),
  CONSTRAINT fk_notif_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 5) Tabla pagos_fijos
DROP TABLE IF EXISTS pagos_fijos;
CREATE TABLE pagos_fijos (
  id             INT            NOT NULL AUTO_INCREMENT,
  descripcion    VARCHAR(255)   DEFAULT NULL,
  monto          FLOAT          DEFAULT NULL,
  fecha          DATE           DEFAULT NULL,
  usuario_id     INT            NOT NULL,
  fecha_creacion TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_pagos_fijos_usuario (usuario_id),
  CONSTRAINT fk_pagos_fijos_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 6) Tabla presupuestos
DROP TABLE IF EXISTS presupuestos;
CREATE TABLE presupuestos (
  id                 INT             NOT NULL AUTO_INCREMENT,
  usuario_id         INT             NOT NULL,
  categoria_id       INT             NOT NULL,
  monto              DECIMAL(10,2)   NOT NULL,
  ano                INT             NOT NULL,
  mes                INT             NOT NULL,
  fecha_creacion     TIMESTAMP       NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP      NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_presup_usuario_cat_mes_ano (usuario_id,categoria_id,mes,ano),
  KEY idx_presup_categoria (categoria_id),
  CONSTRAINT fk_presup_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_presup_categoria FOREIGN KEY (categoria_id)
    REFERENCES categorias (id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 7) Tabla transacciones
DROP TABLE IF EXISTS transacciones;
CREATE TABLE transacciones (
  id             INT             NOT NULL AUTO_INCREMENT,
  usuario_id     INT             NOT NULL,
  monto          DECIMAL(10,2)   NOT NULL,
  categoria_id   INT             NOT NULL,
  tipo           ENUM('ingreso','gasto') NOT NULL,
  descripcion    VARCHAR(255)    DEFAULT NULL,
  fecha          DATE            NOT NULL,
  es_recurrente  TINYINT(1)      DEFAULT '0',
  id_recurrente  INT             DEFAULT NULL,
  fecha_creacion TIMESTAMP       NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_trans_usuario (usuario_id),
  KEY idx_trans_categoria (categoria_id),
  CONSTRAINT fk_trans_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_trans_categoria FOREIGN KEY (categoria_id)
    REFERENCES categorias (id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 8) Datos de ejemplo
INSERT INTO usuarios (nombre_usuario,correo,contraseña_hash,telefono,esta_activo)
VALUES
 ('juanperez','juan.perez@lanaapp.com','$2b$10$EjemploHash1','555-1234',1),
 ('mariagonzalez','maria.gonzalez@lanaapp.com','$2b$10$EjemploHash2','555-5678',1);

INSERT INTO categorias (nombre,tipo,usuario_id,es_predeterminada)
VALUES
 ('Salario','ingreso',1,1),
 ('Freelance','ingreso',1,0),
 ('Alquiler','gasto',1,1),
 ('Compras','gasto',1,0),
 ('Beca','ingreso',2,1),
 ('Transporte','gasto',2,1);

INSERT INTO notificaciones (usuario_id,tipo,asunto,mensaje,fue_enviada,fecha_programada)
VALUES
 (1,'correo','Recordatorio presupuesto','Tu presupuesto mensual está por vencer.',0,'2025-07-05 09:00:00'),
 (2,'sms','Pago fijo próximo','No olvides tu pago fijo de suscripción.',0,'2025-07-10 18:00:00');

INSERT INTO pagos_fijos (descripcion,monto,fecha,usuario_id)
VALUES
 ('Netflix',159.00,'2025-07-15',1),
 ('Spotify',79.99,'2025-07-20',1),
 ('Suscripción gimnasio',299.50,'2025-07-05',2);

INSERT INTO presupuestos (usuario_id,categoria_id,monto,ano,mes)
VALUES
 (1,3,1200.00,2025,7),
 (1,4,500.00,2025,7),
 (2,6,300.00,2025,7);

INSERT INTO transacciones (usuario_id,monto,categoria_id,tipo,descripcion,fecha,es_recurrente)
VALUES
 (1,2500.00,1,'ingreso','Pago de nómina julio','2025-07-01',0),
 (1,75.50,4,'gasto','Supermercado','2025-07-03',0),
 (1,159.00,2,'gasto','Netflix','2025-07-15',1),
 (2,300.00,1,'gasto','Taxi mensual','2025-07-02',1);