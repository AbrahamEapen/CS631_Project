async function login(event) {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await apiRequest("auth/login", "POST", {
    username,
    password,
  });

  if (res.access_token) {
    localStorage.setItem("token", res.access_token);
    window.location.href = "/user/dashboard";
  } else {
    alert(res.msg || "Login failed");
  }
}

async function register(event) {
  event.preventDefault();

  const username = document.getElementById("reg_username").value;
  const password = document.getElementById("reg_password").value;

  const res = await apiRequest("auth/register", "POST", {
    username,
    password,
  });

  alert(res.msg);
}