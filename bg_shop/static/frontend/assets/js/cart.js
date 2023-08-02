var mix = {
    methods: {
        submitBasket () {
            this.postData('/api/orders/', Object.values(this.basket))
                .then(({data: { orderId }}) => {
                    location.assign(`/orders/${orderId}/`)
                }).catch(() => {
                    console.warn('Error when creating an order')
                    alert('Error when creating an order')
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