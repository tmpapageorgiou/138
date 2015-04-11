var app = angular.module('app138', ['onsen.directives']);

app.controller('chat', function($scope, $rootScope) {

  $scope.people = [{
    "name": "fulano"
  }]

  $scope.items = [{
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message",
      "avatar": "http://www.avatarsdb.com/avatars/selly_gomez.jpg"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message",
      "avatar": "http://www.avatarsdb.com/avatars/rihanna_rebelle_fleur.gif"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message",
      "avatar": "http://www.avatarsdb.com/avatars/i_see_dumb_people.jpg"
    }, {
      "from": "me",
      "msg": "Essa é a minha mensagem",
      "type": "message",
      "avatar": "http://www.avatarsdb.com/avatars/pc_user.gif"
    }, {
      "from": "me",
      "msg": "Essa é a minha mensagem",
      "type": "message",
      "avatar": "http://www.avatarsdb.com/avatars/pc_user.gif"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message",
      "avatar": "  http://www.avatarsdb.com/avatars/rihanna_new_ps.jpg"
    }, {
      "from": "me",
      "msg": "Essa é a minha mensagem",
      "type": "message",
      "avatar": "http://www.avatarsdb.com/avatars/pc_user.gif"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message",
      "avatar": "http://www.avatarsdb.com/avatars/rihanna_rebelle_fleur.gif"
    }, {
      "from": "me",
      "msg": "Essa é a minha mensagem",
      "type": "message",
      "avatar": "http://www.avatarsdb.com/avatars/pc_user.gif"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message",
      "avatar": "http://www.avatarsdb.com/avatars/rihanna_rebelle_fleur.gif"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message",
      "avatar": "http://www.avatarsdb.com/avatars/rihanna_rebelle_fleur.gif"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message",
      "avatar": "http://www.avatarsdb.com/avatars/vibrating_cat.gif"
    },

  ];

  $scope.login = function(){
    app.slidingMenu.setSwipeable(true);
    app.slidingMenu.setMainPage("page.html");
  };

  $scope.logout = function(){
    app.slidingMenu.closeMenu();
    app.slidingMenu.setSwipeable(false);
    app.slidingMenu.setMainPage("login.html");
  };

  $scope.sendTo = function(name) {
    $("#fieldMessage").val("@" + name + " ");
    $("#fieldMessage").focus();
  }


  $scope.sendMessage = function(field) {
    $("#fieldMessage").val("");
    $scope.items.unshift({
      "from": "me",
      "msg": field,
      "type": "message",
      "avatar": "http://www.avatarsdb.com/avatars/vibrating_cat.gif"
    });
  }

});
