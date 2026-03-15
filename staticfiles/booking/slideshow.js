// Indian Train Slideshow JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.slideshow-image');
    const dots = document.querySelectorAll('.slideshow-dot');
    const prevBtn = document.querySelector('.slideshow-prev');
    const nextBtn = document.querySelector('.slideshow-next');
    let currentIndex = 0;
    let interval;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.remove('active');
            dots[i].classList.remove('active');
        });
        slides[index].classList.add('active');
        dots[index].classList.add('active');
    }

    function nextSlide() {
        currentIndex = (currentIndex + 1) % slides.length;
        showSlide(currentIndex);
    }

    function prevSlide() {
        currentIndex = (currentIndex - 1 + slides.length) % slides.length;
        showSlide(currentIndex);
    }

    function startSlideshow() {
        interval = setInterval(nextSlide, 5000);
    }

    function stopSlideshow() {
        clearInterval(interval);
    }

    // Event listeners
    prevBtn.addEventListener('click', () => {
        prevSlide();
        stopSlideshow();
        startSlideshow();
    });

    nextBtn.addEventListener('click', () => {
        nextSlide();
        stopSlideshow();
        startSlideshow();
    });

    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            currentIndex = index;
            showSlide(currentIndex);
            stopSlideshow();
            startSlideshow();
        });
    });

    // Pause on hover
    const slideshowContainer = document.querySelector('.slideshow-container');
    if (slideshowContainer) {
        slideshowContainer.addEventListener('mouseenter', stopSlideshow);
        slideshowContainer.addEventListener('mouseleave', startSlideshow);
    }

    // Start the slideshow
    startSlideshow();
});
