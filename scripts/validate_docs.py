#!/usr/bin/env python3
"""
Script de validacion de documentacion del proyecto ISO 27001 Evaluator.
Ejecutar antes de cada commit para asegurar consistencia.
"""

import sys
from pathlib import Path

CURRENT_VERSION = "1.4.1"
DOCS_PATH = Path("docs")
CRITICAL_FILES = [
    "ARCHITECTURE.md",
    "CONFIG_REGISTRY.md",
    "CHANGELOG.md",
    "MASTER_DIAGRAM.md",
    "EXPLICACION_IA.md",
]

print("=" * 70)
print("VALIDACION DE DOCUMENTACION - ISO 27001 Evaluator")
print(f"Version objetivo: v{CURRENT_VERSION}")
print("=" * 70)
print()

all_ok = True

# 1. Verificar archivos criticos
print("1. Verificando archivos criticos:")
for doc_name in CRITICAL_FILES:
    filepath = DOCS_PATH / doc_name
    if filepath.exists():
        print(f"   [OK] {doc_name}")
    else:
        print(f"   [ERROR] {doc_name} no existe")
        all_ok = False

print()

# 2. Verificar versiones
print("2. Verificando versiones:")
for doc_name in ["ARCHITECTURE.md", "CONFIG_REGISTRY.md"]:
    filepath = DOCS_PATH / doc_name
    if filepath.exists():
        content = filepath.read_text(encoding="utf-8")
        if f"Version: {CURRENT_VERSION}" in content or f"v{CURRENT_VERSION}" in content:
            print(f"   [OK] {doc_name}: Version {CURRENT_VERSION} encontrada")
        else:
            print(f"   [WARN] {doc_name}: No se encontro version {CURRENT_VERSION}")
            all_ok = False

print()

# 3. Verificar CHANGELOG
print("3. Verificando CHANGELOG:")
changelog_path = DOCS_PATH / "CHANGELOG.md"
if changelog_path.exists():
    content = changelog_path.read_text(encoding="utf-8")
    if f"[v{CURRENT_VERSION}]" in content:
        print(f"   [OK] CHANGELOG tiene entry para v{CURRENT_VERSION}")
    else:
        print(f"   [WARN] CHANGELOG no tiene entry para v{CURRENT_VERSION}")

print()
print("=" * 70)
if all_ok:
    print("RESULTADO: DOCUMENTACION VALIDADA CORRECTAMENTE")
    sys.exit(0)
else:
    print("RESULTADO: REVISAR PUNTOS ANTERIORES")
    sys.exit(1)
