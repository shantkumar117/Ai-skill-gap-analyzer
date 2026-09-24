function initSingleEye() {
  document.querySelectorAll('.auth-form, .analysis-form').forEach(function(form) {
    const fields = form.querySelectorAll('input[type="password"]');
    if (!fields.length) return;
    // Create a single floating eye that applies to all fields in this form
    if (form.querySelector('.auth-single-eye')) return;
    const btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'auth-single-eye';
    btn.innerHTML = '<svg width="16" height="12" viewBox="0 0 24 16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M2 8c4-6 10-6 14 0s-4 8-10 8c-6 0-10-2-4-8z"/><circle cx="12" cy="8" r="2.5"/></svg>';
    btn.style.cssText = 'position:fixed;right:1.2rem;bottom:5rem;background:#f8f9fa;border:1px solid #d1d5db;border-radius:6px;padding:0.35rem;cursor:pointer;color:#4f46e5;box-shadow:0 2px 6px rgba(79,70,229,0.12);z-index:50;display:block;';
    btn.onclick = function() {
      const showing = fields[0].type === 'text';
      fields.forEach(function(inp){ inp.type = showing ? 'password' : 'text'; });
    };
    btn.setAttribute('aria-label','Toggle password visibility');
    document.body.appendChild(btn);
    // Show eye only when any password field is focused; hide on blur
    fields.forEach(function(f){
      f.addEventListener('focus', function(){ btn.style.display = 'block'; btn.style.position='fixed'; btn.style.right='1.2rem'; btn.style.bottom='5rem'; });
      // blur keep visible
    });
  });
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initSingleEye); else initSingleEye();
