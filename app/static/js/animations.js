// Add fade-in animation to cards when they enter viewport
const observeElements = (elements, className) => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add(className);
            }
        });
    });

    elements.forEach(element => observer.observe(element));
};

// Initialize animations when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    observeElements(cards, 'fade-in');

    // Add pulse animation to match cards
    const matchCards = document.querySelectorAll('.match-card');
    matchCards.forEach(card => card.classList.add('pulse'));

    // Add slide-in animation to messages
    const messages = document.querySelectorAll('.message-content');
    observeElements(messages, 'slide-in');

    // Add loading spinner for async operations
    const addLoadingSpinner = (button) => {
        button.innerHTML = `
            <span class="loading-spinner d-inline-block me-2"></span>
            ${button.innerHTML}
        `;
    };

    // Add loading state to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', () => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) addLoadingSpinner(submitBtn);
        });
    });

    // Smooth scroll to top
    const scrollToTop = () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    };

    // Add scroll to top button when needed
    const addScrollToTopButton = () => {
        const button = document.createElement('button');
        button.innerHTML = '↑';
        button.className = 'scroll-to-top-btn';
        button.onclick = scrollToTop;
        document.body.appendChild(button);

        window.addEventListener('scroll', () => {
            button.style.display = window.scrollY > 300 ? 'block' : 'none';
        });
    };

    addScrollToTopButton();

    // Add smooth transition between pages
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', (e) => {
            if (link.href && link.href.startsWith(window.location.origin)) {
                e.preventDefault();
                document.body.style.opacity = 0;
                setTimeout(() => {
                    window.location.href = link.href;
                }, 300);
            }
        });
    });

    // Fade in page on load
    document.body.style.opacity = 0;
    setTimeout(() => {
        document.body.style.opacity = 1;
    }, 100);
});