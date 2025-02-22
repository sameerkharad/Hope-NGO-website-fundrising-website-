document.addEventListener("DOMContentLoaded", function () {
    // Toggle profile dropdown visibility
    const profileBtn = document.getElementById("profile-btn");
    const profileDropdown = document.getElementById("profile-dropdown");

    if (profileBtn && profileDropdown) {
        profileBtn.addEventListener("click", function () {
            profileDropdown.classList.toggle("hidden");
        });
    }

    // Hero sliding images with fade-out transition
    const images = ["/static/img/1st.jpg", "/static/img/2nd.jpg", "/static/img/3rd.jpg"];
    let currentIndex = 0;
    const slidingImage = document.getElementById("sliding-image");

    if (slidingImage) {
        setInterval(() => {
            slidingImage.classList.add("fade-out");
            setTimeout(() => {
                currentIndex = (currentIndex + 1) % images.length;
                slidingImage.src = images[currentIndex];
                slidingImage.classList.remove("fade-out");
            }, 1000);
        }, 5000);
    }

    // Typing effect
    const words = ["FOOD.", "CLOTHES.", "FOOTWEAR."];
    let wordIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    const typingElement = document.getElementById("typing-effect");

    function typeEffect() {
        if (!typingElement) return;

        const currentWord = words[wordIndex];
        if (isDeleting) {
            charIndex--;
        } else {
            charIndex++;
        }

        typingElement.textContent = currentWord.substring(0, charIndex);

        if (!isDeleting && charIndex === currentWord.length) {
            setTimeout(() => {
                isDeleting = true;
                typeEffect();
            }, 2000);
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            wordIndex = (wordIndex + 1) % words.length;
            setTimeout(typeEffect, 300);
        } else {
            setTimeout(typeEffect, isDeleting ? 50 : 100);
        }
    }

    typeEffect();

    // Display username in profile dropdown
    const usernameDisplay = document.getElementById("user-display");
    const username = sessionStorage.getItem("username");

    if (usernameDisplay) {
        usernameDisplay.textContent = username ? ` ${username}` : "Not logged in";
    }

    // Logout function
    const logoutBtn = document.querySelector("#profile-dropdown a[onclick='logout()']");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", function (event) {
            event.preventDefault();
            sessionStorage.removeItem("username");
            location.reload();
        });
    }
});



