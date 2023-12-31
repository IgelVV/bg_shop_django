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
					this.comment = data.comment
					this.paymentType = data.paymentType
					this.status = data.status
					this.deliveryCost = data.deliveryCost
					this.totalCost = data.totalCost
					this.paid = data.paid
					this.products = data.products
					console.log(this.products)
					if (typeof data.paymentError !== 'undefined') {
						this.paymentError = data.paymentError
					}
				})
				.catch((error) => {
                    console.warn('error:', error.response.data)
                    if (error.response.status === 403){
                        location.assign(`/sign-in/`)
                    }
                    else{
                        alert(JSON.stringify(error.response.data))
                    }
                })
		},
		confirmOrder() {
			if (this.orderId !== null) {
				this.postData(`/api/orders/${this.orderId}/`, { ...this })
					.then(() => {
						alert('The order is confirmed')
						location.replace(`/order-detail/${this.orderId}/`)
					}).catch((error) => {
                        console.warn(error.response.data)
                        alert(JSON.stringify(error.response.data))
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
				}).catch((error) => {
                    console.warn(error.response.data)
                    alert(JSON.stringify(error.response.data))
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
			comment: null,
			paymentType: null,
			status: null,
			deliveryCost: null,
			totalCost: null,
			paid: null,
			products: [],
			paymentError: null,
		}
	},
}