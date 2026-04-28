
// Deposit
async function deposit(accountId) {
  const amount = document.getElementById("amount").value;

  const res = await apiRequest("transactions/deposit", "POST", {
    account_id: accountId,
    amount: parseFloat(amount),
  });

  alert(res.msg);
  loadAccounts();
}

// Withdraw
async function withdraw(accountId) {
  const amount = document.getElementById("amount").value;

  const res = await apiRequest("transactions/withdraw", "POST", {
    account_id: accountId,
    amount: parseFloat(amount),
  });

  alert(res.msg);
  loadAccounts();
}

// Load transaction history
async function loadTransactions(accountId) {
  const txns = await apiRequest(`transactions/${accountId}`);

  const container = document.getElementById("transactions");

  container.innerHTML = "<h4>Transactions</h4>";

  txns.forEach(t => {
    container.innerHTML += `
      <div class="border p-2 mb-1">
        <strong>${t.type}</strong> - $${t.amount}
        <small class="text-muted">${t.date}</small>
      </div>
    `;
  });
}