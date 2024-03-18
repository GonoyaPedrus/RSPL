
document.addEventListener('DOMContentLoaded', function () {
    const players = document.querySelectorAll('.player');
    const teamSlots = document.querySelectorAll('.team-card');
    const remainingAmountSpan = document.getElementById('remaining-amount');
    const totalBudget = 1000; // Budget total disponible
    let draggedPlayer = null;
    let totalCost = 0;
    const teamIdSpan = document.getElementById('team-id');
    const teamId = generate_new_team_id();
    teamIdSpan.textContent = teamId;

    // Ajoutez des écouteurs d'événements pour les éléments glissables dans la barre latérale
    players.forEach(player => {
        player.addEventListener('dragstart', function (e) {
            draggedPlayer = e.target;
            e.target.classList.add('dragging'); // Ajouter la classe 'dragging' pendant le glisser-déposer
            e.dataTransfer.setData('text/plain', ''); // Définir un type de données pour Firefox
        });

        player.addEventListener('dragend', function (e) {
            e.target.classList.remove('dragging'); // Retirer la classe 'dragging' après le glisser-déposer
            updateTeamTotalCost(); // Mettre à jour l'argent restant après chaque glisser-déposer
        });
    });

    // Ajoutez des écouteurs d'événements pour les emplacements d'équipe
    teamSlots.forEach(slot => {
        slot.addEventListener('dragover', function (e) {
            e.preventDefault();
        });

        slot.addEventListener('drop', function (e) {
            e.preventDefault();

            // Récupérer la position de la carte cible (slot)
            const droppedPosition = slot.getAttribute('card-position');
            // Récupérer la position de la carte en cours de glissement (draggedPlayer)
            const draggedPosition = draggedPlayer.getAttribute('card-position');

            // Vérifier si les positions sont différentes
            if (droppedPosition === draggedPosition) {
                // Si les positions sont identiques, effectuer le glisser-déposer

                // Échanger les textes et le titre des cartes
                const tempPlayerTitle = Array.from(this.querySelectorAll('.card-title'));
                const tempPlayerTexts = Array.from(this.querySelectorAll('.card-text'));
                const draggedPlayerTitle = Array.from(draggedPlayer.querySelectorAll('.card-title'));
                const draggedPlayerTexts = Array.from(draggedPlayer.querySelectorAll('.card-text'));

                // Échanger les titres
                tempPlayerTitle.forEach((element, index) => {
                    const tempTitle = element.textContent;
                    element.textContent = draggedPlayerTitle[index].textContent;
                    draggedPlayerTitle[index].textContent = tempTitle;
                });

                // Échanger les textes
                tempPlayerTexts.forEach((element, index) => {
                    const tempText = element.textContent;
                    element.textContent = draggedPlayerTexts[index].textContent;
                    draggedPlayerTexts[index].textContent = tempText;
                });

            } else {
                // Si les positions sont différentes, annuler le glisser-déposer
                return;
            }

            // Réinitialiser la variable draggedPlayer
            draggedPlayer = null;

            // Mettre à jour le coût total de l'équipe après chaque glisser-déposer
            updateTeamTotalCost();
        });
    });

    // Fonction pour extraire la valeur numérique du texte de coût
    function extractCostValue(costText) {
        // Utiliser une expression régulière pour rechercher un nombre dans la chaîne
        const regex = /(\d+)/;
        const match = costText.match(regex);
        if (match) {
            return parseInt(match[0]); // Retourner la valeur numérique trouvée
        } else {
            return 0; // Retourner 0 si aucun nombre n'est trouvé
        }
    }
    function generate_new_team_id() {
        return Math.random().toString(36).substr(2, 9); // Génère une chaîne aléatoire de 9 caractères
    }
    // Fonction pour calculer et mettre à jour le coût total de l'équipe
    function updateTeamTotalCost() {
        totalCost = 0; // Réinitialiser le coût total à 0
        teamSlots.forEach(slot => {
            const costText = slot.querySelector('.card-cost').textContent;
            const costValue = extractCostValue(costText); // Utiliser la fonction pour extraire la valeur numérique
            totalCost += costValue; // Ajouter le coût de chaque joueur
        });
        updateRemainingMoney(); // Mettre à jour l'argent restant
    }

    // Fonction pour calculer et mettre à jour l'argent restant
    function updateRemainingMoney() {
        const remainingMoney = totalBudget - totalCost; // Calculer l'argent restant
        remainingAmountSpan.textContent = remainingMoney; // Afficher l'argent restant
    }
    
    var searchButton = document.getElementById("search-button");

searchButton.addEventListener("click", function() {
    var searchInput = document.getElementById("search-input").value;

    fetch('/api/search?query=' + encodeURIComponent(searchInput))
    .then(response => response.json())
    .then(data => {
        console.log('Search results:', data);

        // Parcourir les données renvoyées par le backend
        data.forEach(player => {
            // Trouver la sidebar card correspondante
            var sidebarCard = document.querySelector('.sidebar-card[data-player-id="' + player.id + '"]');
            if (sidebarCard) {
                // Ajouter une classe pour mettre en surbrillance la sidebar card
                sidebarCard.classList.add('highlight');
            }
        });
    })
    .catch(error => {
        console.error('Error searching:', error);
    });


    });
    
});

document.addEventListener('DOMContentLoaded', function () {
    const saveButton = document.getElementById('save-button');

    // Ajouter un gestionnaire d'événements pour le clic sur le bouton "Save"
    saveButton.addEventListener('click', function () {
        saveTeam(); // Appel de la fonction saveTeam lorsque l'utilisateur clique sur le bouton "Save"
    });

    function saveTeam() {
        const playerCards = document.querySelectorAll('.team-card');
        const playersIdsByPosition = {}; // Dictionnaire pour stocker les IDs des joueurs par position
    
        // Parcourir toutes les cartes de joueur
        playerCards.forEach(card => {
            const playerId = card.querySelector('.card-id').textContent; // Récupérer l'ID du joueur depuis la carte
            const positionElement = card.querySelector('.card-position').textContent; // Sélectionner l'élément qui contient la position du joueur
    
            // Vérifier si l'élément de position existe et n'est pas vide
            if (positionElement) {
                const cleanedPosition = positionElement.replace('POSITION', '').trim(); // Enlever le mot 'POSITION'
    
                // Utiliser une expression régulière pour extraire uniquement les nombres de l'ID du joueur
                const idList = playerId.match(/\d+/g) || []; // Extraire tous les nombres de l'ID
                const cleanedIds = idList.map(id => id.trim()); // Nettoyer les ID en enlevant les espaces
    
                // Vérifier si la position existe déjà dans le dictionnaire, sinon, initialiser un tableau vide
                if (!playersIdsByPosition[cleanedPosition]) {
                    playersIdsByPosition[cleanedPosition] = [];
                }
    
                // Ajouter les ID des joueurs à la liste correspondante à leur position
                playersIdsByPosition[cleanedPosition] = playersIdsByPosition[cleanedPosition].concat(cleanedIds);
            }
        });
    
        fetch('/api/modifier_equipe', { // Assurez-vous que vous appelez la bonne route pour la requête POST
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(playersIdsByPosition) // Envoyer le dictionnaire des IDs des joueurs dans le corps de la requête
        })
        .then(response => {
            if (response.ok) {
                // Extraire week_num de la réponse JSON
                return response.json().then(data => {
                    const week_num = data.week_num;
                    // Redirection vers /api/equipe/{week_num} si la requête est réussie
                    window.location.href = '/api/equipe/' + week_num;
                });
            } else {
                throw new Error('Network response was not ok');
            }
        })
        .catch(error => {
            console.error('There was a problem with your fetch operation:', error);
        });
    }
    
});
