import Dexie from 'dexie';

export const db = new Dexie('KastomPOS');

db.version(1).stores({
  products: '++id, name, category, sku, barcode, sellingPrice',
  sales: '++id, customerId, timestamp, total, status', // status: 'synced' | 'pending'
  saleItems: '++id, saleId, productId, quantity, price, subtotal',
  customers: '++id, name, phone, email',
  stockAdjustments: '++id, productId, type, quantity, reason, timestamp',
  settings: 'key, value'
});

// Initialize default settings if not exists
db.on('ready', async () => {
  const settingsCount = await db.settings.count();
  if (settingsCount === 0) {
    await db.settings.bulkAdd([
      { key: 'businessName', value: 'KastomPOS SME' },
      { key: 'currency', value: 'KES' },
      { key: 'lowStockThreshold', value: 10 },
      { key: 'kraIntegration', value: false },
      { key: 'businessMode', value: 'retail' }
    ]);
  }
});
