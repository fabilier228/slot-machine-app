document.addEventListener("DOMContentLoaded", () => {
    var socket = io();
    socket.on('connect', function() {
        socket.emit('event');
    });

    socket.on('new_winner', (data) => {
        const winnerContainer = document.getElementById('winner-message')
        console.log(data)
        winnerContainer.innerText = `${data.message}`

        setTimeout(() => {
          socket.emit('event')
        },15000)

    })

});
