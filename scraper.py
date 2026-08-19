import csv
import json
import requests
import time
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://campus.fimlm.org/",
    "Origin": "https://campus.fimlm.org",
}

GRUPOS_URL = "https://campus.fimlm.org/mock/grupos/{insc}_tema_{tema}_periodo_{periodo}.json"
CUPOS_URL = "https://registros.fimlm.org/api/convocatorias/horarios-grupos-convocatoria"


def extraer_parametros(url):
    parsed = urlparse(url)
    partes = parsed.path.strip('/').split('/')
    if len(partes) >= 4 and partes[0] == 'inscripcion':
        return {'insc': partes[1], 'tema': partes[2], 'periodo': partes[3]}
    return None


def obtener_grupos(insc, tema, periodo):
    url = GRUPOS_URL.format(insc=insc, tema=tema, periodo=periodo)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  ⚠️ Error grupos: {e}")
        return None


def obtener_cupos(ids_grupos):
    if not ids_grupos:
        return {}
    try:
        resp = requests.post(
            CUPOS_URL,
            headers={**HEADERS, "Content-Type": "application/json"},
            json={"grupos": ids_grupos},
            timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "success":
            return {item["id_curso_grupo"]: item for item in data["data"]}
        return {}
    except Exception as e:
        print(f"  ⚠️ Error cupos: {e}")
        return {}


def scrape_curso(url):
    params = extraer_parametros(url)
    if not params:
        print(f"  ⚠️ URL no válida: {url}")
        return []

    print(f"\n📚 {url}")
    cursos_data = obtener_grupos(params['insc'], params['tema'], params['periodo'])
    if not cursos_data:
        return []

    resultados = []
    for curso in cursos_data:
        nombre_curso = curso.get("curso", "").strip()
        grupos = curso.get("grupos", [])
        if not grupos:
            continue

        ids_grupos = [g["id_grupo"] for g in grupos]
        cupos_map = obtener_cupos(ids_grupos)

        for grupo in grupos:
            id_grupo = grupo.get("id_grupo")
            cupo_info = cupos_map.get(id_grupo, {})
            dias_raw = grupo.get("dias", [])
            dias = ", ".join(dias_raw) if isinstance(dias_raw, list) else str(dias_raw)

            resultados.append({
                "url": url,
                "convocatoria": params['insc'],
                "tema_id": params['tema'],
                "periodo": params['periodo'],
                "curso": nombre_curso,
                "pais": curso.get("pai_nombre", ""),
                "idioma": curso.get("respuesta", ""),
                "id_grupo": id_grupo,
                "codigo_grupo": grupo.get("nombre", ""),
                "dias": dias,
                "horario": grupo.get("horario", ""),
                "zona_horaria": grupo.get("variable_inicial", ""),
                "tipo_grupo": grupo.get("tipo_grupo", ""),
                "cupo_total": cupo_info.get("cupo", grupo.get("cupo", "")),
                "cupo_disponible": cupo_info.get("cupo_disponible", grupo.get("cupo_disponible", "")),
                "tiene_cupos": "Sí" if cupo_info.get("cupo_disponible", 0) > 0 else "No",
            })
    return resultados


def main():
    INPUT_CSV = "urls.csv"          # ← Cambia esto por tu archivo
    OUTPUT_CSV = "cursos_scrapeados.csv"

    urls = []
    try:
        with open(INPUT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                url_col = "url" if "url" in reader.fieldnames else reader.fieldnames[0]
                urls = [row[url_col].strip() for row in reader if row[url_col].strip()]
            else:
                f.seek(0)
                urls = [line.strip() for line in f if line.strip()]
        print(f"✅ {len(urls)} URLs leídas")
    except FileNotFoundError:
        print(f"❌ No se encontró '{INPUT_CSV}'")
        return

    todos = []
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}]")
        todos.extend(scrape_curso(url))
        if i < len(urls):
            time.sleep(1.5)

    if todos:
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "url", "convocatoria", "tema_id", "periodo", "curso", "pais", "idioma",
                "id_grupo", "codigo_grupo", "dias", "horario", "zona_horaria",
                "tipo_grupo", "cupo_total", "cupo_disponible", "tiene_cupos"
            ])
            writer.writeheader()
            writer.writerows(todos)
        print(f"\n🎉 {len(todos)} registros guardados en '{OUTPUT_CSV}'")


if __name__ == "__main__":
    main()