(function () {
  "use strict";

  const items = [
    "7️⃣",
    "❌",
    "🍓",
    "🍋",
    "🍉",
    "🍒",
    "💵",
    "🍊",
    "🍎"
  ];

  const COST_PER_GAME = 15; // Cost for one game
  const multipliers = {
    "7️⃣": 10,
    "❌": 0,
    "🍓": 5,
    "🍋": 3,
    "🍉": 4,
    "🍒": 6,
    "💵": 20,
    "🍊": 2,
    "🍎": 1
  };

  const saldoDisplay = document.querySelector(".saldo-display");
  const displayResult = document.querySelector(".display-result");
  const doors = document.querySelectorAll(".door");
  const spinButton = document.querySelector("#spinner");
  const resetButton = document.querySelector("#reseter");

  spinButton.disabled = false;

  document.querySelector("#spinner").addEventListener("click", spin);
  document.querySelector("#reseter").addEventListener("click", resetGame);

  async function spin() {
    const currentSaldo = parseInt(saldoDisplay.textContent.replace("Saldo: $", ""));

    if (currentSaldo < COST_PER_GAME) {
      updateDisplayResult("Brak wystarczających środków, aby zagrać!");
      return;
    }

    // Deduct game cost
    saldoDisplay.textContent = `Saldo: $${currentSaldo - COST_PER_GAME}`;
    displayResult.innerHTML = ""; // Clear previous results

    fetch("/play_game", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      cost: COST_PER_GAME,  // Koszt gry
    }),
  })
    .then((response) => response.json())
    .catch((error) => {
      console.error("Error:", error);
      info.textContent = "Błąd komunikacji z serwerem!";
    });

    init(false, 1, 2);

    const results = [];
    for (const door of doors) {
      const boxes = door.querySelector(".boxes");
      const duration = parseInt(boxes.style.transitionDuration);
      boxes.style.transform = "translateY(0)";
      await new Promise((resolve) => setTimeout(resolve, duration * 100));

      // Get the visible symbol on the door
      const visibleBox = boxes.firstElementChild;
      results.push(visibleBox.textContent);
    }

    // Check if all results are the same
    if (results.every((val) => val === results[0])) {
      const symbol = results[0];
      const multiplier = multipliers[symbol] || 0;
      const winnings = COST_PER_GAME * multiplier;

      // Send result to the backend
      sendWinToBackend(winnings, symbol);

      // Update result display
      updateDisplayResult(`Congratulations, you won $${winnings}! 🎉`);
    } else {
      updateDisplayResult("Spróbuj ponownie!");
    }

    spinButton.disabled = true
  }

  function resetGame() {
    // Reset game state
    displayResult.innerHTML = "Game reset. Good luck!";
    spinButton.disabled = false
    init(true); // Reset doors to initial state
  }

  function init(firstInit = true, groups = 1, duration = 1) {
    for (const door of doors) {
      if (firstInit) {
        door.dataset.spinned = "0";
      } else if (door.dataset.spinned === "1") {
        return;
      }

      const boxes = door.querySelector(".boxes");
      const boxesClone = boxes.cloneNode(false);

      const pool = ["❓"];
      if (!firstInit) {
        const arr = [];
        for (let n = 0; n < (groups > 0 ? groups : 1); n++) {
          arr.push(...items);
        }
        pool.push(...shuffle(arr));

        boxesClone.addEventListener(
          "transitionstart",
          function () {
            door.dataset.spinned = "1";
            this.querySelectorAll(".box").forEach((box) => {
              box.style.filter = "blur(1px)";
            });
          },
          { once: true }
        );

        boxesClone.addEventListener(
          "transitionend",
          function () {
            this.querySelectorAll(".box").forEach((box, index) => {
              box.style.filter = "blur(0)";
              if (index > 0) this.removeChild(box);
            });
          },
          { once: true }
        );
      }

      for (let i = pool.length - 1; i >= 0; i--) {
        const box = document.createElement("div");
        box.classList.add("box");
        box.style.width = door.clientWidth + "px";
        box.style.height = door.clientHeight + "px";
        box.textContent = pool[i];
        boxesClone.appendChild(box);
      }
      boxesClone.style.transitionDuration = `${duration > 0 ? duration : 1}s`;
      boxesClone.style.transform = `translateY(-${
        door.clientHeight * (pool.length - 1)
      }px)`;
      door.replaceChild(boxesClone, boxes);
    }
  }

  function shuffle([...arr]) {
    let m = arr.length;
    while (m) {
      const i = Math.floor(Math.random() * m--);
      [arr[m], arr[i]] = [arr[i], arr[m]];
    }
    return arr;
  }

  function sendWinToBackend(winnings, symbol) {
    fetch("/update_saldo", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        winnings: winnings,
        cost: COST_PER_GAME,
        symbol: symbol
      })
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          saldoDisplay.textContent = `Saldo: $${data.new_saldo}`;
          updateDisplayResult(`Congratulations, you won $${winnings}! 🎉`);
        } else {
          updateDisplayResult("Błąd aktualizacji salda!");
        }
      })
      .catch((error) => {
        console.error("Error updating saldo:", error);
        updateDisplayResult("Błąd komunikacji z serwerem!");
      });
  }


  function updateDisplayResult(message) {
    // Update the content of the display-result div
    setTimeout(() => {
      displayResult.innerHTML = `<p>${message}</p>`;
    },2150)
  }

  init();
})();
