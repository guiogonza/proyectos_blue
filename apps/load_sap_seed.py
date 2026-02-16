#!/usr/bin/env python3
"""Seed script: Carga datos SAP desde CSV."""
import csv, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from domain.services import sap_service

CSV_PATH = os.path.join(os.path.dirname(__file__), "sap_seed.csv")

def main():
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: No se encontró {CSV_PATH}")
        sys.exit(1)
    
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    print(f"Filas leidas del CSV: {len(rows)}")
    parsed = sap_service.parse_csv_rows(rows, anio=2026)
    print(f"Filas parseadas: {len(parsed)}")
    
    count = sap_service.bulk_upsert(parsed)
    print(f"Filas insertadas/actualizadas en BD: {count}")
    print("Done!")

if __name__ == "__main__":
    main()
