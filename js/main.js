/**
 * 个人学术主页 - JavaScript
 * 重庆大学 · 物理学院
 */

document.addEventListener('DOMContentLoaded', () => {

    'use strict';

    /* =========================================
       1. 页脚年份自动更新
       ========================================= */
    const footerYear = document.getElementById('footerYear');
    if (footerYear) {
        footerYear.textContent = new Date().getFullYear();
    }

    /* =========================================
       2. 移动端导航菜单切换
       ========================================= */
    const navToggle = document.getElementById('navToggle');
    const navMenu   = document.getElementById('navMenu');
    const navLinks  = document.querySelectorAll('.nav-link');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // 点击导航链接后自动关闭菜单
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });

        // 点击页面其他区域关闭菜单
        document.addEventListener('click', (e) => {
            if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });
    }

    /* =========================================
       3. 导航栏滚动效果
       ========================================= */
    const navbar = document.getElementById('navbar');
    let lastScrollY = 0;

    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY;

        // 为导航栏添加阴影
        if (scrollY > 20) {
            navbar.style.boxShadow = '0 4px 24px rgba(0,0,0,0.06)';
        } else {
            navbar.style.boxShadow = 'none';
        }

        // 向下滚动时隐藏导航栏，向上滚动时显示
        if (scrollY > lastScrollY && scrollY > 200) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        lastScrollY = scrollY;
    });

    /* =========================================
       4. 返回顶部按钮
       ========================================= */
    const backToTop = document.getElementById('backToTop');

    if (backToTop) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 400) {
                backToTop.classList.add('show');
            } else {
                backToTop.classList.remove('show');
            }
        });

        backToTop.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    /* =========================================
       5. 滚动入场动画 (IntersectionObserver)
       ========================================= */
    const revealElements = document.querySelectorAll('.section, .research-card, .project-card, .honor-item, .pub-item, .timeline-item, .contact-card');

    // 为每个元素添加 .reveal 类
    revealElements.forEach(el => el.classList.add('reveal'));

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // 可选择只触发一次
                // observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px'
    });

    revealElements.forEach(el => observer.observe(el));

    /* =========================================
       6. 导航栏高亮当前 section
       ========================================= */
    const sections = document.querySelectorAll('section[id]');

    function highlightNavOnScroll() {
        let current = '';
        sections.forEach(section => {
            const rect = section.getBoundingClientRect();
            // 当 section 顶部进入视口上半部分时高亮
            if (rect.top <= window.innerHeight * 0.4) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.style.color = '';
            link.style.background = '';
            if (link.getAttribute('href') === `#${current}`) {
                link.style.color = 'var(--primary)';
                link.style.background = 'var(--primary-light)';
            }
        });
    }

    window.addEventListener('scroll', highlightNavOnScroll);
    highlightNavOnScroll(); // 初始调用

    /* =========================================
       7. 联系方式卡片可点击 (保留默认事件)
       ========================================= */
    document.querySelectorAll('.contact-card[href]').forEach(card => {
        card.addEventListener('click', function(e) {
            // 浏览器会自然处理链接跳转
        });
    });

    /* =========================================
       8. 控制台欢迎信息
       ========================================= */
    console.log('%c 🎓 重庆大学 · 物理学院 ',
        'background:#1a56db;color:#fff;font-size:16px;padding:8px 16px;border-radius:4px;font-weight:bold;');
    console.log('%c 欢迎来访！如有建议请联系我 ~ ',
        'color:#64748b;font-size:13px;');

});
