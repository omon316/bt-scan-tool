// Simple fetch for live scan results
function loadLive() {
  fetch('/live')
    .then(resp => resp.json())
    .then(data => {
      const list = document.getElementById('device-list');
      if (!list) return;
      list.innerHTML = '';
      data.forEach(dev => {
        const li = document.createElement('li');
        li.textContent = dev.address + ' - ' + dev.name;
        list.appendChild(li);
      });
    });
}

// Auto-refresh live view
if (document.getElementById('device-list')) {
  setInterval(loadLive, 5000);
  loadLive();
}
