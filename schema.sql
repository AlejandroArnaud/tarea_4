-- =================================================================
-- Script DDL para la creación de la base de datos OULAD en MySQL
-- =================================================================

-- Deshabilitar la verificación de llaves foráneas temporalmente para permitir la creación de tablas en cualquier orden.
SET FOREIGN_KEY_CHECKS=0;

--
-- Tabla: courses
-- Tabla maestra para las presentaciones de los módulos.
--
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses` (
  `code_module` VARCHAR(20) NOT NULL,
  `code_presentation` VARCHAR(20) NOT NULL,
  `module_presentation_length` INT NOT NULL,
  PRIMARY KEY (`code_module`, `code_presentation`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Tabla: studentInfo
-- Información demográfica de los estudiantes.
--
DROP TABLE IF EXISTS `studentInfo`;
CREATE TABLE `studentInfo` (
  `id_student` INT NOT NULL,
  `gender` CHAR(1) NOT NULL,
  `region` VARCHAR(255) NOT NULL,
  `highest_education` VARCHAR(255) NOT NULL,
  `imd_band` VARCHAR(50) NULL, -- Puede contener '?' que se cargará como NULL
  `age_band` VARCHAR(50) NOT NULL,
  `num_of_prev_attempts` INT NOT NULL,
  `studied_credits` INT NOT NULL,
  `disability` CHAR(1) NOT NULL,
  `final_result` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`id_student`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Tabla: assessments
-- Información sobre las evaluaciones.
--
DROP TABLE IF EXISTS `assessments`;
CREATE TABLE `assessments` (
  `id_assessment` INT NOT NULL,
  `code_module` VARCHAR(20) NOT NULL,
  `code_presentation` VARCHAR(20) NOT NULL,
  `assessment_type` VARCHAR(10) NOT NULL,
  `date` INT NULL, -- Puede contener '?'
  `weight` DECIMAL(5,2) NOT NULL,
  PRIMARY KEY (`id_assessment`),
  CONSTRAINT `fk_assessments_courses` FOREIGN KEY (`code_module`, `code_presentation`) REFERENCES `courses` (`code_module`, `code_presentation`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Tabla: vle (Virtual Learning Environment)
-- Información sobre los materiales del VLE.
--
DROP TABLE IF EXISTS `vle`;
CREATE TABLE `vle` (
  `id_site` INT NOT NULL,
  `code_module` VARCHAR(20) NOT NULL,
  `code_presentation` VARCHAR(20) NOT NULL,
  `activity_type` VARCHAR(50) NOT NULL,
  `week_from` INT NULL,
  `week_to` INT NULL,
  PRIMARY KEY (`id_site`),
  CONSTRAINT `fk_vle_courses` FOREIGN KEY (`code_module`, `code_presentation`) REFERENCES `courses` (`code_module`, `code_presentation`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Tabla: studentRegistration
-- Tabla de unión entre estudiantes y cursos.
--
DROP TABLE IF EXISTS `studentRegistration`;
CREATE TABLE `studentRegistration` (
  `id_student` INT NOT NULL,
  `code_module` VARCHAR(20) NOT NULL,
  `code_presentation` VARCHAR(20) NOT NULL,
  `date_registration` INT NULL,
  `date_unregistration` INT NULL, -- Puede contener '?'
  PRIMARY KEY (`id_student`, `code_module`, `code_presentation`),
  CONSTRAINT `fk_registration_student` FOREIGN KEY (`id_student`) REFERENCES `studentInfo` (`id_student`),
  CONSTRAINT `fk_registration_courses` FOREIGN KEY (`code_module`, `code_presentation`) REFERENCES `courses` (`code_module`, `code_presentation`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Tabla: studentAssessment
-- Resultados de las evaluaciones de los estudiantes.
--
DROP TABLE IF EXISTS `studentAssessment`;
CREATE TABLE `studentAssessment` (
  `id_assessment` INT NOT NULL,
  `id_student` INT NOT NULL,
  `date_submitted` INT NOT NULL,
  `is_banked` TINYINT NOT NULL,
  `score` INT NULL, -- El score puede estar nulo si no se entregó
  PRIMARY KEY (`id_assessment`, `id_student`),
  CONSTRAINT `fk_studentassessment_assessment` FOREIGN KEY (`id_assessment`) REFERENCES `assessments` (`id_assessment`),
  CONSTRAINT `fk_studentassessment_student` FOREIGN KEY (`id_student`) REFERENCES `studentInfo` (`id_student`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Tabla: studentVle
-- Interacciones de los estudiantes con los materiales del VLE.
-- Se añade una PK artificial 'id_interaction' porque no hay una llave natural única.
--
DROP TABLE IF EXISTS `studentVle`;
CREATE TABLE `studentVle` (
  `id_interaction` BIGINT NOT NULL AUTO_INCREMENT, -- Llave subrogada para unicidad
  `id_student` INT NOT NULL,
  `id_site` INT NOT NULL,
  `date` INT NOT NULL,
  `sum_click` INT NOT NULL,
  PRIMARY KEY (`id_interaction`),
  CONSTRAINT `fk_studentvle_student` FOREIGN KEY (`id_student`) REFERENCES `studentInfo` (`id_student`),
  CONSTRAINT `fk_studentvle_vle` FOREIGN KEY (`id_site`) REFERENCES `vle` (`id_site`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Habilitar la verificación de llaves foráneas nuevamente.
SET FOREIGN_KEY_CHECKS=1;