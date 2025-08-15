// auth.js - login & register logic
async function login(e) {
  e.preventDefault();
  const role = document.getElementById('role').value;
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  if (!email || !password) { alert('Email & password required'); return false; }

  try {
    const res = await fetch(`${API_ROOT}/api/login`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ email, password })
    });
    const j = await res.json();
    if (!res.ok) {
      alert(j.message || 'Login failed');
      return false;
    }
    localStorage.setItem('token', j.token);
    localStorage.setItem('role', j.role);
    localStorage.setItem('user_id', j.user_id || '');
    // redirect
    if (j.role === 'patient') window.location = 'patient_dashboard.html';
    else if (j.role === 'doctor') window.location = 'doctor_dashboard.html';
    else window.location = 'staff_dashboard.html';
  } catch (err) {
    console.error(err);
    alert('Network error');
  }
  return false;
}

function onRoleChange() {
  const r = document.getElementById('role').value;
  document.getElementById('patient-fields').style.display = r==='patient' ? 'block' : 'none';
  document.getElementById('doctor-fields').style.display = r==='doctor' ? 'block' : 'none';
  document.getElementById('staff-fields').style.display = r==='staff' ? 'block' : 'none';
}

async function register(e) {
  e.preventDefault();
  const role = document.getElementById('role').value;
  const name = document.getElementById('name').value.trim();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  if (!role || !name || !email || !password) { alert('Please fill required fields'); return false; }

  const form = new FormData();
  form.append('role', role);
  form.append('name', name);
  form.append('email', email);
  form.append('password', password);
  const photo = document.getElementById('photo').files[0];
  if (photo) form.append('photo', photo);

  if (role === 'patient') {
    form.append('address', document.getElementById('address').value || '');
    form.append('age', document.getElementById('age').value || '');
    form.append('contact', document.getElementById('contact').value || '');
  } else if (role === 'doctor') {
    form.append('specialization', document.getElementById('specialization').value || '');
    form.append('qualification', document.getElementById('qualification').value || '');
  } else {
    form.append('qualification', document.getElementById('staff-qualification').value || '');
  }

  try {
    const res = await fetch(`${API_ROOT}/api/register`, {
      method: 'POST',
      body: form
    });
    const j = await res.json();
    if (!res.ok) {
      alert(j.message || JSON.stringify(j));
      return false;
    }
    alert('Registration successful — please login');
    window.location = 'login.html';
  } catch (err) {
    console.error(err);
    alert('Network error during registration');
  }
  return false;
}
