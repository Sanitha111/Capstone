// Basic interactivity
document.addEventListener("DOMContentLoaded", () => {
    // Add active class to navigation links
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll("nav a");
    navLinks.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.style.textDecoration = "underline";
        }
    });

    // Confirm cancellation
    const cancelButtons = document.querySelectorAll(".cancel-booking");
    cancelButtons.forEach(button => {
        button.addEventListener("click", event => {
            if (!confirm("Are you sure you want to cancel this booking?")) {
                event.preventDefault();
            }
        });
    });

    // Confirm payment
    const paymentButtons = document.querySelectorAll(".make-payment");
    paymentButtons.forEach(button => {
        button.addEventListener("click", event => {
            if (!confirm("Are you sure you want to make this payment?")) {
                event.preventDefault();
            }
        });
    });
});
