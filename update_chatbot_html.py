with open('templates/chatbot.html', 'w', encoding='utf-8') as f:
    f.write("""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assistant IA - UFR Sciences</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: #f0f2f5; }
        .bg-custom { background-color: #2c3e50 !important; }
        .chat-container { height: 480px; overflow-y: auto; background: #f8f9fa; border-radius: 12px; padding: 15px; scroll-behavior: smooth; }
        .message-user { background: #2c3e50; color: white; padding: 10px 15px; border-radius: 18px 18px 4px 18px; margin: 8px 0; max-width: 75%; float: right; clear: both; font-size: 0.9rem; }
        .message-bot { background: white; color: #333; padding: 12px 15px; border-radius: 18px 18px 18px 4px; margin: 8px 0; max-width: 80%; float: left; clear: both; font-size: 0.9rem; box-shadow: 0 1px 4px rgba(0,0,0,0.08); white-space: pre-line; }
        .message-bot.mode-diagnostic { border-left: 4px solid #e74c3c; }
        .message-bot.mode-suggestion { border-left: 4px solid #27ae60; }
        .message-bot.mode-procedure { border-left: 4px solid #3498db; }
        .mode-badge { font-size: 0.65rem; padding: 2px 7px; border-radius: 10px; margin-bottom: 4px; display: inline-block; }
        .mode-diagnostic .mode-badge { background: #fde8e8; color: #e74c3c; }
        .mode-suggestion .mode-badge { background: #e8f8e8; color: #27ae60; }
        .mode-procedure .mode-badge { background: #e8f0fe; color: #3498db; }
        .mode-general .mode-badge { background: #f0f0f0; color: #666; }
        .typing { color: #999; font-style: italic; font-size: 0.85rem; clear: both; padding: 5px 10px; }
        .suggestion-chip { display: inline-block; margin: 3px; padding: 5px 12px; border-radius: 20px; font-size: 0.78rem; cursor: pointer; border: 1px solid #dee2e6; background: white; transition: all 0.2s; }
        .suggestion-chip:hover { background: #2c3e50; color: white; border-color: #2c3e50; }
        .suggestion-chip.chip-diagnostic { border-color: #e74c3c; color: #e74c3c; }
        .suggestion-chip.chip-diagnostic:hover { background: #e74c3c; color: white; }
        .suggestion-chip.chip-suggestion { border-color: #27ae60; color: #27ae60; }
        .suggestion-chip.chip-suggestion:hover { background: #27ae60; color: white; }
        .suggestion-chip.chip-procedure { border-color: #3498db; color: #3498db; }
        .suggestion-chip.chip-procedure:hover { background: #3498db; color: white; }
        .chat-input { border-radius: 25px; border: 2px solid #dee2e6; padding: 10px 20px; font-size: 0.9rem; }
        .chat-input:focus { border-color: #2c3e50; box-shadow: none; }
        .btn-send { border-radius: 25px; padding: 10px 22px; background: #2c3e50; border: none; color: white; }
        .btn-send:hover { background: #1a252f; }
        .mode-selector .btn { font-size: 0.8rem; border-radius: 20px; }
        .mode-active { background: #2c3e50 !important; color: white !important; }
    </style>
</head>
<body>
<nav class="navbar navbar-dark bg-custom">
    <div class="container-fluid">
        <span class="navbar-brand"><i class="fas fa-robot"></i> Assistant IA — Materiel Topographique UFR</span>
        <div class="d-flex align-items-center gap-2">
            <span class="text-white small"><i class="fas fa-user"></i> {{ user.username }}</span>
            <a href="{% url 'catalogue' %}" class="btn btn-outline-light btn-sm">Catalogue</a>
            <a href="{% url 'espace_etudiant' %}" class="btn btn-outline-light btn-sm">Mon espace</a>
        </div>
    </div>
</nav>

<div class="container mt-3">
    <div class="row justify-content-center">
        <div class="col-md-9">

            <!-- Modes -->
            <div class="card mb-3 border-0 shadow-sm">
                <div class="card-body py-2">
                    <div class="d-flex align-items-center gap-2 flex-wrap">
                        <small class="text-muted fw-bold">MODE :</small>
                        <button class="btn btn-sm btn-outline-secondary mode-btn mode-active" data-mode="general" onclick="setMode('general', this)">
                            <i class="fas fa-comment"></i> General
                        </button>
                        <button class="btn btn-sm btn-outline-danger mode-btn" data-mode="diagnostic" onclick="setMode('diagnostic', this)">
                            <i class="fas fa-stethoscope"></i> Diagnostic panne
                        </button>
                        <button class="btn btn-sm btn-outline-success mode-btn" data-mode="suggestion" onclick="setMode('suggestion', this)">
                            <i class="fas fa-lightbulb"></i> Recommandation materiel
                        </button>
                        <button class="btn btn-sm btn-outline-primary mode-btn" data-mode="procedure" onclick="setMode('procedure', this)">
                            <i class="fas fa-list-ol"></i> Procedure emprunt
                        </button>
                    </div>
                </div>
            </div>

            <!-- Chat -->
            <div class="card border-0 shadow-sm">
                <div class="card-body p-3">
                    <div class="chat-container" id="chatContainer">
                        <div class="message-bot mode-general">
                            <div class="mode-badge">Assistant UFR</div><br>
                            Bonjour {{ user.username }} ! Je suis votre assistant intelligent pour le materiel topographique.<br><br>
                            Je peux vous aider sur 4 modes :<br>
                            🔧 <strong>Diagnostic</strong> — Decrivez votre panne, je l'analyse<br>
                            💡 <strong>Recommandation</strong> — Decrivez votre mission, je recommande le materiel<br>
                            📋 <strong>Procedure</strong> — Questions sur les emprunts et restitutions<br>
                            💬 <strong>General</strong> — Toute question sur le materiel topo<br><br>
                            Comment puis-je vous aider ?
                        </div>
                    </div>

                    <!-- Suggestions dynamiques -->
                    <div class="mt-2 mb-2" id="suggestionsContainer">
                        <div id="chips-general">
                            <span class="suggestion-chip" onclick="sendSuggestion('Comment utiliser une station totale ?')">📐 Station totale</span>
                            <span class="suggestion-chip" onclick="sendSuggestion('Comment utiliser un GPS GNSS ?')">📡 GPS GNSS</span>
                            <span class="suggestion-chip" onclick="sendSuggestion('Comment faire un nivellement ?')">📏 Nivellement</span>
                            <span class="suggestion-chip" onclick="sendSuggestion('Comment transporter le materiel ?')">🚚 Transport</span>
                        </div>
                        <div id="chips-diagnostic" style="display:none">
                            <span class="suggestion-chip chip-diagnostic" onclick="sendSuggestion('Le niveau ne s allume plus')">💡 Niveau eteint</span>
                            <span class="suggestion-chip chip-diagnostic" onclick="sendSuggestion('Le GPS ne capte pas de signal')">📡 GPS sans signal</span>
                            <span class="suggestion-chip chip-diagnostic" onclick="sendSuggestion('La station totale affiche une erreur')">⚠️ Erreur station totale</span>
                            <span class="suggestion-chip chip-diagnostic" onclick="sendSuggestion('La batterie ne charge plus')">🔋 Batterie</span>
                            <span class="suggestion-chip chip-diagnostic" onclick="sendSuggestion('Les mesures sont incorrectes')">📊 Mesures incorrectes</span>
                        </div>
                        <div id="chips-suggestion" style="display:none">
                            <span class="suggestion-chip chip-suggestion" onclick="sendSuggestion('J ai besoin de materiel pour un leve topographique')">🗺️ Leve topo</span>
                            <span class="suggestion-chip chip-suggestion" onclick="sendSuggestion('Quel materiel pour une mission cadastrale ?')">📋 Cadastre</span>
                            <span class="suggestion-chip chip-suggestion" onclick="sendSuggestion('Materiel pour implantation de batiment ?')">🏗️ Implantation</span>
                            <span class="suggestion-chip chip-suggestion" onclick="sendSuggestion('Que me recommandez-vous pour du nivellement de precision ?')">📏 Nivellement precision</span>
                        </div>
                        <div id="chips-procedure" style="display:none">
                            <span class="suggestion-chip chip-procedure" onclick="sendSuggestion('Comment emprunter un materiel ?')">📦 Emprunter</span>
                            <span class="suggestion-chip chip-procedure" onclick="sendSuggestion('Comment rendre un materiel ?')">↩️ Rendre</span>
                            <span class="suggestion-chip chip-procedure" onclick="sendSuggestion('Comment signaler une panne pendant un emprunt ?')">🚨 Signaler panne</span>
                            <span class="suggestion-chip chip-procedure" onclick="sendSuggestion('Comment voir les reservations d un materiel ?')">📅 Reservations</span>
                        </div>
                    </div>

                    <!-- Input -->
                    <div class="input-group mt-2">
                        <input type="text" id="messageInput" class="form-control chat-input"
                               placeholder="Posez votre question..."
                               onkeypress="if(event.keyCode==13) sendMessage()">
                        <button class="btn btn-send ms-2" onclick="sendMessage()">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                    <div class="text-center mt-1">
                        <small class="text-muted"><i class="fas fa-robot"></i> Propulse par Groq Llama 3.3 — <span id="currentMode">Mode General</span></small>
                    </div>
                </div>
            </div>

        </div>
    </div>
</div>

<script>
let currentMode = 'general';
const modeNames = {
    general: 'Mode General',
    diagnostic: 'Mode Diagnostic Panne',
    suggestion: 'Mode Recommandation Materiel',
    procedure: 'Mode Procedure Emprunt'
};
const modeBadges = {
    general: 'Assistant UFR',
    diagnostic: '🔍 Diagnostic',
    suggestion: '💡 Recommandation',
    procedure: '📋 Procedure'
};

function setMode(mode, btn) {
    currentMode = mode;
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('mode-active'));
    btn.classList.add('mode-active');
    document.getElementById('currentMode').textContent = modeNames[mode];

    // Afficher les chips du bon mode
    ['general','diagnostic','suggestion','procedure'].forEach(m => {
        const el = document.getElementById('chips-' + m);
        if (el) el.style.display = m === mode ? 'block' : 'none';
    });

    // Message contextuel
    const hints = {
        diagnostic: 'Mode Diagnostic active. Decrivez votre panne et j\'analyserai les causes probables.',
        suggestion: 'Mode Recommandation active. Decrivez votre mission terrain et je vous recommande le materiel optimal.',
        procedure: 'Mode Procedure active. Posez vos questions sur les emprunts, restitutions et reservations.',
        general: 'Mode General active. Posez toute question sur le materiel topographique.'
    };
    addBotMessage(hints[mode], mode);
}

function addBotMessage(text, mode) {
    const container = document.getElementById('chatContainer');
    const div = document.createElement('div');
    div.className = 'message-bot mode-' + (mode || 'general');
    div.innerHTML = '<div class="mode-badge">' + (modeBadges[mode] || 'Assistant') + '</div><br>' + text.replace(/\n/g, '<br>');
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function addUserMessage(text) {
    const container = document.getElementById('chatContainer');
    const div = document.createElement('div');
    div.className = 'message-user';
    div.textContent = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function showTyping() {
    const container = document.getElementById('chatContainer');
    const div = document.createElement('div');
    div.id = 'typingIndicator';
    div.className = 'typing';
    const icons = { diagnostic: 'stethoscope', suggestion: 'lightbulb', procedure: 'list-ol', general: 'robot' };
    div.innerHTML = '<i class="fas fa-' + (icons[currentMode] || 'robot') + ' fa-pulse"></i> Analyse en cours...';
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function hideTyping() {
    const t = document.getElementById('typingIndicator');
    if (t) t.remove();
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    if (!message) return;

    addUserMessage(message);
    input.value = '';
    showTyping();

    try {
        const response = await fetch('/chatbot/message/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
            body: JSON.stringify({ message, mode: currentMode })
        });
        const data = await response.json();
        hideTyping();
        addBotMessage(data.response, data.mode || currentMode);
    } catch (error) {
        hideTyping();
        addBotMessage('Erreur de connexion. Veuillez reessayer.', 'general');
    }
}

function sendSuggestion(q) {
    document.getElementById('messageInput').value = q;
    sendMessage();
}

function getCookie(name) {
    let v = null;
    document.cookie.split(';').forEach(c => {
        c = c.trim();
        if (c.startsWith(name + '=')) v = decodeURIComponent(c.substring(name.length + 1));
    });
    return v;
}
</script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>""")
print('chatbot.html mis a jour!')
