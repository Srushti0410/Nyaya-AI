const LAWYERS = [
  {
    id: 0,
    init: 'AK',
    grad: 'linear-gradient(135deg,#0f0f24,#8c1f1f)',
    name: 'Adv. Anika Kapoor',
    title: 'Senior Advocate | High Court',
    yrs: 14,
    court: 'Bombay High Court',
    area: 'property',
    fee: 'Rs 3,000',
    feeSub: '/hr',
    tags: ['Property Law', 'Tenant Rights', 'Civil Disputes'],
    rating: 4.9,
    reviews: 142,
    match: 96,
    about: 'Senior advocate focused on property, tenancy, and civil disputes with extensive courtroom experience.'
  },
  {
    id: 1,
    init: 'RS',
    grad: 'linear-gradient(135deg,#1a3a2e,#2d6a4f)',
    name: 'Adv. Rajan Sharma',
    title: 'Partner | 22 Years',
    yrs: 22,
    court: 'Supreme Court of India',
    area: 'labour',
    fee: 'Rs 5,000',
    feeSub: '/hr',
    tags: ['Labour Law', 'Employment', 'Corporate HR'],
    rating: 4.8,
    reviews: 213,
    match: 91,
    about: 'Labour and employment specialist with top-tier litigation experience across Supreme Court and High Courts.'
  },
  {
    id: 2,
    init: 'PM',
    grad: 'linear-gradient(135deg,#2a1a3a,#5a2d8a)',
    name: 'Adv. Priya Mehta',
    title: 'Advocate | 8 Years',
    yrs: 8,
    court: 'Mumbai District Court',
    area: 'family',
    fee: 'Rs 2,000',
    feeSub: '/hr',
    tags: ['Family Law', 'Divorce', 'Child Custody'],
    rating: 4.7,
    reviews: 96,
    match: 87,
    about: 'Family law advocate known for calm strategy in divorce, custody, and succession cases.'
  },
  {
    id: 3,
    init: 'VK',
    grad: 'linear-gradient(135deg,#2e2a1a,#8a6a1c)',
    name: 'Adv. Varun Kumar',
    title: 'Criminal Defence Specialist',
    yrs: 17,
    court: 'Delhi High Court',
    area: 'criminal',
    fee: 'Rs 4,500',
    feeSub: '/hr',
    tags: ['Criminal Law', 'Bail', 'FIR Defence'],
    rating: 4.9,
    reviews: 178,
    match: 89,
    about: 'Criminal defence advocate with strong record in bail, trial strategy, and white-collar matters.'
  },
  {
    id: 4,
    init: 'NR',
    grad: 'linear-gradient(135deg,#1a2e3a,#1c6a8b)',
    name: 'Adv. Neha Rao',
    title: 'Corporate Counsel | 11 Years',
    yrs: 11,
    court: 'NCLT and High Courts',
    area: 'corporate',
    fee: 'Rs 4,000',
    feeSub: '/hr',
    tags: ['Corporate Law', 'Contracts', 'M&A'],
    rating: 4.6,
    reviews: 84,
    match: 82,
    about: 'Corporate counsel advising startups and enterprises on contracts, compliance, and transactions.'
  },
  {
    id: 5,
    init: 'AR',
    grad: 'linear-gradient(135deg,#1a3a1a,#2d8a4a)',
    name: 'Adv. Amit Rastogi',
    title: 'Cyber and IT Law Expert',
    yrs: 9,
    court: 'Cyber Appellate Tribunal',
    area: 'cyber',
    fee: 'Rs 3,500',
    feeSub: '/hr',
    tags: ['Cyber Law', 'Online Fraud', 'Data Protection'],
    rating: 4.8,
    reviews: 67,
    match: 94,
    about: 'Cyber law specialist handling online fraud, data protection, and IT Act related disputes.'
  }
];

const STEPS = [
  {
    res: () => 'Thank you for sharing that. Please tell me when this started and what documents you have.',
    prog: 1,
    label: 'Q1 of 2 - Gathering details'
  },
  {
    res: () => 'Helpful. What outcome do you want, and which city are you in? I will now show matched lawyers.',
    prog: 2,
    label: 'Q2 of 2 - Clarifying goals',
    showLawyers: true
  },
  {
    res: () => 'Case analysis complete. Recommended first step: send a formal legal notice, then consult a matched lawyer.',
    prog: 3,
    label: 'Analysis complete'
  }
];

let chatStep = 0;
let lawyersLoaded = false;
let matchedLawyers = [];
let matchedIssueType = '';
let chatHistory = [];
const API_BASE = window.NYAYA_API_BASE || 'https://nyaya-ai-hiaj.onrender.com';

function qs(id) {
  return document.getElementById(id);
}

async function apiPost(path, payload) {
  const response = await fetch(API_BASE + path, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  let data = null;
  try {
    data = await response.json();
  } catch (error) {
    data = null;
  }

  if (!response.ok) {
    const detail = data?.detail;
    let message = 'Request failed. Please try again.';

    if (typeof detail === 'string' && detail.trim()) {
      message = detail;
    } else if (Array.isArray(detail) && detail.length) {
      const first = detail[0];
      if (typeof first === 'string' && first.trim()) {
        message = first;
      } else if (first && typeof first === 'object') {
        const loc = Array.isArray(first.loc) ? first.loc.join('.') : '';
        const msg = typeof first.msg === 'string' ? first.msg : '';
        message = [loc, msg].filter(Boolean).join(': ') || JSON.stringify(first);
      }
    } else if (detail && typeof detail === 'object') {
      message = detail.message || JSON.stringify(detail);
    }

    throw new Error(message);
  }

  return data;
}

function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem('nyayaUser') || 'null');
  } catch (error) {
    return null;
  }
}

function updateStoredUser(patch) {
  const current = getStoredUser() || {};
  const next = { ...current, ...patch };
  localStorage.setItem('nyayaUser', JSON.stringify(next));
  return next;
}

function logOutUser() {
  localStorage.removeItem('nyayaUser');
  window.location.href = 'login.html';
}

function hydrateAuthNav() {
  const loginLink = qs('nl-login');
  if (!loginLink) return;

  const user = getStoredUser();
  const navLinks = document.querySelector('.nav-links');
  const existingLogout = qs('nl-logout');
  if (existingLogout) existingLogout.remove();

  if (!user || !user.email) {
    loginLink.textContent = 'Login';
    loginLink.href = 'login.html';
    return;
  }

  const firstName = (user.name || user.email.split('@')[0]).trim().split(' ')[0];
  loginLink.textContent = 'Hi, ' + firstName;
  loginLink.href = 'profile.html';

  if (!navLinks) return;
  const logoutLink = document.createElement('a');
  logoutLink.id = 'nl-logout';
  logoutLink.href = '#';
  logoutLink.textContent = 'Logout';
  logoutLink.addEventListener('click', (event) => {
    event.preventDefault();
    logOutUser();
  });
  navLinks.appendChild(logoutLink);
}

function setActiveNav() {
  const path = window.location.pathname.toLowerCase();
  const map = {
    'home.html': 'nl-home',
    'chat.html': 'nl-chat-page',
    'lawyers.html': 'nl-list-page',
    'login.html': 'nl-login'
  };
  const key = Object.keys(map).find((k) => path.endsWith(k));
  if (!key) return;
  const el = qs(map[key]);
  if (el) el.classList.add('on');
}

function go(pageId) {
  const route = {
    home: 'home.html',
    'chat-page': 'chat.html',
    'list-page': 'lawyers.html',
    'profile-page': 'profile.html',
    'auth-page': 'login.html'
  }[pageId] || 'home.html';
  window.location.href = route;
}

function switchAuth(mode) {
  const signInForm = qs('signin-form');
  const signUpForm = qs('signup-form');
  const signInTab = qs('tab-signin');
  const signUpTab = qs('tab-signup');
  const message = qs('auth-message');

  if (!signInForm || !signUpForm || !signInTab || !signUpTab) return;

  if (mode === 'signup') {
    signUpForm.classList.remove('hidden');
    signInForm.classList.add('hidden');
    signUpTab.classList.add('on');
    signInTab.classList.remove('on');
  } else {
    signInForm.classList.remove('hidden');
    signUpForm.classList.add('hidden');
    signInTab.classList.add('on');
    signUpTab.classList.remove('on');
  }

  if (message) {
    message.textContent = '';
    message.classList.remove('success');
  }
}

async function handleSignIn(event) {
  event.preventDefault();
  const email = qs('signin-email')?.value.trim();
  const password = qs('signin-password')?.value;
  const message = qs('auth-message');
  const form = qs('signin-form');
  const submitBtn = form?.querySelector('button[type="submit"]');
  if (!message) return;

  if (!email || !password) {
    message.textContent = 'Please enter both email and password.';
    message.classList.remove('success');
    return;
  }

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Signing in...';
  }

  try {
    const data = await apiPost('/login', { email, password });
    localStorage.setItem('nyayaUser', JSON.stringify(data.user || { email }));
    message.textContent = 'Signed in successfully. Redirecting to home...';
    message.classList.add('success');
    setTimeout(() => {
      window.location.href = 'home.html';
    }, 900);
  } catch (error) {
    message.textContent = error.message || 'Unable to sign in right now.';
    message.classList.remove('success');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Sign In';
    }
  }
}

async function handleSignUp(event) {
  event.preventDefault();
  const name = qs('signup-name')?.value.trim();
  const email = qs('signup-email')?.value.trim();
  const password = qs('signup-password')?.value;
  const message = qs('auth-message');
  const form = qs('signup-form');
  const submitBtn = form?.querySelector('button[type="submit"]');
  if (!message) return;

  if (!name || !email || !password) {
    message.textContent = 'Please fill all fields to create your account.';
    message.classList.remove('success');
    return;
  }

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating...';
  }

  try {
    const data = await apiPost('/signup', { name, email, password });
    localStorage.setItem('nyayaUser', JSON.stringify(data.user || { name, email }));
    message.textContent = 'Account created. Redirecting to home...';
    message.classList.add('success');
    setTimeout(() => {
      window.location.href = 'home.html';
    }, 900);
  } catch (error) {
    message.textContent = error.message || 'Unable to create account right now.';
    message.classList.remove('success');
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Create Account';
    }
  }
}

function goChat(prefill) {
  window.location.href = 'chat.html?prefill=' + encodeURIComponent(prefill || '');
}

async function sendMsg() {
  const inp = qs('inp');
  const chips = qs('chips');
  if (!inp) return;

  const txt = inp.value.trim();
  if (!txt) return;

  if (txt.length < 3) {
    addMsg('u', txt);
    addMsg('ai', 'Please enter at least 3 characters so I can understand your legal issue.');
    inp.value = '';
    inp.focus();
    return;
  }

  const sendButton = document.querySelector('.send-btn');
  inp.value = '';
  inp.disabled = true;
  if (sendButton) sendButton.disabled = true;
  if (chips) chips.style.display = 'none';

  addMsg('u', txt);
  const history = chatHistory.slice();
  chatHistory.push(txt);

  addTyping();
  try {
    const data = await apiPost('/ask', { query: txt, history });
    removeTyping();
    addMsg('ai', data?.answer || 'I could not generate a response right now.');

    matchedIssueType = data?.issue_type || '';
    matchedLawyers = Array.isArray(data?.lawyers) ? data.lawyers : [];

    updateLawyers(txt).catch(() => { });

    if (Array.isArray(data?.sources) && data.sources.length) {
      addMsg('ai', 'Sources: ' + data.sources.join(', '));
    }

    const s = STEPS[Math.min(chatStep, STEPS.length - 1)];
    setProgress(s.prog, s.label);
    if (s.showLawyers && !lawyersLoaded) {
      lawyersLoaded = true;
      setTimeout(loadLawyers, 350);
    }
    chatStep += 1;
  } catch (error) {
    removeTyping();
    addMsg('ai', 'Unable to reach backend: ' + (error.message || 'Please try again in a moment.'));
  } finally {
    inp.disabled = false;
    if (sendButton) sendButton.disabled = false;
    inp.focus();
  }
}

function addMsg(role, text) {
  const area = qs('msgs');
  if (!area) return;
  const node = document.createElement('div');
  node.className = 'msg ' + role;
  const html = text.replace(/\n/g, '<br>');
  node.innerHTML = '<div class="m-av">' + (role === 'ai' ? 'N' : 'U') + '</div><div class="bubble">' + html + '</div>';
  area.appendChild(node);
  area.scrollTop = area.scrollHeight;
}

function addTyping() {
  const area = qs('msgs');
  if (!area) return;
  const node = document.createElement('div');
  node.className = 'msg ai';
  node.id = 'typing';
  node.innerHTML = '<div class="m-av">N</div><div class="bubble"><div class="typing-dots"><span></span><span></span><span></span></div></div>';
  area.appendChild(node);
  area.scrollTop = area.scrollHeight;
}

function removeTyping() {
  const typing = qs('typing');
  if (typing) typing.remove();
}

function setProgress(step, label) {
  const lab = qs('spLabel');
  if (lab) lab.textContent = label;
  ['sp1', 'sp2', 'sp3'].forEach((id, i) => {
    const el = qs(id);
    if (!el) return;
    el.className = 'sp-dot' + (i + 1 < step ? ' done' : i + 1 === step ? ' active' : '');
  });
}

function getLawyerContainer() {
  return qs('lawyer-list') || qs('panelBody');
}

function renderLawyers(list, issueType) {
  const body = getLawyerContainer();
  const sub = qs('panelSub');
  const empty = qs('emptyState');
  if (!body) return;
  if (empty) empty.remove();
  if (sub) {
    const label = issueType ? issueType.replace(/\b\w/g, (m) => m.toUpperCase()) : 'Your case';
    sub.textContent = list.length ? list.length + ' lawyers matched to ' + label : 'No lawyers found';
  }

  body.innerHTML = '';

  if (!list.length) {
    body.innerHTML = '<div class="empty-state" style="padding:18px;">No lawyers found for this case yet.</div>';
    return;
  }

  list.forEach((l, i) => {
    const hasBackendData = !('area' in l);
    const id = typeof l.id === 'number' ? l.id : i;
    const title = l.title || l.specialization || 'Lawyer';
    const grad = l.grad || 'linear-gradient(135deg,#1a1a2a,#4b2a6a)';
    const init = l.init || (l.name ? l.name.split(' ').map((part) => part[0]).join('').slice(0, 2) : 'LA');
    const match = l.match || l.rating || 90;
    const tags = Array.isArray(l.tags) && l.tags.length ? l.tags : [l.specialization || 'Legal Advice'];
    const court = l.court || l.location || 'Online Consultation';
    const viewButton = hasBackendData
      ? '<button class="pl-cta" onclick="window.location.href=\'lawyers.html\'">View</button>'
      : '<button class="pl-cta" onclick="showProfile(' + id + ')">View</button>';
    const card = document.createElement('div');
    card.className = 'p-lawyer';
    card.style.animationDelay = i * 200 + 'ms';
    card.innerHTML =
      '<div class="pl-top">' +
      '<div class="pl-av" style="background:' + grad + '">' + init + '</div>' +
      '<div><div class="pl-name">' + (l.name || 'Recommended Lawyer') + '</div><div class="pl-spec">' + title + '</div></div>' +
      '<div class="pl-pct">' + match + '%</div>' +
      '</div>' +
      '<div class="pl-tags">' + tags.slice(0, 3).map((t) => '<span class="pl-tag">' + t + '</span>').join('') + '</div>' +
      '<div class="pl-footer"><span class="pl-court">' + court + '</span>' + viewButton + '</div>';
    body.appendChild(card);
  });
}

async function updateLawyers(query) {
  const body = getLawyerContainer();
  const sub = qs('panelSub');
  const empty = qs('emptyState');
  if (!body) return;

  if (empty) empty.remove();
  body.innerHTML = '<div class="empty-state" style="padding:18px;">Finding the best-matched lawyers...</div>';
  if (sub) sub.textContent = 'Matching lawyers to your case...';

  const data = await apiPost('/recommend-lawyers', { query });
  matchedLawyers = Array.isArray(data) ? data : [];

  const issue = matchedLawyers.length ? (matchedLawyers[0].specialization || matchedIssueType || 'Your case') : matchedIssueType;
  renderLawyers(matchedLawyers, issue);
}

function useChip(el) {
  const inp = qs('inp');
  if (!inp || !el) return;
  inp.value = el.textContent;
  sendMsg();
}

function buildGrid(area) {
  const grid = qs('lawyersGrid');
  if (!grid) return;
  const selected = area || 'all';
  grid.innerHTML = '';

  const list = selected === 'all' ? LAWYERS : LAWYERS.filter((l) => l.area === selected);
  list.forEach((l) => {
    const stars = '★'.repeat(Math.floor(l.rating)) + '☆'.repeat(5 - Math.floor(l.rating));
    const card = document.createElement('div');
    card.className = 'l-card';
    card.innerHTML =
      '<div class="lc-top">' +
      '<div class="lc-head">' +
      '<div class="lc-av" style="background:' + l.grad + '">' + l.init + '</div>' +
      '<div><div class="lc-name">' + l.name + '</div><div class="lc-ttl">' + l.title + ' | ' + l.yrs + ' yrs</div></div>' +
      '<div class="lc-right"><div class="lc-stars">' + stars + '</div><div class="lc-cnt">' + l.reviews + ' reviews</div></div>' +
      '</div>' +
      '<div class="lc-tags">' + l.tags.map((t) => '<span class="lc-tag">' + t + '</span>').join('') + '</div>' +
      '</div>' +
      '<div class="lc-bottom">' +
      '<div class="lc-meta">' + l.court + '</div>' +
      '<div style="display:flex;align-items:center;gap:14px">' +
      '<div class="lc-fee">' + l.fee + '<span>' + l.feeSub + '</span></div>' +
      '<button class="lc-view" onclick="showProfile(' + l.id + ')">View Profile</button>' +
      '</div>' +
      '</div>';
    grid.appendChild(card);
  });
}

function filter(el, area) {
  document.querySelectorAll('.f-chip').forEach((chip) => chip.classList.remove('on'));
  if (el) el.classList.add('on');
  buildGrid(area);
}

function loadLawyers() {
  renderLawyers(matchedLawyers.length ? matchedLawyers : LAWYERS.slice(0, 3), matchedIssueType || 'Your case');
}

function showProfile(id) {
  const hasProfileDom = qs('profHeader') && qs('profMain') && qs('profSide');
  if (!hasProfileDom) {
    window.location.href = 'profile.html?id=' + encodeURIComponent(id);
    return;
  }

  const l = LAWYERS.find((x) => x.id === Number(id)) || LAWYERS[0];
  const stars = '★'.repeat(Math.floor(l.rating)) + '☆'.repeat(5 - Math.floor(l.rating));

  qs('profHeader').innerHTML =
    '<button class="back-btn" onclick="window.location.href=\'lawyers.html\'">Back</button>' +
    '<div class="prof-av" style="background:' + l.grad + '">' + l.init + '</div>' +
    '<div><div class="prof-name">' + l.name + '</div><div class="prof-title">' + l.title + '</div>' +
    '<div class="prof-badges"><span class="pbadge pb-gold">Verified Advocate</span><span class="pbadge pb-green">' + l.yrs + '+ Years</span><span class="pbadge pb-gold">' + l.court + '</span></div></div>' +
    '<div class="prof-fee-block"><div class="prof-fee">' + l.fee + '</div><div class="prof-fee-lbl">per hour consultation</div><div class="prof-stars">' + stars + '</div><div class="prof-reviews">' + l.reviews + ' verified reviews</div></div>';

  qs('profMain').innerHTML =
    '<div class="prof-card"><div class="prof-section-title">About</div><p class="prof-about">' + l.about + '</p></div>' +
    '<div class="prof-card"><div class="prof-section-title">Specialisations</div><div class="spec-tags">' + l.tags.map((t) => '<span class="spec-tag">' + t + '</span>').join('') + '</div></div>' +
    '<div class="prof-card"><div class="prof-section-title">Client Reviews</div><div class="reviews">' +
    '<div class="review"><div class="rev-stars">★★★★★</div><p class="rev-text">"Clear advice and strong courtroom strategy."</p><div class="rev-author">- Verified Client</div></div>' +
    '<div class="review"><div class="rev-stars">★★★★☆</div><p class="rev-text">"Professional and responsive throughout the case."</p><div class="rev-author">- Verified Client</div></div>' +
    '</div></div>';

  qs('profSide').innerHTML =
    '<div class="side-card"><div class="side-card-title">Book a Consultation</div>' +
    '<button class="book-btn">Video Call - ' + l.fee + l.feeSub + '</button>' +
    '<button class="book-btn-out">Send a Message</button>' +
    '<div class="prof-stats">' +
    '<div class="ps"><div class="ps-num">' + l.yrs + '+</div><div class="ps-lbl">Yrs Experience</div></div>' +
    '<div class="ps"><div class="ps-num">' + l.reviews + '</div><div class="ps-lbl">Reviews</div></div>' +
    '<div class="ps"><div class="ps-num">' + l.rating + '</div><div class="ps-lbl">Rating</div></div>' +
    '<div class="ps"><div class="ps-num">48h</div><div class="ps-lbl">Response Time</div></div>' +
    '</div></div>' +
    '<div class="side-card"><div class="side-card-title">Need clarity first?</div><p style="font-size:.8rem;color:var(--muted);line-height:1.68;margin-bottom:14px">Use the AI consultation before booking to summarize your case.</p><button class="book-btn" onclick="window.location.href=\'chat.html\'">Start AI Consult</button></div>';
}

function renderUserProfile(noticeText, noticeType) {
  const header = qs('profHeader');
  const main = qs('profMain');
  const side = qs('profSide');
  if (!header || !main || !side) return;

  const user = getStoredUser();
  const email = user?.email || 'guest@nyaya.ai';
  const phone = user?.phone || '';
  const city = user?.city || '';
  const state = user?.state || '';
  const address = user?.address || '';
  const nameSource = (user?.name || email.split('@')[0] || 'Nyaya User').trim();
  const name = nameSource
    .split(' ')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
  const init = name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  header.innerHTML =
    '<div class="prof-av" style="background:linear-gradient(135deg,#0f0f24,#8c1f1f)">' + init + '</div>' +
    '<div><div class="prof-name">' + name + '</div><div class="prof-title">NyayaAI Member</div>' +
    '<div class="prof-badges"><span class="pbadge pb-gold">User Profile</span><span class="pbadge pb-green">Account Active</span></div></div>' +
    '<div class="prof-fee-block"><div class="prof-fee" style="font-size:1.1rem">Member</div><div class="prof-fee-lbl">Secure account</div></div>';

  const noticeClass = noticeType === 'error' ? '#8c1f1f' : '#2d6a4f';
  const noticeHtml = noticeText
    ? '<p id="user-profile-msg" style="margin-top:10px;font-size:.78rem;color:' + noticeClass + ';">' + noticeText + '</p>'
    : '<p id="user-profile-msg" style="margin-top:10px;font-size:.78rem;color:var(--muted);"></p>';

  main.innerHTML =
    '<div class="prof-card"><div class="prof-section-title">Account Details</div>' +
    '<form id="user-profile-form" onsubmit="saveUserProfileDetails(event)">' +
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">' +
    '<input id="profile-name" type="text" value="' + name.replace(/"/g, '&quot;') + '" placeholder="Full name" style="border:1px solid #ddd7cc;border-radius:9px;padding:10px 12px;font-size:.85rem;font-family:Sora,sans-serif;">' +
    '<input id="profile-phone" type="text" value="' + String(phone).replace(/"/g, '&quot;') + '" placeholder="Phone number" style="border:1px solid #ddd7cc;border-radius:9px;padding:10px 12px;font-size:.85rem;font-family:Sora,sans-serif;">' +
    '<input id="profile-city" type="text" value="' + String(city).replace(/"/g, '&quot;') + '" placeholder="City" style="border:1px solid #ddd7cc;border-radius:9px;padding:10px 12px;font-size:.85rem;font-family:Sora,sans-serif;">' +
    '<input id="profile-state" type="text" value="' + String(state).replace(/"/g, '&quot;') + '" placeholder="State" style="border:1px solid #ddd7cc;border-radius:9px;padding:10px 12px;font-size:.85rem;font-family:Sora,sans-serif;">' +
    '</div>' +
    '<textarea id="profile-address" rows="3" placeholder="Address" style="margin-top:10px;width:100%;border:1px solid #ddd7cc;border-radius:9px;padding:10px 12px;font-size:.85rem;font-family:Sora,sans-serif;resize:vertical;">' + String(address) + '</textarea>' +
    '<p class="prof-about" style="margin-top:10px;"><strong>Email:</strong> ' + email + '</p>' +
    '<button class="book-btn" type="submit" style="margin-top:10px;margin-bottom:0;">Save Profile</button>' +
    noticeHtml +
    '</form></div>' +
    '<div class="prof-card"><div class="prof-section-title">Quick Actions</div>' +
    '<div class="spec-tags"><span class="spec-tag">AI Consultation</span><span class="spec-tag">Lawyer Matching</span><span class="spec-tag">Case Guidance</span></div></div>';

  side.innerHTML =
    '<div class="side-card"><div class="side-card-title">Get Legal Help</div>' +
    '<button class="book-btn" onclick="window.location.href=\'chat.html\'">Start AI Consult</button>' +
    '<button class="book-btn-out" onclick="window.location.href=\'lawyers.html\'">Browse Lawyers</button></div>' +
    '<div class="side-card"><div class="side-card-title">Session</div>' +
    '<p style="font-size:.8rem;color:var(--muted);line-height:1.68;margin-bottom:14px">You are signed in as ' + email + '.</p>' +
    '<button class="book-btn-out" onclick="logOutUser()">Logout</button></div>';
}

function saveUserProfileDetails(event) {
  event.preventDefault();

  const name = (qs('profile-name')?.value || '').trim();
  const phoneRaw = (qs('profile-phone')?.value || '').trim();
  const city = (qs('profile-city')?.value || '').trim();
  const state = (qs('profile-state')?.value || '').trim();
  const address = (qs('profile-address')?.value || '').trim();

  const phoneDigits = phoneRaw.replace(/[^0-9+]/g, '');
  if (phoneDigits && !/^\+?[0-9]{8,15}$/.test(phoneDigits)) {
    renderUserProfile('Please enter a valid phone number.', 'error');
    return;
  }

  const currentUser = getStoredUser() || {};
  const safeName = name || currentUser.name || (currentUser.email ? currentUser.email.split('@')[0] : 'Nyaya User');

  updateStoredUser({
    name: safeName,
    phone: phoneDigits,
    city,
    state,
    address
  });

  hydrateAuthNav();
  renderUserProfile('Profile updated successfully.', 'success');
}

function hydrateChatPrefill() {
  const inp = qs('inp');
  if (!inp) return;
  const params = new URLSearchParams(window.location.search);
  const prefill = params.get('prefill');
  if (!prefill) return;
  inp.value = prefill;
  sendMsg();
}

function hydrateProfilePage() {
  if (!qs('profHeader')) return;
  const params = new URLSearchParams(window.location.search);
  const idParam = params.get('id');
  if (idParam !== null && idParam !== '') {
    const id = Number(idParam);
    if (!Number.isNaN(id)) {
      showProfile(id);
      return;
    }
  }
  renderUserProfile();
}

window.addEventListener('DOMContentLoaded', () => {
  hydrateAuthNav();
  setActiveNav();
  if (qs('lawyersGrid')) buildGrid('all');
  hydrateProfilePage();
  hydrateChatPrefill();
  if (qs('signin-form')) switchAuth('signin');
});
