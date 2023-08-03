var mix = {
	methods: {
		signUp () {
			const name = document.querySelector('#name').value
			const username = document.querySelector('#login').value
			const password = document.querySelector('#password').value
			const passwordReply = document.querySelector('#passwordReply').value
			if (
			    !name.trim().length ||
			    !username.trim().length ||
                !password.trim().length ||
                !passwordReply.trim().length ||
                password !== passwordReply
            ) {
                alert('There are blank fields in the form or passwords do not match')
                return
            }
			// this.postData('/api/sign-up/', JSON.stringify({ name, username, password }))
			this.postData('/api/sign-up/', {
				name: name,
				username: username,
				password: password
			})
				.then(({ data, status }) => {
					location.assign(`/`)
				}).catch((error) => {
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