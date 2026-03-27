"""
Comparativa de Evaluaciones - Sprint 2.2
Permite comparar 2+ evaluaciones de la misma norma para ver evolución
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from app.models import Evaluation, ControlResponse, ControlDefinition, Norma, Client
from app.auth import get_current_user
from typing import List

router = APIRouter(prefix="/reports", tags=["comparison"])


@router.get("/comparison")
def comparison_tool(request: Request):
    """Herramienta de comparativa de evaluaciones"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    with Session(engine) as session:
        # Obtener evaluaciones del usuario
        if user.role.value == "superadmin":
            evaluations = session.exec(select(Evaluation)).all()
        else:
            evaluations = session.exec(
                select(Evaluation).where(Evaluation.client_id == user.client_id)
            ).all()

        # Agrupar por norma
        by_norma = {}
        for eval in evaluations:
            norma = session.get(Norma, eval.norma_id) if eval.norma_id else None
            norma_name = norma.name if norma else "Sin Norma"
            if norma_name not in by_norma:
                by_norma[norma_name] = []
            by_norma[norma_name].append(eval)

        return HTMLResponse(render_comparison_tool(by_norma, user))


def render_comparison_tool(by_norma, user):
    """Renderizar herramienta de comparativa"""

    # Selector de normas con evaluaciones
    norma_options = ""
    for norma_name, evals in by_norma.items():
        if len(evals) >= 2:  # Solo mostrar si hay 2+ evaluaciones
            norma_options += f'<option value="{norma_name}">{norma_name} ({len(evals)} evaluaciones)</option>'

    if not norma_options:
        norma_options = '<option value="">No hay normas con 2+ evaluaciones</option>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Comparativa de Evaluaciones</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
        .comparison-container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .selector-section {{ background: #f9fafb; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; }}
        .evaluation-selector {{ display: flex; gap: 1rem; margin: 1rem 0; }}
        .evaluation-selector select {{ flex: 1; }}
        .comparison-results {{ display: none; }}
        .comparison-card {{ background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e5e7eb; margin-bottom: 1.5rem; }}
        .progress-comparison {{ display: flex; gap: 2rem; margin: 2rem 0; }}
        .progress-item {{ flex: 1; text-align: center; }}
        .progress-bar-container {{ width: 100%; height: 24px; background: #e5e7eb; border-radius: 12px; overflow: hidden; margin: 1rem 0; }}
        .progress-bar-fill {{ height: 100%; transition: width 0.5s ease; }}
        .improvement {{ color: #10b981; font-weight: 600; }}
        .regression {{ color: #ef4444; font-weight: 600; }}
        .control-detail {{ margin: 1rem 0; padding: 1rem; background: #f9fafb; border-radius: 8px; }}
        .control-comparison {{ display: flex; align-items: center; gap: 1rem; margin: 0.5rem 0; }}
        .maturity-badge {{ display: inline-block; width: 32px; height: 32px; border-radius: 50%; text-align: center; line-height: 32px; color: white; font-weight: 600; }}
        .maturity-0 {{ background: #6b7280; }}
        .maturity-1 {{ background: #ef4444; }}
        .maturity-2 {{ background: #f59e0b; }}
        .maturity-3 {{ background: #3b82f6; }}
        .maturity-4 {{ background: #10b981; }}
        .maturity-5 {{ background: #059669; }}
        </style>
    </head>
    <body>
        <div class="comparison-container">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2rem;">
                <h1>📊 Comparativa de Evaluaciones</h1>
                <a href="/dashboard" class="btn btn-outline">Volver</a>
            </div>
            
            <div class="selector-section">
                <h2>1. Seleccionar Norma</h2>
                <select id="norma-select" onchange="loadEvaluations()">
                    {norma_options}
                </select>
                
                <div class="evaluation-selector">
                    <div>
                        <label>Evaluación Anterior</label>
                        <select id="eval-1"></select>
                    </div>
                    <div>
                        <label>Evaluación Reciente</label>
                        <select id="eval-2"></select>
                    </div>
                </div>
                
                <button class="btn btn-primary" onclick="compareEvaluations()">
                    <i class="fa-solid fa-arrow-right-arrow-left"></i> Comparar
                </button>
            </div>
            
            <div id="comparison-results" class="comparison-results">
                <div class="comparison-card">
                    <h2>2. Resumen de Comparativa</h2>
                    <div class="progress-comparison">
                        <div class="progress-item">
                            <h3 id="eval1-name"></h3>
                            <div class="progress-bar-container">
                                <div id="eval1-bar" class="progress-bar-fill"></div>
                            </div>
                            <p>Score: <strong id="eval1-score"></strong></p>
                        </div>
                        <div class="progress-item">
                            <h3 id="eval2-name"></h3>
                            <div class="progress-bar-container">
                                <div id="eval2-bar" class="progress-bar-fill"></div>
                            </div>
                            <p>Score: <strong id="eval2-score"></strong></p>
                        </div>
                    </div>
                    <div style="text-align:center;margin:2rem 0;">
                        <h2 id="improvement-text"></h2>
                    </div>
                </div>
                
                <div class="comparison-card">
                    <h2>3. Detalle por Control</h2>
                    <div id="control-details"></div>
                </div>
                
                <div class="comparison-card">
                    <h2>4. Gráfico de Evolución</h2>
                    <canvas id="comparisonChart"></canvas>
                </div>
            </div>
        </div>
        
        <script>
        let chartInstance = null;
        
        function loadEvaluations() {{
            const normaName = document.getElementById('norma-select').value;
            // Simulación - en producción cargar desde backend
            console.log('Cargando evaluaciones para:', normaName);
        }}
        
        function compareEvaluations() {{
            const eval1Id = document.getElementById('eval-1').value;
            const eval2Id = document.getElementById('eval-2').value;
            
            if (!eval1Id || !eval2Id) {{
                alert('Seleccionar ambas evaluaciones');
                return;
            }}
            
            // Mostrar resultados
            document.getElementById('comparison-results').style.display = 'block';
            
            // Simular datos para demo
            setTimeout(() => {{
                const score1 = 65;
                const score2 = 78;
                const improvement = score2 - score1;
                
                document.getElementById('eval1-name').textContent = 'Evaluación 1';
                document.getElementById('eval2-name').textContent = 'Evaluación 2';
                
                document.getElementById('eval1-bar').style.width = score1 + '%';
                document.getElementById('eval1-bar').style.background = score1 >= 70 ? '#10b981' : score1 >= 40 ? '#f59e0b' : '#ef4444';
                document.getElementById('eval1-score').textContent = score1 + '%';
                
                document.getElementById('eval2-bar').style.width = score2 + '%';
                document.getElementById('eval2-bar').style.background = score2 >= 70 ? '#10b981' : score2 >= 40 ? '#f59e0b' : '#ef4444';
                document.getElementById('eval2-score').textContent = score2 + '%';
                
                const improvementText = improvement >= 0 ? 
                    '✅ Mejora del ' + improvement + '%' : 
                    '❌ Retroceso del ' + Math.abs(improvement) + '%';
                document.getElementById('improvement-text').textContent = improvementText;
                document.getElementById('improvement-text').className = improvement >= 0 ? 'improvement' : 'regression';
                
                renderChart(score1, score2);
            }}, 100);
        }}
        
        function renderChart(score1, score2) {{
            const ctx = document.getElementById('comparisonChart').getContext('2d');
            
            if (chartInstance) {{
                chartInstance.destroy();
            }}
            
            chartInstance = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Evaluación 1', 'Evaluación 2'],
                    datasets: [{{
                        label: 'Score de Cumplimiento',
                        data: [score1, score2],
                        backgroundColor: ['#f59e0b', '#10b981'],
                        borderColor: ['#d97706', '#059669'],
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            display: true
                        }}
                    }}
                }}
            }});
        }}
        </script>
    </body>
    </html>
    """


@router.get("/comparison/data/{eval1_id}/{eval2_id}")
def comparison_data(eval1_id: str, eval2_id: str, request: Request):
    """Datos JSON para comparativa"""
    session_id = request.cookies.get("session_id")
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    with Session(engine) as session:
        eval1 = session.get(Evaluation, eval1_id)
        eval2 = session.get(Evaluation, eval2_id)

        if not eval1 or not eval2:
            raise HTTPException(status_code=404, detail="Evaluaciones no encontradas")

        # Obtener respuestas de ambas evaluaciones
        responses1 = session.exec(
            select(ControlResponse).where(ControlResponse.evaluation_id == eval1_id)
        ).all()

        responses2 = session.exec(
            select(ControlResponse).where(ControlResponse.evaluation_id == eval2_id)
        ).all()

        # Calcular scores
        def calc_score(responses):
            if not responses:
                return 0
            total = sum(r.maturity for r in responses if not r.not_applicable)
            count = len([r for r in responses if not r.not_applicable])
            return (total / count * 100) if count > 0 else 0

        score1 = calc_score(responses1)
        score2 = calc_score(responses2)

        improvement = score2 - score1

        return {
            {
                "eval1": {
                    {
                        "id": eval1.id,
                        "name": eval1.name,
                        "score": round(score1, 2),
                        "date": eval1.created_at.strftime("%Y-%m-%d"),
                    }
                },
                "eval2": {
                    {
                        "id": eval2.id,
                        "name": eval2.name,
                        "score": round(score2, 2),
                        "date": eval2.created_at.strftime("%Y-%m-%d"),
                    }
                },
                "improvement": round(improvement, 2),
                "improvement_percent": round(
                    (improvement / score1 * 100) if score1 > 0 else 0, 2
                ),
            }
        }
