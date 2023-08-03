var mix = {
	methods: {
		signIn () {
			const username = document.querySelector('#login').value
			const password = document.querySelector('#password').value
			// this.postData('/api/sign-in/', JSON.stringify({ username, password }))
			this.postData('/api/sign-in/', { username, password })
				.then(({ data, status }) => {
					location.assign(`/`)
				})
				.catch((error) => {
                console.warn(error.response.data)
                alert(JSON.stringify(error.response.data))
            })
		}
	},
	mounted() {
	},
	data() {
		return {}
	}
}