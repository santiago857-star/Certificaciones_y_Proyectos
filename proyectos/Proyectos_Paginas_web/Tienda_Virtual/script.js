
const PLANTS = [
  { id: 'p1', name: 'Monstera Deliciosa', price: 25.0, category: 'Follaje', description: 'Hoja grande perforada, ideal para interiores.', img: 'https://images.unsplash.com/photo-1501004318641-b39e6451bec6?q=80&w=800&auto=format&fit=crop' },
  { id: 'p2', name: 'Lavanda', price: 12.0, category: 'Aromáticas', description: 'Aroma calmante, flores moradas.', img:"imagenes/img.jpg"},
  { id: 'p3', name: 'Aloe Vera', price: 10.0, category: 'Medicinales', description: 'Usos medicinales y fáciles de cuidar.', img: 'https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2?q=80&w=800&auto=format&fit=crop' },
  { id: 'p4', name: 'Pothos', price: 15.0, category: 'Follaje', description: 'Muy resistente y purificadora de aire.', img: 'imagenes/img1.jpg' },
  { id: 'p5', name: 'Menta', price: 8.0, category: 'Aromáticas', description: 'Perfecta para cocinar y refrescar el hogar.', img: 'imagenes/img2.jpg' },
  { id: 'p6', name: 'Caléndula', price: 9.0, category: 'Medicinales', description: 'Propiedades antiinflamatorias y colorido.', img: 'imagenes/img3.jpg' }
];

let cart = loadCartFromStorage();


function saveCartToStorage(){
  localStorage.setItem('pn_cart_v1', JSON.stringify(cart));
}
function loadCartFromStorage(){
  try{
    const raw = localStorage.getItem('pn_cart_v1');
    return raw ? JSON.parse(raw) : {};
  }catch(e){
    return {};
  }
}
function totalItemsInCart(){
  return Object.values(cart).reduce((s,it)=>s + (Number(it.qty)||0), 0);
}
function totalPriceInCart(){

  const cents = Object.values(cart).reduce((s,it)=> s + Math.round((it.price*100) * (it.qty||0)), 0);
  return (cents/100);
}
function formatMoney(n){ return n.toFixed(2) + ' USD'; }


const categoriesContainer = document.getElementById('categories');
const cartCountSpan = document.getElementById('cartCount');
const startBtn = document.getElementById('startBtn');
const cartItemsEl = document.getElementById('cartItems');
const totalItemsEl = document.getElementById('totalItems');
const totalPriceEl = document.getElementById('totalPrice');
const payBtn = document.getElementById('payBtn');
const brandLink = document.getElementById('brandLink');
const yearSpan = document.getElementById('year');


yearSpan.textContent = new Date().getFullYear();
renderHeaderCartCount();
renderProducts();
renderCartView();
setupRouting();
attachUIActions();


function renderProducts(){
  categoriesContainer.innerHTML = '';
  
  const groups = {};
  PLANTS.forEach(p=>{
    if(!groups[p.category]) groups[p.category] = [];
    groups[p.category].push(p);
  });

  for(const [cat, items] of Object.entries(groups)){
    const catDiv = document.createElement('div');
    catDiv.className = 'category';
    catDiv.innerHTML = `<h3>${cat}</h3><div class="products-grid"></div>`;
    const grid = catDiv.querySelector('.products-grid');

    items.forEach(product=>{
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <img src="${product.img}" alt="${escapeHtml(product.name)}" loading="lazy" />

        <h4>${escapeHtml(product.name)}</h4>
        <p>${escapeHtml(product.description)}</p>
        <div class="price">${formatMoney(product.price)}</div>
        <button data-add="${product.id}">Añadir a la cesta</button>
      `;
      grid.appendChild(card);
    });

    categoriesContainer.appendChild(catDiv);
  }

  document.querySelectorAll('[data-add]').forEach(btn=>{
    const id = btn.getAttribute('data-add');
    btn.disabled = !!cart[id];
    btn.textContent = btn.disabled ? 'Añadido' : 'Añadir a la cesta';
    btn.addEventListener('click', ()=>{
      addToCart(id);
      btn.disabled = true;
      btn.textContent = 'Añadido';
    });
  });
}


function addToCart(productId){
  const p = PLANTS.find(x=>x.id===productId);
  if(!p) return;
  if(!cart[productId]) cart[productId] = {...p, qty: 1};
  saveCartToStorage();
  renderHeaderCartCount();
  renderCartView();
}

function incrementQty(productId){
  if(!cart[productId]) return;
  cart[productId].qty = Number(cart[productId].qty || 0) + 1;
  saveCartToStorage();
  renderHeaderCartCount();
  renderCartView();
}
function decrementQty(productId){
  if(!cart[productId]) return;
  cart[productId].qty = Number(cart[productId].qty || 0) - 1;
  if(cart[productId].qty <= 0){
    delete cart[productId];

    const addBtn = document.querySelector(`[data-add="${productId}"]`);
    if(addBtn){ addBtn.disabled = false; addBtn.textContent = 'Añadir a la cesta'; }
  }
  saveCartToStorage();
  renderHeaderCartCount();
  renderCartView();
}
function removeItem(productId){
  if(cart[productId]) delete cart[productId];
  const addBtn = document.querySelector(`[data-add="${productId}"]`);
  if(addBtn){ addBtn.disabled = false; addBtn.textContent = 'Añadir a la cesta'; }
  saveCartToStorage();
  renderHeaderCartCount();
  renderCartView();
}


function renderCartView(){

  const totalItems = totalItemsInCart();
  const totalPrice = totalPriceInCart();
  cartCountSpan.textContent = totalItems;
  totalItemsEl.textContent = totalItems;
  totalPriceEl.textContent = formatMoney(totalPrice);


  cartItemsEl.innerHTML = '';
  const items = Object.values(cart);
  if(items.length === 0){
    cartItemsEl.innerHTML = `<div style="padding:18px;background:#fff;border-radius:12px">Tu carrito está vacío.</div>`;
    return;
  }

  items.forEach(item=>{
    const card = document.createElement('div');
    card.className = 'cart-card';
    const subtotal = Math.round(item.price*100) * item.qty / 100;
    card.innerHTML = `
      <img src="${item.img}" alt="${escapeHtml(item.name)}" class="cart-thumb" />
      <div class="item-info">
        <div style="font-weight:700">${escapeHtml(item.name)}</div>
        <div style="color:gray; font-size:13px">Unit: ${formatMoney(item.price)}</div>
        <div style="color:gray; font-size:13px">Subtotal: ${formatMoney(subtotal)}</div>
      </div>
      <div class="item-controls">
        <button class="icon-btn" data-decrease="${item.id}">−</button>
        <div style="min-width:28px; text-align:center">${item.qty}</div>
        <button class="icon-btn" data-increase="${item.id}">+</button>
        <button class="remove-btn" data-remove="${item.id}" title="Eliminar">Eliminar</button>
      </div>
    `;
    cartItemsEl.appendChild(card);
  });


  cartItemsEl.querySelectorAll('[data-increase]').forEach(b=>{
    b.addEventListener('click', ()=> incrementQty(b.getAttribute('data-increase')));
  });
  cartItemsEl.querySelectorAll('[data-decrease]').forEach(b=>{
    b.addEventListener('click', ()=> decrementQty(b.getAttribute('data-decrease')));
  });
  cartItemsEl.querySelectorAll('[data-remove]').forEach(b=>{
    b.addEventListener('click', ()=> {
      if(confirm('¿Eliminar este producto del carrito?')) removeItem(b.getAttribute('data-remove'));
    });
  });
}


function renderHeaderCartCount(){
  cartCountSpan.textContent = totalItemsInCart();
}

function setupRouting(){
  function showOnly(hash){
    document.querySelectorAll('.page').forEach(p=> p.classList.add('hidden'));
    if(!hash || hash === '' || hash === '#home' || hash === 'home'){
      document.getElementById('home').classList.remove('hidden');
      window.scrollTo(0,0);
    } else if(hash.startsWith('#products') || hash === 'products'){
      document.getElementById('products').classList.remove('hidden');
      window.scrollTo(0,0);
    } else if(hash.startsWith('#cart') || hash === 'cart'){
      document.getElementById('cart').classList.remove('hidden');
      window.scrollTo(0,0);
    } else {
      document.getElementById('home').classList.remove('hidden');
      window.scrollTo(0,0);
    }
  }

  function onHashChange(){
    showOnly(location.hash);

    document.querySelectorAll('[data-add]').forEach(btn=>{
      const id = btn.getAttribute('data-add');
      btn.disabled = !!cart[id];
      btn.textContent = btn.disabled ? 'Añadido' : 'Añadir a la cesta';
    });
  }

  window.addEventListener('hashchange', onHashChange);
  onHashChange();
}

function attachUIActions(){
  startBtn.addEventListener('click', ()=> location.hash = '#products');
  document.getElementById('cartBtn').addEventListener('click', ()=> location.hash = '#cart');
  payBtn.addEventListener('click', ()=> alert('Pagar: Próximamente — método de pago en desarrollo.'));

  brandLink.addEventListener('click', (e)=> {
    e.preventDefault();
    location.hash = '#home';
  });
}


function escapeHtml(text){
  if(!text) return '';
  return text.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
}
