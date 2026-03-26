import json
import random
from datetime import datetime, timedelta

random.seed(42)

# ── Gerar dados fictícios ──────────────────────────────────────────────────────
def gerar_dados():
    hoje = datetime.now()
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    # Receita vs Despesa mensal
    receitas  = [random.randint(45000, 95000) for _ in range(12)]
    despesas  = [int(r * random.uniform(0.55, 0.80)) for r in receitas]
    lucros    = [r - d for r, d in zip(receitas, despesas)]

    # Série temporal de saldo (últimos 30 dias)
    saldo = 128_450.00
    historico = []
    for i in range(30):
        saldo += random.uniform(-3200, 5100)
        historico.append({"dia": i + 1, "saldo": round(saldo, 2)})

    # Categorias de despesa
    categorias = {
        "Pessoal":       random.randint(18000, 28000),
        "Operacional":   random.randint(12000, 20000),
        "Marketing":     random.randint(6000,  14000),
        "Tecnologia":    random.randint(4000,  10000),
        "Infraestrutura":random.randint(3000,   8000),
        "Outros":        random.randint(2000,   5000),
    }

    # Transações recentes
    descricoes = [
        ("Venda Produto A", "receita"),
        ("Fornecedor XYZ",  "despesa"),
        ("Assinatura SaaS", "despesa"),
        ("Serviços B2B",    "receita"),
        ("Folha de Pagamento", "despesa"),
        ("Consultoria",    "receita"),
        ("Aluguel",        "despesa"),
        ("Licença Software","despesa"),
        ("Parceria Comercial","receita"),
        ("Manutenção",     "despesa"),
    ]
    transacoes = []
    for i, (desc, tipo) in enumerate(descricoes):
        d = hoje - timedelta(days=i * 2 + random.randint(0, 1))
        valor = random.randint(800, 25000) * (1 if tipo == "receita" else -1)
        transacoes.append({
            "data": d.strftime("%d/%m"),
            "descricao": desc,
            "tipo": tipo,
            "valor": valor,
        })

    # KPIs
    receita_total  = sum(receitas)
    despesa_total  = sum(despesas)
    lucro_total    = sum(lucros)
    margem         = round((lucro_total / receita_total) * 100, 1)

    return {
        "meses": meses,
        "receitas": receitas,
        "despesas": despesas,
        "lucros": lucros,
        "historico": historico,
        "categorias": categorias,
        "transacoes": transacoes,
        "kpis": {
            "receita_total": receita_total,
            "despesa_total": despesa_total,
            "lucro_total": lucro_total,
            "margem": margem,
        },
    }


dados = gerar_dados()

def fmt(n):
    return f"R$ {abs(n):,.0f}".replace(",", ".")


HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Dashboard Financeiro</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
  :root {{
    --bg:        #0a0d14;
    --surface:   #111520;
    --border:    #1e2535;
    --accent:    #00e5a0;
    --accent2:   #4f7cff;
    --accent3:   #ff6b6b;
    --text:      #e8eaf0;
    --muted:     #5a6280;
    --green:     #00e5a0;
    --red:       #ff5c7a;
    --radius:    16px;
  }}

  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: "DM Sans", sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 32px 40px;
    overflow-x: hidden;
  }}

  /* Fundo com textura sutil */
  body::before {{
    content: "";
    position: fixed; inset: 0;
    background:
      radial-gradient(ellipse 80% 40% at 10% 0%, rgba(0,229,160,.06) 0%, transparent 60%),
      radial-gradient(ellipse 60% 50% at 90% 100%, rgba(79,124,255,.07) 0%, transparent 60%);
    pointer-events: none; z-index: 0;
  }}

  .wrapper {{ position: relative; z-index: 1; max-width: 1400px; margin: 0 auto; }}

  /* ── Header ─────────────────────────────────────────── */
  header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 40px;
  }}
  .logo-area h1 {{
    font-family: "Syne", sans-serif;
    font-weight: 800; font-size: 26px; letter-spacing: -.5px;
    color: #fff;
  }}
  .logo-area h1 span {{ color: var(--accent); }}
  .logo-area p {{ color: var(--muted); font-size: 13px; margin-top: 2px; }}

  .header-right {{
    display: flex; align-items: center; gap: 16px;
  }}
  .badge {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 100px; padding: 8px 18px;
    font-size: 13px; color: var(--muted);
  }}
  .badge strong {{ color: var(--text); }}
  .dot {{ width: 8px; height: 8px; border-radius: 50%;
    background: var(--green); display: inline-block;
    margin-right: 6px; box-shadow: 0 0 8px var(--green); }}

  /* ── KPI Cards ──────────────────────────────────────── */
  .kpi-grid {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
    margin-bottom: 28px;
  }}
  .kpi-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    position: relative; overflow: hidden;
    transition: transform .2s, border-color .2s;
  }}
  .kpi-card:hover {{ transform: translateY(-3px); border-color: #2a3350; }}
  .kpi-card::after {{
    content: "";
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,.02) 0%, transparent 60%);
    pointer-events: none;
  }}
  .kpi-label {{
    font-size: 11px; font-weight: 500; letter-spacing: 1.2px;
    text-transform: uppercase; color: var(--muted); margin-bottom: 12px;
  }}
  .kpi-value {{
    font-family: "Syne", sans-serif; font-size: 28px; font-weight: 700;
    color: #fff; line-height: 1;
  }}
  .kpi-sub {{
    font-size: 12px; color: var(--muted); margin-top: 8px;
  }}
  .kpi-badge {{
    display: inline-block; padding: 3px 10px;
    border-radius: 100px; font-size: 11px; font-weight: 600;
    margin-top: 10px;
  }}
  .up {{ background: rgba(0,229,160,.12); color: var(--green); }}
  .down {{ background: rgba(255,92,122,.12); color: var(--red); }}

  .kpi-accent-line {{
    position: absolute; left: 0; top: 0; bottom: 0;
    width: 3px; border-radius: 0 2px 2px 0;
  }}

  /* ── Chart Grid ─────────────────────────────────────── */
  .chart-grid {{
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 16px; margin-bottom: 16px;
  }}
  .chart-grid-2 {{
    display: grid;
    grid-template-columns: 1.2fr 1.8fr;
    gap: 16px; margin-bottom: 16px;
  }}

  .card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
  }}
  .card-header {{
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 20px;
  }}
  .card-title {{
    font-family: "Syne", sans-serif;
    font-size: 14px; font-weight: 700; color: var(--text);
    letter-spacing: -.2px;
  }}
  .card-sub {{ font-size: 11px; color: var(--muted); margin-top: 2px; }}

  .legend {{
    display: flex; gap: 16px; align-items: center;
    font-size: 11px; color: var(--muted);
  }}
  .legend-dot {{
    width: 8px; height: 8px; border-radius: 2px; display: inline-block;
    margin-right: 5px;
  }}

  canvas {{ max-width: 100%; }}

  /* ── Transações ─────────────────────────────────────── */
  .tx-list {{ display: flex; flex-direction: column; gap: 10px; }}
  .tx-item {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 14px;
    background: rgba(255,255,255,.025);
    border: 1px solid var(--border);
    border-radius: 10px;
    transition: background .15s;
  }}
  .tx-item:hover {{ background: rgba(255,255,255,.04); }}
  .tx-left {{ display: flex; align-items: center; gap: 12px; }}
  .tx-icon {{
    width: 36px; height: 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
  }}
  .tx-icon.in  {{ background: rgba(0,229,160,.1); }}
  .tx-icon.out {{ background: rgba(255,92,122,.1); }}
  .tx-name {{ font-size: 13px; font-weight: 500; color: var(--text); }}
  .tx-date {{ font-size: 11px; color: var(--muted); margin-top: 1px; }}
  .tx-amount {{ font-family: "Syne", sans-serif; font-size: 14px; font-weight: 600; }}
  .tx-amount.in  {{ color: var(--green); }}
  .tx-amount.out {{ color: var(--red); }}

  /* ── Responsivo ─────────────────────────────────────── */
  @media (max-width: 1100px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .chart-grid, .chart-grid-2 {{ grid-template-columns: 1fr; }}
  }}
  @media (max-width: 600px) {{
    body {{ padding: 20px 16px; }}
    .kpi-grid {{ grid-template-columns: 1fr 1fr; }}
    .header-right {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="wrapper">

  <!-- Header -->
  <header>
    <div class="logo-area">
      <h1>Finance<span>OS</span></h1>
      <p>Painel de Controle Financeiro · {datetime.now().strftime("%B %Y")}</p>
    </div>
    <div class="header-right">
      <div class="badge"><span class="dot"></span>Atualizado agora</div>
      <div class="badge">Ano Fiscal <strong>2024</strong></div>
    </div>
  </header>

  <!-- KPIs -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-accent-line" style="background:var(--green)"></div>
      <div class="kpi-label">Receita Total</div>
      <div class="kpi-value">{fmt(dados["kpis"]["receita_total"])}</div>
      <div class="kpi-sub">Acumulado 12 meses</div>
      <span class="kpi-badge up">▲ +14,2%</span>
    </div>
    <div class="kpi-card">
      <div class="kpi-accent-line" style="background:var(--red)"></div>
      <div class="kpi-label">Despesa Total</div>
      <div class="kpi-value">{fmt(dados["kpis"]["despesa_total"])}</div>
      <div class="kpi-sub">Acumulado 12 meses</div>
      <span class="kpi-badge down">▲ +8,7%</span>
    </div>
    <div class="kpi-card">
      <div class="kpi-accent-line" style="background:var(--accent2)"></div>
      <div class="kpi-label">Lucro Líquido</div>
      <div class="kpi-value">{fmt(dados["kpis"]["lucro_total"])}</div>
      <div class="kpi-sub">Resultado consolidado</div>
      <span class="kpi-badge up">▲ +22,5%</span>
    </div>
    <div class="kpi-card">
      <div class="kpi-accent-line" style="background:#f0b429"></div>
      <div class="kpi-label">Margem Líquida</div>
      <div class="kpi-value">{dados["kpis"]["margem"]}%</div>
      <div class="kpi-sub">Sobre receita bruta</div>
      <span class="kpi-badge up">▲ Meta atingida</span>
    </div>
  </div>

  <!-- Chart Row 1 -->
  <div class="chart-grid">
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Receita vs Despesa</div>
          <div class="card-sub">Comparativo mensal 2024</div>
        </div>
        <div class="legend">
          <span><span class="legend-dot" style="background:var(--green)"></span>Receita</span>
          <span><span class="legend-dot" style="background:var(--red)"></span>Despesa</span>
        </div>
      </div>
      <canvas id="barChart" height="220"></canvas>
    </div>
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Categorias de Gasto</div>
          <div class="card-sub">Distribuição percentual</div>
        </div>
      </div>
      <canvas id="doughnutChart" height="220"></canvas>
    </div>
  </div>

  <!-- Chart Row 2 -->
  <div class="chart-grid-2">
    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Últimas Transações</div>
          <div class="card-sub">10 movimentações recentes</div>
        </div>
      </div>
      <div class="tx-list">
        {''.join([
            f'''<div class="tx-item">
              <div class="tx-left">
                <div class="tx-icon {'in' if t['tipo']=='receita' else 'out'}">
                  {'💰' if t['tipo']=='receita' else '💸'}
                </div>
                <div>
                  <div class="tx-name">{t['descricao']}</div>
                  <div class="tx-date">{t['data']}</div>
                </div>
              </div>
              <div class="tx-amount {'in' if t['tipo']=='receita' else 'out'}">
                {'+ ' if t['tipo']=='receita' else '− '}{fmt(t['valor'])}
              </div>
            </div>'''
            for t in dados["transacoes"]
        ])}
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <div>
          <div class="card-title">Evolução do Saldo</div>
          <div class="card-sub">Últimos 30 dias</div>
        </div>
      </div>
      <canvas id="lineChart" height="310"></canvas>
    </div>
  </div>

</div><!-- /wrapper -->

<script>
const C = {{
  green:  '#00e5a0',
  red:    '#ff5c7a',
  blue:   '#4f7cff',
  yellow: '#f0b429',
  muted:  '#5a6280',
  grid:   '#1e2535',
  text:   '#e8eaf0',
}};

Chart.defaults.color = C.muted;
Chart.defaults.font.family = "'DM Sans', sans-serif";

const tooltipPlugin = {{
  backgroundColor: '#111520',
  titleColor: C.text,
  bodyColor: C.muted,
  borderColor: '#2a3350',
  borderWidth: 1,
  padding: 12,
  cornerRadius: 10,
}};

// ── Bar Chart ────────────────────────────────────────────
const barCtx = document.getElementById('barChart').getContext('2d');
new Chart(barCtx, {{
  type: 'bar',
  data: {{
    labels: {json.dumps(dados["meses"])},
    datasets: [
      {{
        label: 'Receita',
        data: {json.dumps(dados["receitas"])},
        backgroundColor: 'rgba(0,229,160,.2)',
        borderColor: C.green,
        borderWidth: 1.5,
        borderRadius: 6,
        borderSkipped: false,
      }},
      {{
        label: 'Despesa',
        data: {json.dumps(dados["despesas"])},
        backgroundColor: 'rgba(255,92,122,.15)',
        borderColor: C.red,
        borderWidth: 1.5,
        borderRadius: 6,
        borderSkipped: false,
      }},
    ],
  }},
  options: {{
    responsive: true,
    interaction: {{ mode: 'index', intersect: false }},
    plugins: {{ legend: {{ display: false }}, tooltip: tooltipPlugin }},
    scales: {{
      x: {{ grid: {{ color: C.grid }}, ticks: {{ font: {{ size: 11 }} }} }},
      y: {{
        grid: {{ color: C.grid }},
        ticks: {{
          font: {{ size: 11 }},
          callback: v => 'R$' + (v/1000).toFixed(0) + 'k',
        }},
      }},
    }},
  }},
}});

// ── Doughnut Chart ───────────────────────────────────────
const dCtx = document.getElementById('doughnutChart').getContext('2d');
const catLabels = {json.dumps(list(dados["categorias"].keys()))};
const catValues = {json.dumps(list(dados["categorias"].values()))};
const catColors = [C.green, C.blue, C.yellow, '#a78bfa', '#fb923c', C.muted];
new Chart(dCtx, {{
  type: 'doughnut',
  data: {{
    labels: catLabels,
    datasets: [{{
      data: catValues,
      backgroundColor: catColors.map(c => c + '99'),
      borderColor: catColors,
      borderWidth: 1.5,
      hoverOffset: 8,
    }}],
  }},
  options: {{
    responsive: true,
    cutout: '68%',
    plugins: {{
      legend: {{
        position: 'bottom',
        labels: {{ boxWidth: 10, padding: 14, font: {{ size: 11 }} }},
      }},
      tooltip: tooltipPlugin,
    }},
  }},
}});

// ── Line Chart ───────────────────────────────────────────
const lCtx = document.getElementById('lineChart').getContext('2d');
const grad = lCtx.createLinearGradient(0, 0, 0, 320);
grad.addColorStop(0,   'rgba(79,124,255,.25)');
grad.addColorStop(1,   'rgba(79,124,255,0)');

const dias   = {json.dumps([h["dia"]    for h in dados["historico"]])};
const saldos = {json.dumps([h["saldo"] for h in dados["historico"]])};

new Chart(lCtx, {{
  type: 'line',
  data: {{
    labels: dias.map(d => 'Dia ' + d),
    datasets: [{{
      label: 'Saldo',
      data: saldos,
      borderColor: C.blue,
      borderWidth: 2.5,
      pointRadius: 0,
      pointHoverRadius: 5,
      fill: true,
      backgroundColor: grad,
      tension: 0.4,
    }}],
  }},
  options: {{
    responsive: true,
    interaction: {{ mode: 'index', intersect: false }},
    plugins: {{ legend: {{ display: false }}, tooltip: tooltipPlugin }},
    scales: {{
      x: {{
        grid: {{ color: C.grid }},
        ticks: {{ font: {{ size: 10 }}, maxTicksLimit: 8 }},
      }},
      y: {{
        grid: {{ color: C.grid }},
        ticks: {{
          font: {{ size: 11 }},
          callback: v => 'R$' + (v/1000).toFixed(0) + 'k',
        }},
      }},
    }},
  }},
}});
</script>
</body>
</html>
"""

output_path = "/mnt/user-data/outputs/dashboard_financeiro.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(HTML)

print(f"✅ Dashboard gerado em: {output_path}")
print(f"   Tamanho: {len(HTML):,} bytes")
