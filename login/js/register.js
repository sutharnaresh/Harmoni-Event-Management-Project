function toggleAdditionalImagesField() {
    // Collecting All Div's
    var eventCategorySelect = document.getElementById("event-category-select");
    var additionalImagesField = document.getElementById("additional-images-field");
    var specialskillfield = document.getElementById("special-skill");
    var user_profile_pic = document.getElementById("user_profile_pic")
    var Discriotion_field = document.getElementById("Discriotion-field");
    var company_name = document.getElementById("company-name");
    var first_name =  document.getElementById("first_name");
    var last_name = document.getElementById("last_name");

    // Collecting All Fields 
    var firstNameField = document.getElementById("firstNameField");
    var lastNameField = document.getElementById("lastNameField");
    var workhand_category = document.getElementById("workhand_category");

    var descriptionField = document.getElementById("descriptionField");
    var companyNameField = document.getElementById("companyNameField");

    var CompanyImageField = document.getElementById("additional-images");
    
    if (eventCategorySelect.value === "vendor") {
        Discriotion_field.style.display = "block";
        additionalImagesField.style.display = "block";
        company_name.style.display = "block";
        specialskillfield.style.display = "none";
        user_profile_pic.style.display = "none";
        first_name.style.display = "none";
        last_name.style.display = "none";
        firstNameField.required = false;
        lastNameField.required = false;
        workhand_category.required = false;
        CompanyImageField.required = true;
        descriptionField.required = true;
        companyNameField.required = true;
    } else {
        Discriotion_field.style.display = "none"
        additionalImagesField.style.display = "none";
        company_name.style.display = "none";
        specialskillfield.style.display = "block";
        user_profile_pic.style.display = "block";
        first_name.style.display = "block";
        last_name.style.display = "block";
        firstNameField.required = true;
        lastNameField.required = true;
        workhand_category.required = true;
        descriptionField.required = false;
        companyNameField.required = false;
    }
}

$(document).ready(function() {
    $("#state").change(function() {
        var state_id = $(this).val();
        var url = "/get-city/?state_id="+state_id;
        $.get(url, function(data,status){
            $("#city").html(data);
        });
    });
});