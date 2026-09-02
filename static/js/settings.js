/* Smart Learning preferences: shared, dependency-free client state. */
(() => {
  const KEY = 'sl_settings';

  const defaults = {
    language: 'en-us',
    age_group: '4-6',
    daily_goal: 30,
    content_filter: 'strict',
    auto_play: true,
    offline_mode: false,
    theme: 'light',
    font_size: 'medium',
    master_volume: 80,
    music_volume: 70,
    effects_volume: 90,
    notifications: true,
    learning_reminders: true,
    achievement_notifications: true,
    screen_time_limit: '60',
    quiz_permissions: 'all',
    purchase_settings: 'password'
  };

  const read = () => {
    try {
      return {
        ...defaults,
        ...(JSON.parse(localStorage.getItem(KEY)) || {})
      };
    } catch (_) {
      return { ...defaults };
    }
  };

  const write = (next) => {
    const state = {
      ...defaults,
      ...next
    };

    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch (_) {}

    apply(state);

    window.dispatchEvent(
      new CustomEvent('sl-settings-changed', {
        detail: state
      })
    );

    return state;
  };

  function apply(state) {
    const root = document.documentElement;

    root.dataset.slTheme = state.theme;
    root.dataset.slFontSize = state.font_size;

    const langMap = {
      'en-us': 'en',
      te: 'te',
      hi: 'hi',
      ta: 'ta',
      kn: 'kn',
      ml: 'ml'
    };

    root.lang = langMap[state.language] || 'en';

    if (!document.getElementById('sl-settings-style')) {
      const style = document.createElement('style');

      style.id = 'sl-settings-style';

      style.textContent = `
        html[data-sl-theme="dark"] body {
          background: #15142a !important;
          color: #f8f7ff !important;
        }

        html[data-sl-theme="dark"] .sidebar,
        html[data-sl-theme="dark"] .topnav,
        html[data-sl-theme="dark"] .top-actions > *,
        html[data-sl-theme="dark"] .panel,
        html[data-sl-theme="dark"] .qcard,
        html[data-sl-theme="dark"] .card,
        html[data-sl-theme="dark"] .voice,
        html[data-sl-theme="dark"] .profile,
        html[data-sl-theme="dark"] .bell,
        html[data-sl-theme="dark"] .settings-shell,
        html[data-sl-theme="dark"] .settings-card,
        html[data-sl-theme="dark"] .settings-category,
        html[data-sl-theme="dark"] .settings-option-card,
        html[data-sl-theme="dark"] .settings-side-card {
          background: #211f3a !important;
          border-color: #3b365d !important;
          color: #f8f7ff !important;
        }

        html[data-sl-theme="dark"] .menu a,
        html[data-sl-theme="dark"] .topnav a,
        html[data-sl-theme="dark"] .settings-category button,
        html[data-sl-theme="dark"] .setting-row,
        html[data-sl-theme="dark"] .setting-row label,
        html[data-sl-theme="dark"] .settings-copy,
        html[data-sl-theme="dark"] .settings-title {
          color: #f8f7ff !important;
        }

        html[data-sl-theme="dark"] p,
        html[data-sl-theme="dark"] small,
        html[data-sl-theme="dark"] .settings-copy small,
        html[data-sl-theme="dark"] .settings-help,
        html[data-sl-theme="dark"] .muted {
          color: #c8c4dc !important;
        }

        html[data-sl-theme="dark"] .hero,
        html[data-sl-theme="dark"] .settings-hero {
          background: linear-gradient(
            105deg,
            #25355e,
            #4b356d 62%,
            #30265a
          ) !important;
        }

        html[data-sl-theme="dark"] input,
        html[data-sl-theme="dark"] select,
        html[data-sl-theme="dark"] textarea {
          background: #17152a !important;
          color: #fff !important;
          border-color: #4a436c !important;
        }

        html[data-sl-theme="dark"] .menu a.active,
        html[data-sl-theme="dark"] .topnav a.active {
          background: #382a68 !important;
        }

        html[data-sl-theme="dark"] .settings-row:hover {
          background: #2b2748 !important;
        }

        html[data-sl-font-size="small"] body {
          font-size: 14px !important;
        }

        html[data-sl-font-size="medium"] body {
          font-size: 16px !important;
        }

        html[data-sl-font-size="large"] body {
          font-size: 18px !important;
        }

        html[data-sl-font-size="large"] .settings-shell {
          font-size: 1.02em;
        }

        html[data-sl-font-size="small"] .settings-shell {
          font-size: 0.94em;
        }
      `;

      document.head.appendChild(style);
    }
  }

  window.SmartLearningSettings = {
    defaults,

    get: read,

    set: (patch) => {
      return write({
        ...read(),
        ...patch
      });
    },

    reset: () => {
      return write({
        ...defaults
      });
    }
  };

  apply(read());
})();