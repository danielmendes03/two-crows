document.addEventListener('DOMContentLoaded', () => {

    // -------------------------------------
    // 1. ANIMAÇÃO DE FADE-IN
    // -------------------------------------
    const faders = document.querySelectorAll('.fade-in');
    const appearOptions = { threshold: 0.2, rootMargin: "0px 0px -50px 0px" };
    const appearOnScroll = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        });
    }, appearOptions);
    faders.forEach(fader => appearOnScroll.observe(fader));

    // -------------------------------------
    // 2. GERADOR DE PALAVRAS FLUTUANTES
    // -------------------------------------
    const problemSection = document.getElementById('problem');
    const contactSection = document.getElementById('contact');
    const chaosWords = { words: ["Deepfake", "Phishing", "Golpe", "IA Maliciosa", "Fake News", "Manipulação", "Vírus", "Invasão de Privacidade", "Roubo de Dados"], colors: ['var(--white)', 'var(--red-alert)'], animationClass: 'chaos' };
    const trustWords = { words: ["Verificado", "Auditado", "Transparência", "Integridade", "Autenticidade", "Segurança", "Confiável", "Certificado", "Proteção", "Veracidade", "Privacidade", "Legítimo", "Atestado", "Validado", "Precisão", "À Prova de Fraude", "Consistente", "Algoritmo Ético", "Verificação de Fatos"], colors: ['var(--white)', 'var(--green-safe)'], animationClass: 'trust' };
    
    function createFloatingWord(word, color, fontSize, top, left, animationClass) {
        const wordEl = document.createElement('div');
        wordEl.className = `floating-word ${animationClass}`;
        wordEl.textContent = word;
        wordEl.style.color = color;
        wordEl.style.fontSize = `${fontSize}rem`;
        wordEl.style.top = `${top}px`;
        wordEl.style.left = `${left}px`;
        return wordEl;
    }

    function manageFloatingWords(section, contentSelector, wordConfig, interval) {
        let wordInterval;
        const contentBox = section.querySelector(contentSelector);
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                if (!wordInterval) {
                    wordInterval = setInterval(() => {
                        const boxRect = contentBox.getBoundingClientRect();
                        const sectionRect = section.getBoundingClientRect();
                        const boxTop = boxRect.top - sectionRect.top;
                        const boxBottom = boxRect.bottom - sectionRect.top;
                        const boxLeft = boxRect.left - sectionRect.left;
                        const boxRight = boxRect.right - sectionRect.left;
                        const zone = Math.floor(Math.random() * 4);
                        let top, left;
                        if (zone === 0) {
                            top = Math.random() * boxTop;
                            left = Math.random() * section.offsetWidth;
                        } else if (zone === 1) {
                            const safeZoneBottom = section.offsetHeight * 0.85;
                            top = boxBottom + Math.random() * (safeZoneBottom - boxBottom);
                            left = Math.random() * section.offsetWidth;
                        } else if (zone === 2) {
                            top = Math.random() * section.offsetHeight;
                            left = Math.random() * boxLeft;
                        } else {
                            top = Math.random() * section.offsetHeight;
                            left = boxRight + Math.random() * (section.offsetWidth - boxRight);
                        }
                        const word = wordConfig.words[Math.floor(Math.random() * wordConfig.words.length)];
                        const color = wordConfig.colors[Math.floor(Math.random() * wordConfig.colors.length)];
                        const isChaos = wordConfig.animationClass === 'chaos';
                        const fontSize = isChaos ? Math.random() * (3.5 - 1.5) + 1.5 : Math.random() * (2.5 - 1.2) + 1.2;
                        const wordElement = createFloatingWord(word, color, fontSize, top, left, wordConfig.animationClass);
                        section.appendChild(wordElement);
                        setTimeout(() => wordElement.remove(), 3000);
                    }, interval);
                }
            } else {
                clearInterval(wordInterval);
                wordInterval = null;
            }
        }, { threshold: 0.1 });
        observer.observe(section);
    }
    
    manageFloatingWords(problemSection, '.problem-container', chaosWords, 700);
    manageFloatingWords(contactSection, '.contact-container', trustWords, 1200);

    // -------------------------------------
    // 3. ATUALIZAÇÃO DO VALOR DO RATING
    // -------------------------------------
    const ratingSlider = document.getElementById('enthusiasm');
    const ratingValueOutput = document.getElementById('rating-value');
    if (ratingSlider && ratingValueOutput) {
        ratingSlider.addEventListener('input', (event) => {
            ratingValueOutput.textContent = event.target.value;
        });
    }

    // -------------------------------------
    // 4. ANIMAÇÃO DO SCANNER COM PORCENTAGEM
    // -------------------------------------
    const heroSection = document.getElementById('hero');
    const scannerElement = heroSection.querySelector('.scanner');
    const scanPercentageElement = heroSection.querySelector('.scan-percentage');
    const scanDuration = 7000; 

    function updateScanPercentage(currentTime, startTime) {
        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / scanDuration, 1);
        const percentage = Math.floor(progress * 100);
        scanPercentageElement.textContent = `${percentage}%`;
        if (progress < 1) {
            requestAnimationFrame((time) => updateScanPercentage(time, startTime));
        }
    }
    
    scannerElement.addEventListener('animationiteration', () => {
        requestAnimationFrame((time) => updateScanPercentage(time, time));
    });

    const heroObserver = new IntersectionObserver((entries) => {
        scannerElement.classList.toggle('visible', entries[0].isIntersecting);
        if (entries[0].isIntersecting) {
            requestAnimationFrame((time) => updateScanPercentage(time, time));
        }
    }, { threshold: 0.5 });
    heroObserver.observe(heroSection);
    
    // -------------------------------------
    // 5. LÓGICA DA NAVEGAÇÃO LATERAL (SIDE-NAV)
    // -------------------------------------
    const sideNav = document.getElementById('side-nav');
    const navDots = document.querySelectorAll('.nav-dot');
    const navSections = document.querySelectorAll('section[data-nav-id]');
    
    setTimeout(() => {
        sideNav.classList.add('visible');
    }, 500);

    const navObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const currentSectionId = entry.target.getAttribute('data-nav-id');
                let activeIndex = 0;

                navDots.forEach((dot, index) => {
                    const dotId = dot.getAttribute('data-nav-id');
                    if (dotId === currentSectionId) {
                        dot.classList.add('active');
                        activeIndex = index;
                    } else {
                        dot.classList.remove('active');
                    }
                });

                const progressHeight = (activeIndex / (navDots.length - 1)) * 100;
                document.documentElement.style.setProperty('--nav-progress-height', `${progressHeight}%`);
            }
        });
    }, { threshold: 0.5 });

    navSections.forEach(section => navObserver.observe(section));
    
    document.documentElement.style.setProperty('--nav-progress-height', '0%');
});