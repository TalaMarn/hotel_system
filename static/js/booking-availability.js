(function () {
  const dataEl = document.getElementById('blocked-periods-data');
  const submitBtn = document.getElementById('submit-booking');
  const calendarEl = document.getElementById('availability-calendar');
  const feedbackEl = document.getElementById('date-selection-feedback');
  const checkInEl = document.getElementById('id_check_in');
  const checkOutEl = document.getElementById('id_check_out');
  const receiptSection = document.getElementById('receipt-section');

  if (!dataEl || !calendarEl) {
    return;
  }

  const blockedPeriods = JSON.parse(dataEl.textContent);

  function parseDate(value) {
    const [year, month, day] = value.split('-').map(Number);
    return new Date(year, month - 1, day);
  }

  function formatIso(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }

  function isNightBlocked(date) {
    const iso = formatIso(date);
    return blockedPeriods.some((period) => iso >= period.check_in && iso < period.check_out);
  }

  function rangesOverlap(startA, endA, startB, endB) {
    return startA < endB && endA > startB;
  }

  function selectionHasConflict(checkIn, checkOut) {
    return blockedPeriods.some((period) =>
      rangesOverlap(checkIn, checkOut, period.check_in, period.check_out)
    );
  }

  function renderCalendar() {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const monthsToShow = 3;
    calendarEl.innerHTML = '';

    for (let monthOffset = 0; monthOffset < monthsToShow; monthOffset += 1) {
      const monthDate = new Date(today.getFullYear(), today.getMonth() + monthOffset, 1);
      const monthLabel = monthDate.toLocaleString('default', { month: 'long', year: 'numeric' });

      const monthBlock = document.createElement('div');
      monthBlock.className = 'calendar-month';

      const title = document.createElement('h4');
      title.className = 'calendar-month-title';
      title.textContent = monthLabel;
      monthBlock.appendChild(title);

      const grid = document.createElement('div');
      grid.className = 'calendar-grid';

      ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].forEach((label) => {
        const head = document.createElement('span');
        head.className = 'calendar-weekday';
        head.textContent = label;
        grid.appendChild(head);
      });

      const firstWeekday = monthDate.getDay();
      const daysInMonth = new Date(monthDate.getFullYear(), monthDate.getMonth() + 1, 0).getDate();

      for (let i = 0; i < firstWeekday; i += 1) {
        const empty = document.createElement('span');
        empty.className = 'calendar-day empty';
        grid.appendChild(empty);
      }

      for (let day = 1; day <= daysInMonth; day += 1) {
        const cellDate = new Date(monthDate.getFullYear(), monthDate.getMonth(), day);
        const cell = document.createElement('span');
        cell.className = 'calendar-day';
        cell.textContent = String(day);

        if (cellDate < today) {
          cell.classList.add('past');
        } else if (isNightBlocked(cellDate)) {
          cell.classList.add('blocked');
        } else {
          cell.classList.add('available');
        }

        grid.appendChild(cell);
      }

      monthBlock.appendChild(grid);
      calendarEl.appendChild(monthBlock);
    }
  }

  function updateDateFeedback() {
    if (!feedbackEl || !checkInEl || !checkOutEl) {
      return;
    }

    const checkIn = checkInEl.value;
    const checkOut = checkOutEl.value;

    feedbackEl.classList.remove('alert-success', 'alert-error', 'alert-warning');
    feedbackEl.hidden = true;

    if (!checkIn && !checkOut) {
      if (receiptSection) receiptSection.classList.add('receipt-locked');
      lockSubmission();
      return;
    }

    if (!checkIn || !checkOut) {
      feedbackEl.hidden = false;
      feedbackEl.classList.add('alert-warning');
      feedbackEl.textContent = 'Select both check-in and check-out dates to confirm availability.';
      if (receiptSection) receiptSection.classList.add('receipt-locked');
      lockSubmission();
      return;
    }

    if (checkOut <= checkIn) {
      feedbackEl.hidden = false;
      feedbackEl.classList.add('alert-error');
      feedbackEl.textContent = 'Check-out must be after check-in.';
      if (receiptSection) receiptSection.classList.add('receipt-locked');
      lockSubmission();
      return;
    }

    if (selectionHasConflict(checkIn, checkOut)) {
      feedbackEl.hidden = false;
      feedbackEl.classList.add('alert-error');
      feedbackEl.textContent =
        'These dates overlap an existing reservation. Please choose different dates.';
      if (receiptSection) receiptSection.classList.add('receipt-locked');
      lockSubmission();
      return;
    }

    const nights = Math.round((parseDate(checkOut) - parseDate(checkIn)) / (1000 * 60 * 60 * 24));
    feedbackEl.hidden = false;
    feedbackEl.classList.add('alert-success');
    feedbackEl.textContent = `These dates are available (${nights} night${nights === 1 ? '' : 's'}). You can upload your payment receipt below.`;
    if (receiptSection) {
      receiptSection.classList.remove('receipt-locked');
    }
    if (submitBtn) {
      submitBtn.disabled = false;
    }
  }

  function lockSubmission() {
    if (submitBtn) {
      submitBtn.disabled = true;
    }
  }

  renderCalendar();
  updateDateFeedback();

  if (checkInEl) {
    checkInEl.addEventListener('change', updateDateFeedback);
  }
  if (checkOutEl) {
    checkOutEl.addEventListener('change', updateDateFeedback);
  }
})();
