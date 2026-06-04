(function () {
  const POLL_INTERVAL_MS = 7000;

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(';') : [];

    for (const cookie of cookies) {
      const trimmedCookie = cookie.trim();
      const prefix = `${name}=`;

      if (trimmedCookie.startsWith(prefix)) {
        return decodeURIComponent(trimmedCookie.slice(prefix.length));
      }
    }

    return '';
  }

  function renderNotification(notification) {
    const unreadClass = notification.is_read ? '' : ' unread';
    const unreadDot = notification.is_read
      ? ''
      : '<span class="dashboard-notification-dot"></span>';

    return `
      <a
        href="${escapeHtml(notification.url)}"
        class="dashboard-notification-item${unreadClass}"
      >
        <span class="dashboard-notification-icon">
          <i class="bi bi-file-earmark-text"></i>
        </span>

        <span class="dashboard-notification-body">
          <span class="dashboard-notification-item-title">
            ${escapeHtml(notification.title)}
          </span>
          <span class="dashboard-notification-message">
            ${escapeHtml(notification.message)}
          </span>
        </span>

        <span class="dashboard-notification-time">
          ${escapeHtml(notification.time_label)}
        </span>

        ${unreadDot}
      </a>
    `;
  }

  function renderNotifications(widget, data) {
    const badge = widget.querySelector('[data-notification-badge]');
    const unreadLabel = widget.querySelector('[data-notification-unread-label]');
    const list = widget.querySelector('[data-notification-list]');
    const readForm = widget.querySelector('[data-notification-read-form]');
    const unreadCount = Number(data.unread_count || 0);

    if (badge) {
      badge.textContent = unreadCount;
      badge.classList.toggle('d-none', unreadCount === 0);
    }

    if (unreadLabel) {
      unreadLabel.textContent = `No le\u00eddas (${unreadCount})`;
    }

    if (readForm) {
      readForm.classList.toggle('d-none', unreadCount === 0);
    }

    if (!list) {
      return;
    }

    if (!data.notifications || data.notifications.length === 0) {
      list.innerHTML = `
        <div class="dashboard-notification-empty">
          No tienes notificaciones.
        </div>
      `;
      return;
    }

    list.innerHTML = data.notifications.map(renderNotification).join('');
  }

  async function fetchNotifications(widget) {
    const summaryUrl = widget.dataset.summaryUrl;

    if (!summaryUrl) {
      return;
    }

    const response = await fetch(summaryUrl, {
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      return;
    }

    renderNotifications(widget, await response.json());
  }

  function setupReadAll(widget) {
    const form = widget.querySelector('[data-notification-read-form]');

    if (!form) {
      return;
    }

    form.addEventListener('submit', async function (event) {
      event.preventDefault();

      const response = await fetch(widget.dataset.readUrl || form.action, {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest',
        },
      });

      if (response.ok) {
        renderNotifications(widget, await response.json());
      }
    });
  }

  function setupWidget(widget) {
    setupReadAll(widget);
    fetchNotifications(widget).catch(() => {});

    window.setInterval(function () {
      fetchNotifications(widget).catch(() => {});
    }, POLL_INTERVAL_MS);

    document.addEventListener('visibilitychange', function () {
      if (!document.hidden) {
        fetchNotifications(widget).catch(() => {});
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    document
      .querySelectorAll('[data-notifications-widget]')
      .forEach(setupWidget);
  });
})();
