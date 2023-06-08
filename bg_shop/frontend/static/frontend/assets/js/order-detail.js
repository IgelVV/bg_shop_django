var mix = {
	methods: {
		getOrder(orderId) {
			if(typeof orderId !== 'number') return
			this.getData(`/api/orders/${orderId}/`)
				.then(data => {
					this.orderId = data.id
					this.createdAt = data.createdAt
					this.fullName = data.fullName
					this.phone = data.phone
					this.email = data.email
					this.deliveryType = data.deliveryType
					this.city = data.city
					this.address = data.address
					this.paymentType = data.paymentType
					this.status = data.status
					this.totalCost = data.totalCost
					this.products = data.products
					console.log(this.products)
					if (typeof data.paymentError !== 'undefined') {
						this.paymentError = data.paymentError
					}
				})
				.catch(() => {
					console.warn('Ошибка при получении заказа')
				})
		},
		confirmOrder() {
			if (this.orderId !== null) {
				this.postData(`/api/orders/${this.orderId}/`, { ...this })
					.then(() => {
						alert('Заказ подтвержден')
						location.replace(`/payment/${this.orderId}/`)
					})
					.catch(() => {
						console.warn('Ошибка при подтверждения заказа')
					})
			}
		},
		auth() {
			const username = document.querySelector('#username').value
			const password = document.querySelector('#password').value
//			this.postData('/api/sign-in/', JSON.stringify({ username, password }))
            this.postData('/api/sign-in/', { username, password })
				.then(({ data, status }) => {
					location.assign(`/orders/${this.orderId}/`)
				})
				.catch(() => {
					alert('Ошибка авторизации')
				})
		}
	},
	mounted() {
		if(location.pathname.startsWith('/orders/')) {
			const orderId = location.pathname.replace('/orders/', '').replace('/', '')
			this.orderId = orderId.length ? Number(orderId) : null
			this.id = this.orderId
			this.getOrder(this.orderId);
		}
		else if (location.pathname.startsWith('/order-detail/')) {
			const orderId = location.pathname.replace('/order-detail/', '').replace('/', '')
			this.orderId = orderId.length ? Number(orderId) : null
			this.id = this.orderId
			this.getOrder(this.orderId);
		}
		else if (location.pathname.startsWith('/order-detail/')) {
			const orderId = location.pathname.replace('/order-detail/', '').replace('/', '')
			this.orderId = orderId.length ? Number(orderId) : null
			this.getOrder(this.orderId);
		}
	},
	data() {
		return {
			orderId: null,
			createdAt: null,
			fullName: null,
			phone: null,
			email: null,
			deliveryType: null,
			city: null,
			address: null,
			paymentType: null,
			status: null,
			totalCost: null,
			products: [],
			paymentError: null,
		}
	},
}