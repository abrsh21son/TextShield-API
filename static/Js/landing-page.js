// Mobile menu functionality
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
    
    // Toggle mobile menu
    hamburger.addEventListener('click', function() {
        this.classList.toggle('active');
        mobileMenu.classList.toggle('active');
    });
    
    // Close mobile menu when a link is clicked
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            mobileMenu.classList.remove('active');
        });
    });
    
    // Animate progress bars on scroll
    const progressBars = document.querySelectorAll('.progress-fill');
    
    function animateProgressBars() {
        progressBars.forEach(bar => {
            const width = bar.getAttribute('data-width');
            if (isElementInViewport(bar)) {
                bar.style.width = width + '%';
            }
        });
    }
    
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
    
    // Initial check and scroll listener
    animateProgressBars();
    window.addEventListener('scroll', animateProgressBars);
    
    // Demo functionality
    const analyzeBtn = document.getElementById('analyze-btn');
    const demoInput = document.getElementById('demo-input');
    const demoResult = document.getElementById('demo-result');
    const processingTime = document.getElementById('processing-time');
    const resultStatus = document.getElementById('result-status');
    const toxicityBar = document.getElementById('toxicity-bar');
    const toxicityScore = document.getElementById('toxicity-score');
    const confidenceBar = document.getElementById('confidence-bar');
    const confidenceScore = document.getElementById('confidence-score');
    
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async function() {
            const text = demoInput.value.trim();
            
            if (!text) {
                alert('Please enter some text to analyze.');
                return;
            }
    
            // Show loading state
            this.disabled = true;
            this.textContent = 'Analyzing...';
            processingTime.textContent = '0.00s';
            demoResult.classList.add('hidden');
    
            const startTime = performance.now();
    
            try {
                const response = await fetch("/api/demo-analyze", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ text })
                });
    
                if (!response.ok) throw new Error(`Server returned ${response.status}`);
    
                const data = await response.json();
    
                if (!data.success || !data.result) {
                    throw new Error("Invalid response format");
                }
    
                const result = data.result;
    
                // Compute max toxicity
                const toxicity = Math.max(
                    result.toxicity ?? 0,
                    result.severe_toxicity ?? 0,
                    result.obscene ?? 0,
                    result.identity_attack ?? 0,
                    result.insult ?? 0,
                    result.threat ?? 0,
                    result.sexual_explicit ?? 0,
                    result.average ?? 0
                );
    
                // Confidence = same as model certainty in its prediction
                const confidence = toxicity;
    
                // Show result UI
                demoResult.classList.remove('hidden');
    
                // Determine toxicity level and color
                if (toxicity < 30) {
                    resultStatus.textContent = 'Safe';
                    resultStatus.className = 'px-3 py-1 rounded-full text-sm font-medium bg-green-500/20 text-green-400';
                    toxicityBar.className = 'bg-green-500 h-full rounded-full transition-all duration-1000';
                } else if (toxicity < 70) {
                    resultStatus.textContent = 'Moderate';
                    resultStatus.className = 'px-3 py-1 rounded-full text-sm font-medium bg-yellow-500/20 text-yellow-400';
                    toxicityBar.className = 'bg-yellow-500 h-full rounded-full transition-all duration-1000';
                } else {
                    resultStatus.textContent = 'Toxic';
                    resultStatus.className = 'px-3 py-1 rounded-full text-sm font-medium bg-red-500/20 text-red-400';
                    toxicityBar.className = 'bg-red-500 h-full rounded-full transition-all duration-1000';
                }
    
                // Animate bars
                setTimeout(() => {
                    toxicityBar.style.width = `${toxicity.toFixed(1)}%`;
                    confidenceBar.style.width = `${confidence.toFixed(1)}%`;
                }, 100);
    
                // Update scores
                toxicityScore.textContent = `${toxicity.toFixed(1)}%`;
                confidenceScore.textContent = `${confidence.toFixed(1)}%`;
    
                // Measure real processing time
                const endTime = performance.now();
                const elapsed = ((endTime - startTime) / 1000).toFixed(2);
                processingTime.textContent = `${elapsed}s`;
    
            } catch (error) {
                console.error("Analysis failed:", error);
                alert("Failed to analyze text. Please try again.");
            } finally {
                this.disabled = false;
                this.textContent = 'Analyze Text';
            }
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
});