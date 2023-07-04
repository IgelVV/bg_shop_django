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
                alert('В форме присутствуют незаполненные поля или пароли не совпадают')
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
				})
		}
	},
	mounted() {
	},
	data() {
		return {}
	}
}