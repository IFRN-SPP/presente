class QRCodeManager {
  constructor(serverTime) {
    const serverTimeMs = new Date(serverTime).getTime();
    const clientTimeMs = new Date().getTime();
    this.timeOffset = serverTimeMs - clientTimeMs;
  }

  getServerTime() {
    return new Date(new Date().getTime() + this.timeOffset);
  }

  updateDateTime() {
    const currentTimeEl = document.getElementById('current-time');
    const currentDateEl = document.getElementById('current-date');
    if (!currentTimeEl) return;

    const update = () => {
      const now = this.getServerTime();
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      const seconds = String(now.getSeconds()).padStart(2, '0');
      currentTimeEl.textContent = hours + ':' + minutes + ':' + seconds;

      if (currentDateEl) {
        const day = String(now.getDate()).padStart(2, '0');
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const year = now.getFullYear();
        currentDateEl.textContent = day + '/' + month + '/' + year;
      }
    };

    update();
    setInterval(update, 1000);
  }

  initActivityStartCountdown(startTime) {
    const startTimeMs = new Date(startTime).getTime();
    const countdownEl = document.getElementById('start-countdown');
    if (!countdownEl) return;

    const updateCountdown = () => {
      const now = this.getServerTime().getTime();
      const distance = startTimeMs - now;

      if (distance < 0) {
        countdownEl.textContent = 'iniciando...';
        return;
      }

      const days = Math.floor(distance / (1000 * 60 * 60 * 24));
      const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((distance % (1000 * 60)) / 1000);

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
    };

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);

    const observer = new MutationObserver(function(mutations) {
      if (!document.contains(countdownEl)) {
        clearInterval(interval);
        observer.disconnect();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  initQRCode(checkinUrl, timeout) {
    let timeLeft = timeout;

    const getQRSize = () => {
      const screenWidth = window.innerWidth;
      const screenHeight = window.innerHeight;

      if (screenWidth < 576) {
        return Math.min(300, screenWidth - 60);
      } else if (screenWidth < 768) {
        return Math.min(360, screenWidth - 100);
      } else if (screenHeight < 800) {
        return 340;
      } else {
        return 420;
      }
    };

    const initQR = () => {
      const qrcodeDiv = document.getElementById('qrcode');
      if (qrcodeDiv && !qrcodeDiv.hasChildNodes() && typeof QRCode !== 'undefined') {
        const qrSize = getQRSize();

        new QRCode(qrcodeDiv, {
          text: checkinUrl,
          width: qrSize,
          height: qrSize,
          colorDark: '#000000',
          colorLight: '#ffffff',
          correctLevel: QRCode.CorrectLevel.H
        });

        this.startQRCountdown(timeLeft);
      } else if (typeof QRCode === 'undefined') {
        setTimeout(initQR, 50);
      }
    };

    initQR();

    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        const qrcodeDiv = document.getElementById('qrcode');
        if (qrcodeDiv) {
          qrcodeDiv.innerHTML = '';
          initQR();
        }
      }, 250);
    });
  }

  startQRCountdown(timeLeft) {
    const countdownText = document.getElementById('countdown-text');
    const qrcodeDiv = document.getElementById('qrcode');
    if (!countdownText) return;

    const interval = setInterval(() => {
      timeLeft--;
      countdownText.textContent = timeLeft;

      if (timeLeft === 3 && qrcodeDiv) {
        qrcodeDiv.classList.add('qr-fade-out');
      }

      if (timeLeft <= 0) {
        clearInterval(interval);
      }
    }, 1000);
  }
}
