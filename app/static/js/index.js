document.addEventListener("DOMContentLoaded", () => {
  const BONUS_AMOUNT = 300; // Bonus amount
  const COOLDOWN_HOURS = 12; // Cooldown period in hours
  const bonusButton = document.getElementById("collect-bonus");
  const bonusInfo = document.querySelector(".bonus-info");
  const saldoDisplay = document.querySelector(".saldo-display");

  // Fetch the last collected time from the server or local storage
  let lastCollected = localStorage.getItem("lastCollected");

  function updateButtonState() {
    const now = Date.now();
    if (lastCollected) {
      const timeElapsed = now - parseInt(lastCollected, 10);
      // const remainingTime = COOLDOWN_HOURS * 3600 * 1000 - timeElapsed;
      const remainingTime = 0;

      if (remainingTime > 0) {
        const hours = Math.floor(remainingTime / 3600000);
        const minutes = Math.floor((remainingTime % 3600000) / 60000);
        bonusButton.disabled = true;
        bonusInfo.textContent = `Bonus available in ${hours}h ${minutes}m`;
        return;
      }
    }

    bonusButton.disabled = false;
    bonusInfo.textContent = "Bonus available! Collect now.";
  }

  // Handle bonus collection
  bonusButton.addEventListener("click", () => {
    fetch("/collect_bonus", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ bonus: BONUS_AMOUNT }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          lastCollected = Date.now();
          localStorage.setItem("lastCollected", lastCollected);
          bonusInfo.textContent = `Successfully collected $${BONUS_AMOUNT}!`;
          updateButtonState();
        } else {
          bonusInfo.textContent = "Failed to collect bonus. Try again later.";
        }
      })
      .catch((error) => {
        console.error("Error collecting bonus:", error);
        bonusInfo.textContent = "Error connecting to server.";
      });
  });

  const currentSaldo = parseInt(saldoDisplay.textContent.replace("Saldo: $", ""));
  saldoDisplay.textContent = `Saldo: $${currentSaldo}`;

  // Initialize button state on page load
  updateButtonState();
  setInterval(updateButtonState, 60000); // Update button state every minute
});
