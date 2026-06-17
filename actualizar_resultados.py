import requests
import json
import base64
import re
import os
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USER = "CM123789"
GITHUB_REPO = "Mundial2026v2"
ARCHIVO_HTML = "index.html"

headers_gh = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ============================================================
# RESULTADOS CONOCIDOS DEL MUNDIAL 2026
# Se actualiza manualmente aquí después de cada jornada
# ============================================================
RESULTADOS = {
    "México-Sudáfrica": "2-0",
    "Corea del Sur-Chequia": "2-1",
    "Estados Unidos-Paraguay": "4-1",
    "Australia-Turquía": "2-0",
    "Brasil-Marruecos": "1-1",
    "Haití-Escocia": "0-1",
    "Qatar-Suiza": "1-1",
}

def obtener_html_github():
    """Descarga el HTML actual de GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{ARCHIVO_HTML}"
    r = requests.get(url, headers=headers_gh)
    if r.status_code == 200:
        data = r.json()
        contenido = base64.b64decode(data["content"]).decode("utf-8")
        sha = data["sha"]
        return contenido, sha
    else:
        print(f"❌ Error al obtener HTML: {r.status_code}")
        return None, None

def actualizar_resultados_en_html(html):
    """Actualiza los resultados en el JS del HTML"""
    for partido, resultado in RESULTADOS.items():
        local, visitante = partido.split("-", 1)
        # Buscar el partido en el JS y actualizar res:null por el resultado real
        patron = rf'({{g:"[A-L]",l:"{re.escape(local)}",v:"{re.escape(visitante)}"[^}}]+?res:)(null|"[^"]*")'
        reemplazo = rf'\1"{resultado} ✅"'
        nuevo_html = re.sub(patron, reemplazo, html)
        if nuevo_html != html:
            print(f"  ✅ Actualizado: {local} vs {visitante} → {resultado}")
            html = nuevo_html
        else:
            print(f"  ⚠️  No encontrado: {local} vs {visitante}")
    return html

def subir_html_github(html, sha):
    """Sube el HTML actualizado a GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{ARCHIVO_HTML}"
    contenido_b64 = base64.b64encode(html.encode("utf-8")).decode("utf-8")
    payload = {
        "message": f"🤖 Auto-update resultados Mundial 2026 - {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "content": contenido_b64,
        "sha": sha
    }
    r = requests.put(url, headers=headers_gh, json=payload)
    if r.status_code in [200, 201]:
        print(f"\n✅ GitHub actualizado exitosamente!")
        print(f"   Ver en: https://{GITHUB_USER.lower()}.github.io/{GITHUB_REPO}/")
    else:
        print(f"❌ Error al subir: {r.status_code} - {r.text}")

def agregar_resultado(local, visitante, goles_local, goles_visitante):
    """Agrega un nuevo resultado al diccionario y actualiza GitHub"""
    key = f"{local}-{visitante}"
    RESULTADOS[key] = f"{goles_local}-{goles_visitante}"
    print(f"➕ Agregado: {local} {goles_local}-{goles_visitante} {visitante}")

def main():
    print("=" * 55)
    print("🌍 ACTUALIZADOR AUTOMÁTICO - MUNDIAL 2026")
    print("=" * 55)
    print(f"\n📋 Resultados a actualizar: {len(RESULTADOS)}")
    for k, v in RESULTADOS.items():
        print(f"   {k}: {v}")
    
    print("\n📥 Descargando HTML de GitHub...")
    html, sha = obtener_html_github()
    if not html:
        return
    
    print("\n🔄 Actualizando resultados en el HTML...")
    html_nuevo = actualizar_resultados_en_html(html)
    
    print("\n📤 Subiendo a GitHub...")
    subir_html_github(html_nuevo, sha)
    
    print("\n" + "=" * 55)
    print("🏆 ¡Listo! Tu web se actualiza en ~2 minutos")
    print("=" * 55)

if __name__ == "__main__":
    main()
