const state = {
  currentModule: 'overview',
  users: [
    { id: 101, name: 'Alice Nguyen', email: 'alice@example.com', status: 'Active' },
    { id: 102, name: 'Brian Lee', email: 'brian@example.com', status: 'Invited' },
    { id: 103, name: 'Celine Park', email: 'celine@example.com', status: 'Inactive' },
    { id: 104, name: 'Daniel Kits', email: 'daniel@example.com', status: 'Active' },
  ],
  activities: [
    'New signup: thabo@domain.com',
    'Server CPU at 78%',
    'Weekly report generated',
    'Password reset requested by user #102',
  ],
  products: ['Pro Plan', 'Growth Suite', 'Enterprise', 'Starter'],
};

const query = (selector) => document.querySelector(selector);

function init() {
  renderModule('overview');
  renderUsers();
  renderActivities();
  renderProducts();
  renderTasks();

  document.getElementById('menuToggle').addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('collapsed');
  });

  document.querySelectorAll('.nav-link').forEach((link) => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const module = link.dataset.module;
      setActiveNav(module);
      renderModule(module);
    });
  });

  document.getElementById('globalSearch').addEventListener('input', onSearch);
  document.getElementById('clearSearch').addEventListener('click', () => {
    const s = query('#globalSearch');
    s.value = '';
    onSearch();
  });
}

function setActiveNav(module) {
  state.currentModule = module;
  document.querySelectorAll('.nav-link').forEach((link) => {
    link.classList.toggle('active', link.dataset.module === module);
  });
}

function renderModule(module) {
  ['overview', 'users', 'analytics', 'tasks', 'settings'].forEach((m) => {
    const el = document.getElementById(`${m}View`);
    if (el) el.classList.toggle('hidden', m !== module);
  });
}

function renderUsers() {
  const tbody = query('#usersTable');
  tbody.innerHTML = '';
  state.users.forEach((user) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${user.id}</td>
      <td>${user.name}</td>
      <td>${user.email}</td>
      <td>${user.status}</td>
      <td><button class="btn-ghost" data-user-id="${user.id}">Toggle Status</button></td>
    `;
    tbody.appendChild(row);
  });

  tbody.querySelectorAll('button').forEach((btn) => {
    btn.addEventListener('click', () => {
      const userId = Number(btn.dataset.userId);
      const u = state.users.find((x) => x.id === userId);
      if (u) {
        u.status = u.status === 'Active' ? 'Inactive' : 'Active';
        renderUsers();
      }
    });
  });
}

function renderActivities() {
  const list = query('#activityList');
  list.innerHTML = state.activities.map((item) => `<li>${item}</li>`).join('');
}

function renderProducts() {
  const products = query('#topProducts');
  products.innerHTML = state.products.map((item, i) => `<li>${i + 1}. ${item}</li>`).join('');
}

function renderTasks() {
  const tasks = [
    { text: 'Deploy new version', done: false },
    { text: 'Review security policy', done: true },
    { text: 'Design feature roadmap', done: false },
  ];
  const list = query('#tasksList');
  list.innerHTML = tasks.map((task, i) => `
    <li class="${task.done ? 'completed' : ''}">
      <span>${task.text}</span>
      <button data-task-id="${i}">${task.done ? 'Undo' : 'Done'}</button>
    </li>
  `).join('');

  list.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', () => {
      const i = Number(button.dataset.taskId);
      tasks[i].done = !tasks[i].done;
      renderTasks();
    });
  });
}

function onSearch() {
  const phrase = query('#globalSearch').value.trim().toLowerCase();

  if (!phrase) {
    renderActivities();
    renderProducts();
    renderUsers();
    return;
  }

  const filter = (arr) => arr.filter((entry) => entry.toLowerCase().includes(phrase));

  query('#activityList').innerHTML = filter(state.activities).map((item) => `<li>${item}</li>`).join('');
  query('#topProducts').innerHTML = filter(state.products).map((item, i) => `<li>${i + 1}. ${item}</li>`).join('');
  query('#usersTable').innerHTML = state.users
    .filter((user) => [user.name, user.email, user.status].some((v) => v.toLowerCase().includes(phrase)))
    .map((user) => `
      <tr>
        <td>${user.id}</td><td>${user.name}</td><td>${user.email}</td><td>${user.status}</td>
        <td><button class="btn-ghost" data-user-id="${user.id}">Toggle Status</button></td>
      </tr>
    `)
    .join('');

  query('#usersTable').querySelectorAll('button').forEach((btn) => {
    btn.addEventListener('click', () => {
      const id = Number(btn.dataset.userId);
      const user = state.users.find((x) => x.id === id);
      user.status = user.status === 'Active' ? 'Inactive' : 'Active';
      onSearch();
    });
  });
}

init();
