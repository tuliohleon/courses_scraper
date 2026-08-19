# Scraper de Cursos

Script en Python para extraer información de grupos y cupos de cursos desde la plataforma.

## Descripción

El script lee una lista de URLs de inscripción desde un archivo CSV y, para cada una, obtiene:
- Los grupos disponibles (curso, país, idioma, horario, días, etc.)
- El estado de cupos (total y disponible) mediante una consulta adicional a la API

## Requisitos

- Python 3.8 o superior
- Librería `requests` (instalar con `pip install requests`)

## Uso

1. Crea o edita el archivo `urls.csv` con una columna `url` (o la primera columna del archivo) conteniendo las URLs de inscripción, una por línea.

2. Ejecuta el script:

```bash
python scraper.py
```

3. Los resultados se guardan en `cursos_scrapeados.csv`.

## Estructura de salida

El CSV resultante contiene las siguientes columnas:

| Columna | Descripción |
|---------|-------------|
| `convocatoria` | Identificador de convocatoria (parte 1 de la URL) |
| `tema_id` | Identificador del tema (parte 2 de la URL) |
| `periodo` | Período (parte 3 de la URL) |
| `curso` | Nombre del curso |
| `pais` | País del curso |
| `idioma` | Idioma |
| `idGrupo` | Identificador del grupo |
| `codigoGrupo` | Código del grupo |
| `dias` | Días de clase (separados por coma) |
| `horario` | Horario de clase |
| `zonaHoraria` | Zona horaria |
| `tipoGrupo` | Tipo de grupo |
| `cupoTotal` | Cupo total del grupo |
| `cupoDisponible` | Cupo disponible |
| `tieneCupos` | "Sí" o "No" según haya cupos disponibles |

## Notas

- El script incluye un delay de 1.5 segundos entre requests para respetar al servidor.