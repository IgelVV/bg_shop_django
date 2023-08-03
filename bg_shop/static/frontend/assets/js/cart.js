var mix = {
    methods: {
        submitBasket () {
            this.postData('/api/orders/', Object.values(this.basket))
                .then(({data: { orderId }}) => {
                    location.assign(`/orders/${orderId}/`)
                }).catch((error) => {
                        console.warn(error.response.data)
                        alert(JSON.stringify(error.response.data))
                    })
        },
        goLogin () {
            location.assign(`/sign-in/`)
        },
        isBasketEmpty () {
            return JSON.stringify(this.basket) === '{}'
        },
    },
    mounted() {},
    data() {
        return {}
    }
}