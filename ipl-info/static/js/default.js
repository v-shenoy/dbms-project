// Disabling Flash Message
flash = document.querySelector(".alert")
cross = document.querySelector(".fa-times")

if(cross != null)
{
    cross.addEventListener("click", function()
    {
        flash.style.display = "none";
    });
}