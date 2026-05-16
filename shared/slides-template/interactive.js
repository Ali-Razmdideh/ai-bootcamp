/* Interactive exercises for slides.
 *
 * Markup pattern (inside a Reveal section):
 *   <section class="exercise" data-packages="numpy">
 *     <h2>Exercise N — Task M</h2>
 *     <div class="ex-prompt">Description shown to the learner.</div>
 *     <textarea class="ex-code"># starter code</textarea>
 *     <div class="ex-controls">
 *       <button class="ex-run">Run &amp; Check</button>
 *       <button class="ex-reset">Reset</button>
 *       <button class="ex-show">Show solution</button>
 *       <span class="ex-status"></span>
 *     </div>
 *     <pre class="ex-output"></pre>
 *     <div class="ex-feedback"></div>
 *     <script type="text/x-check">
 *       # Python that raises AssertionError on failure. Runs in same namespace
 *       # as user code. Use `assert` with a message.
 *     </script>
 *     <script type="text/x-solution"># reference solution shown on failure</script>
 *     <script type="text/x-explain">Prose explanation shown on failure.</script>
 *   </section>
 *
 * data-packages: comma-separated extra Pyodide packages to load (numpy, pandas, matplotlib, scipy).
 *                "numpy" is loaded by default.
 */
(function () {
  const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js';
  let pyodidePromise = null;
  const loadedPackages = new Set();

  function loadPyodide() {
    if (pyodidePromise) return pyodidePromise;
    pyodidePromise = new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = PYODIDE_URL;
      s.onload = async () => {
        try {
          const py = await window.loadPyodide();
          await py.loadPackage(['numpy']);
          loadedPackages.add('numpy');
          resolve(py);
        } catch (e) { reject(e); }
      };
      s.onerror = () => reject(new Error('Failed to load Pyodide'));
      document.head.appendChild(s);
    });
    return pyodidePromise;
  }

  // Python snippet that closes any open matplotlib figures and returns
  // the most recent ones as base64-encoded PNGs. Safe to run even when
  // matplotlib was never imported by the user code.
  const COLLECT_FIGS_PY = `\
import sys as _sys
_figs_b64 = []
if 'matplotlib' in _sys.modules:
    import io as _io, base64 as _b64
    from matplotlib import pyplot as _plt
    for _n in _plt.get_fignums():
        _f = _plt.figure(_n)
        _buf = _io.BytesIO()
        try:
            _f.savefig(_buf, format='png', dpi=110, bbox_inches='tight')
            _figs_b64.append(_b64.b64encode(_buf.getvalue()).decode('ascii'))
        except Exception:
            pass
    _plt.close('all')
_figs_b64
`;

  async function renderFigures(py, section) {
    let result;
    try {
      result = await py.runPythonAsync(COLLECT_FIGS_PY);
    } catch (_) { return; }
    let imgs = [];
    try { imgs = result.toJs ? result.toJs() : Array.from(result); } catch (_) { imgs = []; }
    try { result.destroy && result.destroy(); } catch (_) {}
    let container = section.querySelector('.ex-figures');
    if (!container) {
      container = el('div', { cls: 'ex-figures' });
      const out = section.querySelector('.ex-output');
      out.parentNode.insertBefore(container, out.nextSibling);
    }
    clear(container);
    imgs.forEach(b64 => {
      const img = document.createElement('img');
      img.src = 'data:image/png;base64,' + b64;
      img.alt = 'figure';
      container.appendChild(img);
    });
  }

  async function ensurePackages(py, pkgs) {
    const needed = pkgs.filter(p => p && !loadedPackages.has(p));
    if (!needed.length) return;
    // Try loadPackage first (built-in Pyodide packages); fall back to
    // micropip per-package for anything Pyodide doesn't ship as a wheel
    // (e.g. seaborn on some Pyodide builds).
    try {
      await py.loadPackage(needed);
      needed.forEach(p => loadedPackages.add(p));
      return;
    } catch (e) {
      // Retry individually, falling back to micropip on miss.
      if (!loadedPackages.has('micropip')) {
        await py.loadPackage(['micropip']);
        loadedPackages.add('micropip');
      }
      for (const p of needed) {
        if (loadedPackages.has(p)) continue;
        try {
          await py.loadPackage([p]);
        } catch (_) {
          await py.runPythonAsync(
            `import micropip\nawait micropip.install(${JSON.stringify(p)})`
          );
        }
        loadedPackages.add(p);
      }
    }
  }

  function getScriptText(section, type) {
    const el = section.querySelector(`script[type="text/x-${type}"]`);
    return el ? el.textContent.replace(/^\n/, '') : '';
  }

  function setStatus(section, text, cls) {
    const s = section.querySelector('.ex-status');
    if (!s) return;
    s.textContent = text || '';
    s.className = 'ex-status' + (cls ? ' ' + cls : '');
  }

  function el(tag, opts) {
    const e = document.createElement(tag);
    if (!opts) return e;
    if (opts.text !== undefined) e.textContent = opts.text;
    if (opts.cls) e.className = opts.cls;
    if (opts.children) opts.children.forEach(c => c && e.appendChild(c));
    return e;
  }

  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }

  function renderFeedback(feedback, kind, parts) {
    clear(feedback);
    feedback.className = 'ex-feedback' + (kind ? ' ' + kind : '');
    parts.filter(Boolean).forEach(p => feedback.appendChild(p));
  }

  function header(text) { return el('h4', { text }); }
  function para(label, text) {
    const p = el('p');
    if (label) {
      const b = el('strong', { text: label + ' ' });
      p.appendChild(b);
    }
    p.appendChild(document.createTextNode(text));
    return p;
  }
  function codeBlock(text) { return el('pre', { text }); }

  async function runExercise(section) {
    const isExample = section.classList.contains('example');
    const textarea = section.querySelector('textarea.ex-code');
    const output = section.querySelector('.ex-output');
    const feedback = section.querySelector('.ex-feedback');
    const userCode = textarea.value;
    const checkCode = isExample ? '' : getScriptText(section, 'check');
    const solution = getScriptText(section, 'solution');
    const explain = getScriptText(section, 'explain');
    const pkgs = (section.dataset.packages || 'numpy').split(',').map(s => s.trim()).filter(Boolean);

    output.textContent = '';
    if (feedback) renderFeedback(feedback, '', []);
    setStatus(section, 'loading Python…', 'loading');

    let py;
    try {
      py = await loadPyodide();
      await ensurePackages(py, pkgs);
    } catch (e) {
      setStatus(section, 'runtime error');
      const msg = 'Could not load the in-browser Python runtime: ' + (e && e.message ? e.message : String(e));
      if (isExample) {
        output.textContent = msg;
      } else if (feedback) {
        renderFeedback(feedback, 'err', [para('', msg)]);
      }
      return;
    }
    setStatus(section, 'running…', 'loading');

    const buf = { out: '' };
    py.setStdout({ batched: (s) => { buf.out += s + '\n'; } });
    py.setStderr({ batched: (s) => { buf.out += s + '\n'; } });

    const ns = py.toPy({});
    try {
      await py.runPythonAsync(userCode, { globals: ns });
    } catch (e) {
      output.textContent = buf.out;
      setStatus(section, '');
      if (isExample) {
        // For examples, just surface the error in the output pane.
        output.textContent = (buf.out + '\n' + e.message.split('\n').slice(-6).join('\n')).trimStart();
        ns.destroy();
        return;
      }
      const parts = [
        header('Your code raised an error'),
        codeBlock(e.message.split('\n').slice(-6).join('\n')),
      ];
      if (explain) parts.push(para('Hint:', explain));
      if (solution) {
        parts.push(para('', 'Reference solution:'));
        parts.push(codeBlock(solution));
      }
      renderFeedback(feedback, 'err', parts);
      ns.destroy();
      return;
    }

    let checkError = null;
    if (checkCode.trim()) {
      try {
        await py.runPythonAsync(checkCode, { globals: ns });
      } catch (e) { checkError = e.message; }
    }
    output.textContent = buf.out;
    setStatus(section, '');
    await renderFigures(py, section);

    if (isExample) {
      // No check, no feedback — just the printed output and any figures.
      ns.destroy();
      return;
    }

    if (checkError) {
      const m = checkError.match(/AssertionError:?\s*(.*?)(?:\n|$)/);
      const reason = m && m[1] ? m[1] : checkError.split('\n').slice(-3).join('\n');
      const parts = [header('Not quite right'), para('', reason)];
      if (explain) parts.push(para('Why:', explain));
      if (solution) {
        parts.push(para('', 'Reference solution:'));
        parts.push(codeBlock(solution));
      }
      renderFeedback(feedback, 'err', parts);
    } else {
      renderFeedback(feedback, 'ok', [header('Correct ✓')]);
    }
    ns.destroy();
  }

  function wireExercise(section) {
    if (section.dataset.wired) return;
    section.dataset.wired = '1';
    const textarea = section.querySelector('textarea.ex-code');
    const starter = textarea ? textarea.value : '';
    const runBtn = section.querySelector('.ex-run');
    const resetBtn = section.querySelector('.ex-reset');
    const showBtn = section.querySelector('.ex-show');

    if (textarea) {
      textarea.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
          e.preventDefault();
          const s = textarea.selectionStart, en = textarea.selectionEnd;
          textarea.value = textarea.value.slice(0, s) + '    ' + textarea.value.slice(en);
          textarea.selectionStart = textarea.selectionEnd = s + 4;
        }
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
          e.preventDefault();
          runBtn && runBtn.click();
        }
      });
    }

    if (runBtn) runBtn.addEventListener('click', async () => {
      runBtn.disabled = true;
      try { await runExercise(section); } finally { runBtn.disabled = false; }
    });
    if (resetBtn) resetBtn.addEventListener('click', () => {
      if (textarea) textarea.value = starter;
      section.querySelector('.ex-output').textContent = '';
      const fb = section.querySelector('.ex-feedback');
      if (fb) renderFeedback(fb, '', []);
      const figs = section.querySelector('.ex-figures');
      if (figs) clear(figs);
    });
    if (showBtn) showBtn.addEventListener('click', () => {
      const solution = getScriptText(section, 'solution');
      const explain = getScriptText(section, 'explain');
      const parts = [];
      if (explain) parts.push(para('Idea:', explain));
      if (solution) {
        parts.push(para('', 'Reference solution:'));
        parts.push(codeBlock(solution));
      }
      renderFeedback(section.querySelector('.ex-feedback'), 'err', parts);
    });
  }

  function init() {
    document.querySelectorAll('section.exercise, section.example').forEach(wireExercise);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
