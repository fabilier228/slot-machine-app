document.addEventListener("DOMContentLoaded", () => {
    var es = new EventSource("/events/datetime");
            es.onmessage = function(event) {
                const eventDiv = document.getElementById("ad-text");
                eventDiv.innerHTML = '<div>' + event.data + '</div>';
            }
});
