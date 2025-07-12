$(document).ready(function() {
    $.validator.addMethod("phoneValidation", function(value, element) {
        return this.optional(element) || /^[0-9]{10}$/.test(value);
    }, "Please enter a valid 10-digit mobile number");
    $.validator.addMethod('c_password', function(value, element) {
        return value == $("#id_password1").val();
    }, "Passwords do not match.");
    $("#signupform").validate({
                rules: {
                    username: {
                        required: true,
                    },
                    email: {
                        required: true,
                        email: true
                    },
                    password1: {
                        required: true,
                        minlength: 8, // Minimum 8 characters
                        // Add a custom rule for password strength (using a regex)
                        pwcheck: function(value, element) {
                            return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(value);
                        }
                    },
                    password2: {
                        required: true,
                        c_password: true
                    },
                    mobile_number_1: {
                        required: true,
                        phoneValidation: true
                    }
                },
                messages: {
                    username: {
                        required: "Please enter your username",
                    },
                    email: {
                        required: "Please enter your email address",
                        email: "Please enter a valid email address"
                    },
                    password1: {
                        required: "Please enter your password",
                        minlength: "Password must be at least 8 characters long",
                        pwcheck: "Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
                    },
                    mobile_number_1: {
                        required: "Please enter your mobile number."
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