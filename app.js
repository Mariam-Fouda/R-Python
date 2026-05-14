const API = '';

let token = localStorage.getItem('token');
let currentUser = JSON.parse(localStorage.getItem('user') || 'null');
let examTimer = null;
let questionCounter = 0;

// ===================== INIT =====================
window.onload = () => {
  if (token && currentUser) {
    showDashboard();
  }
};

// ===================== AUTH =====================
function showTab(tab) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.getElementById(`${tab}-tab`).classList.add('active');
  event.target.classList.add('active');
}

async function login() {
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  const errEl = document.getElementById('login-error');
  errEl.textContent = '';

  if (!username || !password) { errEl.textContent = 'Please fill all fields'; return; }

  try {
    const res = await fetch(`${API}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) { errEl.textContent = data.detail || 'Login failed'; return; }

    token = data.access_token;
    currentUser = data.user;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(currentUser));
    showDashboard();
  } catch (e) {
    errEl.textContent = 'Connection error. Is the backend running?';
  }
}

async function register() {
  const username = document.getElementById('reg-username').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value;
  const role = document.getElementById('reg-role').value;
  const errEl = document.getElementById('register-error');
  const sucEl = document.getElementById('register-success');
  errEl.textContent = ''; sucEl.textContent = '';

  if (!username || !email || !password) { errEl.textContent = 'Please fill all fields'; return; }

  try {
    const res = await fetch(`${API}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password, role }),
    });
    const data = await res.json();
    if (!res.ok) { errEl.textContent = data.detail || 'Registration failed'; return; }
    sucEl.textContent = `✅ Registered as ${data.role}! You can now login.`;
    document.getElementById('login-username').value = username;
  } catch (e) {
    errEl.textContent = 'Connection error.';
  }
}

function logout() {
  token = null; currentUser = null;
  localStorage.removeItem('token'); localStorage.removeItem('user');
  if (examTimer) clearInterval(examTimer);
  showPage('auth-page');
}

// ===================== PAGES =====================
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function showDashboard() {
  if (currentUser.role === 'admin') {
    showPage('admin-page');
    loadAdminExams();
  } else {
    showPage('student-page');
    loadStudentExams();
  }
}

function showSection(id) {
  document.querySelectorAll('#admin-page .section').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  if (id === 'admin-results') loadAllResults();
  if (id === 'admin-monitoring') loadMonitoring();
}

function showStudentSection(id) {
  document.querySelectorAll('#student-page .section').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  if (id === 'student-results') loadMyResults();
  if (id === 'student-exams') loadStudentExams();
}

// ===================== ADMIN: EXAMS =====================
async function loadAdminExams() {
  const res = await apiFetch('/api/exams/');
  const exams = await res.json();
  const el = document.getElementById('exams-list');
  if (!exams.length) { el.innerHTML = '<p style="color:#6b7280">No exams yet.</p>'; return; }
  el.innerHTML = exams.map(e => `
    <div class="card">
      <h3>${e.title}</h3>
      <p>📋 ${e.question_count || 0} questions</p>
      <p>⏱ ${e.duration_minutes} minutes</p>
      <p>${e.description || ''}</p>
      <div class="card-actions">
        <button class="btn-danger" onclick="deleteExam(${e.id})">Delete</button>
        <button class="btn-secondary" onclick="viewAnalytics(${e.id}, '${e.title}')">Analytics</button>
      </div>
    </div>
  `).join('');
}

function showCreateExam() {
  document.getElementById('create-exam-form').classList.remove('hidden');
  document.getElementById('questions-container').innerHTML = '';
  questionCounter = 0;
  addQuestion();
}
function hideCreateExam() {
  document.getElementById('create-exam-form').classList.add('hidden');
}

function addQuestion() {
  questionCounter++;
  const qc = document.getElementById('questions-container');
  const div = document.createElement('div');
  div.className = 'question-block';
  div.id = `q-${questionCounter}`;
  div.innerHTML = `
    <div class="q-header">
      <strong>Question ${questionCounter}</strong>
      <button class="btn-danger" onclick="removeQuestion(${questionCounter})">Remove</button>
    </div>
    <textarea class="q-text-${questionCounter}" placeholder="Question text *" rows="2" style="width:100%;margin-bottom:8px"></textarea>
    <select class="q-type-${questionCounter}" onchange="toggleOptions(${questionCounter}, this.value)" style="width:100%;margin-bottom:8px">
      <option value="multiple_choice">Multiple Choice</option>
      <option value="true_false">True / False</option>
    </select>
    <div class="options-div-${questionCounter}">
      <div class="options-grid">
        <input class="q-oa-${questionCounter}" placeholder="Option A *" />
        <input class="q-ob-${questionCounter}" placeholder="Option B *" />
        <input class="q-oc-${questionCounter}" placeholder="Option C" />
        <input class="q-od-${questionCounter}" placeholder="Option D" />
      </div>
      <select class="q-ans-${questionCounter}" style="width:100%;margin-top:8px">
        <option value="A">A is correct</option>
        <option value="B">B is correct</option>
        <option value="C">C is correct</option>
        <option value="D">D is correct</option>
      </select>
    </div>
    <div class="tf-div-${questionCounter}" style="display:none">
      <select class="q-tf-${questionCounter}" style="width:100%;margin-top:8px">
        <option value="T">True</option>
        <option value="F">False</option>
      </select>
    </div>
    <input type="number" class="q-pts-${questionCounter}" value="1" min="1" placeholder="Points" style="width:100%;margin-top:8px" />
  `;
  qc.appendChild(div);
}

function removeQuestion(n) {
  document.getElementById(`q-${n}`)?.remove();
}

function toggleOptions(n, type) {
  const opts = document.querySelector(`.options-div-${n}`);
  const tf = document.querySelector(`.tf-div-${n}`);
  if (type === 'true_false') { opts.style.display='none'; tf.style.display='block'; }
  else { opts.style.display='block'; tf.style.display='none'; }
}

async function createExam() {
  const title = document.getElementById('exam-title').value.trim();
  const description = document.getElementById('exam-desc').value.trim();
  const duration = parseInt(document.getElementById('exam-duration').value);
  const msgEl = document.getElementById('create-exam-msg');
  msgEl.textContent = '';

  if (!title) { msgEl.style.color='red'; msgEl.textContent='Title is required'; return; }

  const questions = [];
  for (let i = 1; i <= questionCounter; i++) {
    const textEl = document.querySelector(`.q-text-${i}`);
    if (!textEl || !textEl.closest('#questions-container')) continue;
    const text = textEl.value.trim();
    if (!text) continue;
    const type = document.querySelector(`.q-type-${i}`).value;
    const pts = parseInt(document.querySelector(`.q-pts-${i}`).value) || 1;

    if (type === 'true_false') {
      questions.push({ text, question_type: 'true_false', correct_answer: document.querySelector(`.q-tf-${i}`).value, points: pts });
    } else {
      questions.push({
        text, question_type: 'multiple_choice',
        option_a: document.querySelector(`.q-oa-${i}`).value,
        option_b: document.querySelector(`.q-ob-${i}`).value,
        option_c: document.querySelector(`.q-oc-${i}`).value || null,
        option_d: document.querySelector(`.q-od-${i}`).value || null,
        correct_answer: document.querySelector(`.q-ans-${i}`).value,
        points: pts,
      });
    }
  }

  const res = await apiFetch('/api/exams/', {
    method: 'POST',
    body: JSON.stringify({ title, description, duration_minutes: duration, questions }),
  });
  const data = await res.json();
  if (res.ok) {
    msgEl.style.color='green'; msgEl.textContent=`✅ Exam created! ID: ${data.exam_id}`;
    hideCreateExam(); loadAdminExams();
  } else {
    msgEl.style.color='red'; msgEl.textContent = data.detail || 'Error creating exam';
  }
}

async function deleteExam(id) {
  if (!confirm('Delete this exam?')) return;
  await apiFetch(`/api/exams/${id}`, { method: 'DELETE' });
  loadAdminExams();
}

async function viewAnalytics(examId, title) {
  const res = await apiFetch(`/api/results/analytics/${examId}`);
  const data = await res.json();
  alert(`📊 Analytics: ${title}\n\nAttempts: ${data.total_attempts}\nAvg Score: ${data.average_percentage?.toFixed(1)}%\nPass Rate: ${data.pass_rate?.toFixed(1)}%\nHighest: ${data.highest_score?.toFixed(1)}%\nLowest: ${data.lowest_score?.toFixed(1)}%`);
}

// ===================== ADMIN: RESULTS =====================
async function loadAllResults() {
  const res = await apiFetch('/api/results/admin/all');
  const results = await res.json();
  const el = document.getElementById('all-results-table');
  if (!results.length) { el.innerHTML = '<p style="color:#6b7280;margin-top:16px">No submissions yet.</p>'; return; }
  el.innerHTML = `<table>
    <thead><tr><th>#</th><th>Student</th><th>Exam</th><th>Score</th><th>Status</th><th>Date</th></tr></thead>
    <tbody>${results.map((r,i) => `
      <tr>
        <td>${i+1}</td>
        <td>${r.student_name || r.student_id}</td>
        <td>${r.exam_title || r.exam_id}</td>
        <td>${r.percentage?.toFixed(1)}%</td>
        <td><span class="badge ${r.passed?'pass':'fail'}">${r.passed?'Passed':'Failed'}</span></td>
        <td>${new Date(r.completed_at).toLocaleDateString()}</td>
      </tr>`).join('')}
    </tbody>
  </table>`;
}

// ===================== ADMIN: MONITORING =====================
async function loadMonitoring() {
  const res = await apiFetch('/api/monitoring/stats');
  const data = await res.json();
  const statsEl = document.getElementById('monitoring-stats');
  statsEl.innerHTML = `
    <div class="stat-card"><div class="stat-val">${data.users?.total||0}</div><div class="stat-label">Total Users</div></div>
    <div class="stat-card"><div class="stat-val">${data.users?.students||0}</div><div class="stat-label">Students</div></div>
    <div class="stat-card"><div class="stat-val">${data.exams?.total||0}</div><div class="stat-label">Total Exams</div></div>
    <div class="stat-card"><div class="stat-val">${data.submissions?.total||0}</div><div class="stat-label">Submissions</div></div>
    <div class="stat-card"><div class="stat-val">${data.submissions?.pass_rate||0}%</div><div class="stat-label">Pass Rate</div></div>
    <div class="stat-card"><div class="stat-val" style="font-size:1rem">${data.redis?.connected?'🟢 Online':'🔴 Offline'}</div><div class="stat-label">Redis Cache</div></div>
  `;

  const logsRes = await apiFetch('/api/monitoring/logs');
  const logsData = await logsRes.json();
  document.getElementById('logs-container').textContent = logsData.logs?.slice(-50).join('\n') || 'No logs';
}

// ===================== STUDENT: EXAMS =====================
async function loadStudentExams() {
  const res = await apiFetch('/api/exams/');
  const exams = await res.json();
  const el = document.getElementById('student-exams-list');
  if (!exams.length) { el.innerHTML = '<p style="color:#6b7280">No exams available.</p>'; return; }
  el.innerHTML = exams.map(e => `
    <div class="card">
      <h3>${e.title}</h3>
      <p>📋 ${e.question_count || 0} questions</p>
      <p>⏱ ${e.duration_minutes} minutes</p>
      <p>${e.description || ''}</p>
      <div class="card-actions">
        <button class="btn-primary" onclick="startExam(${e.id})">Take Exam</button>
      </div>
    </div>
  `).join('');
}

async function startExam(examId) {
  const res = await apiFetch(`/api/exams/${examId}`);
  const exam = await res.json();

  // Switch to take exam section
  document.querySelectorAll('#student-page .section').forEach(s => s.classList.remove('active'));
  document.getElementById('take-exam-section').classList.add('active');

  let timeLeft = exam.duration_minutes * 60;
  const container = document.getElementById('exam-container');

  function renderExam() {
    const mins = String(Math.floor(timeLeft / 60)).padStart(2, '0');
    const secs = String(timeLeft % 60).padStart(2, '0');
    container.innerHTML = `
      <div class="exam-header">
        <span class="timer" id="timer-display">⏱ ${mins}:${secs}</span>
        <h2>${exam.title}</h2>
        <p style="color:#6b7280;margin-top:8px">${exam.description || ''}</p>
      </div>
      ${(exam.questions || []).map((q, idx) => `
        <div class="question-card">
          <div class="q-text">Q${idx+1}. ${q.text} <span style="color:#6b7280;font-size:0.85rem">(${q.points} pt${q.points>1?'s':''})</span></div>
          ${q.question_type === 'true_false' ? `
            <label class="option-label"><input type="radio" name="q${q.id}" value="T" /> True</label>
            <label class="option-label"><input type="radio" name="q${q.id}" value="F" /> False</label>
          ` : `
            ${q.option_a ? `<label class="option-label"><input type="radio" name="q${q.id}" value="A" /> A. ${q.option_a}</label>` : ''}
            ${q.option_b ? `<label class="option-label"><input type="radio" name="q${q.id}" value="B" /> B. ${q.option_b}</label>` : ''}
            ${q.option_c ? `<label class="option-label"><input type="radio" name="q${q.id}" value="C" /> C. ${q.option_c}</label>` : ''}
            ${q.option_d ? `<label class="option-label"><input type="radio" name="q${q.id}" value="D" /> D. ${q.option_d}</label>` : ''}
          `}
        </div>
      `).join('')}
      <div style="display:flex;gap:12px;margin-top:16px;margin-bottom:32px">
        <button class="btn-primary" onclick="submitExam(${examId}, ${JSON.stringify(exam.questions.map(q=>q.id))})">Submit Exam</button>
        <button class="btn-cancel" onclick="showStudentSection('student-exams')">Cancel</button>
      </div>
    `;
  }

  renderExam();

  if (examTimer) clearInterval(examTimer);
  examTimer = setInterval(() => {
    timeLeft--;
    const timerEl = document.getElementById('timer-display');
    if (timerEl) {
      const mins = String(Math.floor(timeLeft / 60)).padStart(2, '0');
      const secs = String(timeLeft % 60).padStart(2, '0');
      timerEl.textContent = `⏱ ${mins}:${secs}`;
      if (timeLeft <= 60) timerEl.style.color = '#dc2626';
    }
    if (timeLeft <= 0) {
      clearInterval(examTimer);
      submitExam(examId, exam.questions.map(q => q.id));
    }
  }, 1000);
}

async function submitExam(examId, questionIds) {
  if (examTimer) clearInterval(examTimer);
  const answers = questionIds.map(qid => {
    const selected = document.querySelector(`input[name="q${qid}"]:checked`);
    return { question_id: qid, selected_answer: selected ? selected.value : 'A' };
  });

  const res = await apiFetch('/api/results/submit', {
    method: 'POST',
    body: JSON.stringify({ exam_id: examId, answers }),
  });
  const data = await res.json();

  const container = document.getElementById('exam-container');
  if (res.ok) {
    const passed = data.passed;
    container.innerHTML = `
      <div class="result-summary">
        <div class="big-score ${passed ? 'pass' : 'fail'}">${data.percentage?.toFixed(1)}%</div>
        <h2 style="margin:12px 0">${passed ? '🎉 Passed!' : '❌ Failed'}</h2>
        <p>Score: ${data.earned_points} / ${data.total_points} points</p>
      </div>
      <div style="text-align:center;margin-top:20px">
        <button class="btn-primary" onclick="showStudentSection('student-results')">View My Results</button>
        <button class="btn-secondary" style="margin-left:12px" onclick="showStudentSection('student-exams')">Back to Exams</button>
      </div>
    `;
  } else {
    container.innerHTML = `<div class="card"><p style="color:red">${data.detail || 'Submission failed'}</p><button class="btn-secondary" onclick="showStudentSection('student-exams')">Back</button></div>`;
  }
}

// ===================== STUDENT: RESULTS =====================
async function loadMyResults() {
  const res = await apiFetch('/api/results/my');
  const results = await res.json();
  const el = document.getElementById('my-results-table');
  if (!results.length) { el.innerHTML = '<p style="color:#6b7280;margin-top:16px">No results yet. Take an exam first!</p>'; return; }
  el.innerHTML = `<table>
    <thead><tr><th>#</th><th>Exam</th><th>Score</th><th>Status</th><th>Date</th></tr></thead>
    <tbody>${results.map((r,i) => `
      <tr>
        <td>${i+1}</td>
        <td>${r.exam_title || r.exam_id}</td>
        <td>${r.percentage?.toFixed(1)}% (${r.earned_points}/${r.total_points})</td>
        <td><span class="badge ${r.passed?'pass':'fail'}">${r.passed?'Passed':'Failed'}</span></td>
        <td>${new Date(r.completed_at).toLocaleDateString()}</td>
      </tr>`).join('')}
    </tbody>
  </table>`;
}

// ===================== API HELPER =====================
async function apiFetch(url, options = {}) {
  return fetch(`${API}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
}
