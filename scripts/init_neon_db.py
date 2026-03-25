#!/usr/bin/env python3
"""
Script para inicializar la base de datos PostgreSQL en Neon.
Uso: python scripts/init_neon_db.py
"""

import os
import sys


def main():
    # Connection string de Neon (production - QA)
    DATABASE_URL = os.environ.get(
        "DATABASE_URL",
        "postgresql://neondb_owner:npg_PhU0gVlXJ5yW@ep-cold-forest-acp1td9k-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require",
    )

    print(f"Conectando a Neon PostgreSQL...")
    print(
        f"URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configurada'}"
    )

    try:
        from sqlmodel import create_engine, SQLModel
        from app.models import (
            User,
            Client,
            Evaluation,
            Norma,
            ControlDefinition,
            ControlResponse,
            Session as UserSession,
            AuditLog,
            Document,
            DocumentVersion,
            RFC,
            Sprint,
            SprintTask,
            BibliotecaDocument,
        )

        engine = create_engine(DATABASE_URL, echo=True)

        print("\nCreando tablas...")
        SQLModel.metadata.create_all(engine)

        print("\nTablas creadas exitosamente!")
        print("\nTablas disponibles:")
        for table in SQLModel.metadata.tables:
            print(f"  - {table}")

    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
