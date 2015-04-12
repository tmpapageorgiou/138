/*=============================================================
    Authour URL: www.designbootstrap.com

    http://www.designbootstrap.com/

    License: MIT

    http://opensource.org/licenses/MIT

    100% Free To use For Personal And Commercial Use.

    IN EXCHANGE JUST TELL PEOPLE ABOUT THIS WEBSITE

========================================================  */
$(document).ready(function () {

    /*====================================
          SUBSCRIPTION   SCRIPTS
    ======================================*/

    // SCROLL SCRIPTS
    $('.scroll-me a').bind('click', function (event) { //just pass scroll-me class and start scrolling
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top
        }, 1000, 'easeInOutQuad');
        event.preventDefault();
    });


    // LOGIN CHAT
    $("#user-login").submit(function(event){
      event.preventDefault();

      data = {
        "name": $("#user-nickname").val(),
        "avatar": $("#user-avatar").val()
      }

      $.ajax({
          type: "POST",
          url: "http://172.16.5.182:8888/new/"+$("#user-nickname").val(),
          data: JSON.stringify(data),
          contentType: 'application/json; charset=utf-8',
          dataType: "json",
          success: function(response) {
            localStorage.setItem("username", data.name);
            window.location.replace("chat.html")
          },
          error: function(response){
            var error;
            if(response.code == 409)
            {
              error = "Nickname já utilizado, escolha outro."
            }else
            {
              error = "Não foi possível conectar, tente mais tarde."
            }

            $("#login-error").html(error)
          }
      });

    })

 });
