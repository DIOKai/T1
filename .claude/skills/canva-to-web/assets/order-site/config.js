/* Site settings. Leave supabaseUrl empty to run in demo mode (orders stay in this browser).
   The publishable key is meant to be public: what it may do is limited by supabase/schema.sql.
   Never put the secret / service_role key here. */
window.SITE_CONFIG = {
  supabaseUrl: '',            // e.g. 'https://abcdefgh.supabase.co'
  publishableKey: '',         // Supabase dashboard > Project Settings > API Keys > publishable (or legacy anon) key
  menuFile: 'menu.sample.json', // demo mode only: the menu to load
  duitnowQrImage: '',         // e.g. 'img/duitnow-qr.png' - the shop's own static DuitNow QR from its bank
  privacyUrl: 'privacy.html', // your privacy notice (PDPA)
  pollSeconds: 8              // how often the order-status and staff screens refresh
};
