import re

with open('templates/nouvelle_demande.html', encoding='utf-8') as f:
    content = f.read()

with open('templates/nouvelle_demande.html.bak', 'w', encoding='utf-8') as f:
    f.write(content)
print('Sauvegarde creee')

pattern_dates = r'(<div class="row">\s*<div class="col-md-6 mb-3">\s*<label[^>]*>.*?Date de d[^<]*</label>\s*<input[^>]*date_debut[^>]*>\s*</div>\s*<div class="col-md-6 mb-3">\s*<label[^>]*>.*?Date de fin[^<]*</label>\s*<input[^>]*date_fin[^>]*>\s*</div>\s*</div>)'

new_dates = '''<div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-semibold"><i class="fas fa-calendar-alt me-1"></i> Date de debut *</label>
                                <input type="date" name="date_debut" id="date_debut" class="form-control" required onchange="checkConflict()">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-semibold"><i class="fas fa-clock me-1"></i> Heure de debut *</label>
                                <input type="time" name="heure_debut" id="heure_debut" class="form-control" required value="08:00">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-semibold"><i class="fas fa-calendar-alt me-1"></i> Date de fin *</label>
                                <input type="date" name="date_fin" id="date_fin" class="form-control" required onchange="checkConflict()">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label class="form-label fw-semibold"><i class="fas fa-clock me-1"></i> Heure de fin *</label>
                                <input type="time" name="heure_fin" id="heure_fin" class="form-control" required value="17:00">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-semibold"><i class="fas fa-cubes me-1"></i> Quantite *</label>
                            <div class="d-flex align-items-center gap-2">
                                <button type="button" class="btn btn-outline-secondary btn-sm px-3" onclick="changeQte(-1)"><i class="fas fa-minus"></i></button>
                                <input type="number" name="quantite" id="quantiteInput" class="form-control text-center fw-bold" value="1" min="1" max="10" readonly style="width:80px;font-size:1.2rem">
                                <button type="button" class="btn btn-outline-secondary btn-sm px-3" onclick="changeQte(1)"><i class="fas fa-plus"></i></button>
                                <small class="text-muted ms-2" id="qteDispoInfo"></small>
                            </div>
                        </div>'''

content_new, n = re.subn(pattern_dates, new_dates, content, flags=re.DOTALL)
print(f'Section dates: {n} remplacement(s)')

content_new, n2 = re.subn(
    r'<button type="submit"[^>]*id="submitBtn"[^>]*>.*?</button>',
    '''<div class="d-flex gap-2 mt-3">
                            <a href="{% url 'espace_etudiant' %}" class="btn btn-outline-secondary w-50 py-2" style="border-radius:10px">
                                <i class="fas fa-times me-2"></i> Annuler
                            </a>
                            <button type="submit" class="btn btn-custom w-50 py-2" id="submitBtn" style="border-radius:10px">
                                <i class="fas fa-paper-plane me-2"></i> Envoyer
                            </button>
                        </div>''',
    content_new, flags=re.DOTALL
)
print(f'Bouton submit: {n2} remplacement(s)')

js_quantite = '''
function changeQte(delta) {
    const input = document.getElementById('quantiteInput');
    const opt = document.getElementById('materielSelect').options[document.getElementById('materielSelect').selectedIndex];
    const maxDispo = parseInt(opt.getAttribute('data-quantite')) || 10;
    let val = Math.max(1, Math.min(parseInt(input.value) + delta, maxDispo));
    input.value = val;
}
document.getElementById('materielSelect').addEventListener('change', function() {
    const dispo = this.options[this.selectedIndex].getAttribute('data-quantite');
    document.getElementById('quantiteInput').value = 1;
    document.getElementById('quantiteInput').max = dispo || 10;
    document.getElementById('qteDispoInfo').textContent = dispo ? 'Max : ' + dispo : '';
});
'''

marker = 'window.onload = function() {'
if marker in content_new:
    content_new = content_new.replace(marker, js_quantite + marker, 1)
    print('JS quantite: OK')

with open('templates/nouvelle_demande.html', 'w', encoding='utf-8') as f:
    f.write(content_new)
print('Fichier mis a jour!')
