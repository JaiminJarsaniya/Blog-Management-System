// ALL LIKE BUTTONS
document.querySelectorAll(".like-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const blogId = btn.dataset.blogId;
    const response = await fetch(`/like/${blogId}`, {method: "POST",});
    const data = await response.json();

    if (data.login_required) {
      window.location.href = "/login";
      return;
    }

    const icon = btn.querySelector("i");
    const count = btn.querySelector(".like-count");
    count.innerText = data.count;

    if (data.liked) {
      icon.classList.remove("fa-regular");
      icon.classList.add("fa-solid");
      btn.classList.add("active");
    } else {
      icon.classList.remove("fa-solid");
      icon.classList.add("fa-regular");
      btn.classList.remove("active");
    }
  });
});

// ALL COMMENT SECTIONS
document.querySelectorAll(".comment-toggle-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const wrapper = btn.closest(".blg-content").querySelector(".comments-wrapper");
    if (!wrapper) return;
    if (wrapper.style.display === "block") {
      wrapper.style.display = "none";
    } else {
      wrapper.style.display = "block";
    }
  });
});

document.querySelectorAll(".send-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const blogId = btn.dataset.blogId;
    const commentBox = btn.closest(".comment-box");
    const input = commentBox.querySelector(".comment-input");
    const text = input.value.trim();

    if (!text) {
      alert("Please enter a comment");
      return;
    }

    const formData = new FormData();
    formData.append(
      "comment",
      text
    );

    try {
      const response = await fetch(
          `/comment/${blogId}`,
          {
            method: "POST",
            body: formData
          }
        );

      const data = await response.json();
      if (data.login_required) {
        window.location.href = "/login";
        return;
      }
      if (data.success) {
        location.reload();
      }

    } catch (error) {
      console.log(error);
    }
  });
});
