//var mix = {
//    methods: {
//        getUserAccount() {
//            this.getData("/api/account/").then(data => {
//                this.firstname = data.firstname
//                this.secondname = data.secondname
//                this.surname = data.surname
//                this.avatar = data.avatar
//                this.orders = data.orders
//            })
//        },
//    },
//    mounted() {
//        this.getUserAccount();
//    },
//    data() {
//        return {
//            firstname: "",
//            secondname: "",
//            surname: "",
//            avatar: {},
//            orders: [],
//        }
//    },
//    computed: {
//        fullName() {
//            return [this.surname, this.firstname, this.secondname].join(" ")
//        },
//    },
//}
var mix = {
    methods: {
        getUserAccount() {
            this.getData("/api/profile/").then(data => {
                this.fullName = data.fullName
                this.avatar = data.avatar
                this.orders = data.orders
                this.email = data.email
                this.phone = data.phone
            }).catch((error) => {
                console.warn('error:', error.response.data)
                if (error.response.status === 403){
                    location.assign(`/sign-in/`)
                }
                else{
                    alert(JSON.stringify(error.response.data))
                }
            })
        },
		getLastOrder() {
			this.getData("/api/orders/")
				.then(data => {
				    if (data){
				        this.order = data[0]
				    }
				}).catch(() => {
				this.order = {}
				console.warn('Error when receiving the last order')
			})
		},
	},
    mounted() {
        this.getUserAccount();
		this.getLastOrder();
    },
    data() {
        return {
            firstname: "",
            secondname: "",
            surname: "",
            avatar: {},
            order: {},
        }
    },
    computed: {
//        getOrders() {
//            this.getData("/api/orders/").then(data => {
//                ...data
//            })
//        }
    },
}