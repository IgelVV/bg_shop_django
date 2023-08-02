var mix = {
    methods: {
        getProfile() {
            this.getData(`/api/profile/`).then(data => {
                this.fullName = data.fullName
                this.avatar = data.avatar
                this.phone = data.phone
                this.email = data.email
            }).catch(() => {
                console.warn('Error when getting a profile')
            })
        },
        changeProfile () {
            if(!this.fullName.trim().length || !this.phone.trim().length || !this.email.trim().length) {
                alert('There are blank fields in the form')
                return
            }

            this.postData('/api/profile/', {
                fullName: this.fullName,
                avatar: this.avatar,
                phone: this.phone,
                email: this.email
            }).then(({data}) => {
                this.fullName = data.fullName
                this.avatar = data.avatar
                this.phone = data.phone
                this.email = data.email
               alert('Successfully saved')
            }).catch(() => {
                console.warn('Error updating profile')
                alert('Error updating profile')
            })
        },
        changePassword () {
            if (
                !this.passwordCurrent.trim().length ||
                !this.password.trim().length ||
                !this.passwordReply.trim().length ||
                this.password !== this.passwordReply
            ) {
                alert('There are blank fields in the form or passwords do not match')
                return
            }
            this.postData('/api/profile/password/', {'password': this.password})
              .then(({data}) => {
                   alert('Successfully saved')
                    this.passwordCurrent = ''
                    this.password = ''
                    this.passwordReply = ''
                }).catch(() => {
                    console.warn('Error saving password')
                    alert('Error saving password')
                })
        },
        setAvatar (event) {
            const target = event.target
            const file = target.files?.[0] ?? null
            if (!file) return

            const formData = new FormData()
            formData.append('avatar', file)

            this.postData('/api/profile/avatar/', formData, {'Content-Type': 'multipart/form-data'}).then((data) => {
                this.avatar = data.data
            }).catch(() => {
                 console.warn('Error updating the image')
                 alert('Error updating the image')
            })
        },
        getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },
        clearAvatar() {
            this.avatar = null
        }
    },
    created() {
        this.getProfile();
    },
    data() {
        return {
            fullName: null,
            phone: null,
            email: null,
            avatar: null,
            password: '',
            passwordCurrent: '',
            passwordReply: ''
        }
    },
}