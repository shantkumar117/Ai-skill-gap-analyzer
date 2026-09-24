// Shared eye-icon widget for auth password fields
function initAuthEyes() {
  document.querySelectorAll('.auth-form .password-wrap').forEach(function(wrap) {
    var input = wrap.querySelector('input[type="password"], input[type="text"]');
    if (!input || wrap.querySelector('.eye-btn')) return;
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'eye-btn';
    btn.setAttribute('aria-label', 'Show password');
    btn.innerHTML = '<svg width="18" height="14" viewBox="0 0 24 18" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 9s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="9" r="3"/></svg>';
    btn.style.cssText = 'position:absolute;right:0.6rem;top:50%;transform:translateY(-50%);background:none;border:none;padding:0.2rem;cursor:pointer;color:#4f46e5;line-height:1;';
    btn.onclick = function() {
      if (input.type === 'password') {
        input.type = 'text';
        btn.setAttribute('aria-label', 'Hide password');
        btn.innerHTML = '<svg width="18" height="14" viewBox="0 0 24 18" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-7-11-7a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 7 11 7a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>';
      } else {
        input.type = 'password';
        btn.setAttribute('aria-label', 'Show password');
        btn.innerHTML = '<svg width="18" height="14" viewBox="0 0 24 18" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 9s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"/><circle cx="12" cy="9" r="3"/></svg>';
      }
    };
    wrap.style.position = 'relative';
    wrap.appendChild(btn);
  });
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initAuthEyes); else initAuthEyes();
