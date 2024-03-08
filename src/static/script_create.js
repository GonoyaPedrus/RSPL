document.addEventListener('DOMContentLoaded', function () {
    const players = document.querySelectorAll('.player');
    const teamCards = document.querySelectorAll('.team .card');

    let draggedPlayer = null;

    // Ajoutez des écouteurs d'événements pour les éléments glissables dans la barre latérale
    players.forEach(player => {
        player.addEventListener('dragstart', function (e) {
            draggedPlayer = e.target;
        });
    });

    // Ajoutez des écouteurs d'événements pour les cartes de l'équipe
    teamCards.forEach(card => {
        card.addEventListener('dragover', function (e) {
            e.preventDefault();
        });

        card.addEventListener('drop', function (e) {
            e.preventDefault();
            if (draggedPlayer) {
                // Échangez les joueurs entre la barre latérale et l'équipe
                const playerName = draggedPlayer.querySelector('span').textContent;
                const playerPosition = draggedPlayer.querySelector('.element-type').textContent;
                const cardPlayerName = card.querySelector('p').textContent;

                // Mettez en œuvre la logique pour échanger les joueurs
                // Vous devrez ajuster votre logique pour gérer correctement les échanges de joueurs dans votre application
                draggedPlayer.querySelector('span').textContent = cardPlayerName;
                card.querySelector('p').textContent = playerName;

                draggedPlayer = null;
            }
        });
    });
});
