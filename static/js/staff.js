// staff.js - staff dashboard functionality
document.addEventListener('DOMContentLoaded', () => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  if (!token || role !== 'staff') {
    alert('Please login as staff');
    window.location = 'login.html';
    return;
  }
  document.getElementById('logoutBtn')?.addEventListener('click', () => {
    localStorage.clear(); window.location = 'login.html';
  });

  loadAppointments();
});

async function loadAppointments() {
  try {
    const res = await fetch(`${API_ROOT}/api/staff/appointments`, { headers: authHeader() });
    const arr = await res.json();
    const cont = document.getElementById('staffAppointments');
    if (!res.ok) { cont.innerText = arr.message || 'Error'; return; }
    if (!arr.length) { cont.innerText = 'No appointments found'; return; }
    cont.innerHTML = arr.map(a => `<div class="p-3 mb-2 border rounded">
      <div><strong>Appointment #${a.id}</strong> — <span class="small-muted">${a.status}</span></div>
      <div>Patient: ${escapeHtml(a.patient_name || a.patient_id)} • Doctor: ${escapeHtml(a.doctor_name || a.doctor_id)}</div>
      <div class="small-muted">${a.appointment_time}</div>
      <div class="mt-2 d-flex gap-2">
        <button class="btn btn-sm btn-outline-primary" onclick="generateLetter(${a.id})">Generate Letter</button>
        <button class="btn btn-sm btn-outline-secondary" onclick="markDone(${a.id}, this)">Mark done (client)</button>
      </div>
    </div>`).join('');
  } catch (err) { console.error(err); document.getElementById('staffAppointments').innerText = 'Network error'; }
}

async function generateLetter(appointment_id) {
  try {
    const res = await fetch(`${API_ROOT}/api/staff/generate_letter/${appointment_id}`, { headers: authHeader() });
    const j = await res.json();
    if (!res.ok) { alert(j.message || 'Error'); return; }
    // Create downloadable text file
    const blob = new Blob([j.letter || ''], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `appointment_${appointment_id}.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (err) { console.error(err); alert('Network error'); }
}

function markDone(appointment_id, btn) {
  // Note: backend does not provide a staff->mark-done endpoint in starter code.
  // This function removes the appointment card on the client to simulate marking done.
  if (!confirm('Mark this appointment done (client side)?')) return;
  const card = btn.closest('.border');
  if (card) card.remove();
  // To persist on server, add an endpoint /staff/mark_done and call it here.
}

function escapeHtml(s) {
  if (!s) return '';
  return s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
}
