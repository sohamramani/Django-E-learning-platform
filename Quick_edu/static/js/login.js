$(document).ready(function() {
    $("#loginform").validate({
                rules: {
                    username: {
                        required: true,
                    },
                    password: {
                        required: true,
                        minlength: 8, // Minimum 8 characters
                        // Add a custom rule for password strength (using a regex)
                        pwcheck: function(value, element) {
                            return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(value);
                        }
                    }
                },
                messages: {
                    username: {
                        required: "Please enter your username",
                    },
                    password: {
                        required: "Please enter your password",
                        minlength: "Password must be at least 8 characters long",
                        pwcheck: "Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
                    }
                },
                submitHandler: function(form) {
                    form.submit();
                },
                errorPlacement: function(error, element) {
                    error.insertAfter(element); // Places the error message right below the input
                },
        });
});