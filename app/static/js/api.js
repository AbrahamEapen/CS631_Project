// Stores the JWT token in localStorage so admin API calls can attach it
function getToken() {
  return localStorage.getItem("token") || "";
}

function setToken(token) {
  if (token) localStorage.setItem("token", token);
}

async function apiRequest(url, method = "GET", body = null) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch("/" + url, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });
  return res.json();
}
