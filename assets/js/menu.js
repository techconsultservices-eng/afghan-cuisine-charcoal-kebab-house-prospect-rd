// Afghan Cuisine — menu.js
// Fetches menu.json, renders tab bar + card grid

document.addEventListener('DOMContentLoaded', async () => {
  const tabBar = document.querySelector('.tab-bar-inner');
  const menuContent = document.querySelector('.menu-content');

  if (!tabBar || !menuContent) return;

  menuContent.innerHTML = '<div class="menu-loading">Loading menu…</div>';

  let data;
  try {
    const res = await fetch('menu.json');
    if (!res.ok) throw new Error('Failed to load menu');
    data = await res.json();
  } catch (err) {
    menuContent.innerHTML = '<div class="menu-loading">Unable to load menu. Please try again shortly.</div>';
    console.error(err);
    return;
  }

  const { categories, items } = data;

  // Build tabs
  tabBar.innerHTML = '';
  categories.forEach((cat, i) => {
    const btn = document.createElement('button');
    btn.className = 'tab-btn' + (i === 0 ? ' active' : '');
    btn.textContent = cat;
    btn.dataset.category = cat;
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.querySelectorAll('.menu-category').forEach(s => s.classList.remove('active'));
      document.getElementById('cat-' + slugify(cat))?.classList.add('active');
      // Smooth scroll to content top
      menuContent.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    tabBar.appendChild(btn);
  });

  // Build category sections
  menuContent.innerHTML = '';
  categories.forEach((cat, i) => {
    const catItems = items.filter(item => item.category === cat);
    const section = document.createElement('section');
    section.className = 'menu-category section' + (i === 0 ? ' active' : '');
    section.id = 'cat-' + slugify(cat);

    const desc = categoryDesc(cat);
    section.innerHTML = `
      <div class="container">
        <div class="menu-category-header">
          <h2>${cat}</h2>
          ${desc ? `<p>${desc}</p>` : ''}
        </div>
        ${catItems.length > 0
          ? `<div class="menu-grid">${catItems.map(renderCard).join('')}</div>`
          : `<p style="color: var(--parchment-dim); font-style: italic; padding: 20px 0;">
              More dishes coming soon — ask our team about today's specials.
             </p>`
        }
      </div>
    `;
    menuContent.appendChild(section);
  });

  // Attach image error handlers
  menuContent.querySelectorAll('.dish-card-img img').forEach(img => {
    img.addEventListener('error', () => handleImgError(img));
    // Also trigger if already errored (cached failure)
    if (img.complete && img.naturalWidth === 0) handleImgError(img);
  });
});

function renderCard(item) {
  const hasImage = item.image && item.image.trim() !== '';
  const imgMarkup = hasImage
    ? `<img src="${escapeAttr(item.image)}" alt="${escapeAttr(item.name)} — Afghan Cuisine and Charcoal Kebab House" loading="lazy">`
    : `<div class="dish-card-placeholder">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="6" y="6" width="36" height="36" rx="4" stroke="#C9943A" stroke-width="1.5"/>
          <circle cx="18" cy="19" r="4" stroke="#C9943A" stroke-width="1.5"/>
          <path d="M6 32l10-10 6 6 6-8 14 14" stroke="#C9943A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>Photo coming soon</span>
      </div>`;

  return `
    <article class="dish-card">
      <div class="dish-card-img">${imgMarkup}</div>
      <div class="dish-card-body">
        <p class="dish-card-name">${escapeHtml(item.name)}</p>
        <p class="dish-card-desc">${escapeHtml(item.description)}</p>
        <p class="dish-card-price">${escapeHtml(item.price)}</p>
      </div>
    </article>
  `;
}

function categoryDesc(cat) {
  const map = {
    'Featured': 'Our most-loved dishes — signature charcoal-grilled kebabs and traditional Afghan mains.',
    'Sides': 'Perfect accompaniments to any meal, from house-made sauces to hearty curries.',
    'Extras': 'Add ons to complete your plate.',
    'Desserts': 'A sweet finish to your Afghan dining experience.',
    'Mains': 'Heartier dishes from the Afghan table.',
    'Combos': 'Great value combination meals for every appetite.',
    'Beverages': 'Drinks to accompany your meal.'
  };
  return map[cat] || '';
}

function slugify(str) {
  return str.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function escapeAttr(str) {
  return String(str).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
