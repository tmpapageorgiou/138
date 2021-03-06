﻿
/*=============================================================
    Authour URL: www.designbootstrap.com

    http://www.designbootstrap.com/

    License: MIT

    http://opensource.org/licenses/MIT

    100% Free To use For Personal And Commercial Use.

    IN EXCHANGE JUST TELL PEOPLE ABOUT THIS WEBSITE

========================================================  */
$(document).ready(function() {

  //Cache Of Geo
  if (navigator.geolocation) {

    navigator.geolocation.getCurrentPosition(function() {}, function() {}, {
      maximumAge: 10000,
      timeout: 1000,
      enableHighAccuracy: true
    });

  }

  //AVATAR
  $('.avatars-image').click(function(event) {
    var urlImage = $(this).find("img").attr("src");

    $('.avatars-image img').removeClass("avatar-selected");
    $(this).find("img").addClass("avatar-selected");

    $("#user-avatar").val(urlImage);
  })

  validName = function(name) {
    return /^.*([a-z]|[0-9]|[A-Z])$/.test(name)
  }

  // LOGIN CHAT
  $("#user-login").submit(function(event) {
    event.preventDefault();

    if (!validName) {
      $("#login-error").html("Nickname deve conter apenas letras ou números.")
    } else {
      data = {
        "name": $("#user-nickname").val(),
        "avatar": $("#user-avatar").val()
      }

      $.ajax({
        type: "POST",
        url: "http://" + window.location.host + "/new/" + $("#user-nickname").val(),
        data: JSON.stringify(data),
        contentType: 'application/json; charset=utf-8',
        dataType: "json",
        success: function(response) {
          localStorage.setItem("username", data.name);
          window.location.replace("chat.html")
        },
        error: function(response) {
          var error;
          if (response.status == 409) {
            error = "Nickname já utilizado, escolha outro."
          } else {
            error = "Não foi possível conectar, tente mais tarde."
          }

          $("#login-error").html(error)
        }
      });
    }

  })


  /*====================================
        SUBSCRIPTION   SCRIPTS
  ======================================*/

  // SCROLL SCRIPTS
  $('.scroll-me a').bind('click', function(event) { //just pass scroll-me class and start scrolling
    var $anchor = $(this);
    $('html, body').stop().animate({
      scrollTop: $($anchor.attr('href')).offset().top
    }, 1000, 'easeInOutQuad');
    event.preventDefault();
  });



});
