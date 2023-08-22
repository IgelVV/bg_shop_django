var mix = {
	methods: {
		getHistoryOrder() {
			this.getData("/api/orders/")
				.then(data => {
					console.log(data)
					this.orders = data
				}).catch((error) => {
                    this.orders = []
                    console.warn('error:', error.response.data)
                    if (error.response.status === 403){
                        location.assign(`/sign-in/`)
                    }
                    else{
                        alert(JSON.stringify(error.response.data))
                    }
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