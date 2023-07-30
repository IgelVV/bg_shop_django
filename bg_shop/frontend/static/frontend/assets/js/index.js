var mix = {
	methods: {
		getBanners() {
			this.getData("/api/banners")
				.then(data => {
					this.banners = data
				}).catch(() => {
				this.banners = []
				console.warn('Error when receiving banners')
			})
		},
		getPopularProducts() {
			this.getData("/api/products/popular/")
				.then(data => {
					this.popularCards = data
				})
				.catch((error) => {
					console.log('----', error)
					this.popularCards = []
					console.warn('Error when getting a list of popular products')
				})
		},
		getLimitedProducts() {
			this.getData("/api/products/limited/")
				.then(data => {
					this.limitedCards = data
				}).catch(() => {
				this.limitedCards = []
				console.warn('Error when receiving a list of limited goods')
			})
		},
	},
	mounted() {
		this.getBanners();
		this.getPopularProducts();
		this.getLimitedProducts();
	},
   created() {
     this.getLimitedProducts()
   },
	data() {
		return {
			banners: [],
			popularCards: [],
			limitedCards: [],
		}
	}
}