document.addEventListener("DOMContentLoaded", () => {
  const BONUS_AMOUNT = 300; // Bonus amount
  const COOLDOWN_HOURS = 12; // Cooldown period in hours
  const bonusButton = document.getElementById("collect-bonus");
  const bonusInfo = document.querySelector(".bonus-info");
  const saldoDisplay = document.querySelector(".saldo-display");
  const deleteHistoryButton = document.getElementById("delete-history")
  const updateInput = document.querySelector("#update-input")
  const updateButton = document.querySelector('#update-button')

  // Fetch user bonus status from the server
  function fetchBonusStatus() {
    fetch("/bonus_status")
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          const now = new Date();
          const lastCollected = new Date(data.last_bonus_collected);
          const timeElapsed = now - lastCollected;
          const remainingTime = COOLDOWN_HOURS * 3600 * 1000 - timeElapsed;

          if (remainingTime > 0) {
            const hours = Math.floor(remainingTime / 3600000);
            const minutes = Math.floor((remainingTime % 3600000) / 60000);
            bonusButton.disabled = true;
            bonusInfo.textContent = `Bonus available in ${hours}h ${minutes}m`;
          } else {
            bonusButton.disabled = false;
            bonusInfo.textContent = "Bonus available! Collect now.";
          }
        } else {
          bonusButton.disabled = true;
          bonusInfo.textContent = "Error fetching bonus status.";
        }
      })
      .catch((error) => {
        console.error("Error fetching bonus status:", error);
        bonusInfo.textContent = "Failed to connect to server.";
      });
  }

  function deleteHistory() {
    fetch('/delete_history', {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        return response.json();
    })
    .catch(error => {
        console.error("Error deleting history:", error);
    });
  }

  function updateUsername() {
      const inputUpdateValue = updateInput.value
      console.log(inputUpdateValue)

      fetch('/update_username', {
            method: 'UPDATE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ newUsername: inputUpdateValue }),
        })
            .then((response) => response.json())
            .catch((error) => {
                console.error('Error:', error);
                alert('An error occurred while updating.');
            });
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
          saldoDisplay.textContent = `Saldo: $${data.new_saldo}`;
          bonusInfo.textContent = `Successfully collected $${BONUS_AMOUNT}!`;
          fetchBonusStatus(); // Update bonus state
        } else {
          bonusInfo.textContent = data.message || "Failed to collect bonus. Try again later.";
        }
      })
      .catch((error) => {
        console.error("Error collecting bonus:", error);
        bonusInfo.textContent = "Error connecting to server.";
      });
  });

  fetchBonusStatus();
  setInterval(fetchBonusStatus, 60000);

  deleteHistoryButton.addEventListener('click', () => {
    deleteHistory()
  })
    updateButton.addEventListener('click', () => {
    updateUsername()
    })



});
