var mix = {
	methods: {
		submitPayment() {
			console.log('submitPayment is called')
//			const orderId = location.pathname.startsWith('/payment/')
//				? Number(location.pathname.replace('/payment/', '').replace('/', ''))
//				: null
			if (location.pathname.startsWith('/payment/')) {
				var orderId = Number(
					location.pathname
						.replace('/payment/', '')
						.replace('/', '')
				)
			}
			else if (location.pathname.startsWith('/payment-someone/')) {
				var orderId = Number(
					location.pathname
						.replace('/payment-someone/', '')
						.replace('/', '')
				)
			}
			else {
				var orderId = null
			}
			const numero1 = document.getElementById('numero1').value.replace(' ', '');
			this.postData(`/api/payment/${orderId}/`, {
				name: this.name,
				number: numero1,
				year: this.year,
				month: this.month,
				code: this.code
			})
				.then(() => {
					alert('We are waiting for payment confirmation from the payment system')
					this.number = ''
					this.name = ''
					this.year = ''
					this.month = ''
					this.code = ''
					location.assign(`/order-detail/${orderId}/`)
				}).catch((error) => {
                console.warn(error.response.data)
                alert(JSON.stringify(error.response.data))
            })
		}
	},
	data() {
		return {
			number: '',
			month: '',
			year: '',
			name: '',
			code: ''
		}
	}
}