// Mobile Carousel Optimizations
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a mobile device
    function isMobile() {
        return window.innerWidth <= 767.98;
    }

    // Optimize carousel for mobile
    function optimizeCarouselForMobile() {
        if (isMobile()) {
            const carouselItems = document.querySelectorAll('.fade-carousel-item');
            const carouselTrack = document.querySelector('.fade-carousel-track');
            const carouselContainer = document.querySelector('.fade-carousel-container');
            
            if (carouselContainer && carouselTrack && carouselItems.length > 0) {
                // Add mobile-specific classes
                carouselContainer.classList.add('mobile-optimized');
                
                // Ensure images are loaded before showing
                carouselItems.forEach((item, index) => {
                    const img = item.querySelector('img');
                    if (img) {
                        img.addEventListener('load', function() {
                            item.style.opacity = '1';
                        });
                        
                        img.addEventListener('error', function() {
                            // Hide items with failed images on mobile
                            item.style.display = 'none';
                        });
                        
                        // Set initial opacity to 0 until loaded
                        item.style.opacity = '0';
                        item.style.transition = 'opacity 0.3s ease';
                        
                        // Force image loading
                        if (img.complete) {
                            item.style.opacity = '1';
                        }
                    }
                });
                
                // Ensure carousel scrolls automatically - minimal interference
                carouselTrack.style.animationPlayState = 'running';
                
                // Only brief pause on touch to maintain smooth scrolling
                carouselContainer.addEventListener('touchstart', function(e) {
                    carouselTrack.style.animationPlayState = 'paused';
                    
                    setTimeout(() => {
                        carouselTrack.style.animationPlayState = 'running';
                    }, 500); // Very brief pause
                });
                
                // Simple visibility check to keep animation running
                if ('IntersectionObserver' in window) {
                    const observer = new IntersectionObserver((entries) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting) {
                                carouselTrack.style.animationPlayState = 'running';
                            }
                        });
                    }, { threshold: 0.5 }); // Only when 50% visible
                    
                    observer.observe(carouselContainer);
                }
            }
        }
    }

    // Optimize button sizes for mobile
    function optimizeButtonsForMobile() {
        if (isMobile()) {
            const buttons = document.querySelectorAll('.btn');
            const registerBtn = document.querySelector('.register-btn');
            const matchImage = document.querySelector('.match-image');
            
            // Ensure consistent button sizing
            buttons.forEach(btn => {
                btn.style.minHeight = '48px';
                btn.style.fontSize = '16px';
                btn.style.padding = '12px 16px';
            });
            
            // Ensure register button consistency - SMALLER FOR MOBILE
            if (registerBtn) {
                registerBtn.style.maxWidth = '220px'; // Reduced size
                registerBtn.style.width = '80%';
                registerBtn.style.height = 'auto';
                registerBtn.style.display = 'block';
                registerBtn.style.margin = '0 auto';
            }
            
            // Ensure match image consistency
            if (matchImage) {
                matchImage.style.maxWidth = '240px'; // Slightly larger than register button
                matchImage.style.width = '85%';
                matchImage.style.height = 'auto';
                matchImage.style.display = 'block';
                matchImage.style.margin = '10px auto';
            }
        }
    }

    // Fix image aspect ratios on mobile
    function fixImageAspectRatios() {
        if (isMobile()) {
            const heroImage = document.querySelector('.welcome-container img');
            if (heroImage) {
                heroImage.style.maxWidth = '85%';
                heroImage.style.height = 'auto';
                heroImage.style.margin = '5px auto 15px auto';
                heroImage.style.display = 'block';
            }
        }
    }

    // Handle orientation changes
    function handleOrientationChange() {
        setTimeout(() => {
            optimizeCarouselForMobile();
            optimizeButtonsForMobile();
            fixImageAspectRatios();
        }, 100);
    }

    // Initialize optimizations
    optimizeCarouselForMobile();
    optimizeButtonsForMobile();
    fixImageAspectRatios();

    // Handle window resize and orientation change
    window.addEventListener('resize', handleOrientationChange);
    window.addEventListener('orientationchange', handleOrientationChange);

    // Add loading states for images
    const allImages = document.querySelectorAll('img');
    allImages.forEach(img => {
        if (!img.complete) {
            img.style.opacity = '0.5';
            img.addEventListener('load', function() {
                this.style.opacity = '1';
            });
        }
    });

    // Lazy loading for carousel images on mobile
    if (isMobile() && 'IntersectionObserver' in window) {
        const carouselImages = document.querySelectorAll('.fade-carousel-item img');
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                }
            });
        });
        
        carouselImages.forEach(img => {
            if (img.src) {
                img.dataset.src = img.src;
                img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PC9zdmc+';
                imageObserver.observe(img);
            }
        });
    }
});
