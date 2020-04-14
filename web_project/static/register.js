// Line: 33: Replace ajaxfile.php with corresponding RESTful URL: called with parameter userName. Return data true if username is available false otherwise. Please check the catch function: it was giving cannot read property push of undefined. This part is commented for this reason
window.onload = function () {
	var formApp = new Vue({
		el: '#registerFormId',
		data: {
			errors: [],
			nameInputText: null,
			emailInputText: null,
			userNameInputText: null,
			userPassInputText: null,
			userPassInputCnfText: null,
			success: null,
			regSuccess: false,
			regFail: false,
			regDone: false
		},
		methods: {
			validateForm: function (e) {
				e.preventDefault();
				obj = this;
				this.errors = [];
				
				if(!this.nameInputText) {
					this.errors.push('Name required');
				}
				else if(!(/^[a-zA-Z]+$/.test(this.nameInputText))) {
					this.errors.push('Name must contain letters only');
				}
				if(!this.emailInputText) {
					this.errors.push('Email required');
				}
				if(!this.userNameInputText) {
					this.errors.push('Username required');
				}
				else {
					var uNameAvailable = false;
					axios.get('/register_user/check_user/'+this.userNameInputText, {})
					.then(function (response) {
						if(typeof(response.data) == "string") {
							obj.errors.push('Check your internet connection and try again')
						}
						if(typeof(response.data) == "number") {
							if(response.data == 0) {
								obj.errors.push('Username is taken')
							}
						}
					})
					.catch(function (e) {
						console.log('error:', e)
						obj.errors.push('Check your internet connection and try again');
					})
				}
				// Add regex for email: accepts a@a
				if(!this.userPassInputText) {
					this.errors.push('Password required');
				}
				else if(this.userPassInputText.length < 4) {
					this.errors.push('Password must be atleast 4 characters long');
				}
				if(!this.userPassInputCnfText) {
					this.errors.push('Confirm Password required');
				}
				else if(this.userPassInputText != this.userPassInputCnfText) {
					this.errors.push('Password and Confirm Password do not match');
				}

				if(this.errors.length == 0) {
					// Submit the form
					axios.get('/register_user', {
						params: {
							userName: this.userNameInputText,
							userPass: this.userPassInputText,
							name: this.nameInputText,
							email: this.emailInputText
						}
					})
					.then(
						function (response) {
							if(obj.errors.length != 0) {
								obj.regSuccess = false
							}
							else if(!(response.data.localeCompare("Failed to insert!"))) {
								obj.regSuccess = true;
								obj.msgSuccess = "Registration Failed. Check your connection and try again"
								obj.regFail = true;
								obj.regDone = false;
							}
							else {
								obj.regSuccess = true;
								obj.msgSuccess = "Registered Successfully";
								obj.regFail = false;
								obj.regDone = true;
							}
						}
					).catch(
						function (e) {
							if(obj.errors.length != 0) {
								obj.regSuccess = false
							}
							else {
								obj.regSuccess = true;
								obj.msgSuccess = "Registration Failed. Check your connection and try again"
								obj.regFail = true;
								obj.regDone = false;
							}
						}
					)
				}
			}
		}
	});
}