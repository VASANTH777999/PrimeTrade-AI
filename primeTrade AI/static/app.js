const apiBase = "/api/v1";

const navLogin = document.getElementById("nav-login");
const navRegister = document.getElementById("nav-register");
const navDashboard = document.getElementById("nav-dashboard");
const navLogout = document.getElementById("nav-logout");

const formRegister = document.getElementById("form-register");
const formLogin = document.getElementById("form-login");
const formTask = document.getElementById("form-task");
const toggleAll = document.getElementById("toggle-all");
const registerMessage = document.getElementById("register-message");
const loginMessage = document.getElementById("login-message");
const taskMessage = document.getElementById("task-message");
const taskList = document.getElementById("task-list");

function token() { return localStorage.getItem("pta_token") || ""; }
function setToken(t) { localStorage.setItem("pta_token", t); }
function clearToken() { localStorage.removeItem("pta_token"); }

function updateNav() {
  const loggedIn = !!token();
  if (navLogin) navLogin.classList.toggle("hidden", loggedIn);
  if (navRegister) navRegister.classList.toggle("hidden", loggedIn);
  if (navDashboard) navDashboard.classList.toggle("hidden", !loggedIn);
  if (navLogout) navLogout.classList.toggle("hidden", !loggedIn);
}

if (navLogout) {
  navLogout.addEventListener("click", () => {
    clearToken();
    updateNav();
    window.location.href = "/";
  });
}

if (formRegister) {
  formRegister.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (registerMessage) registerMessage.textContent = "";
    const email = document.getElementById("register-email").value.trim();
    const password = document.getElementById("register-password").value;
    try {
      const res = await fetch(`${apiBase}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (res.ok) {
        if (registerMessage) {
          registerMessage.textContent = "Registered successfully. Redirecting to login...";
          registerMessage.className = "mt-4 text-sm text-green-600";
        }
        setTimeout(() => { window.location.href = "/login"; }, 600);
      } else {
        const d = await res.json().catch(() => ({}));
        if (registerMessage) {
          registerMessage.textContent = d.detail || "Registration failed";
          registerMessage.className = "mt-4 text-sm text-red-600";
        }
      }
    } catch (_) {
      if (registerMessage) {
        registerMessage.textContent = "Network error";
        registerMessage.className = "mt-4 text-sm text-red-600";
      }
    }
  });
}

if (formLogin) {
  formLogin.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (loginMessage) loginMessage.textContent = "";
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-password").value;
    try {
      const res = await fetch(`${apiBase}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.access_token) {
        setToken(data.access_token);
        updateNav();
        window.location.href = "/dashboard";
      } else {
        if (loginMessage) {
          loginMessage.textContent = data.detail || "Login failed";
          loginMessage.className = "mt-4 text-sm text-red-600";
        }
      }
    } catch (_) {
      if (loginMessage) {
        loginMessage.textContent = "Network error";
        loginMessage.className = "mt-4 text-sm text-red-600";
      }
    }
  });
}

if (formTask) {
  formTask.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (taskMessage) taskMessage.textContent = "";
    const title = document.getElementById("task-title").value.trim();
    const description = document.getElementById("task-desc").value.trim();
    try {
      const res = await fetch(`${apiBase}/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token()}` },
        body: JSON.stringify({ title, description }),
      });
      if (res.ok) {
        document.getElementById("task-title").value = "";
        document.getElementById("task-desc").value = "";
        if (taskMessage) {
          taskMessage.textContent = "Task added";
          taskMessage.className = "mt-4 text-sm text-green-600";
        }
        loadTasks();
      } else {
        const d = await res.json().catch(() => ({}));
        if (taskMessage) {
          taskMessage.textContent = d.detail || "Failed to add task";
          taskMessage.className = "mt-4 text-sm text-red-600";
        }
      }
    } catch (_) {
      if (taskMessage) {
        taskMessage.textContent = "Network error";
        taskMessage.className = "mt-4 text-sm text-red-600";
      }
    }
  });
}

if (toggleAll) toggleAll.addEventListener("change", () => loadTasks());

async function loadTasks() {
  if (!taskList) return;
  taskList.innerHTML = "";
  const all = toggleAll && toggleAll.checked ? "?all=true" : "";
  try {
    const res = await fetch(`${apiBase}/tasks${all}`, { headers: { "Authorization": `Bearer ${token()}` } });
    const items = await res.json().catch(() => []);
    if (!Array.isArray(items)) return;
    items.forEach(renderTask);
  } catch (_) {}
}

function renderTask(t) {
  const li = document.createElement("li");
  li.className = "border rounded px-4 py-3 flex items-center justify-between";
  const left = document.createElement("div");
  left.className = "flex-1";
  const title = document.createElement("div");
  title.className = "font-semibold";
  title.textContent = t.title;
  const desc = document.createElement("div");
  desc.className = "text-sm text-gray-600";
  desc.textContent = t.description || "";
  const meta = document.createElement("span");
  const statusClass = t.status === "done" ? "badge badge-done" : (t.status === "undone" ? "badge badge-undone" : "badge badge-pending");
  meta.className = statusClass;
  meta.textContent = t.status;
  left.appendChild(title);
  left.appendChild(desc);
  left.appendChild(meta);
  const right = document.createElement("div");
  right.className = "flex items-center space-x-2";
  const doneBtn = document.createElement("button");
  doneBtn.className = "btn text-sm bg-green-600 hover:bg-green-700 text-white";
  doneBtn.textContent = "Mark Done";
  doneBtn.addEventListener("click", () => updateTask(t.id, { status: "done" }));
  const undoBtn = document.createElement("button");
  undoBtn.className = "btn text-sm bg-blue-600 hover:bg-blue-700 text-white";
  undoBtn.textContent = "Undo";
  undoBtn.addEventListener("click", () => updateTask(t.id, { status: "undone" }));
  const editBtn = document.createElement("button");
  editBtn.className = "btn text-sm bg-yellow-500 hover:bg-yellow-600 text-white";
  editBtn.textContent = "Edit";
  editBtn.addEventListener("click", () => {
    const newTitle = prompt("Update title", t.title) || t.title;
    const newDesc = prompt("Update description", t.description || "") || t.description || "";
    updateTask(t.id, { title: newTitle, description: newDesc, status: "undone" });
  });
  const delBtn = document.createElement("button");
  delBtn.className = "btn text-sm bg-red-600 hover:bg-red-700 text-white";
  delBtn.textContent = "Delete";
  delBtn.addEventListener("click", () => deleteTask(t.id));
  right.appendChild(doneBtn);
  right.appendChild(undoBtn);
  right.appendChild(editBtn);
  right.appendChild(delBtn);
  li.appendChild(left);
  li.appendChild(right);
  taskList.appendChild(li);
}

async function updateTask(id, payload) {
  try {
    const res = await fetch(`${apiBase}/tasks/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token()}` },
      body: JSON.stringify(payload),
    });
    if (res.ok) loadTasks();
  } catch (_) {}
}

async function deleteTask(id) {
  try {
    const res = await fetch(`${apiBase}/tasks/${id}`, {
      method: "DELETE",
      headers: { "Authorization": `Bearer ${token()}` },
    });
    if (res.status === 204) loadTasks();
  } catch (_) {}
}

updateNav();
const path = window.location.pathname;
const loggedIn = !!token();
if (path === "/dashboard" && !loggedIn) {
  window.location.href = "/login";
} else if ((path === "/login" || path === "/register") && loggedIn) {
  window.location.href = "/dashboard";
} else if (path === "/dashboard" && loggedIn) {
  loadTasks();
}
