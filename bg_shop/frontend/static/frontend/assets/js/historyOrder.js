var mix = {
	methods: {
		getHistoryOrder() {
			this.getData("/api/orders/")
				.then(data => {
					console.log(data)
					this.orders = data
				}).catch(() => {
				this.orders = []
				console.warn('Error when receiving the list of orders')
				alert('Error when receiving the list of orders')
			})
		}
	},
	mounted() {
		this.getHistoryOrder();
	},
	data() {
		return {
			orders: [],
		}
	}
}