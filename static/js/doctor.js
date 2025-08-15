// doctor.js - doctor dashboard functionality
document.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  if (!token || role !== 'doctor') {
    alert('Please login as doctor');
    window.location = 'login.html';
    return;
  }
  document.getElementById('logoutBtn')?.addEventListener('click', () => {
    localStorage.clear(); window.location = 'login.html';
  });

  loadPending();
  loadMyPatients();

  document.getElementById('prescribeForm')?.addEventListener('submit', (e) => prescribe(e));
});

async function loadPending() {
  try {
    const res = await fetch(`${API_ROOT}/api/doctor/appointments/pending`, { headers: authHeader() });
    const arr = await res.json();
    const cont = document.getElementById('pendingList');
    if (!res.ok) { cont.innerText = arr.message || 'Error'; return; }
    if (!arr.length) { cont.innerText = 'No pending appointments'; return; }
    cont.innerHTML = arr.map(a => `<div class="p-2 mb-2 border rounded">
        <div><strong>Appointment #${a.id}</strong> • Patient ID: ${a.patient_id}</div>
        <div class="small text-muted">${a.appointment_time}</div>
        <div class="mt-2"><button class="btn btn-sm btn-success" onclick="approve(${a.id})">Approve</button></div>
      </div>`).join('');
  } catch (err) { console.error(err); document.getElementById('pendingList').innerText = 'Network error'; }
}

async function approve(appt_id) {
  if (!confirm('Approve this appointment?')) return;
  try {
    const res = await fetch(`${API_ROOT}/api/doctor/appointments/approve`, {
      method: 'POST',
      headers: Object.assign({'Content-Type':'application/json'}, authHeader()),
      body: JSON.stringify({ appointment_id: appt_id })
    });
    const j = await res.json();
    if (!res.ok) { alert(j.message || 'Error approving'); return; }
    alert('Approved');
    loadPending();
  } catch (err) { console.error(err); alert('Network error'); }
}

async function loadMyPatients() {
  try {
    const res = await fetch(`${API_ROOT}/api/doctor/patients`, { headers: authHeader() });
    const arr = await res.json();
    const cont = document.getElementById('myPatients');
    if (!res.ok) { cont.innerText = arr.message || 'Error'; return; }
    if (!arr.length) { cont.innerText = 'No patients yet'; return; }
    cont.innerHTML = arr.map(p => `<div class="p-2 mb-2 border rounded">
        <div><strong>${p.name}</strong> • ID: ${p.id}</div>
        <div class="small-muted">Contact: ${p.contact || '-'}</div>
      </div>`).join('');
  } catch (err) { console.error(err); document.getElementById('myPatients').innerText = 'Network error'; }
}

async function prescribe(e) {
  e.preventDefault();
  const patient_id = document.getElementById('pres_patient_id').value;
  const content = document.getElementById('pres_content').value;
  const file = document.getElementById('pres_file').files[0];

  if (!patient_id || !content) { alert('Patient ID and content required'); return false; }
  const fd = new FormData();
  fd.append('patient_id', patient_id);
  fd.append('content', content);
  if (file) fd.append('file', file);

  try {
    const res = await fetch(`${API_ROOT}/api/doctor/prescribe`, {
      method: 'POST',
      headers: authHeader(),
      body: fd
    });
    const j = await res.json();
    if (!res.ok) { alert(j.message || 'Error'); return; }
    alert('Prescription sent');
    e.target.reset();
  } catch (err) { console.error(err); alert('Network error'); }
  return false;
}
