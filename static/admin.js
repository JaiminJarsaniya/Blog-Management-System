const loginPage = document.getElementById("loginPage");
const adminPanel = document.getElementById("adminPanel");

function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const errorMsg = document.getElementById("error-msg");
  // Dummy Admin Login
  const adminEmail = "admin@gmail.com";
  const adminPassword = "123456";

  if (email === adminEmail && password === adminPassword) {
    loginPage.style.display = "none";
    adminPanel.style.display = "flex";

    localStorage.setItem("adminLoggedIn", true);
    localStorage.setItem("adminEmail", email);

    document.getElementById("adminEmailDisplay").innerText = email;
  } else {
    errorMsg.innerText = "Invalid Email or Password";
  }
}

// Auto Login Check
if (localStorage.getItem("adminLoggedIn")) {
  loginPage.style.display = "none";
  adminPanel.style.display = "flex";
  const savedEmail = localStorage.getItem("adminEmail");
  document.getElementById("adminEmailDisplay").innerText = savedEmail;
}

// Logout
function logout() {
  localStorage.removeItem("adminLoggedIn");
  localStorage.removeItem("adminEmail");

  loginPage.style.display = "flex";
  adminPanel.style.display = "none";

  document.getElementById("email").value = "";
  document.getElementById("password").value = "";
  document.getElementById("error-msg").innerText = "";
}

// Sidebar Page Navigation

function showPage(pageId, element, addHistory = true) {
  // Hide all pages
  let pages = document.querySelectorAll(".page");

  pages.forEach((page) => {
    page.classList.remove("active-page");
  });

  // Show selected page
  document.getElementById(pageId).classList.add("active-page");

  // Remove active menu
  let menus = document.querySelectorAll(".menu li");

  menus.forEach((item) => {
    item.classList.remove("active");
  });

  // Current menu active
  if (element) {
    element.classList.add("active");
  }

  // Browser history me save karo
  if (addHistory) {
    history.pushState({ page: pageId }, "", "#" + pageId);
  }
}

window.addEventListener("popstate", function (event) {
  if (event.state && event.state.page) {
    const pageId = event.state.page;

    const menuItems = document.querySelectorAll(".menu li");

    let menuElement = null;

    menuItems.forEach((item) => {
      if (item.textContent.trim().toLowerCase() === pageId.toLowerCase()) {
        menuElement = item;
      }
    });

    showPage(pageId, menuElement, false);
  } else {
    showPage("dashboard", document.querySelector(".menu li"), false);
  }
});

window.onload = function () {
  if (localStorage.getItem("adminLoggedIn")) {
    history.replaceState({ page: "dashboard" }, "", "#dashboard");
  }
};