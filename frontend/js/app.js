async function loadInventory() {
  try {
    const res = await fetch('http://localhost:3000/api/equipment');
    const data = await res.json();

    const tbody = document.querySelector('#inventoryTable tbody');
    tbody.innerHTML = '';

    data.forEach(item => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${item.name}</td>
        <td>${item.description || '-'}</td>
        <td>${item.brand || '-'}</td>
        <td>${item.quantity}</td>
        <td>${item.image ? `<img src="http://localhost:3000/${item.image}" alt="${item.name}">` : '-'}</td>
      `;
      tbody.appendChild(row);
    });
  } catch (err) {
    console.error('Erro ao carregar inventário:', err);
  }
}

document.addEventListener('DOMContentLoaded', loadInventory);