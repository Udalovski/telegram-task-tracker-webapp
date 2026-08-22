const { createApp, ref, computed, onMounted, watch, h } = Vue;


const ICONS = {
  'moon': '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
  'smartphone': '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/>',
  'refresh-cw': '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
  'calendar-check': '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/><path d="m9 16 2 2 4-4"/>',
  'history': '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
  'settings': '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/>',
  'check-circle-2': '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
  'check-circle': '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
  'send': '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
  'copy': '<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
  'plus-circle': '<circle cx="12" cy="12" r="10"/><path d="M8 12h8"/><path d="M12 8v8"/>',
  'plus': '<path d="M5 12h14"/><path d="M12 5v14"/>',
  'list-todo': '<rect x="3" y="5" width="6" height="6" rx="1"/><path d="m3 17 2 2 4-4"/><path d="M13 6h8"/><path d="M13 12h8"/><path d="M13 18h8"/>',
  'clipboard-list': '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/>',
  'edit-3': '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
  'trash-2': '<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/>',
  'calendar': '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
  'palette': '<circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>',
  'clock': '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
  'sparkles': '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>',
  'archive': '<rect width="20" height="5" x="2" y="3" rx="1"/><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8"/><path d="M10 12h4"/>',
  'x': '<path d="M18 6 6 18"/><path d="M6 6l12 12"/>',
  'check': '<path d="M20 6 9 17l-5-5"/>',
  'chevron-down': '<path d="m6 9 6 6 6-6"/>',
  'loader-2': '<path d="M21 12a9 9 0 1 1-6.219-8.56"/>'
};

const app = createApp({
  setup() {
    const tg = window.Telegram?.WebApp;


    const themeMode = ref(localStorage.getItem('task_tracker_theme') || 'dark');


    const currentTab = ref('today');
    const todayTasks = ref([]);
    const historyList = ref([]);
    const expandedDays = ref({});
    const userProfile = ref({
      first_name: '',
      username: '',
      report_time: '20:00',
      timezone: 'Europe/Warsaw',
      current_date: new Date().toISOString().split('T')[0],
      formatted_date: ''
    });

    const loading = ref(false);
    const historyLoading = ref(false);
    const actionLoading = ref(false);
    const savingSettings = ref(false);
    const savingEdit = ref(false);
    const liveTranslating = ref(false);


    const newTaskText = ref('');
    const newTaskPolish = ref('');
    let translateTimer = null;


    const editingTask = ref(null);
    const editForm = ref({
      id: null,
      raw_text: '',
      polish_text: ''
    });


    const toast = ref({
      show: false,
      message: '',
      icon: 'check-circle'
    });


    const userAvatarUrl = computed(() => {
      return tg?.initDataUnsafe?.user?.photo_url || null;
    });

    const userName = computed(() => {
      const tgUser = tg?.initDataUnsafe?.user;
      if (tgUser?.first_name) {
        return tgUser.first_name;
      }
      return userProfile.value.first_name || ' ';
    });

    const userInitials = computed(() => {
      const name = userName.value.trim();
      return name ? name.charAt(0).toUpperCase() : 'M';
    });

    const formattedDate = computed(() => {
      if (userProfile.value.formatted_date) {
        return userProfile.value.formatted_date;
      }
      const now = new Date();
      const d = String(now.getDate()).padStart(2, '0');
      const m = String(now.getMonth() + 1).padStart(2, '0');
      const y = now.getFullYear();
      return `${d}.${m}.${y}`;
    });


    const applyTheme = (mode) => {
      const root = document.documentElement;
      let isDark = true;
      if (mode === 'light') {
        isDark = false;
      } else if (mode === 'auto') {
        isDark = tg?.colorScheme === 'dark' || window.matchMedia('(prefers-color-scheme: dark)').matches;
      }

      if (isDark) {
        root.classList.add('dark');
        document.body.style.backgroundColor = '#0b0f17';
        document.body.style.color = '#f8fafc';
        if (tg?.setHeaderColor) tg.setHeaderColor('#0b0f17');
        if (tg?.setBackgroundColor) tg.setBackgroundColor('#0b0f17');
      } else {
        root.classList.remove('dark');
        document.body.style.backgroundColor = '#f1f5f9';
        document.body.style.color = '#0f172a';
        if (tg?.setHeaderColor) tg.setHeaderColor('#f1f5f9');
        if (tg?.setBackgroundColor) tg.setBackgroundColor('#f1f5f9');
      }
    };

    const setTheme = (mode) => {
      themeMode.value = mode;
      localStorage.setItem('task_tracker_theme', mode);
      applyTheme(mode);
      triggerHaptic('light');
    };

    const toggleTheme = () => {
      if (themeMode.value === 'dark') {
        setTheme('light');
      } else if (themeMode.value === 'light') {
        setTheme('auto');
      } else {
        setTheme('dark');
      }
    };


    const triggerHaptic = (type = 'light') => {
      try {
        if (tg?.HapticFeedback) {
          if (type === 'success' || type === 'error' || type === 'warning') {
            tg.HapticFeedback.notificationOccurred(type);
          } else {
            tg.HapticFeedback.impactOccurred(type);
          }
        }
      } catch (e) {}
    };


    const showToast = (message, icon = 'check-circle') => {
      toast.value = { show: true, message, icon };
      triggerHaptic('success');
      setTimeout(() => {
        toast.value.show = false;
      }, 2500);
    };


    const getHeaders = () => {
      const headers = { 'Content-Type': 'application/json' };
      if (tg?.initData) {
        headers['X-Telegram-Init-Data'] = tg.initData;
      }
      return headers;
    };


    const fetchUserProfile = async () => {
      try {
        const res = await fetch('/api/user/profile', { headers: getHeaders() });
        if (res.ok) {
          const data = await res.json();
          userProfile.value = data;
        }
      } catch (e) {
        console.error('Error fetching profile:', e);
      }
    };


    const fetchTodayTasks = async () => {
      loading.value = true;
      try {
        const res = await fetch('/api/tasks/today', { headers: getHeaders() });
        if (res.ok) {
          const data = await res.json();
          todayTasks.value = data.tasks || [];
        }
      } catch (e) {
        console.error('Error fetching today tasks:', e);
      } finally {
        loading.value = false;
      }
    };


    const clientTranslationCache = {};
    const lastTranslatedSource = ref('');

    const onTaskInput = () => {
      clearTimeout(translateTimer);
      const text = newTaskText.value.trim();


      if (text !== lastTranslatedSource.value) {
        newTaskPolish.value = '';
      }

      if (!text || text.length < 3) {
        liveTranslating.value = false;
        return;
      }

      if (clientTranslationCache[text]) {
        newTaskPolish.value = clientTranslationCache[text];
        lastTranslatedSource.value = text;
        liveTranslating.value = false;
        return;
      }

      liveTranslating.value = true;
      translateTimer = setTimeout(async () => {
        const queryText = newTaskText.value.trim();
        if (!queryText || queryText.length < 3) {
          liveTranslating.value = false;
          return;
        }

        try {
          const res = await fetch('/api/tasks/translate', {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ text: queryText })
          });
          if (res.ok) {
            const data = await res.json();
            if (newTaskText.value.trim() === queryText) {
              newTaskPolish.value = data.translated || '';
              lastTranslatedSource.value = queryText;
              clientTranslationCache[queryText] = data.translated || '';
            }
          }
        } catch (e) {
          console.error(e);
        } finally {
          liveTranslating.value = false;
        }
      }, 400);
    };


    const addNewTask = async () => {
      const text = newTaskText.value.trim();
      if (!text) return;

      clearTimeout(translateTimer);
      actionLoading.value = true;
      triggerHaptic('medium');


      const polish = (lastTranslatedSource.value === text && newTaskPolish.value.trim())
        ? newTaskPolish.value.trim()
        : undefined;

      try {
        const res = await fetch('/api/tasks', {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({
            raw_text: text,
            polish_text: polish
          })
        });

        if (res.ok) {
          const data = await res.json();
          todayTasks.value.push(data.task);
          newTaskText.value = '';
          newTaskPolish.value = '';
          lastTranslatedSource.value = '';
          showToast('     !');
        }
      } catch (e) {
        console.error('Error creating task:', e);
        showToast('   ', 'alert-circle');
      } finally {
        actionLoading.value = false;
      }
    };


    const openEditModal = (task) => {
      editingTask.value = task;
      editForm.value = {
        id: task.id,
        raw_text: task.raw_text,
        polish_text: task.polish_text
      };
      triggerHaptic('light');
    };


    const retranslateEditTask = async () => {
      const text = editForm.value.raw_text.trim();
      if (!text) return;
      try {
        const res = await fetch('/api/tasks/translate', {
          method: 'POST',
          headers: getHeaders(),
          body: JSON.stringify({ text })
        });
        if (res.ok) {
          const data = await res.json();
          editForm.value.polish_text = data.translated;
          triggerHaptic('light');
        }
      } catch (e) {
        console.error(e);
      }
    };


    const saveEditTask = async () => {
      if (!editForm.value.raw_text.trim()) return;
      savingEdit.value = true;
      try {
        const res = await fetch(`/api/tasks/${editForm.value.id}`, {
          method: 'PUT',
          headers: getHeaders(),
          body: JSON.stringify({
            raw_text: editForm.value.raw_text,
            polish_text: editForm.value.polish_text
          })
        });

        if (res.ok) {
          const data = await res.json();
          const idx = todayTasks.value.findIndex(t => t.id === editForm.value.id);
          if (idx !== -1) {
            todayTasks.value[idx] = data.task;
          }
          editingTask.value = null;
          showToast('   !');
        }
      } catch (e) {
        console.error('Error updating task:', e);
        showToast('   ', 'alert-circle');
      } finally {
        savingEdit.value = false;
      }
    };


    const deleteTaskItem = async (taskId) => {
      triggerHaptic('medium');
      try {
        const res = await fetch(`/api/tasks/${taskId}`, {
          method: 'DELETE',
          headers: getHeaders()
        });

        if (res.ok) {
          todayTasks.value = todayTasks.value.filter(t => t.id !== taskId);
          showToast('   ', 'trash-2');
        }
      } catch (e) {
        console.error('Error deleting task:', e);
      }
    };


    const fetchHistory = async () => {
      historyLoading.value = true;
      try {
        const res = await fetch('/api/tasks/history', { headers: getHeaders() });
        if (res.ok) {
          const data = await res.json();
          historyList.value = data.history || [];

          if (historyList.value.length > 0 && Object.keys(expandedDays.value).length === 0) {
            expandedDays.value[historyList.value[0].date] = true;
          }
        }
      } catch (e) {
        console.error('Error fetching history:', e);
      } finally {
        historyLoading.value = false;
      }
    };


    const toggleDayExpand = (dayDate) => {
      expandedDays.value[dayDate] = !expandedDays.value[dayDate];
      triggerHaptic('selection');
    };


    const copyText = async (text, msg = '     !') => {
      try {
        if (navigator.clipboard) {
          await navigator.clipboard.writeText(text);
        } else {
          const el = document.createElement('textarea');
          el.value = text;
          document.body.appendChild(el);
          el.select();
          document.execCommand('copy');
          document.body.removeChild(el);
        }
        showToast(msg, 'copy');
      } catch (e) {
        console.error('Copy failed', e);
      }
    };


    const copyTodayReport = () => {
      if (todayTasks.value.length === 0) return;
      const lines = [
        `📋 Raport dzienny (${formattedDate.value}):`,
        ''
      ];
      todayTasks.value.forEach(t => {
        lines.push(`• ${t.polish_text || t.raw_text}`);
      });
      lines.push('');
      lines.push(`Łącznie zadań: ${todayTasks.value.length}`);

      copyText(lines.join('\n'), '     !');
    };


    const sendReportTelegram = async () => {
      if (todayTasks.value.length === 0) return;
      actionLoading.value = true;
      triggerHaptic('medium');
      try {
        const res = await fetch('/api/report/send-now', {
          method: 'POST',
          headers: getHeaders()
        });

        if (res.ok) {
          showToast('       ! 🚀', 'send');
          if (tg?.close) {
            setTimeout(() => tg.close(), 1500);
          }
        } else {
          const err = await res.json();
          showToast(err.detail || '   ', 'alert-circle');
        }
      } catch (e) {
        console.error('Error sending report:', e);
        showToast('   \' ', 'alert-circle');
      } finally {
        actionLoading.value = false;
      }
    };


    const saveSettings = async () => {
      savingSettings.value = true;
      triggerHaptic('medium');
      try {
        const res = await fetch('/api/user/settings', {
          method: 'PUT',
          headers: getHeaders(),
          body: JSON.stringify({
            report_time: userProfile.value.report_time,
            timezone: userProfile.value.timezone
          })
        });

        if (res.ok) {
          showToast('   !', 'check');
        }
      } catch (e) {
        console.error('Error saving settings:', e);
        showToast('   ', 'alert-circle');
      } finally {
        savingSettings.value = false;
      }
    };


    const pluralizeTasks = (n) => {
      if (n % 10 === 1 && n % 100 !== 11) return ' ';
      if ([2, 3, 4].includes(n % 10) && ![12, 13, 14].includes(n % 100)) return ' ';
      return ' ';
    };


    const formatDayOfWeek = (dateStr) => {
      const days = [' ', ' ', ' ', ' ', ' ', ' \' ', ' '];
      const d = dateStr ? new Date(dateStr) : new Date();
      return days[d.getDay()] || '';
    };


    onMounted(async () => {
      if (tg) {
        tg.ready();
        tg.expand();
      }

      applyTheme(themeMode.value);

      await fetchUserProfile();
      await fetchTodayTasks();
    });

    return {
      themeMode,
      currentTab,
      todayTasks,
      historyList,
      expandedDays,
      userProfile,
      loading,
      historyLoading,
      actionLoading,
      savingSettings,
      savingEdit,
      liveTranslating,
      newTaskText,
      newTaskPolish,
      editingTask,
      editForm,
      toast,
      userAvatarUrl,
      userName,
      userInitials,
      formattedDate,
      fetchTodayTasks,
      onTaskInput,
      addNewTask,
      openEditModal,
      retranslateEditTask,
      saveEditTask,
      deleteTaskItem,
      fetchHistory,
      toggleDayExpand,
      copyText,
      copyTodayReport,
      sendReportTelegram,
      saveSettings,
      setTheme,
      toggleTheme,
      pluralizeTasks,
      formatDayOfWeek
    };
  }
});


app.component('app-icon', {
  props: {
    name: {
      type: String,
      required: true
    }
  },
  setup(props) {
    return () => {
      const innerSvg = ICONS[props.name] || '';
      return h('svg', {
        viewBox: '0 0 24 24',
        fill: 'none',
        stroke: 'currentColor',
        'stroke-width': '2',
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        innerHTML: innerSvg
      });
    };
  }
});

app.mount('#app');

