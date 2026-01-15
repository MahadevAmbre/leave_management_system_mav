/*********************************************************
 * CONFIG
 *********************************************************/
const API_BASE = "http://127.0.0.1:5000";

// TEMP IDs (will come from AWS Cognito later)
const EMPLOYEE_ID = 1;
const MANAGER_ID = 2;

/*********************************************************
 * CLIENT DATA CACHE
 *********************************************************/
const leaveData = {
  employee: {
    name: "John Cena",
    paidLeaveRemaining: 12,
    unpaidLeaveTaken: 0,
    totalLeaveTaken: 0,
    leaveHistory: [],
  },
  manager: {
    name: "Mahadev Ambre",
    allLeaveRequests: [],
  },
};

/*********************************************************
 * EMPLOYEE DASHBOARD
 *********************************************************/
function initEmployeeDashboard() {
  const nameEl = document.getElementById("employeeName");
  if (nameEl) nameEl.textContent = leaveData.employee.name;

  fetch(`${API_BASE}/view-leaves?user_id=${EMPLOYEE_ID}`)
    .then((res) => res.json())
    .then((leaves) => {
      leaveData.employee.leaveHistory = leaves.map((l) => ({
        id: l.id,
        dateApplied: new Date().toISOString().split("T")[0],
        days: l.days,
        reason: "—",
        status: l.status.toLowerCase(),
      }));

      // Update totals from real data
      leaveData.employee.totalLeaveTaken = leaves.reduce(
        (sum, l) => sum + l.days,
        0
      );

      document.getElementById("totalLeaveTaken").textContent =
        leaveData.employee.totalLeaveTaken;

      document.getElementById("paidLeaveRemaining").textContent =
        leaveData.employee.paidLeaveRemaining;

      document.getElementById("unpaidLeaveTaken").textContent =
        leaveData.employee.unpaidLeaveTaken;

      renderLeaveHistory();
    });

  const form = document.getElementById("leaveForm");
  if (form) {
    form.addEventListener("submit", handleLeaveSubmit);
  }
}

function renderLeaveHistory() {
  const tbody = document.getElementById("leaveHistory");
  if (!tbody) return;

  if (leaveData.employee.leaveHistory.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="4" class="empty-state">No leave history found</td></tr>';
    return;
  }

  tbody.innerHTML = leaveData.employee.leaveHistory
    .sort((a, b) => new Date(b.dateApplied) - new Date(a.dateApplied))
    .map(
      (leave) => `
        <tr>
          <td>${formatDate(leave.dateApplied)}</td>
          <td>${leave.days}</td>
          <td>${leave.reason}</td>
          <td>
            <span class="status-badge status-${leave.status}">
              ${capitalizeFirst(leave.status)}
            </span>
          </td>
        </tr>
      `
    )
    .join("");
}

function handleLeaveSubmit(e) {
  e.preventDefault();

  const days = Number.parseInt(
    document.getElementById("leaveDays").value
  );

  fetch(`${API_BASE}/apply-leave`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: EMPLOYEE_ID,
      days: days,
    }),
  })
    .then(() => {
      e.target.reset();
      alert("Leave application submitted successfully!");
      initEmployeeDashboard();
    });
}

/*********************************************************
 * MANAGER DASHBOARD
 *********************************************************/
function initManagerDashboard() {
  const nameEl = document.getElementById("managerName");
  if (nameEl) nameEl.textContent = leaveData.manager.name;

  fetch(`${API_BASE}/view-leaves?user_id=${MANAGER_ID}`)
    .then((res) => res.json())
    .then((leaves) => {
      leaveData.manager.allLeaveRequests = leaves.map((l) => ({
        id: l.id,
        employeeName: `Employee #${l.id}`, // backend does not send name yet
        dateApplied: new Date().toISOString().split("T")[0],
        days: l.days,
        reason: "—",
        status: l.status.toLowerCase(),
      }));

      updateManagerStats();
      renderLeaveRequests();
    });
}

function updateManagerStats() {
  const pending = leaveData.manager.allLeaveRequests.filter(
    (req) => req.status === "pending"
  ).length;
  const approved = leaveData.manager.allLeaveRequests.filter(
    (req) => req.status === "approved"
  ).length;
  const rejected = leaveData.manager.allLeaveRequests.filter(
    (req) => req.status === "rejected"
  ).length;

  document.getElementById("pendingCount").textContent = pending;
  document.getElementById("approvedCount").textContent = approved;
  document.getElementById("rejectedCount").textContent = rejected;
}

function renderLeaveRequests() {
  const tbody = document.getElementById("leaveRequests");
  if (!tbody) return;

  if (leaveData.manager.allLeaveRequests.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="6" class="empty-state">No leave requests found</td></tr>';
    return;
  }

  tbody.innerHTML = leaveData.manager.allLeaveRequests
    .sort((a, b) => {
      if (a.status === "pending" && b.status !== "pending") return -1;
      if (a.status !== "pending" && b.status === "pending") return 1;
      return new Date(b.dateApplied) - new Date(a.dateApplied);
    })
    .map(
      (request) => `
        <tr>
          <td>${request.employeeName}</td>
          <td>${request.days}</td>
          <td>${request.reason}</td>
          <td>${formatDate(request.dateApplied)}</td>
          <td>
            <span class="status-badge status-${request.status}">
              ${capitalizeFirst(request.status)}
            </span>
          </td>
          <td>
            ${
              request.status === "pending"
                ? `
                  <button onclick="approveLeave(${request.id})">Approve</button>
                  <button onclick="rejectLeave(${request.id})">Reject</button>
                `
                : "-"
            }
          </td>
        </tr>
      `
    )
    .join("");
}

function approveLeave(id) {
  fetch(`${API_BASE}/approve-leave`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      manager_id: MANAGER_ID,
      leave_id: id,
    }),
  }).then(() => initManagerDashboard());
}

function rejectLeave(id) {
  fetch(`${API_BASE}/reject-leave`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      manager_id: MANAGER_ID,
      leave_id: id,
    }),
  }).then(() => initManagerDashboard());
}

/*********************************************************
 * UTILITIES
 *********************************************************/
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function capitalizeFirst(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
