"""
Reportes Avanzados y Dashboard de Cumplimiento
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select, func
from app.models import (
    Evaluation,
    ControlResponse,
    ControlDefinition,
    Norma,
    Client,
    User,
)
from app.auth import get_current_user, require_no_vista_solo
from app.database import engine
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/compliance/{client_id}")
def compliance_dashboard(request: Request, client_id: str):
    """Dashboard de cumplimiento por cliente"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    with Session(engine) as session:
        # Obtener cliente
        client = session.get(Client, client_id)
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Validar permisos
        if user.role.value != "superadmin" and user.client_id != client_id:
            raise HTTPException(status_code=403, detail="No autorizado")

        # Obtener todas las evaluaciones del cliente
        evaluations = session.exec(
            select(Evaluation).where(Evaluation.client_id == client_id)
        ).all()

        # Calcular métricas por norma
        norm_metrics = {}
        total_controls = 0
        total_compliant = 0
        total_non_compliant = 0
        total_in_progress = 0

        for eval in evaluations:
            norma = session.get(Norma, eval.norma_id) if eval.norma_id else None
            norma_name = norma.name if norma else "Sin Norma"

            if norma_name not in norm_metrics:
                norm_metrics[norma_name] = {
                    "total": 0,
                    "compliant": 0,
                    "non_compliant": 0,
                    "in_progress": 0,
                    "evaluations": [],
                }

            # Obtener respuestas de esta evaluación
            responses = session.exec(
                select(ControlResponse).where(ControlResponse.evaluation_id == eval.id)
            ).all()

            eval_total = len(responses)
            eval_compliant = sum(1 for r in responses if r.maturity >= 3)
            eval_non_compliant = sum(
                1 for r in responses if r.maturity < 3 and r.maturity > 0
            )
            eval_in_progress = sum(
                1 for r in responses if r.maturity == 0 or r.maturity == 1
            )

            norm_metrics[norma_name]["total"] += eval_total
            norm_metrics[norma_name]["compliant"] += eval_compliant
            norm_metrics[norma_name]["non_compliant"] += eval_non_compliant
            norm_metrics[norma_name]["in_progress"] += eval_in_progress
            norm_metrics[norma_name]["evaluations"].append(
                {
                    "name": eval.name,
                    "date": eval.created_at.strftime("%d/%m/%Y"),
                    "score": eval_compliant / eval_total * 100 if eval_total > 0 else 0,
                }
            )

            total_controls += eval_total
            total_compliant += eval_compliant
            total_non_compliant += eval_non_compliant
            total_in_progress += eval_in_progress

        # Calcular porcentaje de cumplimiento
        compliance_rate = (
            (total_compliant / total_controls * 100) if total_controls > 0 else 0
        )

        # Top 5 controles críticos (más fallidos)
        critical_controls = []
        if evaluations:
            eval_ids = [e.id for e in evaluations]
            responses_all = session.exec(
                select(ControlResponse, ControlDefinition)
                .join(
                    ControlDefinition,
                    ControlResponse.control_definition_id == ControlDefinition.id,
                )
                .where(ControlResponse.evaluation_id.in_(eval_ids))
                .where(ControlResponse.maturity < 2)
            ).all()

            control_failures = {}
            for resp, ctrl in responses_all:
                key = f"{ctrl.code} - {ctrl.title[:50]}"
                if key not in control_failures:
                    control_failures[key] = 0
                control_failures[key] += 1

            critical_controls = sorted(
                control_failures.items(), key=lambda x: x[1], reverse=True
            )[:5]

        return HTMLResponse(
            render_compliance_dashboard(
                client=client,
                norm_metrics=norm_metrics,
                total_controls=total_controls,
                total_compliant=total_compliant,
                total_non_compliant=total_non_compliant,
                total_in_progress=total_in_progress,
                compliance_rate=compliance_rate,
                critical_controls=critical_controls,
                user=user,
            )
        )


def render_compliance_dashboard(
    client,
    norm_metrics,
    total_controls,
    total_compliant,
    total_non_compliant,
    total_in_progress,
    compliance_rate,
    critical_controls,
    user,
):
    """Renderizar dashboard de cumplimiento"""

    normas_html = ""
    for norma_name, metrics in norm_metrics.items():
        score = (
            (metrics["compliant"] / metrics["total"] * 100)
            if metrics["total"] > 0
            else 0
        )
        color = "#10b981" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"

        normativas_html = f"""
        <div class="norma-card">
            <h3>{norma_name}</h3>
            <div class="score-circle" style="border-color: {color};">
                <span class="score-value" style="color: {color};">{score:.1f}%</span>
            </div>
            <div class="metrics-grid">
                <div class="metric">
                    <span class="metric-label">Controles</span>
                    <span class="metric-value">{metrics["total"]}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Conformes</span>
                    <span class="metric-value" style="color: #10b981;">{metrics["compliant"]}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">No Conformes</span>
                    <span class="metric-value" style="color: #ef4444;">{metrics["non_compliant"]}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">En Progreso</span>
                    <span class="metric-value" style="color: #f59e0b;">{metrics["in_progress"]}</span>
                </div>
            </div>
        </div>
        """
        normas_html += normativas_html

    critical_html = ""
    if critical_controls:
        critical_html = """
        <div class="critical-section">
            <h3>🔴 Controles Más Críticos</h3>
            <ol class="critical-list">
        """
        for control, count in critical_controls:
            critical_html += (
                f"<li><strong>{control}</strong> - {count} no conformidades</li>"
            )
        critical_html += "</ol></div>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard de Cumplimiento - {client.name}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
        <style>
        .dashboard {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .kpi-card {{ padding: 1.5rem; border-radius: 12px; background: linear-gradient(135deg, #f9fafb, #ffffff); border: 1px solid #e5e7eb; }}
        .kpi-value {{ font-size: 2.5rem; font-weight: 700; color: #1f2937; }}
        .kpi-label {{ color: #6b7280; font-size: 0.875rem; }}
        .normas-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }}
        .norma-card {{ background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e5e7eb; }}
        .score-circle {{ width: 120px; height: 120px; border-radius: 50%; border: 4px solid; margin: 1rem auto; display: flex; align-items: center; justify-content: center; }}
        .score-value {{ font-size: 1.5rem; font-weight: 700; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem; margin-top: 1rem; }}
        .metric {{ text-align: center; padding: 0.5rem; background: #f9fafb; border-radius: 6px; }}
        .metric-label {{ display: block; font-size: 0.75rem; color: #6b7280; }}
        .metric-value {{ display: block; font-size: 1.25rem; font-weight: 600; }}
        .critical-section {{ margin-top: 2rem; background: #fef2f2; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ef4444; }}
        .critical-list {{ margin: 1rem 0 0 1.5rem; }}
        .critical-list li {{ margin-bottom: 0.5rem; color: #991b1b; }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="header">
                <div>
                    <h1>📊 Dashboard de Cumplimiento</h1>
                    <p style="color: #6b7280;">Cliente: <strong>{client.name}</strong></p>
                </div>
                <div>
                    <a href="/dashboard" class="btn btn-outline">Volver al Dashboard</a>
                </div>
            </div>
            
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value">{total_controls}</div>
                    <div class="kpi-label">Total Controles</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value" style="color: #10b981;">{total_compliant}</div>
                    <div class="kpi-label">Conformes</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value" style="color: #ef4444;">{total_non_compliant}</div>
                    <div class="kpi-label">No Conformes</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-value" style="color: {"#10b981" if compliance_rate >= 70 else "#f59e0b" if compliance_rate >= 40 else "#ef4444"};">
                        {compliance_rate:.1f}%
                    </div>
                    <div class="kpi-label">Cumplimiento Global</div>
                </div>
            </div>
            
            <h2 style="margin: 2rem 0 1rem 0;">Cumplimiento por Norma</h2>
            <div class="normas-grid">
                {normas_html}
            </div>
            
            {critical_html}
        </div>
    </body>
    </html>
    """
