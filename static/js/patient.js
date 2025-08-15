// patient.js - patient dashboard functionality
document.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  if (!token || role !== 'patient') {
    alert('Please login as patient');
    window.location = 'login.html';
    return;
  }
  document.getElementById('logoutBtn')?.addEventListener('click', () => {
    localStorage.clear(); window.location = 'login.html';
  });

  loadProfile();
  loadDoctors();
  loadTreatments();
  loadBills();
});

async function loadProfile() {
  try {
    const res = await fetch(`${API_ROOT}/api/patient/profile`, { headers: authHeader() });
    const j = await res.json();
    if (!res.ok) { document.getElementById('profile').innerText = j.message || 'Error'; return; }
    const html = `Name: ${j.name || ''}\nEmail: ${j.email || ''}\nAge: ${j.age || ''}\nGender: ${j.gender || ''}\nContact: ${j.contact || ''}\nAddress: ${j.address || ''}`;
    document.getElementById('profile').innerText = html;
  } catch (err) {
    console.error(err); document.getElementById('profile').innerText = 'Network error';
  }
}

async function loadDoctors() {
  const spec = document.getElementById('filter_specialization')?.value || '';
  let url = `${API_ROOT}/api/patient/doctors`;
  if (spec) url += `?specialization=${encodeURIComponent(spec)}`;
  try {
    const res = await fetch(url, { headers: authHeader() });
    const list = await res.json();
    const cont = document.getElementById('doctorsList');
    if (!res.ok) { cont.innerText = list.message || 'Error loading doctors'; return; }
    if (!list.length) { cont.innerHTML = '<div class="small-muted">No doctors found</div>'; return; }
    cont.innerHTML = list.map(d => `
      <div class="col-md-6 mb-2">
        <div class="card p-2 d-flex align-items-center doctor-card">
          <div class="d-flex align-items-center">
            <img src="${d.photo || 'https://via.placeholder.com/60'}" alt="photo">
            <div>
              <div><strong>${d.name}</strong></div>
              <div class="small-muted">${d.specialization || ''} • ${d.qualification || ''}</div>
            </div>
          </div>
          <div class="mt-2 d-flex gap-2">
            <button class="btn btn-sm btn-primary" onclick="promptBook(${d.id})">Book</button>
            <button class="btn btn-sm btn-outline-secondary" onclick="copyDoctorId(${d.id})">Copy ID</button>
          </div>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.error(err); document.getElementById('doctorsList').innerText = 'Network error';
  }
}

function copyDoctorId(id) {
  navigator.clipboard?.writeText(String(id));
  alert('Doctor id copied: ' + id);
}

function promptBook(doctor_id) {
  const iso = prompt('Enter appointment datetime in ISO format (example: 2025-08-21T10:00:00)');
  if (!iso) return;
  bookAppointment(doctor_id, iso);
}

async function bookAppointment(doctor_id, appointment_time) {
  try {
    const res = await fetch(`${API_ROOT}/api/patient/appointment`, {
      method: 'POST',
      headers: Object.assign({'Content-Type':'application/json'}, authHeader()),
      body: JSON.stringify({ doctor_id, appointment_time })
    });
    const j = await res.json();
    if (!res.ok) { alert(j.message || 'Error'); return; }
    alert('Appointment requested. Message: ' + j.message);
  } catch (err) {
    console.error(err); alert('Network error booking');
  }
}

async function sendMessage(e) {
  e.preventDefault();
  const form = document.getElementById('msgForm');
  const fd = new FormData();
  fd.append('doctor_id', document.getElementById('msg_doctor_id').value);
  fd.append('content', document.getElementById('msg_content').value);
  const img = document.getElementById('msg_image').files[0];
  if (img) fd.append('image', img);
  try {
    const res = await fetch(`${API_ROOT}/api/patient/message`, {
      method: 'POST',
      headers: authHeader(),
      body: fd
    });
    const j = await res.json();
    if (!res.ok) { alert(j.message || 'Error sending message'); return; }
    alert('Message sent');
    form.reset();
  } catch (err) { console.error(err); alert('Network error'); }
  return false;
}

async function loadTreatments() {
  try {
    const res = await fetch(`${API_ROOT}/api/patient/treatments`, { headers: authHeader() });
    const arr = await res.json();
    const cont = document.getElementById('treatments');
    if (!res.ok) { cont.innerText = arr.message || 'Error'; return; }
    if (!arr.length) { cont.innerText = 'No treatments found'; return; }
    cont.innerHTML = arr.map(t => `<div class="mb-2 small"><strong>Doctor ID:</strong> ${t.doctor_id} • <strong>Start:</strong> ${t.start_date || '-'} • <strong>Days:</strong> ${t.days_estimate || '-'} • <strong>Status:</strong> ${t.status}<br/><strong>Medicines:</strong> ${t.medicines || '-'}</div>`).join('');
  } catch (err) { console.error(err); document.getElementById('treatments').innerText = 'Network error'; }
}

async function loadBills() {
  try {
    const res = await fetch(`${API_ROOT}/api/patient/bills`, { headers: authHeader() });
    const arr = await res.json();
    const cont = document.getElementById('bills');
    if (!res.ok) { cont.innerText = arr.message || 'Error'; return; }
    if (!arr.length) { cont.innerText = 'No bills yet'; return; }
    cont.innerHTML = arr.map(b => `<div class="mb-2"><strong>Amount:</strong> ₹${b.amount || 0} • <strong>Paid:</strong> ${b.paid ? 'Yes' : 'No'}<br/><small>${b.details || ''}</small><br/><small class="text-muted">${b.created_at || ''}</small></div>`).join('');
  } catch (err) { console.error(err); document.getElementById('bills').innerText = 'Network error'; }
}
