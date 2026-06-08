/*
 * Plataforma Estadual de Sustentabilidade em Contratações Públicas (PESCP)
 * Laboratório de Inovação em Logística Pública (LILP) | SGGD
 *
 * main.js — controles do lado cliente:
 *   - A11y:        fonte +/-, alto contraste, persistência localStorage
 *   - Atalhos:     Alt+1..4 — conteúdo, menu, busca, rodapé
 *   - Menu:        hambúrguer mobile com aria-expanded e ESC fecha
 *   - Cookies:     banner LGPD + modal de personalização
 *   - AvisoVersao: faixa amarela fechável por sessão
 *   - Copiar:      botão "Copiar Providência" em /criterios/<slug>/
 *
 * Conformidade: eMAG 3.1 (R6.1 atalhos, R5.4 foco), WCAG 2.0 AA,
 *               LGPD (Lei 13.709/2018).
 *
 * Arquivo único IIFE — sem build tooling. Compatível com CSP
 * script-src 'self' (zero inline handlers).
 */

(function () {
    'use strict';

    var STORAGE_KEYS = {
        contraste: 'sp-a11y:contraste',
        fonte:     'sp-a11y:fonte-escala',
        cookies:   'sp-lgpd-consent'
    };
    var SESSION_KEYS = {
        avisoVersao: 'pescp-aviso-versao-fechado'
    };

    var FONTE_MIN = -2;
    var FONTE_MAX = 4;

    /* ============================================================
       Módulo: Acessibilidade (fonte + contraste)
       ============================================================ */
    var A11y = {
        init: function () {
            this.applyStoredPrefs();
            this.bindFonteControls();
            this.bindContrasteControl();
        },
        bindFonteControls: function () {
            var btns = document.querySelectorAll('[data-a11y-action="font-up"], [data-a11y-action="font-down"]');
            for (var i = 0; i < btns.length; i++) {
                btns[i].addEventListener('click', this.onFontClick.bind(this));
            }
        },
        bindContrasteControl: function () {
            var btn = document.querySelector('[data-a11y-action="contrast"]');
            if (!btn) return;
            btn.addEventListener('click', this.onContrasteClick.bind(this));
        },
        onFontClick: function (event) {
            var action = event.currentTarget.getAttribute('data-a11y-action');
            var atual = this.getFonteEscala();
            var novo = action === 'font-up' ? atual + 1 : atual - 1;
            if (novo < FONTE_MIN) novo = FONTE_MIN;
            if (novo > FONTE_MAX) novo = FONTE_MAX;
            this.setFonteEscala(novo);
        },
        onContrasteClick: function (event) {
            var btn = event.currentTarget;
            var ativo = document.body.classList.toggle('sp-alto-contraste');
            btn.setAttribute('aria-pressed', ativo ? 'true' : 'false');
            try { localStorage.setItem(STORAGE_KEYS.contraste, ativo ? '1' : '0'); } catch (e) { /* noop */ }
        },
        getFonteEscala: function () {
            try {
                var v = parseInt(localStorage.getItem(STORAGE_KEYS.fonte) || '0', 10);
                return isNaN(v) ? 0 : v;
            } catch (e) { return 0; }
        },
        setFonteEscala: function (escala) {
            try { localStorage.setItem(STORAGE_KEYS.fonte, String(escala)); } catch (e) { /* noop */ }
            this.applyFonteEscala(escala);
        },
        applyFonteEscala: function (escala) {
            var html = document.documentElement;
            for (var i = FONTE_MIN; i <= FONTE_MAX; i++) {
                if (i > 0) html.classList.remove('sp-fonte-aumentada-' + i);
                if (i < 0) html.classList.remove('sp-fonte-diminuida-' + Math.abs(i));
            }
            if (escala > 0) html.classList.add('sp-fonte-aumentada-' + escala);
            if (escala < 0) html.classList.add('sp-fonte-diminuida-' + Math.abs(escala));
        },
        applyStoredPrefs: function () {
            this.applyFonteEscala(this.getFonteEscala());
            try {
                var contraste = localStorage.getItem(STORAGE_KEYS.contraste) === '1';
                if (contraste) {
                    document.body.classList.add('sp-alto-contraste');
                    var btn = document.querySelector('[data-a11y-action="contrast"]');
                    if (btn) btn.setAttribute('aria-pressed', 'true');
                }
            } catch (e) { /* noop */ }
        }
    };

    /* ============================================================
       Módulo: Atalhos de teclado (eMAG R6.1) — Alt+1..4
       ============================================================ */
    var Atalhos = {
        init: function () {
            document.addEventListener('keydown', this.onKey.bind(this));
        },
        onKey: function (event) {
            if (!event.altKey || event.ctrlKey || event.metaKey) return;
            var alvo = null;
            switch (event.key) {
                case '1': alvo = document.getElementById('sp-conteudo'); break;
                case '2': alvo = document.getElementById('sp-menu'); break;
                case '3': alvo = document.getElementById('sp-busca-input') || document.getElementById('sp-busca'); break;
                case '4': alvo = document.getElementById('sp-rodape'); break;
                default: return;
            }
            if (!alvo) return;
            event.preventDefault();
            if (!alvo.hasAttribute('tabindex')) alvo.setAttribute('tabindex', '-1');
            alvo.focus();
            alvo.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    /* ============================================================
       Módulo: Menu hambúrguer mobile
       ============================================================ */
    var Menu = {
        init: function () {
            this.toggleBtn = document.querySelector('.sp-menu-principal__toggle');
            this.container = document.querySelector('.sp-menu-principal');
            this.lista = document.getElementById('sp-menu-lista');
            if (!this.toggleBtn || !this.container || !this.lista) return;
            this.toggleBtn.addEventListener('click', this.toggle.bind(this));
            document.addEventListener('keydown', this.onKey.bind(this));
            document.addEventListener('click', this.onDocClick.bind(this));
        },
        abrir: function () {
            this.container.setAttribute('data-aberto', 'true');
            this.toggleBtn.setAttribute('aria-expanded', 'true');
            this.toggleBtn.setAttribute('aria-label', 'Fechar menu de navegação');
            var primeiro = this.lista.querySelector('a');
            if (primeiro) primeiro.focus();
        },
        fechar: function (devolverFoco) {
            this.container.removeAttribute('data-aberto');
            this.toggleBtn.setAttribute('aria-expanded', 'false');
            this.toggleBtn.setAttribute('aria-label', 'Abrir menu de navegação');
            if (devolverFoco) this.toggleBtn.focus();
        },
        toggle: function () {
            var aberto = this.container.getAttribute('data-aberto') === 'true';
            if (aberto) this.fechar(false); else this.abrir();
        },
        onKey: function (event) {
            if (event.key === 'Escape' && this.container.getAttribute('data-aberto') === 'true') {
                this.fechar(true);
            }
        },
        onDocClick: function (event) {
            if (this.container.getAttribute('data-aberto') !== 'true') return;
            if (this.container.contains(event.target)) return;
            this.fechar(false);
        }
    };

    /* ============================================================
       Módulo: Banner de cookies LGPD
       ============================================================ */
    var CONSENT_VERSION = 1;
    var Cookies = {
        init: function () {
            this.banner = document.querySelector('[data-cookies-banner]');
            this.modal = document.querySelector('[data-cookies-modal]');
            if (!this.banner) return;
            var consent = this.getConsent();
            if (!consent || consent.versao !== CONSENT_VERSION) this.exibirBanner();
            this.bindAcoes();
        },
        bindAcoes: function () {
            var self = this;
            var nodes = document.querySelectorAll('[data-cookies-action]');
            for (var i = 0; i < nodes.length; i++) {
                nodes[i].addEventListener('click', function (event) {
                    var acao = event.currentTarget.getAttribute('data-cookies-action');
                    self.onAcao(acao, event);
                });
            }
            document.addEventListener('keydown', function (event) {
                if (event.key === 'Escape' && self.modal && !self.modal.hasAttribute('hidden')) {
                    self.fecharModal();
                }
            });
        },
        onAcao: function (acao) {
            switch (acao) {
                case 'accept-all':
                    this.salvarConsentimento({ funcionalidades: true, analytics: true });
                    this.ocultarBanner();
                    break;
                case 'essential-only':
                    this.salvarConsentimento({ funcionalidades: false, analytics: false });
                    this.ocultarBanner();
                    break;
                case 'customize':
                    this.abrirModal();
                    break;
                case 'save-customize':
                    var func = !!document.querySelector('[data-cookies-cat="funcionalidades"]:checked');
                    var anal = !!document.querySelector('[data-cookies-cat="analytics"]:checked');
                    this.salvarConsentimento({ funcionalidades: func, analytics: anal });
                    this.fecharModal();
                    this.ocultarBanner();
                    break;
                case 'close-modal':
                    this.fecharModal();
                    break;
            }
        },
        exibirBanner: function () { this.banner.removeAttribute('hidden'); },
        ocultarBanner: function () { this.banner.setAttribute('hidden', ''); },
        abrirModal: function () {
            if (!this.modal) return;
            var consent = this.getConsent();
            var inputs = this.modal.querySelectorAll('[data-cookies-cat]');
            for (var i = 0; i < inputs.length; i++) {
                var cat = inputs[i].getAttribute('data-cookies-cat');
                inputs[i].checked = !!(consent && consent.categorias && consent.categorias[cat]);
            }
            this.modal.removeAttribute('hidden');
            this.previousFocus = document.activeElement;
            var primeiro = this.modal.querySelector('button, input, [tabindex]');
            if (primeiro) primeiro.focus();
        },
        fecharModal: function () {
            if (!this.modal) return;
            this.modal.setAttribute('hidden', '');
            if (this.previousFocus && this.previousFocus.focus) this.previousFocus.focus();
        },
        getConsent: function () {
            try {
                var raw = localStorage.getItem(STORAGE_KEYS.cookies);
                return raw ? JSON.parse(raw) : null;
            } catch (e) { return null; }
        },
        salvarConsentimento: function (categorias) {
            var registro = {
                versao: CONSENT_VERSION,
                timestamp: new Date().toISOString(),
                categorias: {
                    necessarios:     true,
                    funcionalidades: !!categorias.funcionalidades,
                    analytics:       !!categorias.analytics
                }
            };
            try { localStorage.setItem(STORAGE_KEYS.cookies, JSON.stringify(registro)); } catch (e) { /* noop */ }
        }
    };

    /* ============================================================
       Módulo: Aviso de versão 1.0 (faixa amarela, fechável por sessão)
       ============================================================ */
    var AvisoVersao = {
        init: function () {
            var aviso = document.querySelector('[data-aviso-versao]');
            if (!aviso) return;
            try {
                if (sessionStorage.getItem(SESSION_KEYS.avisoVersao) === '1') {
                    aviso.setAttribute('hidden', '');
                    return;
                }
            } catch (e) { /* noop */ }
            var btn = aviso.querySelector('[data-aviso-fechar]');
            if (!btn) return;
            btn.addEventListener('click', function () {
                aviso.setAttribute('hidden', '');
                try { sessionStorage.setItem(SESSION_KEYS.avisoVersao, '1'); } catch (e) { /* noop */ }
            });
        }
    };

    /* ============================================================
       Módulo: Botão Copiar Providência
       ============================================================ */
    var Copiar = {
        init: function () {
            var botoes = document.querySelectorAll('[data-copiar-target]');
            for (var i = 0; i < botoes.length; i++) {
                botoes[i].addEventListener('click', this.onClick.bind(this));
            }
        },
        onClick: function (event) {
            var btn = event.currentTarget;
            var seletor = btn.getAttribute('data-copiar-target');
            var alvo = document.querySelector(seletor);
            if (!alvo) return;
            var texto = alvo.innerText || alvo.textContent || '';
            var feedbackOriginal = btn.innerHTML;

            var onSucesso = function () {
                btn.innerHTML = '✓ Copiado';
                setTimeout(function () { btn.innerHTML = feedbackOriginal; }, 2000);
            };
            var onFalha = function () {
                btn.innerHTML = '✗ Falha';
                setTimeout(function () { btn.innerHTML = feedbackOriginal; }, 2000);
            };

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(texto).then(onSucesso, onFalha);
            } else {
                try {
                    var ta = document.createElement('textarea');
                    ta.value = texto;
                    ta.setAttribute('readonly', '');
                    ta.style.position = 'absolute';
                    ta.style.left = '-9999px';
                    document.body.appendChild(ta);
                    ta.select();
                    document.execCommand('copy');
                    document.body.removeChild(ta);
                    onSucesso();
                } catch (e) { onFalha(); }
            }
        }
    };

    /* ============================================================
       Inicialização
       ============================================================ */
    function init() {
        try { A11y.init(); }        catch (e) { console.error('[PESCP] A11y init falhou:', e); }
        try { Atalhos.init(); }     catch (e) { console.error('[PESCP] Atalhos init falhou:', e); }
        try { Menu.init(); }        catch (e) { console.error('[PESCP] Menu init falhou:', e); }
        try { Cookies.init(); }     catch (e) { console.error('[PESCP] Cookies init falhou:', e); }
        try { AvisoVersao.init(); } catch (e) { console.error('[PESCP] AvisoVersao init falhou:', e); }
        try { Copiar.init(); }      catch (e) { console.error('[PESCP] Copiar init falhou:', e); }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
