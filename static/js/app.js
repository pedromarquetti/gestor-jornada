// Toggle user menu dropdown
function toggleUserMenu(event) {
  event.preventDefault();
  const dropdown = document.getElementById("userDropdown");
  if (dropdown.classList.contains("show")) {
    dropdown.classList.remove("show");
  } else {
    // Close other open menus first
    document.querySelectorAll(".user-dropdown").forEach((el) =>
      el.classList.remove("show")
    );
    dropdown.classList.add("show");
  }
}

// Handle logout with CSRF token
function handleLogout(event) {
  event.preventDefault();

  const logoutForm = document.createElement("form");
  logoutForm.method = "POST";
  logoutForm.action = '{% url "jornadas_logout" %}';

  // Add CSRF token from existing form or cookie
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]") ||
    document.querySelector("[name=csrf_token]");
  if (csrfToken) {
    logoutForm.appendChild(csrfToken.cloneNode(true));
  } else {
    try {
      const cookies = document.cookie.split(";").map((c) => c.trim());
      const csrfCookie = cookies.find((c) => c.startsWith("csrftoken="));
      if (csrfCookie) {
        const csrfInput = document.createElement("input");
        csrfInput.type = "hidden";
        csrfInput.name = "csrfmiddlewaretoken";
        csrfInput.value = csrfCookie.split("=")[1];
        logoutForm.appendChild(csrfInput);
      }
    } catch (e) {}
  }

  document.body.appendChild(logoutForm);
  logoutForm.submit();
}

// Close dropdown when navigating away from the page
document.addEventListener("visibilitychange", function () {
  if (!document.hidden) {
    const dropdown = document.getElementById("userDropdown");
    if (dropdown && dropdown.classList.contains("show")) {
      dropdown.classList.remove("show");
    }
  }
});


// Close dropdown when clicking outside
document.addEventListener("click", function (event) {
  if (!event.target.closest(".user-menu")) {
    const dropdown = document.getElementById("userDropdown");
    if (dropdown && dropdown.classList.contains("show")) {
      dropdown.classList.remove("show");
    }
  }
});

