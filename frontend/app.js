/**
 * PharmaMS - Medicine Store Management System Client Controller
 * Provides SPA navigation, reactive cart calculation, REST API calls,
 * modal dialogs, and real-time alerts.
 */

// Auto-detect API base (works when served from backend or standalone file)
const API_BASE = window.location.protocol === 'file:' 
  ? 'http://localhost:8000/api' 
  : '/api';

// Reactive App State
const state = {
  dashboard: {},
  medicines: [],
  customers: [],
  suppliers: [],
  prescriptions: [],
  sales: [],
  bills: [],
  cart: [] // [{ medicine, quantity, line_total }]
};

let currentReceiptText = "";

// ==========================================================================
// 1. API SERVICE HELPERS
// ==========================================================================

async function fetchApi(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      ...options
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      const errorMsg = data.error || `HTTP error! Status: ${res.status}`;
      throw new Error(errorMsg);
    }

    return data;
  } catch (err) {
    console.error(`API Call failed [${endpoint}]:`, err);
    throw err;
  }
}

function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const icon = type === 'success' ? '✓' : type === 'error' ? '⚠️' : 'ℹ️';
  toast.innerHTML = `<span style="font-weight:700; font-size:1.1rem;">${icon}</span><span>${escapeHtml(message)}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(40px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function escapeHtml(str) {
  return String(str ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}

// ==========================================================================
// 2. DATA INITIALIZATION & REFRESH
// ==========================================================================

async function loadAllData() {
  try {
    const [dash, meds, custs, sups, rxs, sales, bills] = await Promise.all([
      fetchApi('/dashboard'),
      fetchApi('/medicines'),
      fetchApi('/customers'),
      fetchApi('/suppliers'),
      fetchApi('/prescriptions'),
      fetchApi('/sales'),
      fetchApi('/bills')
    ]);

    state.dashboard = dash;
    state.medicines = meds;
    state.customers = custs;
    state.suppliers = sups;
    state.prescriptions = rxs;
    state.sales = sales;
    state.bills = bills;

    updateBackendStatus(true);
    renderDashboard();
    renderMedicinesTable();
    populateCategoryDropdowns();
    renderPosCustomerSelect();
    renderPosPrescriptionSelect();
    renderPosGrid();
    renderCustomersTable();
    renderSuppliersTable();
    renderPrescriptionsTable();
    renderBillsTable();

  } catch (err) {
    updateBackendStatus(false, err.message);
    showToast(`Failed to connect to backend: ${err.message}`, 'error');
  }
}

function updateBackendStatus(isOnline, err = "") {
  const txt = document.getElementById('backend-status-text');
  const dot = document.querySelector('.status-dot');
  if (isOnline) {
    txt.textContent = "Connected: REST API";
    dot.style.backgroundColor = "#34d399";
    dot.style.boxShadow = "0 0 8px #34d399";
  } else {
    txt.textContent = "Offline (Run backend.py)";
    dot.style.backgroundColor = "#ef4444";
    dot.style.boxShadow = "0 0 8px #ef4444";
  }
}

async function saveStoreData() {
  try {
    await fetchApi('/save', { method: 'POST', body: '{}' });
    showToast('All medicine store records saved to disk!');
  } catch (err) {
    showToast(`Save failed: ${err.message}`, 'error');
  }
}

// ==========================================================================
// 3. NAVIGATION & TABS
// ==========================================================================

function setupNavigation() {
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
      const tabId = item.getAttribute('data-tab');
      if (tabId) switchTab(tabId);
    });
  });
}

function switchTab(tabId) {
  // Update sidebar active state
  document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
  const activeLink = document.querySelector(`.nav-item[data-tab="${tabId}"]`);
  if (activeLink) activeLink.classList.add('active');

  // Update Panes
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  const targetPane = document.getElementById(tabId);
  if (targetPane) targetPane.classList.add('active');

  // Update Page Title
  const titles = {
    'tab-dashboard': 'Dashboard Overview',
    'tab-pos': 'Point of Sale (POS) & Billing',
    'tab-medicines': 'Medicines & Inventory Management',
    'tab-customers': 'Customer Directory',
    'tab-suppliers': 'Supplier Directory',
    'tab-prescriptions': 'Prescription Verification',
    'tab-bills': 'Invoices & Receipts History',
    'tab-reports': 'Reports & CSV Exports',
    'tab-docs': 'System OOP Architecture'
  };
  document.getElementById('page-title').textContent = titles[tabId] || 'Medicine Store System';

  // Close sidebar on mobile
  if (window.innerWidth <= 768) {
    document.getElementById('sidebar').classList.remove('open');
  }
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// ==========================================================================
// 4. DASHBOARD RENDERER
// ==========================================================================

function renderDashboard() {
  const d = state.dashboard;
  document.getElementById('kpi-revenue').textContent = `₹${Number(d.revenue || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
  document.getElementById('kpi-medicines').textContent = d.medicines || 0;
  document.getElementById('kpi-low-stock').textContent = d.low_stock_count || 0;
  document.getElementById('kpi-expired').textContent = d.expired_count || 0;

  // Sidebar badge for stock warnings
  const alertCount = (d.low_stock_count || 0) + (d.expired_count || 0);
  const badge = document.getElementById('sidebar-alert-badge');
  if (alertCount > 0) {
    badge.textContent = alertCount;
    badge.style.display = 'inline-block';
  } else {
    badge.style.display = 'none';
  }

  // Dashboard alert banner
  const banner = document.getElementById('dashboard-alert-banner');
  const bannerText = document.getElementById('alert-banner-text');
  if (alertCount > 0) {
    banner.style.display = 'flex';
    bannerText.textContent = `You have ${d.low_stock_count} low-stock medicine(s) and ${d.expired_count} expired medication(s) requiring attention.`;
  } else {
    banner.style.display = 'none';
  }

  // Recent Sales Table
  const tbody = document.getElementById('dashboard-recent-sales');
  const recent = d.recent_sales || [];
  if (!recent.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:24px; color:var(--text-muted);">No sales processed yet.</td></tr>';
    return;
  }

  tbody.innerHTML = recent.map(s => `
    <tr>
      <td><strong>${escapeHtml(s.sale_id)}</strong></td>
      <td>${escapeHtml(s.customer_name)}</td>
      <td>${(s.items || []).map(i => `${escapeHtml(i.name)} (x${i.quantity})`).join(', ')}</td>
      <td><strong style="color:var(--primary)">₹${Number(s.total).toFixed(2)}</strong></td>
      <td>${escapeHtml(s.sale_date)}</td>
      <td>
        <button class="btn btn-sm btn-outline" onclick="viewBillBySaleId('${escapeHtml(s.sale_id)}')">View Bill</button>
      </td>
    </tr>
  `).join('');
}

// ==========================================================================
// 5. MEDICINES CATALOG & INVENTORY TABLE
// ==========================================================================

function populateCategoryDropdowns() {
  const categories = Array.from(new Set(state.medicines.map(m => m.category).filter(Boolean))).sort();
  
  const medCatFilter = document.getElementById('med-filter-category');
  const posCatFilter = document.getElementById('pos-category-filter');

  const optionsHtml = '<option value="All">All Categories</option>' + 
    categories.map(c => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join('');

  if (medCatFilter) medCatFilter.innerHTML = optionsHtml;
  if (posCatFilter) posCatFilter.innerHTML = optionsHtml;
}

function renderMedicinesTable(itemsToRender = null) {
  const tbody = document.getElementById('medicines-table-body');
  const list = itemsToRender || state.medicines;

  if (!list.length) {
    tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding:30px; color:var(--text-muted);">No medicines found matching criteria.</td></tr>';
    return;
  }

  tbody.innerHTML = list.map(m => {
    let statusBadge = '<span class="badge badge-success">In Stock</span>';
    if (m.is_expired) {
      statusBadge = '<span class="badge badge-danger">Expired</span>';
    } else if (m.quantity <= m.reorder_level) {
      statusBadge = '<span class="badge badge-warning">Low Stock</span>';
    }

    const rxBadge = m.requires_prescription 
      ? '<span class="badge badge-danger">Rx Required</span>' 
      : '<span class="badge badge-neutral">OTC</span>';

    return `
      <tr>
        <td><code>${escapeHtml(m.medicine_id)}</code></td>
        <td><strong>${escapeHtml(m.name)}</strong></td>
        <td>${escapeHtml(m.company)}</td>
        <td><span class="badge badge-info">${escapeHtml(m.category)}</span></td>
        <td>₹${Number(m.price).toFixed(2)}</td>
        <td><strong>${m.quantity}</strong></td>
        <td>${escapeHtml(m.expiry_date)}</td>
        <td>${rxBadge}</td>
        <td>${statusBadge}</td>
        <td>
          <div class="table-actions">
            <button class="btn btn-sm btn-outline" title="Adjust Stock Quantity" onclick="openStockAdjustModal('${escapeHtml(m.medicine_id)}')">± Stock</button>
            <button class="btn btn-sm btn-secondary" title="Edit Medicine" onclick="openEditMedicineModal('${escapeHtml(m.medicine_id)}')">Edit</button>
            <button class="btn btn-sm btn-danger" title="Delete Medicine" onclick="deleteMedicine('${escapeHtml(m.medicine_id)}')">✕</button>
          </div>
        </td>
      </tr>
    `;
  }).join('');
}

function filterMedicinesTable() {
  const search = document.getElementById('med-search').value.toLowerCase().trim();
  const cat = document.getElementById('med-filter-category').value;
  const status = document.getElementById('med-filter-status').value;

  const filtered = state.medicines.filter(m => {
    const matchesSearch = !search || 
      m.name.toLowerCase().includes(search) || 
      m.medicine_id.toLowerCase().includes(search) || 
      m.company.toLowerCase().includes(search);

    const matchesCat = (cat === 'All') || (m.category === cat);

    let matchesStatus = true;
    if (status === 'low_stock') {
      matchesStatus = m.quantity <= m.reorder_level && !m.is_expired;
    } else if (status === 'expired') {
      matchesStatus = m.is_expired;
    }

    return matchesSearch && matchesCat && matchesStatus;
  });

  renderMedicinesTable(filtered);
}

// Add/Edit Medicine Modal Handlers
function openEditMedicineModal(medId) {
  const med = state.medicines.find(m => m.medicine_id === medId);
  if (!med) return;

  document.getElementById('medicine-modal-title').textContent = `Edit Medicine: ${med.name}`;
  document.getElementById('med-form-mode').value = 'edit';
  document.getElementById('med-id').value = med.medicine_id;
  document.getElementById('med-id').disabled = true;
  document.getElementById('med-name').value = med.name;
  document.getElementById('med-company').value = med.company;
  document.getElementById('med-category').value = med.category;
  document.getElementById('med-price').value = med.price;
  document.getElementById('med-quantity').value = med.quantity;
  document.getElementById('med-expiry').value = med.expiry_date;
  document.getElementById('med-reorder').value = med.reorder_level || 15;
  document.getElementById('med-prescription').checked = !!med.requires_prescription;

  openModal('modal-add-medicine');
}

async function handleSaveMedicine(e) {
  e.preventDefault();
  const mode = document.getElementById('med-form-mode').value;
  const medId = document.getElementById('med-id').value.trim();

  const payload = {
    name: document.getElementById('med-name').value.trim(),
    company: document.getElementById('med-company').value.trim(),
    category: document.getElementById('med-category').value.trim(),
    price: parseFloat(document.getElementById('med-price').value) || 0,
    quantity: parseInt(document.getElementById('med-quantity').value, 10) || 0,
    expiry_date: document.getElementById('med-expiry').value,
    reorder_level: parseInt(document.getElementById('med-reorder').value, 10) || 15,
    requires_prescription: document.getElementById('med-prescription').checked
  };

  try {
    if (mode === 'edit') {
      await fetchApi(`/medicines/${encodeURIComponent(medId)}`, {
        method: 'PUT',
        body: JSON.stringify(payload)
      });
      showToast(`Medicine ${payload.name} updated!`);
    } else {
      if (medId) payload.medicine_id = medId;
      await fetchApi('/medicines', {
        method: 'POST',
        body: JSON.stringify(payload)
      });
      showToast(`Medicine ${payload.name} registered!`);
    }

    closeModal('modal-add-medicine');
    document.getElementById('form-medicine').reset();
    document.getElementById('med-id').disabled = false;
    document.getElementById('med-form-mode').value = 'add';
    document.getElementById('medicine-modal-title').textContent = 'Add New Medicine';
    await loadAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function deleteMedicine(medId) {
  if (!confirm(`Are you sure you want to delete medicine '${medId}'?`)) return;
  try {
    await fetchApi(`/medicines/${encodeURIComponent(medId)}`, { method: 'DELETE' });
    showToast(`Deleted medicine ${medId}`);
    await loadAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Quick Stock Adjustment
function openStockAdjustModal(medId) {
  const med = state.medicines.find(m => m.medicine_id === medId);
  if (!med) return;
  document.getElementById('adjust-med-id').value = med.medicine_id;
  document.getElementById('adjust-med-name').textContent = `${med.name} (Current Stock: ${med.quantity})`;
  document.getElementById('adjust-qty-delta').value = "";
  openModal('modal-adjust-stock');
}

async function handleStockAdjust(e) {
  e.preventDefault();
  const medId = document.getElementById('adjust-med-id').value;
  const delta = parseInt(document.getElementById('adjust-qty-delta').value, 10);
  if (isNaN(delta) || delta === 0) {
    showToast('Please enter a valid stock delta (+ or -)', 'warning');
    return;
  }

  try {
    await fetchApi(`/medicines/${encodeURIComponent(medId)}/stock`, {
      method: 'POST',
      body: JSON.stringify({ quantity: delta })
    });
    showToast(`Stock updated for ${medId}`);
    closeModal('modal-adjust-stock');
    await loadAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ==========================================================================
// 6. POINT OF SALE (POS) & CART ENGINE
// ==========================================================================

function renderPosCustomerSelect() {
  const sel = document.getElementById('pos-customer-select');
  if (!sel) return;
  const current = sel.value;
  sel.innerHTML = '<option value="WALKIN">Walk-in Customer</option>' +
    state.customers.map(c => `
      <option value="${escapeHtml(c.customer_id)}">${escapeHtml(c.name)} (${escapeHtml(c.mobile)})</option>
    `).join('');
  if (current) sel.value = current;
}

function renderPosPrescriptionSelect() {
  const sel = document.getElementById('pos-prescription-select');
  if (!sel) return;
  const current = sel.value;
  sel.innerHTML = '<option value="">No Prescription / Over The Counter</option>' +
    state.prescriptions.map(p => `
      <option value="${escapeHtml(p.prescription_id)}">Rx #${escapeHtml(p.prescription_id)} — ${escapeHtml(p.patient_name)} (${escapeHtml(p.doctor_name)})</option>
    `).join('');
  if (current) sel.value = current;
}

function renderPosGrid() {
  const grid = document.getElementById('pos-grid');
  if (!grid) return;

  const search = (document.getElementById('pos-search')?.value || '').toLowerCase().trim();
  const cat = document.getElementById('pos-category-filter')?.value || 'All';

  const items = state.medicines.filter(m => {
    const matchesSearch = !search || 
      m.name.toLowerCase().includes(search) || 
      m.medicine_id.toLowerCase().includes(search);
    const matchesCat = (cat === 'All') || (m.category === cat);
    return matchesSearch && matchesCat;
  });

  if (!items.length) {
    grid.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:30px; color:var(--text-muted);">No matching medicines available.</div>';
    return;
  }

  grid.innerHTML = items.map(m => {
    const isOut = m.quantity <= 0;
    const isExp = m.is_expired;
    const isDisabled = isOut || isExp;

    let statusPill = `<span class="badge badge-success">Stock: ${m.quantity}</span>`;
    if (isExp) statusPill = `<span class="badge badge-danger">Expired</span>`;
    else if (isOut) statusPill = `<span class="badge badge-danger">Out of Stock</span>`;
    else if (m.quantity <= m.reorder_level) statusPill = `<span class="badge badge-warning">Low: ${m.quantity}</span>`;

    return `
      <div class="pos-product-card ${isDisabled ? 'disabled' : ''}" style="${isDisabled ? 'opacity:0.6;' : ''}">
        <div>
          <div style="font-size:0.75rem; color:var(--text-muted); font-weight:600;">${escapeHtml(m.company)}</div>
          <div style="font-weight:700; font-size:0.95rem; margin:2px 0 6px;">${escapeHtml(m.name)}</div>
          <div style="margin-bottom:8px;">${statusPill}</div>
        </div>
        <div style="display:flex; align-items:center; justify-content:space-between; margin-top:8px;">
          <strong style="color:var(--primary); font-size:1.05rem;">₹${Number(m.price).toFixed(2)}</strong>
          <button class="btn btn-sm ${isDisabled ? 'btn-secondary' : 'btn-primary'}" 
            ${isDisabled ? 'disabled' : ''} 
            onclick="addToCart('${escapeHtml(m.medicine_id)}')">
            + Add
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function addToCart(medId) {
  const med = state.medicines.find(m => m.medicine_id === medId);
  if (!med) return;

  if (med.is_expired) {
    showToast(`Cannot sell '${med.name}': Expired medicine!`, 'error');
    return;
  }

  const existing = state.cart.find(item => item.medicine.medicine_id === medId);
  if (existing) {
    if (existing.quantity + 1 > med.quantity) {
      showToast(`Cannot add more. Only ${med.quantity} in stock for '${med.name}'.`, 'warning');
      return;
    }
    existing.quantity += 1;
    existing.line_total = round(existing.quantity * med.price);
  } else {
    if (med.quantity < 1) {
      showToast(`'${med.name}' is out of stock!`, 'warning');
      return;
    }
    state.cart.push({
      medicine: med,
      quantity: 1,
      line_total: round(med.price)
    });
  }

  renderCart();
}

function updateCartQty(medId, delta) {
  const item = state.cart.find(i => i.medicine.medicine_id === medId);
  if (!item) return;

  const newQty = item.quantity + delta;
  if (newQty <= 0) {
    removeFromCart(medId);
    return;
  }

  if (newQty > item.medicine.quantity) {
    showToast(`Cannot exceed available stock (${item.medicine.quantity}).`, 'warning');
    return;
  }

  item.quantity = newQty;
  item.line_total = round(item.quantity * item.medicine.price);
  renderCart();
}

function removeFromCart(medId) {
  state.cart = state.cart.filter(i => i.medicine.medicine_id !== medId);
  renderCart();
}

function clearCart() {
  state.cart = [];
  renderCart();
}

function renderCart() {
  const container = document.getElementById('pos-cart-items');
  if (!state.cart.length) {
    container.innerHTML = '<div style="text-align:center; color:var(--text-muted); padding:30px 10px;">Cart is empty. Click any medicine on the left to add it.</div>';
    calculateCartTotals();
    return;
  }

  container.innerHTML = state.cart.map(i => `
    <div class="cart-item-row">
      <div style="flex:1;">
        <div style="font-weight:700; font-size:0.88rem;">${escapeHtml(i.medicine.name)}</div>
        <div style="font-size:0.78rem; color:var(--text-muted);">₹${i.medicine.price.toFixed(2)} each</div>
      </div>
      <div class="qty-control">
        <button class="qty-btn" onclick="updateCartQty('${escapeHtml(i.medicine.medicine_id)}', -1)">-</button>
        <span style="font-weight:700; min-width:24px; text-align:center;">${i.quantity}</span>
        <button class="qty-btn" onclick="updateCartQty('${escapeHtml(i.medicine.medicine_id)}', 1)">+</button>
      </div>
      <div style="font-weight:700; min-width:65px; text-align:right;">₹${i.line_total.toFixed(2)}</div>
      <button style="background:none; border:none; color:var(--danger); cursor:pointer; font-size:1.1rem; padding:0 4px;" 
        onclick="removeFromCart('${escapeHtml(i.medicine.medicine_id)}')">✕</button>
    </div>
  `).join('');

  calculateCartTotals();
}

function calculateCartTotals() {
  const subtotal = state.cart.reduce((sum, item) => sum + item.line_total, 0);
  const gstRate = parseFloat(document.getElementById('pos-gst-rate')?.value || 0.18);
  const discount = Math.max(0, parseFloat(document.getElementById('pos-discount')?.value || 0));

  const gstAmount = round(subtotal * gstRate);
  const total = Math.max(0, round(subtotal + gstAmount - discount));

  document.getElementById('pos-subtotal').textContent = `₹${subtotal.toFixed(2)}`;
  document.getElementById('pos-gst-amount').textContent = `₹${gstAmount.toFixed(2)}`;
  document.getElementById('pos-grand-total').textContent = `₹${total.toFixed(2)}`;
}

async function processSaleCheckout() {
  if (!state.cart.length) {
    showToast('Cart is empty. Please add medicines before checkout.', 'warning');
    return;
  }

  const customerId = document.getElementById('pos-customer-select').value;
  const prescriptionId = document.getElementById('pos-prescription-select').value || null;
  const gstRate = parseFloat(document.getElementById('pos-gst-rate').value || 0.18);
  const discount = Math.max(0, parseFloat(document.getElementById('pos-discount').value || 0));
  const paymentMethod = document.getElementById('pos-payment-method').value;

  const items = state.cart.map(i => ({
    medicine_id: i.medicine.medicine_id,
    quantity: i.quantity
  }));

  try {
    const res = await fetchApi('/sales', {
      method: 'POST',
      body: JSON.stringify({
        customer_id: customerId,
        items,
        prescription_id: prescriptionId,
        gst_rate: gstRate,
        discount,
        payment_method: paymentMethod
      })
    });

    showToast(`Sale completed! Invoice #${res.bill.bill_id} generated.`);
    clearCart();

    // Show thermal receipt
    displayReceipt(res.bill.receipt_text);

    // Refresh state
    await loadAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function round(val) {
  return Math.round((val + Number.EPSILON) * 100) / 100;
}

// ==========================================================================
// 7. CUSTOMERS TABLE & HISTORY
// ==========================================================================

function renderCustomersTable(list = null) {
  const tbody = document.getElementById('customers-table-body');
  const items = list || state.customers;

  if (!items.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:24px; color:var(--text-muted);">No customers registered.</td></tr>';
    return;
  }

  tbody.innerHTML = items.map(c => `
    <tr>
      <td><code>${escapeHtml(c.customer_id)}</code></td>
      <td><strong>${escapeHtml(c.name)}</strong></td>
      <td>${escapeHtml(c.mobile)}</td>
      <td>${escapeHtml(c.address)}</td>
      <td><span class="badge badge-info">${c.purchase_count || (c.purchase_history || []).length} orders</span></td>
      <td>
        <div class="table-actions">
          <button class="btn btn-sm btn-outline" onclick="viewCustomerHistory('${escapeHtml(c.customer_id)}')">History</button>
          <button class="btn btn-sm btn-danger" onclick="deleteCustomer('${escapeHtml(c.customer_id)}')">✕</button>
        </div>
      </td>
    </tr>
  `).join('');
}

function filterCustomersTable() {
  const q = document.getElementById('cust-search').value.toLowerCase().trim();
  const filtered = state.customers.filter(c => 
    c.name.toLowerCase().includes(q) || 
    c.mobile.toLowerCase().includes(q) || 
    c.customer_id.toLowerCase().includes(q)
  );
  renderCustomersTable(filtered);
}

async function handleSaveCustomer(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById('cust-name').value.trim(),
    mobile: document.getElementById('cust-mobile').value.trim(),
    address: document.getElementById('cust-address').value.trim()
  };

  try {
    const cust = await fetchApi('/customers', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    showToast(`Customer ${cust.name} registered!`);
    closeModal('modal-add-customer');
    document.getElementById('cust-name').value = '';
    document.getElementById('cust-mobile').value = '';
    document.getElementById('cust-address').value = '';
    await loadAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function deleteCustomer(cid) {
  if (!confirm(`Delete customer '${cid}'?`)) return;
  try {
    await fetchApi(`/customers/${encodeURIComponent(cid)}`, { method: 'DELETE' });
    showToast(`Customer deleted`);
    await loadAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function viewCustomerHistory(cid) {
  const cust = state.customers.find(c => c.customer_id === cid);
  if (!cust) return;

  try {
    const history = await fetchApi(`/customers/${encodeURIComponent(cid)}/history`);
    document.getElementById('cust-history-title').textContent = `Purchase History: ${cust.name}`;
    const tbody = document.getElementById('cust-history-body');

    if (!history.length) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:20px;">No purchases recorded yet for this customer.</td></tr>';
    } else {
      tbody.innerHTML = history.map(h => `
        <tr>
          <td><code>${escapeHtml(h.sale_id)}</code></td>
          <td>${escapeHtml(h.sale_date)}</td>
          <td>${(h.items || []).map(i => `${escapeHtml(i.name)} x${i.quantity}`).join(', ')}</td>
          <td><strong>₹${Number(h.total).toFixed(2)}</strong></td>
        </tr>
      `).join('');
    }

    openModal('modal-customer-history');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ==========================================================================
// 8. SUPPLIERS TABLE
// ==========================================================================

function renderSuppliersTable() {
  const tbody = document.getElementById('suppliers-table-body');
  if (!state.suppliers.length) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:24px; color:var(--text-muted);">No suppliers registered.</td></tr>';
    return;
  }

  tbody.innerHTML = state.suppliers.map(s => `
    <tr>
      <td><code>${escapeHtml(s.supplier_id)}</code></td>
      <td><strong>${escapeHtml(s.name)}</strong></td>
      <td>${escapeHtml(s.company)}</td>
      <td>${escapeHtml(s.mobile)}</td>
      <td>${escapeHtml(s.address)}</td>
      <td><span class="badge badge-neutral">${(s.supplied_medicines || []).join(', ') || 'General Supply'}</span></td>
      <td>
        <button class="btn btn-sm btn-danger" onclick="deleteSupplier('${escapeHtml(s.supplier_id)}')">✕</button>
      </td>
    </tr>
  `).join('');
}

async function handleSaveSupplier(e) {
  e.preventDefault();
  const payload = {
    name: document.getElementById('sup-name').value.trim(),
    company: document.getElementById('sup-company').value.trim(),
    mobile: document.getElementById('sup-mobile').value.trim(),
    address: document.getElementById('sup-address').value.trim()
  };

  try {
    await fetchApi('/suppliers', { method: 'POST', body: JSON.stringify(payload) });
    showToast(`Supplier ${payload.company} added!`);
    closeModal('modal-add-supplier');
    e.target.reset();
    await loadAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function deleteSupplier(sid) {
  if (!confirm(`Delete supplier '${sid}'?`)) return;
  try {
    await fetchApi(`/suppliers/${encodeURIComponent(sid)}`, { method: 'DELETE' });
    showToast(`Supplier deleted`);
    await loadAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ==========================================================================
// 9. PRESCRIPTIONS TABLE
// ==========================================================================

function renderPrescriptionsTable() {
  const tbody = document.getElementById('prescriptions-table-body');
  if (!state.prescriptions.length) {
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:24px; color:var(--text-muted);">No prescriptions on record.</td></tr>';
    return;
  }

  tbody.innerHTML = state.prescriptions.map(p => `
    <tr>
      <td><code>${escapeHtml(p.prescription_id)}</code></td>
      <td><strong>${escapeHtml(p.doctor_name)}</strong></td>
      <td>${escapeHtml(p.patient_name)}</td>
      <td>${(p.prescribed_medicines || []).map(m => `<span class="badge badge-info" style="margin:2px;">${escapeHtml(m)}</span>`).join(' ')}</td>
      <td>${escapeHtml(p.date_issued)}</td>
      <td>
        <span class="badge ${p.verified ? 'badge-success' : 'badge-warning'}">
          ${p.verified ? '✓ Verified' : 'Pending Verification'}
        </span>
      </td>
      <td>
        <div class="table-actions">
          ${!p.verified ? `<button class="btn btn-sm btn-secondary" onclick="verifyPrescription('${escapeHtml(p.prescription_id)}')">Verify</button>` : ''}
          <button class="btn btn-sm btn-danger" onclick="deletePrescription('${escapeHtml(p.prescription_id)}')">✕</button>
        </div>
      </td>
    </tr>
  `).join('');
}

async function handleSavePrescription(e) {
  e.preventDefault();
  const medsStr = document.getElementById('rx-medicines').value.trim();
  const meds = medsStr.split(',').map(s => s.trim()).filter(Boolean);

  const payload = {
    doctor_name: document.getElementById('rx-doctor').value.trim(),
    patient_name: document.getElementById('rx-patient').value.trim(),
    prescribed_medicines: meds,
    verified: true
  };

  try {
    await fetchApi('/prescriptions', { method: 'POST', body: JSON.stringify(payload) });
    showToast('Prescription saved!');
    closeModal('modal-add-prescription');
    e.target.reset();
    await loadAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function verifyPrescription(pid) {
  try {
    await fetchApi(`/prescriptions/${encodeURIComponent(pid)}/verify`, { method: 'PUT', body: '{}' });
    showToast(`Prescription ${pid} verified.`);
    await loadAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function deletePrescription(pid) {
  if (!confirm(`Delete prescription '${pid}'?`)) return;
  try {
    await fetchApi(`/prescriptions/${encodeURIComponent(pid)}`, { method: 'DELETE' });
    showToast(`Prescription deleted`);
    await loadAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// ==========================================================================
// 10. BILLS & INVOICES TABLE & RECEIPT VIEWER
// ==========================================================================

function renderBillsTable() {
  const tbody = document.getElementById('bills-table-body');
  if (!state.bills.length) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:24px; color:var(--text-muted);">No invoices generated yet.</td></tr>';
    return;
  }

  tbody.innerHTML = state.bills.map(b => `
    <tr>
      <td><code>${escapeHtml(b.bill_id)}</code></td>
      <td><code>${escapeHtml(b.sale_id)}</code></td>
      <td><strong>${escapeHtml(b.customer_name)}</strong></td>
      <td>₹${Number(b.subtotal).toFixed(2)}</td>
      <td>₹${Number(b.gst).toFixed(2)}</td>
      <td><strong style="color:var(--primary);">₹${Number(b.total).toFixed(2)}</strong></td>
      <td><span class="badge badge-neutral">${escapeHtml(b.payment_method || 'Cash')}</span></td>
      <td>${escapeHtml(b.bill_date)}</td>
      <td>
        <button class="btn btn-sm btn-outline" onclick="displayReceipt('${escapeHtml(b.receipt_text).replace(/'/g, "\\'")}')">View Receipt</button>
      </td>
    </tr>
  `).join('');
}

function viewBillBySaleId(saleId) {
  const bill = state.bills.find(b => b.sale_id === saleId);
  if (bill && bill.receipt_text) {
    displayReceipt(bill.receipt_text);
  } else {
    showToast(`Receipt for sale '${saleId}' not found.`, 'warning');
  }
}

function displayReceipt(asciiText) {
  currentReceiptText = asciiText || "No receipt content available.";
  document.getElementById('receipt-text-view').textContent = currentReceiptText;
  openModal('modal-receipt');
}

function printReceiptTerminal() {
  const printWindow = window.open('', '', 'width=600,height=700');
  printWindow.document.write(`
    <html>
      <head>
        <title>Print Receipt</title>
        <style>
          body { font-family: 'JetBrains Mono', monospace, Courier; font-size: 13px; line-height: 1.5; padding: 20px; white-space: pre-wrap; }
        </style>
      </head>
      <body>${escapeHtml(currentReceiptText)}</body>
    </html>
  `);
  printWindow.document.close();
  printWindow.focus();
  printWindow.print();
  printWindow.close();
}

function downloadReceiptTxt() {
  const blob = new Blob([currentReceiptText], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `receipt_${Date.now()}.txt`;
  a.click();
  URL.revokeObjectURL(url);
}

// ==========================================================================
// 11. REPORTS & EXPORTS
// ==========================================================================

function exportResource(resourceName) {
  const downloadUrl = `${API_BASE}/export/${encodeURIComponent(resourceName)}`;
  window.open(downloadUrl, '_blank');
  showToast(`Downloading ${resourceName}.csv...`);
}

// ==========================================================================
// 12. MODAL CONTROLLER
// ==========================================================================

function openModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.add('open');
}

function closeModal(modalId) {
  const m = document.getElementById(modalId);
  if (m) m.classList.remove('open');
}

// Close modals when clicking backdrop
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-backdrop')) {
    e.target.classList.remove('open');
  }
});

// Close modals with Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-backdrop.open').forEach(m => m.classList.remove('open'));
  }
});

// ==========================================================================
// 13. DOM READY INITIALIZATION
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  loadAllData();
});
