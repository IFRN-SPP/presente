class QRCodeManager {
  constructor(serverTime) {
    const serverTimeMs = new Date(serverTime).getTime();
    const clientTimeMs = new Date().getTime();
    this.timeOffset = serverTimeMs - clientTimeMs;
    this.intervals = [];
  }

  clearIntervals() {
    this.intervals.forEach(interval => clearInterval(interval));
    this.intervals = [];
  }

  getServerTime() {
    return new Date(new Date().getTime() + this.timeOffset);
  }

  updateDateTime() {
    const currentTimeEl = document.getElementById('current-time');
    const currentDateEl = document.getElementById('current-date');
    if (!currentTimeEl) return;

    // Create formatters once for efficiency
    const timeFormatter = new Intl.DateTimeFormat('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });

    const dateFormatter = new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });

    const update = () => {
      const now = this.getServerTime();
      currentTimeEl.textContent = timeFormatter.format(now);
      if (currentDateEl) {
        currentDateEl.textContent = dateFormatter.format(now);
      }
    };

    update();
    this.intervals.push(setInterval(update, 1000));
  }

  initActivityStartCountdown(secondsLeft) {
    const countdownEl = document.getElementById('start-countdown');
    if (!countdownEl) return;

    const updateCountdown = () => {
      if (secondsLeft <= 0) {
        countdownEl.textContent = 'iniciando...';
        return;
      }

      const days = Math.floor(secondsLeft / 86400);
      const hours = Math.floor((secondsLeft % 86400) / 3600);
      const minutes = Math.floor((secondsLeft % 3600) / 60);
      const seconds = secondsLeft % 60;

      let timeString = '';
      if (days > 0) {
        timeString = days + 'd ' + hours + 'h ' + minutes + 'm';
      } else if (hours > 0) {
        timeString = hours + 'h ' + minutes + 'm ' + seconds + 's';
      } else if (minutes > 0) {
        timeString = minutes + 'm ' + seconds + 's';
      } else {
        timeString = seconds + 's';
      }

      countdownEl.textContent = timeString;
      secondsLeft--;
    };

    updateCountdown();
    this.intervals.push(setInterval(updateCountdown, 1000));
  }

  initQRCountdown(timeout) {
    this.startQRCountdown(timeout);
  }

  startQRCountdown(timeLeft) {
    const countdownText = document.getElementById('countdown-text');
    const qrLink = document.querySelector('.qr-code-link');
    if (!countdownText) return;

    countdownText.textContent = timeLeft;

    const interval = setInterval(() => {
      timeLeft--;
      countdownText.textContent = timeLeft;

      if (timeLeft === 3 && qrLink) {
        qrLink.classList.add('qr-fade-out');
      }

      if (timeLeft <= 0) {
        clearInterval(interval);
      }
    }, 1000);

    this.intervals.push(interval);
  }
}

if (!window.qrManager) {
  window.qrManager = null;
}
