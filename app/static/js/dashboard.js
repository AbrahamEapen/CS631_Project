async function loadAccounts() {
  const accounts = await apiRequest("user/accounts");

  const container = document.getElementById("accounts");

  container.innerHTML = "";

  accounts.forEach(acc => {
    container.innerHTML += `
      <div class="card mb-2 p-3">
        <h5>Account #${acc.account_number}</h5>
        <p>Balance: $${acc.balance}</p>

        <button class="btn btn-sm btn-success"
          onclick="openDeposit(${acc.account_number})">
          Deposit
        </button>

        <button class="btn btn-sm btn-danger"
          onclick="openWithdraw(${acc.account_number})">
          Withdraw
        </button>

        <button class="btn btn-sm btn-primary"
          onclick="loadTransactions(${acc.account_number})">
          View Transactions
        </button>
      </div>
    `;
  });
}