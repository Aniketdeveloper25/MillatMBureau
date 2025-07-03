// This script creates a simple notification sound using the Web Audio API
// It's used as a fallback when the MP3 file is not available

function playNotificationSound() {
  try {
    // Create audio context
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const audioCtx = new AudioContext();
    
    // Create oscillator for the notification sound
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    
    // Configure the sound - use a higher frequency for better attention
    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(1000, audioCtx.currentTime); // Higher note for better attention
    
    // Configure volume envelope - slightly louder
    gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
    gainNode.gain.linearRampToValueAtTime(0.7, audioCtx.currentTime + 0.05);
    gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.5);
    
    // Create a second oscillator for a more complex sound
    const oscillator2 = audioCtx.createOscillator();
    oscillator2.type = 'sine';
    oscillator2.frequency.setValueAtTime(1200, audioCtx.currentTime);
    oscillator2.frequency.linearRampToValueAtTime(800, audioCtx.currentTime + 0.2);
    
    const gainNode2 = audioCtx.createGain();
    gainNode2.gain.setValueAtTime(0, audioCtx.currentTime);
    gainNode2.gain.linearRampToValueAtTime(0.5, audioCtx.currentTime + 0.1);
    gainNode2.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.3);
    
    // Connect nodes
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    
    oscillator2.connect(gainNode2);
    gainNode2.connect(audioCtx.destination);
    
    // Play the sound
    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.5);
    
    oscillator2.start();
    oscillator2.stop(audioCtx.currentTime + 0.3);
    
    return true;
  } catch (e) {
    console.error('Failed to play notification sound:', e);
    return false;
  }
}