document.addEventListener('DOMContentLoaded', function () {
    const players = document.querySelectorAll('.player');
    const teamSlots = document.querySelectorAll('.team-slot');

    let draggedPlayer = null;

    // Ajoutez des écouteurs d'événements pour les éléments glissables dans la barre latérale
    players.forEach(player => {
        player.addEventListener('dragstart', function (e) {
            draggedPlayer = e.target;
        });
    });

    // Ajoutez des écouteurs d'événements pour les emplacements d'équipe
    teamSlots.forEach(slot => {
        slot.addEventListener('dragover', function (e) {
            e.preventDefault();
        });

        slot.addEventListener('drop', function (e) {
            e.preventDefault();
            if (draggedPlayer) {
                // Retirer le joueur existant dans la fente d'équipe (s'il y en a un)
                const existingPlayer = this.querySelector('.player');
                if (existingPlayer) {
                    // Réinitialiser la position du joueur existant à la barre latérale
                    document.getElementById('players-container').appendChild(existingPlayer);
                }
                // Ajouter le joueur glissé à l'emplacement de l'équipe
                this.appendChild(draggedPlayer);
                // Réinitialiser la variable
                draggedPlayer = null;
            }
        });
    });
});
