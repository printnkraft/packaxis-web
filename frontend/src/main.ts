import '../static/css/styles.css';
import '../static/css/responsive.css';
import '../static/css/pages/blog.css';
import '../static/css/pages/product-detail.css';

import { initCart } from './modules/cart';
import { initWishlist } from './modules/wishlist';
import { initAddresses } from './modules/addresses';
import { initCheckout } from './modules/checkout';
import { initAccount } from './modules/account';

document.addEventListener('DOMContentLoaded', () => {
	initCart();
	initWishlist();
	initAddresses();
	initCheckout();
	initAccount();
});

console.info('Packaxis frontend bundle loaded');
