$(".alert .fa-times").on("click", function()
{
    $(".alert").css("display", "none");
});

$(".side-arrow .fa-angle-double-left").on("click", function()
{
    $(".sidebar").animate({width: "toggle"});
});

$(".side-header .fa-times").on("click", function()
{
    $(".sidebar").animate({width: "toggle"});
});