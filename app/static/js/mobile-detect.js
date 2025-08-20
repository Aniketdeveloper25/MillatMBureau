// Mobile detection and video source setting
document.addEventListener('DOMContentLoaded', function() {
    // Get video elements
    var videoElement = document.getElementById('hero-video');
    var videoSource = document.getElementById('video-source');
    var videoContainer = document.querySelector('.video-container');
    
    // Function to check if device is mobile
    function isMobile() {
        return window.innerWidth <= 767.98;
    }
    
    // Function to check aspect ratio
    function isWideScreen() {
        return window.innerWidth / window.innerHeight > 16/9;
    }
    
    // Function to set appropriate video source and styling
    function setVideoSource() {
        if (!videoElement || !videoSource) return;
        
        // First pause the video to prevent rendering issues during source change
        videoElement.pause();
        
        if (isMobile()) {
            // Mobile device
            videoSource.setAttribute('src', mobileVideoUrl);
            
            // Apply mobile-specific styling
            videoElement.style.objectFit = "cover";
            videoElement.style.objectPosition = "center";
            
            if (window.matchMedia("(orientation: portrait)").matches) {
                // Portrait orientation on mobile
                videoElement.style.width = "100%";
                videoElement.style.height = "100%";
            } else {
                // Landscape orientation on mobile
                videoElement.style.width = "100%";
                videoElement.style.height = "100%";
            }
        } else {
            // Desktop device
            videoSource.setAttribute('src', desktopVideoUrl);
            
            // Apply desktop-specific styling
            videoElement.style.objectFit = "cover";
            videoElement.style.objectPosition = "center center";
            
            // Handle different aspect ratios
            if (isWideScreen()) {
                // Widescreen - ensure video covers width
                videoElement.style.width = "100%";
                videoElement.style.height = "auto";
                videoElement.style.top = "50%";
                videoElement.style.left = "50%";
                videoElement.style.transform = "translate(-50%, -50%)";
            } else {
                // Taller screen - ensure video covers height
                videoElement.style.width = "auto";
                videoElement.style.height = "100%";
                videoElement.style.top = "50%";
                videoElement.style.left = "50%";
                videoElement.style.transform = "translate(-50%, -50%)";
            }
        }
        
        // Force video to reload
        videoElement.load();
        
        // Ensure video is visible
        if (videoContainer) {
            videoContainer.style.display = 'block';
            videoContainer.style.visibility = 'visible';
        }
        
        // Make sure video plays after loading
        videoElement.onloadeddata = function() {
            videoElement.play().catch(function(error) {
                console.log("Auto-play prevented: ", error);
                // If autoplay is prevented, try again with user interaction
                document.addEventListener('click', function playVideoOnce() {
                    videoElement.play();
                    document.removeEventListener('click', playVideoOnce);
                }, { once: true });
            });
        };
    }
    
    // Set video source on page load
    setVideoSource();
    
    // Update video source on window resize with debounce
    var resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            setVideoSource();
        }, 200);
    });
    
    // Update video source on orientation change for mobile devices
    window.addEventListener('orientationchange', function() {
        setTimeout(function() {
            setVideoSource();
        }, 200);
    });
}); 