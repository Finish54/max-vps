document.addEventListener('DOMContentLoaded', () => {
    
    // -------------------------------------------------------------
    // 1. Matrix Digital Rain Canvas Animation
    // -------------------------------------------------------------
    const canvas = document.getElementById('matrix-rain');
    const ctx = canvas.getContext('2d');

    // Resize canvas to full screen
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Characters list (Russian Cyrillic, Latin and numbers)
    const chars = '0123456789АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const charArray = chars.split('');

    const fontSize = 16;
    // Calculate columns amount
    let columns = canvas.width / fontSize;

    // Track drop positions for each column
    const drops = [];
    for (let i = 0; i < columns; i++) {
        drops[i] = Math.random() * -100; // Initialize at random negative heights
    }

    function drawMatrixRain() {
        // Clear with slight transparency for trail effect
        ctx.fillStyle = 'rgba(5, 8, 12, 0.08)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#00ff41'; // Matrix neon green
        ctx.font = fontSize + 'px "Share Tech Mono", monospace';

        // Recalculate columns on screen resize implicitly
        if (columns < canvas.width / fontSize) {
            const diff = Math.floor(canvas.width / fontSize) - columns;
            for (let i = 0; i < diff; i++) {
                drops.push(Math.random() * -100);
            }
            columns = canvas.width / fontSize;
        }

        // Draw drops
        for (let i = 0; i < columns; i++) {
            const char = charArray[Math.floor(Math.random() * charArray.length)];
            
            // Randomize brightness for some characters
            if (Math.random() > 0.98) {
                ctx.fillStyle = '#ffffff'; // White highlight character
            } else if (Math.random() > 0.95) {
                ctx.fillStyle = '#003b00'; // Dim green
            } else {
                ctx.fillStyle = '#00ff41'; // Standard green
            }
            
            const x = i * fontSize;
            const y = drops[i] * fontSize;

            ctx.fillText(char, x, y);

            // Reset drop to top once it goes offscreen, with random delay
            if (y > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }

            drops[i]++;
        }
    }
    
    // Matrix Rain animation loop
    setInterval(drawMatrixRain, 33);

    // -------------------------------------------------------------
    // 2. Header Clock System (UTC)
    // -------------------------------------------------------------
    const clockElement = document.getElementById('digital-clock');
    
    function updateClock() {
        const now = new Date();
        const utcTimeString = now.toUTCString().replace('GMT', 'UTC');
        clockElement.textContent = utcTimeString;
    }
    updateClock();
    setInterval(updateClock, 1000);

    // -------------------------------------------------------------
    // 3. Boot Terminal Emulator typing effect
    // -------------------------------------------------------------
    const bootLog = document.getElementById('boot-log');
    const logLines = bootLog.querySelectorAll('.log-line');

    function executeBootLog() {
        logLines.forEach((line, index) => {
            const delay = parseInt(line.getAttribute('data-delay') || '0', 10);
            setTimeout(() => {
                line.classList.remove('hidden');
                
                // Set the active typing line cursor
                if (index > 0) {
                    logLines[index - 1].classList.remove('typing');
                }
                
                line.classList.add('typing');
                
                // Remove cursor from last line
                if (index === logLines.length - 1) {
                    setTimeout(() => {
                        line.classList.remove('typing');
                    }, 1000);
                }
            }, delay);
        });
    }
    executeBootLog();

    // -------------------------------------------------------------
    // 4. Pill Choices Interactions
    // -------------------------------------------------------------
    const pillBlue = document.getElementById('pill-blue-trigger');
    const pillRed = document.getElementById('pill-red-trigger');
    const welcomeConsole = document.getElementById('welcome-console');
    const pillSection = document.getElementById('pill-section');
    
    const illusionScreen = document.getElementById('illusion-screen');
    const backToRealityBtn = document.getElementById('back-to-reality-btn');
    const unlockedContent = document.getElementById('real-world-content');
    const userIpSpan = document.querySelector('.user-ip');

    // Fetch user IP for the "illusion" screen
    async function fetchUserIP() {
        try {
            const response = await fetch('https://api.ipify.org?format=json');
            const data = await response.json();
            userIpSpan.textContent = data.ip;
        } catch (e) {
            // Fallback mock IP if blocked or offline
            userIpSpan.textContent = '195.144.20.73 [ЗАБЛОКИРОВАНО ПРОВАЙДЕРОМ]';
        }
    }

    // Choose Blue Pill: show error screen
    pillBlue.addEventListener('click', () => {
        fetchUserIP();
        illusionScreen.classList.remove('hidden');
        document.body.style.overflow = 'hidden'; // Lock scrolling
    });

    // Go back from blue screen (Accept reality)
    backToRealityBtn.addEventListener('click', () => {
        illusionScreen.classList.add('hidden');
        document.body.style.overflow = ''; // Unlock scrolling
        unlockRealWorld();
    });

    // Choose Red Pill: unlock landing page content
    pillRed.addEventListener('click', () => {
        unlockRealWorld();
    });

    function unlockRealWorld() {
        // Unlock real world info block
        unlockedContent.classList.remove('hidden');
        
        // Hide initial console & pill chooser
        welcomeConsole.classList.add('hidden');
        pillSection.classList.add('hidden');
        
        // Scroll smoothly to features
        const featuresSection = document.getElementById('features');
        featuresSection.scrollIntoView({ behavior: 'smooth' });

        // Add cyber override line to console or top level logging
        console.log("SYSTEM OVERRIDE: MATRIX DECRYPTED. VPN ACCESS GRANTED.");
    }

    // -------------------------------------------------------------
    // 5. Pricing Terminal Controller
    // -------------------------------------------------------------
    const priceOptions = document.querySelectorAll('.price-option');
    const summaryMonthsVal = document.getElementById('summary-months-val');
    const summaryPriceVal = document.getElementById('summary-price-val');

    priceOptions.forEach(option => {
        option.addEventListener('click', () => {
            // Deactivate all options
            priceOptions.forEach(opt => opt.classList.remove('active'));
            
            // Activate selected
            option.classList.add('active');

            // Read dataset values
            const months = option.getAttribute('data-months');
            const priceTotal = option.getAttribute('data-total');

            // Update UI elements
            summaryMonthsVal.textContent = months === '1' ? '1 МЕСЯЦ' : 
                                           months === '3' ? '3 МЕСЯЦА' : 
                                           months === '6' ? '6 МЕСЯЦЕВ' : '12 МЕСЯЦЕВ';
            summaryPriceVal.textContent = priceTotal + ' ₽';
        });
    });

    // -------------------------------------------------------------
    // 6. FAQ Accordion Toggle
    // -------------------------------------------------------------
    const faqTriggers = document.querySelectorAll('.faq-trigger');

    faqTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const faqItem = trigger.parentElement;
            const statusSpan = trigger.querySelector('.faq-status');
            
            // Toggle active class
            faqItem.classList.toggle('active');
            
            // Update accordion symbols
            if (faqItem.classList.contains('active')) {
                statusSpan.textContent = '[-]';
            } else {
                statusSpan.textContent = '[+]';
            }
        });
    });
});
