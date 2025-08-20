// Carousel Debug Script - Add this temporarily to troubleshoot mobile issues

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 Carousel Debug: Page loaded');
    
    function debugCarousel() {
        const container = document.querySelector('.fade-carousel-container');
        const track = document.querySelector('.fade-carousel-track');
        const items = document.querySelectorAll('.fade-carousel-item');
        
        console.log('📱 Is Mobile:', window.innerWidth <= 767.98);
        console.log('🎠 Container found:', !!container);
        console.log('🚂 Track found:', !!track);
        console.log('🖼️ Items found:', items.length);
        
        if (container) {
            const containerStyles = window.getComputedStyle(container);
            console.log('📦 Container styles:');
            console.log('  - Width:', containerStyles.width);
            console.log('  - Height:', containerStyles.height);
            console.log('  - Overflow:', containerStyles.overflow);
            console.log('  - Position:', containerStyles.position);
        }
        
        if (track) {
            const trackStyles = window.getComputedStyle(track);
            console.log('🚂 Track styles:');
            console.log('  - Width:', trackStyles.width);
            console.log('  - Height:', trackStyles.height);
            console.log('  - Animation:', trackStyles.animation);
            console.log('  - Animation-name:', trackStyles.animationName);
            console.log('  - Animation-duration:', trackStyles.animationDuration);
            console.log('  - Animation-play-state:', trackStyles.animationPlayState);
            console.log('  - Transform:', trackStyles.transform);
            console.log('  - Display:', trackStyles.display);
            console.log('  - Position:', trackStyles.position);
        }
        
        if (items.length > 0) {
            console.log('🖼️ First item styles:');
            const firstItemStyles = window.getComputedStyle(items[0]);
            console.log('  - Flex:', firstItemStyles.flex);
            console.log('  - Width:', firstItemStyles.width);
            console.log('  - Height:', firstItemStyles.height);
            console.log('  - Margin:', firstItemStyles.margin);
            console.log('  - Display:', firstItemStyles.display);
        }
        
        // Check if animation is running
        setTimeout(() => {
            if (track) {
                const currentTransform = window.getComputedStyle(track).transform;
                console.log('⏱️ Animation check after 2s:');
                console.log('  - Current transform:', currentTransform);
                
                setTimeout(() => {
                    const newTransform = window.getComputedStyle(track).transform;
                    console.log('⏱️ Animation check after 4s:');
                    console.log('  - New transform:', newTransform);
                    
                    if (currentTransform === newTransform) {
                        console.log('❌ Animation appears to be stuck!');
                        
                        // Try to restart animation
                        track.style.animation = 'none';
                        track.offsetHeight; // Force reflow
                        track.style.animation = 'carousel-scroll 40s linear infinite';
                        console.log('🔄 Attempted to restart animation');
                    } else {
                        console.log('✅ Animation is working!');
                    }
                }, 2000);
            }
        }, 2000);
    }
    
    // Run debug after a short delay
    setTimeout(debugCarousel, 1000);
    
    // Also run debug on resize
    window.addEventListener('resize', () => {
        console.log('📱 Window resized to:', window.innerWidth + 'x' + window.innerHeight);
        setTimeout(debugCarousel, 500);
    });
});
