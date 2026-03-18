document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navLinks.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
        });
    });

    const loadContent = async (url, container) => {
        try {
            const response = await fetch(url);
            const data = await response.json();
            document.querySelector(container).innerHTML = JSON.stringify(data, null, 2);
        } catch (error) {
            console.error('Error loading content:', error);
        }
    };

    if (document.querySelector('#portfolio')) {
        loadContent('/api/portfolio/demo', '#portfolio');
    }

    if (document.querySelector('#market-trends')) {
        loadContent('/api/market-trends', '#market-trends');
    }

    const smoothScroll = (target, duration) => {
        const targetPosition = document.querySelector(target).offsetTop;
        const startPosition = window.pageYOffset;
        const distance = targetPosition - startPosition;
        let startTime = null;

        function animation(currentTime) {
            if (startTime === null) startTime = currentTime;
            const timeElapsed = currentTime - startTime;
            const run = ease(timeElapsed, startPosition, distance, duration);
            window.scrollTo(0, run);
            if (timeElapsed < duration) requestAnimationFrame(animation);
        }

        function ease(t, b, c, d) {
            t /= d / 2;
            if (t < 1) return c / 2 * t * t + b;
            t--;
            return -c / 2 * (t * (t - 2) - 1) + b;
        }

        requestAnimationFrame(animation);
    };

    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const target = this.getAttribute('href');
            if (target.startsWith('#')) {
                e.preventDefault();
                smoothScroll(target, 1000);
            }
        });
    });
});
