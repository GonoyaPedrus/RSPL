document.addEventListener('DOMContentLoaded', function () {
    const players = document.querySelectorAll('.player');
    const teamSlots = document.querySelectorAll('.team-card');
    const remainingAmountSpan = document.getElementById('remaining-amount');
    const totalBudget = 1000; // Budget total disponible
    const totalCostSpan = document.getElementById('total-cost');

    let draggedPlayer = null;

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

    // Fonction pour calculer et mettre à jour le coût total de l'équipe
    function updateTeamTotalCost() {
        let totalCost = 0;
        teamSlots.forEach(slot => {
            const costText = slot.querySelector('.card-cost').textContent;
            const costValue = parseInt(costText);
            if (!isNaN(costValue)) {
                totalCost += costValue; // Ajouter le coût de chaque joueur
            }
        });
        totalCostSpan.textContent = totalCost; // Afficher le coût total de l'équipe
        updateRemainingMoney(); // Mettre à jour l'argent restant
    }

    // Fonction pour calculer et mettre à jour l'argent restant
    function updateRemainingMoney() {
        const remainingMoney = totalBudget - parseInt(totalCostSpan.textContent);
        remainingAmountSpan.textContent = remainingMoney; // Afficher l'argent restant
    }

    // Appel initial pour mettre à jour le coût total de l'équipe
    updateTeamTotalCost();
});
