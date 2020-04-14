window.onload = function () {
	var loginFormApp = new Vue({
		el: '#loginFormId',
		data: {
			errors: [],
			userNameText: null,
			userPassText: null,
			loginSuccess: false,
			msgSuccess: null,
			logDone: false,
			logFail: false
		},
		methods: {
			validateForm: function (e) {
				e.preventDefault();
				obj = this;
				if(!this.userNameText) {
					this.errors.push('Username is required');
				}
				if(!this.userPassText) {
					this.errors.push('Password is required')
				}
				else if(this.userPassText.length < 4) {
					this.errors.push('Password must be atleast 4 characters long');
				}
				if(this.errors.length == 0) {
					axios.get('/login/user_login', {
						params: {
							userName: this.userNameText,
							userPass: this.userPassText
						}
					})
					.then(function (response) {
						obj.loginSuccess = true
						if(!(response.data.localeCompare("User not registered!"))) {
							obj.msgSuccess = response.data
							obj.logDone = false
							obj.logFail = true
						}
						else if(!(response.data.localeCompare("Wrong Password"))) {
							obj.msgSuccess = response.data
							obj.logDone = false
							obj.logFail = true
						}
						else if(!(response.data.localeCompare("Failed to validate user"))) {
							obj.msgSuccess = response.data
							obj.logDone = false
							obj.logFail = true
						}
						else {
							localStorage.token = response.data
							localStorage.username = obj.userNameText
							window.location.replace("index.html")
						}
					})
					.catch(function (response) {

					})
				}
			}
		}
	})
}