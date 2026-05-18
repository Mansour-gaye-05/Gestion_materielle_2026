with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = """new Chart(document.getElementById('evolutionChart'), {
    type: 'line',
    data: { labels: {{ jours_labels|safe }}, datasets: [
        { label: 'Valides', data: {{ emprunts_valides_jour|safe }}, borderColor: '#2c3e50', backgroundColor: 'rgba(44,62,80,0.1)', fill: true, tension: 0.3, pointRadius: 3 },
        { label: 'En cours', data: {{ emprunts_encours_jour|safe }}, borderColor: '#e67e22', backgroundColor: 'rgba(230,126,34,0.05)', fill: false, tension: 0.3, pointRadius: 3 }
    ]},
    options: { responsive: true, plugins: { legend: { position: 'top' } }, scales: { y: { beginAtZero: true } } }
});"""

new = """new Chart(document.getElementById('evolutionChart'), {
    type: 'line',
    data: {
        labels: {{ jours_labels|safe }},
        datasets: [
            {
                label: 'Demandes validees',
                data: {{ emprunts_valides_jour|safe }},
                borderColor: '#2c3e50',
                backgroundColor: 'rgba(44,62,80,0.15)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#2c3e50',
                pointHoverRadius: 7,
                borderWidth: 3
            },
            {
                label: 'Emprunts en cours',
                data: {{ emprunts_encours_jour|safe }},
                borderColor: '#e67e22',
                backgroundColor: 'rgba(230,126,34,0.08)',
                fill: false,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: '#e67e22',
                pointHoverRadius: 7,
                borderWidth: 2,
                borderDash: [5, 3]
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: { position: 'top', labels: { usePointStyle: true, padding: 20 } },
            tooltip: {
                mode: 'index',
                intersect: false,
                callbacks: {
                    label: function(ctx) { return ctx.dataset.label + ': ' + ctx.parsed.y + ' emprunt(s)'; }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: { stepSize: 1, precision: 0 },
                grid: { color: 'rgba(0,0,0,0.05)' },
                title: { display: true, text: 'Nombre d emprunts', font: { size: 11 } }
            },
            x: {
                grid: { display: false },
                ticks: { maxRotation: 45, font: { size: 10 } }
            }
        },
        interaction: { mode: 'nearest', axis: 'x', intersect: false }
    }
});"""

if old in content:
    content = content.replace(old, new)
    print('Chart remplace!')
else:
    import re
    content = re.sub(
        r"new Chart\(document\.getElementById\('evolutionChart'\).*?\}\);",
        new,
        content,
        flags=re.DOTALL
    )
    print('Chart remplace par regex!')

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
