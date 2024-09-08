document.addEventListener('DOMContentLoaded', () => {
    const content = document.querySelector('.scroll-content');
    const container = document.querySelector('.scroll-container');
    
    const scrollSpeed = 50;
    
    content.style.animationDuration = `${scrollSpeed}s`;
});

// Get testimonial slides and navigation buttons
const testimonialSlides = document.querySelectorAll('.testimonial-slide');
const prevBtn = document.querySelector('.prev-btn');
const nextBtn = document.querySelector('.next-btn');

// Set initial active slide
let activeSlideIndex = 0;
testimonialSlides[activeSlideIndex].classList.add('active');

// Function to show next slide
function showNextSlide() {
  testimonialSlides[activeSlideIndex].classList.remove('active');
  activeSlideIndex = (activeSlideIndex + 1) % testimonialSlides.length;
  testimonialSlides[activeSlideIndex].classList.add('active');
}

// Function to show previous slide
function showPrevSlide() {
  testimonialSlides[activeSlideIndex].classList.remove('active');
  activeSlideIndex = (activeSlideIndex - 1 + testimonialSlides.length) % testimonialSlides.length;
  testimonialSlides[activeSlideIndex].classList.add('active');
}

// Add event listeners to navigation buttons
prevBtn.addEventListener('click', showPrevSlide);
nextBtn.addEventListener('click', showNextSlide);

// Auto-slide every 5 seconds
setInterval(showNextSlide, 5000);

