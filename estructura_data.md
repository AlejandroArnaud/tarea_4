# Análisis de la Estructura del Dataset OULAD para MySQL

Este documento detalla el diseño del esquema de la base de datos para el dataset OULAD, optimizado para MySQL. Se analizan las tablas, se definen los tipos de datos, y se establecen las llaves primarias y foráneas para garantizar la integridad referencial.

## Consideraciones Generales

1.  **Valores Nulos (`?`)**: En varios archivos, el carácter `?` se utiliza para representar datos faltantes. En el esquema de la base de datos, estos campos se definirán como `NULL` para manejar la ausencia de datos de manera estándar.
2.  **Fechas como Enteros**: Las columnas de fecha (`date`, `date_registration`, `date_unregistration`, `date_submitted`) no son fechas calendario, sino números enteros que representan el número de días transcurridos desde el inicio del módulo/presentación. Por lo tanto, se utilizará el tipo de dato `INT`.
3.  **Llaves Compuestas**: Varias tablas no tienen un único identificador, sino que su unicidad depende de la combinación de varias columnas. Estas se implementarán como llaves primarias compuestas.

---

## Análisis por Tabla

### 1. `courses` (Cursos)

Tabla maestra que define cada presentación de un módulo.

-   **Columnas:**
    -   `code_module` (VARCHAR(20)): Identificador del módulo (ej. 'AAA').
    -   `code_presentation` (VARCHAR(20)): Identificador de la presentación (ej. '2013J').
    -   `module_presentation_length` (INT): Duración de la presentación en días.
-   **Llave Primaria (PK):** Compuesta por `(code_module, code_presentation)`. Esta combinación identifica de manera única cada curso impartido en un semestre específico.

### 2. `studentInfo` (Información del Estudiante)

Contiene la información demográfica de cada estudiante.

-   **Columnas:**
    -   `id_student` (INT): Identificador único para cada estudiante.
    -   `gender` (CHAR(1)): Género del estudiante ('M' o 'F').
    -   `region` (VARCHAR(255)): Región del estudiante.
    -   `highest_education` (VARCHAR(255)): Nivel educativo más alto.
    -   `imd_band` (VARCHAR(50)): Banda del Índice de Múltiple Privación (puede ser `NULL`).
    -   `age_band` (VARCHAR(50)): Rango de edad.
    -   `num_of_prev_attempts` (INT): Número de intentos previos en otros módulos.
    -   `studied_credits` (INT): Créditos estudiados por el estudiante.
    -   `disability` (CHAR(1)): Indica si el estudiante tiene una discapacidad ('Y' o 'N').
    -   `final_result` (VARCHAR(50)): Resultado final del estudiante en la presentación.
-   **Llave Primaria (PK):** `id_student`.

*Nota: Las columnas `code_module` y `code_presentation` aparecen en el snippet `studentInfo.csv` pero conceptualmente pertenecen a la tabla de registro (`studentRegistration`). Las mantendremos separadas para un mejor diseño normalizado.*

### 3. `assessments` (Evaluaciones)

Define cada evaluación dentro de una presentación de un módulo.

-   **Columnas:**
    -   `id_assessment` (INT): Identificador único de la evaluación.
    -   `code_module` (VARCHAR(20)): FK que referencia a `courses`.
    -   `code_presentation` (VARCHAR(20)): FK que referencia a `courses`.
    -   `assessment_type` (VARCHAR(10)): Tipo de evaluación (ej. 'TMA', 'Exam').
    -   `date` (INT): Fecha de la evaluación en días desde el inicio (puede ser `NULL`).
    -   `weight` (DECIMAL(5, 2)): Ponderación de la evaluación sobre la nota final (ej. 10.00, 20.00).
-   **Llave Primaria (PK):** `id_assessment`.
-   **Llave Foránea (FK):** `(code_module, code_presentation)` referencia a `courses(code_module, code_presentation)`.

### 4. `vle` (Entorno Virtual de Aprendizaje)

Contiene la información sobre los materiales disponibles en el Entorno Virtual de Aprendizaje (VLE).

-   **Columnas:**
    -   `id_site` (INT): Identificador único del material/sitio en el VLE.
    -   `code_module` (VARCHAR(20)): FK que referencia a `courses`.
    -   `code_presentation` (VARCHAR(20)): FK que referencia a `courses`.
    -   `activity_type` (VARCHAR(50)): Tipo de actividad (ej. 'resource', 'oucontent').
    -   `week_from` (INT): Semana de inicio de disponibilidad (puede ser `NULL`).
    -   `week_to` (INT): Semana de fin de disponibilidad (puede ser `NULL`).
-   **Llave Primaria (PK):** `id_site`.
-   **Llave Foránea (FK):** `(code_module, code_presentation)` referencia a `courses(code_module, code_presentation)`.

### 5. `studentRegistration` (Registro de Estudiantes)

Tabla de unión que vincula a un estudiante con una presentación de módulo específica.

-   **Columnas:**
    -   `id_student` (INT): FK que referencia a `studentInfo`.
    -   `code_module` (VARCHAR(20)): FK que referencia a `courses`.
    -   `code_presentation` (VARCHAR(20)): FK que referencia a `courses`.
    -   `date_registration` (INT): Fecha de registro en días (un valor negativo significa antes del inicio).
    -   `date_unregistration` (INT): Fecha de baja en días (puede ser `NULL`).
-   **Llave Primaria (PK):** Compuesta por `(id_student, code_module, code_presentation)`.
-   **Llaves Foráneas (FK):**
    -   `id_student` referencia a `studentInfo(id_student)`.
    -   `(code_module, code_presentation)` referencia a `courses(code_module, code_presentation)`.

### 6. `studentAssessment` (Evaluaciones de Estudiantes)

Tabla de unión que almacena los resultados de las evaluaciones para cada estudiante.

-   **Columnas:**
    -   `id_assessment` (INT): FK que referencia a `assessments`.
    -   `id_student` (INT): FK que referencia a `studentInfo`.
    -   `date_submitted` (INT): Fecha de entrega de la evaluación.
    -   `is_banked` (TINYINT): Bandera que indica si la nota fue transferida de un intento previo (0 o 1).
    -   `score` (INT): Puntuación obtenida por el estudiante (puede ser `NULL`).
-   **Llave Primaria (PK):** Compuesta por `(id_assessment, id_student)`.
-   **Llaves Foráneas (FK):**
    -   `id_assessment` referencia a `assessments(id_assessment)`.
    -   `id_student` referencia a `studentInfo(id_student)`.

### 7. `studentVle` (Interacción del Estudiante con el VLE)

Registra las interacciones (clics) de un estudiante con los materiales del VLE.

-   **Columnas:**
    -   **`id_interaction` (INT AUTO_INCREMENT):** Se añade una llave primaria subrogada (artificial) porque no hay una combinación de columnas que garantice la unicidad (un estudiante puede hacer clic en el mismo sitio varias veces el mismo día).
    -   `id_student` (INT): FK que referencia a `studentInfo`.
    -   `id_site` (INT): FK que referencia a `vle`.
    -   `code_module` (VARCHAR(20)): Dato presente en el CSV, redundante si se une con `vle`.
    -   `code_presentation` (VARCHAR(20)): Dato presente en el CSV, redundante si se une con `vle`.
    -   `date` (INT): Fecha de la interacción en días.
    -   `sum_click` (INT): Número de clics en esa interacción.
-   **Llave Primaria (PK):** `id_interaction`.
-   **Llaves Foráneas (FK):**
    -   `id_student` referencia a `studentInfo(id_student)`.
    -   `id_site` referencia a `vle(id_site)`.