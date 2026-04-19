/**
 * AutoCPD Portal Mapper Script
 * 
 * Injected into the target website to provide an interactive Element Picker HUD.
 * Uses a Shadow DOM to stay isolated from the host page's styling.
 */

(function() {
    if (window._autocpd_mapping_active) return;
    window._autocpd_mapping_active = true;

    // --- State ---
    let lastClickedElement = null;
    let lastSelector = null;
    let currentTargetName = "Title"; // Initial field
    
    // --- Global Signals for Selenium ---
    window._autocpd_verified_selector = null;
    window._autocpd_skipped = false;
    window._autocpd_is_ready = false;

    // --- UI Setup (Shadow DOM) ---
    const host = document.createElement('div');
    host.id = 'autocpd-mapper-host';
    document.body.appendChild(host);
    const shadow = host.attachShadow({ mode: 'closed' });

    // Using standard strings to avoid injection issues with backticks
    const styles = "#hud {" +
        "position: fixed; top: 10px; left: 50%; transform: translateX(-50%);" +
        "width: 500px; background: #2c3e50; color: #ecf0f1; padding: 15px;" +
        "border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);" +
        "z-index: 2147483647; font-family: sans-serif; display: flex;" +
        "flex-direction: column; gap: 10px; border: 2px solid #3498db;" +
        "}" +
        ".header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #34495e; padding-bottom: 5px; }" +
        ".target { font-weight: bold; color: #3498db; font-size: 16px; }" +
        ".info { font-size: 12px; background: #1a252f; padding: 8px; border-radius: 4px; word-break: break-all; min-height: 20px; }" +
        ".buttons { display: flex; gap: 8px; justify-content: flex-end; }" +
        "button { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: opacity 0.2s; }" +
        "button:hover { opacity: 0.8; }" +
        ".btn-confirm { background: #27ae60; color: white; }" +
        ".btn-skip { background: #f39c12; color: white; }" +
        ".btn-clear { background: #c0392b; color: white; }" +
        ".btn-start { background: #3498db; color: white; width: 100%; font-size: 14px; margin-top: 5px; }" +
        "#highlighter { position: absolute; pointer-events: none; border: 2px dashed #3498db; background: rgba(52, 152, 219, 0.1); z-index: 2147483646; transition: all 0.1s ease-out; display: none; }";

    const hudHtml = '<div id="hud">' +
        '<div class="header">' +
        "<div>AutoCPD Portal Mapper</div>" +
        '<div class="target" id="target-display">Preparation</div>' +
        "</div>" +
        '<div id="info-display" class="info">Please navigate to the portal\'s entry form and log in if required. Once you are at the form, click "I am Ready" below.</div>' +
        '<div id="setup-controls">' +
        '<button class="btn-start" id="btn-start">I am Ready - Start Mapping</button>' +
        "</div>" +
        '<div class="buttons" id="mapping-controls" style="display:none">' +
        '<button class="btn-clear" id="btn-clear">Clear</button>' +
        '<button class="btn-skip" id="btn-skip">Skip Field</button>' +
        '<button class="btn-confirm" id="btn-confirm" style="display:none">Confirm Selection</button>' +
        "</div>" +
        "</div>" +
        '<div id="highlighter"></div>';

    const styleSheet = document.createElement("style");
    styleSheet.innerText = styles;
    shadow.appendChild(styleSheet);

    const container = document.createElement("div");
    container.innerHTML = hudHtml;
    shadow.appendChild(container);

    const targetDisplay = shadow.getElementById('target-display');
    const infoDisplay = shadow.getElementById('info-display');
    const btnConfirm = shadow.getElementById('btn-confirm');
    const btnSkip = shadow.getElementById('btn-skip');
    const btnClear = shadow.getElementById('btn-clear');
    const btnStart = shadow.getElementById('btn-start');
    const setupControls = shadow.getElementById('setup-controls');
    const mappingControls = shadow.getElementById('mapping-controls');
    const highlighter = shadow.getElementById('highlighter');

    // --- Helpers ---
    function getCleanSelector(el) {
        if (el.id) return '#' + el.id;
        if (el.getAttribute('name')) {
            return el.tagName.toLowerCase() + '[name="' + el.getAttribute('name') + '"]';
        }
        
        let path = [];
        while (el.nodeType === Node.ELEMENT_NODE) {
            let selector = el.nodeName.toLowerCase();
            if (el.id) {
                selector += '#' + el.id;
                path.unshift(selector);
                break;
            } else {
                let siblings = Array.from(el.parentNode.children).filter(c => c.nodeName === el.nodeName);
                if (siblings.length > 1) {
                    selector += ':nth-child(' + (siblings.indexOf(el) + 1) + ')';
                }
            }
            path.unshift(selector);
            el = el.parentNode;
        }
        return path.join(' > ');
    }

    function updateHighlighter(el) {
        if (!el) {
            highlighter.style.display = 'none';
            return;
        }
        const rect = el.getBoundingClientRect();
        highlighter.style.top = (rect.top + window.scrollY) + 'px';
        highlighter.style.left = (rect.left + window.scrollX) + 'px';
        highlighter.style.width = rect.width + 'px';
        highlighter.style.height = rect.height + 'px';
        highlighter.style.display = 'block';
    }

    // --- Logic ---
    window.addEventListener('click', (e) => {
        if (!window._autocpd_is_ready) return; // Ignore clicks during preparation
        if (host.contains(e.target)) return;

        lastClickedElement = e.target;
        lastSelector = getCleanSelector(e.target);

        const nameOrId = e.target.id || e.target.getAttribute('name') || e.target.tagName;
        const type = e.target.getAttribute('type') || '';
        infoDisplay.innerText = "Selected: " + nameOrId + " [" + type + "]\nSelector: " + lastSelector;
        
        btnConfirm.style.display = 'inline-block';
        updateHighlighter(e.target);
    }, true);

    btnStart.onclick = function() {
        window._autocpd_is_ready = true;
        setupControls.style.display = 'none';
        mappingControls.style.display = 'flex';
    };

    btnClear.onclick = function() {
        lastClickedElement = null;
        lastSelector = null;
        infoDisplay.innerText = "Click a field on the page to select it...";
        btnConfirm.style.display = 'none';
        updateHighlighter(null);
    };

    btnConfirm.onclick = function() {
        if (!lastSelector) return;
        window._autocpd_verified_selector = lastSelector;
    };

    btnSkip.onclick = function() {
        window._autocpd_skipped = true;
    };

    window._autocpd_set_target = function(name) {
        window._autocpd_is_ready = true;
        setupControls.style.display = 'none';
        mappingControls.style.display = 'flex';
        
        currentTargetName = name;
        targetDisplay.innerText = "Mapping: " + name;
        infoDisplay.innerText = "Click the field for '" + name + "'...";
        btnConfirm.style.display = 'none';
        updateHighlighter(null);
        window._autocpd_verified_selector = null;
        window._autocpd_skipped = false;
    };

    console.log("AutoCPD Mapper Injected.");
})();
