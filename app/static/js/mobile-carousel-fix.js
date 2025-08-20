// Mobile Carousel Fix - Force Working Animation

document.addEventListener('DOMContentLoaded', function() {
    
    function isMobileDevice() {
        return window.innerWidth <= 767.98;
    }
    
    function forceCarouselAnimation() {
        if (isMobileDevice()) {
            console.log('🔧 Forcing mobile carousel animation...');
            
            const track = document.querySelector('.fade-carousel-track');
            const container = document.querySelector('.fade-carousel-container');
            const items = document.querySelectorAll('.fade-carousel-item');
            
            if (track && container && items.length > 0) {
                // Force remove any conflicting styles
                track.style.animation = 'none';
                track.style.transform = 'translateX(0)';
                
                // Force reflow
                track.offsetHeight;
                
                // Apply correct styles
                track.style.display = 'flex';
                track.style.position = 'absolute';
                track.style.left = '0';
                track.style.top = '0';
                track.style.width = '300%';
                track.style.height = '100%';
                track.style.padding = '0';
                track.style.margin = '0';
                track.style.willChange = 'transform';
                
                // Force animation
                track.style.animation = 'carousel-scroll 40s linear infinite';
                track.style.animationPlayState = 'running';
                
                console.log('✅ Mobile carousel animation applied');
                
                // Ensure items have correct sizing
                items.forEach((item, index) => {
                    item.style.flex = '0 0 140px';
                    item.style.width = '140px';
                    item.style.height = '130px';
                    item.style.margin = '0 8px';
                    item.style.minWidth = '140px';
                    item.style.maxWidth = '140px';
                    item.style.flexShrink = '0';
                    item.style.flexGrow = '0';
                    
                    const img = item.querySelector('img');
                    if (img) {
                        img.style.width = '100%';
                        img.style.height = '100%';
                        img.style.objectFit = 'contain';
                        img.style.padding = '4px';
                        img.style.display = 'block';
                        img.style.margin = '0 auto';
                    }
                });
                
                // Force container properties
                container.style.position = 'relative';
                container.style.width = '100%';
                container.style.height = '160px';
                container.style.overflow = 'hidden';
                
                console.log('✅ Mobile carousel items styled');
                
                // Fix register button and match image sizes
                const registerBtn = document.querySelector('.register-btn');
                const matchImage = document.querySelector('.match-image');
                
                if (registerBtn) {
                    registerBtn.style.maxWidth = '180px';
                    registerBtn.style.width = '70%';
                    registerBtn.style.height = 'auto';
                    registerBtn.style.display = 'block';
                    registerBtn.style.margin = '0 auto';
                    console.log('✅ Register button resized for mobile');
                }
                
                if (matchImage) {
                    matchImage.style.maxWidth = '200px';
                    matchImage.style.width = '75%';
                    matchImage.style.height = 'auto';
                    matchImage.style.display = 'block';
                    matchImage.style.margin = '10px auto';
                    console.log('✅ Match image resized for mobile');
                }
                
                // Monitor animation
                let lastTransform = '';
                const checkAnimation = setInterval(() => {
                    const currentTransform = window.getComputedStyle(track).transform;
                    if (currentTransform === lastTransform) {
                        console.log('⚠️ Animation stuck, restarting...');
                        track.style.animation = 'none';
                        track.offsetHeight;
                        track.style.animation = 'carousel-scroll 40s linear infinite';
                    }
                    lastTransform = currentTransform;
                }, 5000);
                
                // Stop monitoring after 30 seconds
                setTimeout(() => clearInterval(checkAnimation), 30000);
            } else {
                console.log('❌ Carousel elements not found');
            }
        }
    }
    
    // Apply fix immediately
    setTimeout(forceCarouselAnimation, 100);
    
    // Apply fix on resize/orientation change
    window.addEventListener('resize', () => {
        setTimeout(forceCarouselAnimation, 200);
    });
    
    window.addEventListener('orientationchange', () => {
        setTimeout(forceCarouselAnimation, 500);
    });
    
});
