import { reactive } from 'vue'
import api from '@/services/apiClient'

export interface Product {
  id: number
  name: string
  description: string
  price: number
  min_order_qty: number
  quantity_in_stock: number
  unit: string
  stockKg: number
  pricePerKg: number
  category?: {
    id: number
    name: string
  }
  enterprise?: {
    id: number
    short_name: string
  }
}

export interface Supplier {
  id: number
  name: string
  company: string
  rating: number
  reviews: number
  region: string
  city?: string | null
  locations: string
  description: string
  products: Product[]
  since?: string
  minOrder?: string
  delivery?: string
  reviews_list?: any[]
  users?: { id: number; email: string }[]
}

export interface CartItem {
  id: number
  product_id: number
  quantity: number
  product: Product
}

export interface OrderItem {
  id: number
  product_id: number
  quantity: number
  price: number
  product?: Product
}

export interface EnterpriseShort {
  id: number
  short_name: string
  inn?: string
  region?: string
}

export interface Order {
  id: number
  status: string
  total_amount: number | null
  created_at: string
  seller_enterprise: EnterpriseShort
  buyer_enterprise?: EnterpriseShort | null
  items: OrderItem[]
}

export interface CheckoutResult {
  orders: Order[]
}

const state = reactive({
  favoriteProductIds: [] as number[],
  favoriteProducts: [] as Product[],
  favoriteSuppliers: [] as Supplier[],
  cartItems: [] as CartItem[],
  cartId: null as number | null,
  products: [] as Product[],
  suppliers: [] as Supplier[],
  currentSupplier: null as Supplier | null,
  loading: false,
  error: null as string | null,
  myOrders: [] as Order[],
  supplierOrders: [] as Order[],
  ordersLoading: false,
  lastSeenOrderId: Number(localStorage.getItem('lastCheckedOrderId') || 0),
  orderTemplate: JSON.parse(localStorage.getItem('orderTemplate') || 'null') as { product_id: number; quantity: number }[] | null,
  comparisonSupplierIds: [] as number[],
  supplierReviews: [] as any[],
})

export function useShopStore() {
  const mapProduct = (p: any): Product => ({
    id: p.id,
    name: p.name,
    description: p.description || '',
    price: Number(p.price),
    min_order_qty: p.min_order_qty || 0,
    quantity_in_stock: p.quantity_in_stock ?? 0,
    unit: 'кг',
    stockKg: p.quantity_in_stock ?? 0,
    pricePerKg: Number(p.price),
    category: p.category ? { id: p.category.id, name: p.category.name } : undefined,
    enterprise: p.enterprise ? { id: p.enterprise.id, short_name: p.enterprise.short_name } : undefined,
  })

  const mapSupplier = (e: any): Supplier => ({
    id: e.id,
    name: e.short_name,
    company: e.short_name,
    rating: e.rating || 0,
    reviews: e.review_count || 0,
    region: e.region || '',
    city: e.city || null,
    locations: [e.region, e.city].filter(Boolean).join(', '),
    description: e.description || 'Надёжный поставщик качественной продукции.',
    products: (e.products || []).map(mapProduct),
    since: e.created_at ? new Date(e.created_at).getFullYear().toString() : '2023',
    minOrder: 'от 50 000 ₽',
    delivery: 'Завтра 06:00–10:00',
    users: e.users || [],
  })

  const fetchProducts = async () => {
    state.loading = true
    state.error = null
    try {
      const response = await api.get('/products')
      state.products = response.data.map(mapProduct)
    } catch (err: any) {
      state.error = 'Ошибка при загрузке товаров'
      console.error(err)
    } finally {
      state.loading = false
    }
  }

  const fetchSuppliers = async () => {
    state.loading = true
    state.error = null
    try {
      const response = await api.get('/enterprises')
      state.suppliers = response.data.map(mapSupplier)
    } catch (err: any) {
      state.error = 'Ошибка при загрузке поставщиков'
      console.error(err)
    } finally {
      state.loading = false
    }
  }

  const fetchSupplierDetail = async (id: number) => {
    state.loading = true
    state.error = null
    try {
      const response = await api.get(`/enterprises/${id}`)
      state.currentSupplier = mapSupplier(response.data)
    } catch (err: any) {
      state.error = 'Ошибка при загрузке данных поставщика'
      console.error(err)
    } finally {
      state.loading = false
    }
  }

  const fetchFavoriteProducts = async () => {
    const token = localStorage.getItem('token')
    if (!token) return
    try {
      const response = await api.get('/favorites/products')
      state.favoriteProducts = response.data.map(mapProduct)
      state.favoriteProductIds = state.favoriteProducts.map((p) => p.id)
    } catch (err: any) {
      console.error('Ошибка при загрузке избранного:', err)
    }
  }

  const fetchFavoriteSuppliers = async () => {
    const token = localStorage.getItem('token')
    if (!token) return
    try {
      const response = await api.get('/favorites/suppliers')
      state.favoriteSuppliers = response.data.map(mapSupplier)
    } catch (err: any) {
      console.error('Ошибка при загрузке избранных поставщиков:', err)
    }
  }

  const toggleFavoriteProduct = async (product: Product) => {
    const token = localStorage.getItem('token')
    if (!token) return
    const isFav = state.favoriteProductIds.includes(product.id)
    if (isFav) {
      state.favoriteProductIds = state.favoriteProductIds.filter((id) => id !== product.id)
      state.favoriteProducts = state.favoriteProducts.filter((p) => p.id !== product.id)
    } else {
      state.favoriteProductIds.push(product.id)
      state.favoriteProducts.push(product)
    }
    try {
      if (isFav) {
        await api.delete(`/favorites/products/${product.id}`)
      } else {
        await api.post(`/favorites/products/${product.id}`)
      }
    } catch (err: any) {
      console.error('Ошибка при изменении избранного:', err)
      if (isFav) {
        state.favoriteProductIds.push(product.id)
        state.favoriteProducts.push(product)
      } else {
        state.favoriteProductIds = state.favoriteProductIds.filter((id) => id !== product.id)
        state.favoriteProducts = state.favoriteProducts.filter((p) => p.id !== product.id)
      }
    }
  }

  const toggleFavoriteSupplier = async (supplier: Supplier) => {
    const token = localStorage.getItem('token')
    if (!token) return
    const index = state.favoriteSuppliers.findIndex((s) => s.id === supplier.id)
    const isFav = index >= 0

    if (isFav) {
      state.favoriteSuppliers.splice(index, 1)
    } else {
      state.favoriteSuppliers.push(supplier)
    }

    try {
      if (isFav) {
        await api.delete(`/favorites/suppliers/${supplier.id}`)
      } else {
        await api.post(`/favorites/suppliers/${supplier.id}`)
      }
    } catch (err: any) {
      console.error('Ошибка при изменении избранных поставщиков:', err)
      if (isFav) {
        state.favoriteSuppliers.push(supplier)
      } else {
        state.favoriteSuppliers = state.favoriteSuppliers.filter((s) => s.id !== supplier.id)
      }
    }
  }

  const isProductFavorite = (productId: number) => state.favoriteProductIds.includes(productId)

  const isSupplierFavorite = (supplierId: number) =>
    state.favoriteSuppliers.some((s) => s.id === supplierId)

  const fetchCart = async () => {
    const token = localStorage.getItem('token')
    if (!token) return
    try {
      const response = await api.get('/cart/me')
      state.cartId = response.data.id
      state.cartItems = (response.data.items || []).map((item: any) => ({
        id: item.id,
        product_id: item.product_id,
        quantity: item.quantity,
        product: mapProduct(item.product),
      }))
    } catch (err: any) {
      console.error('Ошибка при загрузке корзины:', err)
    }
  }

  const addToCart = async (product: Product, quantityKg: number) => {
    const token = localStorage.getItem('token')
    if (!token) return
    if (quantityKg <= 0) return
    try {
      await api.post('/cart/me/items', { product_id: product.id, quantity: quantityKg })
      await fetchCart()
    } catch (err: any) {
      console.error('Ошибка при добавлении в корзину:', err)
    }
  }

  const setCartQuantity = async (productId: number, quantityKg: number) => {
    const token = localStorage.getItem('token')
    if (!token) return
    const item = state.cartItems.find((i) => i.product_id === productId)
    if (!item) return
    try {
      if (quantityKg <= 0) {
        await api.delete(`/cart/me/items/${item.id}`)
      } else {
        await api.patch(`/cart/me/items/${item.id}`, { quantity: quantityKg })
      }
      await fetchCart()
    } catch (err: any) {
      console.error('Ошибка при обновлении корзины:', err)
    }
  }

  const removeFromCart = async (productId: number) => {
    const token = localStorage.getItem('token')
    if (!token) return
    const item = state.cartItems.find((i) => i.product_id === productId)
    if (!item) return
    try {
      await api.delete(`/cart/me/items/${item.id}`)
      await fetchCart()
    } catch (err: any) {
      console.error('Ошибка при удалении из корзины:', err)
    }
  }

  const fetchMyProducts = async () => {
    state.loading = true
    state.error = null
    try {
      const response = await api.get('/products/my')
      state.products = response.data.map(mapProduct)
    } catch (err: any) {
      state.error = 'Ошибка при загрузке ваших товаров'
      console.error(err)
    } finally {
      state.loading = false
    }
  }

  const createProduct = async (data: any) => {
    state.loading = true
    state.error = null
    try {
      const response = await api.post('/products', data)
      const newProduct = mapProduct(response.data)
      state.products.unshift(newProduct)
      return newProduct
    } catch (err: any) {
      state.error = 'Ошибка при создании товара'
      console.error(err)
      throw err
    } finally {
      state.loading = false
    }
  }

  const updateProduct = async (id: number, data: any) => {
    state.loading = true
    state.error = null
    try {
      const response = await api.patch(`/products/${id}`, data)
      const updatedProduct = mapProduct(response.data)
      const index = state.products.findIndex((p) => p.id === id)
      if (index !== -1) {
        state.products[index] = updatedProduct
      }
      return updatedProduct
    } catch (err: any) {
      state.error = 'Ошибка при обновлении товара'
      console.error(err)
      throw err
    } finally {
      state.loading = false
    }
  }

  const deleteProduct = async (id: number) => {
    state.loading = true
    state.error = null
    try {
      await api.delete(`/products/${id}`)
      state.products = state.products.filter((p) => p.id !== id)
    } catch (err: any) {
      state.error = 'Ошибка при удалении товара'
      console.error(err)
      throw err
    } finally {
      state.loading = false
    }
  }

  const mapOrder = (o: any): Order => ({
    id: o.id,
    status: o.status,
    total_amount: o.total_amount ? Number(o.total_amount) : null,
    created_at: o.created_at,
    seller_enterprise: o.seller_enterprise,
    buyer_enterprise: o.buyer_enterprise || null,
    items: (o.items || []).map((item: any) => ({
      id: item.id,
      product_id: item.product_id,
      quantity: item.quantity,
      price: Number(item.price),
      product: item.product ? mapProduct(item.product) : undefined,
    })),
  })

  const checkoutCart = async (): Promise<CheckoutResult> => {
    const token = localStorage.getItem('token')
    if (!token || state.cartItems.length === 0) return { orders: [] }

    const groups: Map<number, typeof state.cartItems> = new Map()
    for (const item of state.cartItems) {
      const supplierId = item.product.enterprise?.id
      if (!supplierId) {
        throw new Error(`Product ${item.product_id} has no supplier`)
      }
      if (!groups.has(supplierId)) groups.set(supplierId, [])
      groups.get(supplierId)!.push(item)
    }

    const createdOrders: Order[] = []
    for (const [supplierId, items] of groups) {
      const payload = {
        seller_enterprise_id: supplierId,
        items: items.map((i) => ({ product_id: i.product_id, quantity: i.quantity })),
      }
      try {
        const res = await api.post('/orders', payload)
        createdOrders.push(mapOrder(res.data))
      } catch (err: any) {
        if (err.response?.status === 400 && err.response?.data?.detail?.includes('enterprise')) {
          throw new Error('Для оформления заказа необходимо привязать предприятие в профиле.')
        }
        throw err
      }
    }

    await api.post('/cart/me/clear')
    await fetchCart()
    return { orders: createdOrders }
  }

  const fetchMyOrders = async () => {
    const token = localStorage.getItem('token')
    if (!token) return
    state.ordersLoading = true
    try {
      const res = await api.get('/orders/my-as-buyer')
      state.myOrders = res.data.map(mapOrder)
    } catch (err: any) {
      if (err.response?.status === 400 && err.response?.data?.detail?.includes('enterprise')) {
        state.error = 'Сначала привяжите ваше предприятие в профиле, чтобы видеть заказы.'
      } else {
        state.error = 'Ошибка загрузки заказов покупателя'
      }
      console.error('Ошибка загрузки заказов покупателя:', err)
    } finally {
      state.ordersLoading = false
    }
  }

  const fetchSupplierOrders = async () => {
    const token = localStorage.getItem('token')
    if (!token) return
    state.ordersLoading = true
    try {
      const res = await api.get('/orders/my-as-supplier')
      state.supplierOrders = res.data.map(mapOrder)
    } catch (err: any) {
      console.error('Ошибка загрузки заказов поставщика:', err)
    } finally {
      state.ordersLoading = false
    }
  }

  const updateOrderStatus = async (orderId: number, status: string): Promise<Order | null> => {
    try {
      const res = await api.patch(`/orders/${orderId}/status`, { status })
      return mapOrder(res.data)
    } catch (err: any) {
      console.error('Ошибка обновления статуса заказа:', err)
      throw err
    }
  }

  const markOrdersSeen = (role: 'BUYER' | 'SUPPLIER') => {
    const list = role === 'SUPPLIER' ? state.supplierOrders : state.myOrders
    if (list.length > 0) {
      const maxId = Math.max(...list.map(o => o.id))
      if (maxId > state.lastSeenOrderId) {
        state.lastSeenOrderId = maxId
        localStorage.setItem('lastCheckedOrderId', String(maxId))
      }
    }
  }

  return {
    state,
    fetchProducts,
    fetchMyProducts,
    fetchSuppliers,
    fetchSupplierDetail,
    fetchFavoriteProducts,
    fetchFavoriteSuppliers,
    fetchCart,
    createProduct,
    updateProduct,
    deleteProduct,
    toggleFavoriteProduct,
    toggleFavoriteSupplier,
    isProductFavorite,
    isSupplierFavorite,
    addToCart,
    setCartQuantity,
    removeFromCart,
    checkoutCart,
    fetchMyOrders,
    fetchSupplierOrders,
    updateOrderStatus,
    markOrdersSeen,
    saveOrderTemplate: () => {
      const template = state.cartItems.map((item) => ({
        product_id: item.product_id,
        quantity: item.quantity,
      }))
      state.orderTemplate = template
      localStorage.setItem('orderTemplate', JSON.stringify(template))
    },
    deleteOrderTemplate: () => {
      state.orderTemplate = null
      localStorage.setItem('orderTemplate', 'null')
    },
    checkoutWithItems: async (items: { product_id: number; quantity: number }[]): Promise<CheckoutResult> => {
      const token = localStorage.getItem('token')
      if (!token || items.length === 0) return { orders: [] }

      const groups: Map<number, { product_id: number; quantity: number }[]> = new Map()
      for (const item of items) {
        const product = state.products.find(p => p.id === item.product_id)
        if (!product) {
          throw new Error(`Product ${item.product_id} not found`)
        }
        const supplierId = product.enterprise?.id
        if (!supplierId) {
          throw new Error(`Product ${item.product_id} has no supplier`)
        }
        if (!groups.has(supplierId)) groups.set(supplierId, [])
        groups.get(supplierId)!.push(item)
      }

      const createdOrders: Order[] = []
      for (const [supplierId, groupItems] of groups) {
        const payload = {
          seller_enterprise_id: supplierId,
          items: groupItems.map((i) => ({ product_id: i.product_id, quantity: i.quantity })),
        }
        try {
          const res = await api.post('/orders', payload)
          createdOrders.push(mapOrder(res.data))
        } catch (err: any) {
          if (err.response?.status === 400 && err.response?.data?.detail?.includes('enterprise')) {
            throw new Error('Для оформления заказа необходимо привязать предприятие в профиле.')
          }
          throw err
        }
      }

      await api.post('/cart/me/clear')
      await fetchCart()
      return { orders: createdOrders }
    },
    fetchSupplierReviews: async (id: number) => {
      try {
        const res = await api.get(`/enterprises/${id}/reviews`)
        state.supplierReviews = res.data
      } catch (err) {
        console.error('Ошибка загрузки отзывов:', err)
      }
    },
    submitReview: async (id: number, rating: number, comment: string) => {
      try {
        await api.post(`/enterprises/${id}/reviews`, {
          target_enterprise_id: id,
          rating,
          comment
        })
        const detailRes = await api.get(`/enterprises/${id}`)
        state.currentSupplier = mapSupplier(detailRes.data)
        const reviewsRes = await api.get(`/enterprises/${id}/reviews`)
        state.supplierReviews = reviewsRes.data
      } catch (err: any) {
        throw err
      }
    },
    toggleComparison: (id: number) => {
      const idx = state.comparisonSupplierIds.indexOf(id)
      if (idx === -1) {
        if (state.comparisonSupplierIds.length >= 4) {
          throw new Error('Максимум 4 поставщика для сравнения')
        }
        state.comparisonSupplierIds.push(id)
      } else {
        state.comparisonSupplierIds.splice(idx, 1)
      }
    },
    clearComparison: () => {
      state.comparisonSupplierIds = []
    },
  }
}
