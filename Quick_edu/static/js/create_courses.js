$(document).ready(function() {
    $.validator.addMethod("greaterThan", function(value, element, params) {
        if (!/Invalid|NaN/.test(new Date(value))) {
            return new Date(value) >= new Date($(params).val());
        }
        return isNaN(value) && isNaN($(params).val()) || (Number(value) >= Number($(params).val()));
    },'Must be greater than or equal to Start Date.');
        
    $("#courseForm").validate({
            rules: {
                title: {
                    required: true,
                    minlength: 5
                },
                end_date: {
                    greaterThan: "#start_date"
                }
            },
            messages: {
                course_name: {
                    required: "Please enter course title",
                    minlength: "Course name must be at least 5 characters"
                },
                end_date: {
                    greaterThan: "End date must be greater than or equal to start date"
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