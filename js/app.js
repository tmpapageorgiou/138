var app = angular.module('app138', ['onsen.directives']);

app.controller('chat', function($scope, $rootScope, $timeout) {

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

  $scope.login = function() {
    app.slidingMenu.setSwipeable(true);
    app.slidingMenu.setMainPage("page.html");
    $("#fieldMessage").removeAttr("readonly");
    $("#fieldMessage").val("");
    $scope.doAnimate = false;
  };

  $scope.logout = function() {
    app.slidingMenu.closeMenu();
    app.slidingMenu.setSwipeable(false);
    app.slidingMenu.setMainPage("login.html");
    $("#fieldMessage").addAttr("readonly");
    $scope.doAnimate = true;
  };

  $scope.sendTo = function(name) {
    $("#fieldMessage").val("@" + name + " ");
    $("#fieldMessage").focus();
  }

  $scope.field = "";
  $scope.randomSentences = ["Conheça novas pessoas.",
    "Converse pessoas pŕoximas a você.",
    "Fale com pessoas no seu círculo de bate papo.",
    "E aí, quer tc?"
  ];
  $scope.charIndex = 0;
  $scope.sentenceIndex = 0;
  $scope.currentSentences = $scope.randomSentences[0];
  $scope.doAnimate = true;

  $scope.animateText = function() {
    $timeout(function() {

      if ($scope.doAnimate) {
        $scope.field = $scope.currentSentences.substring(0, $scope.charIndex);
        $scope.charIndex++;
        if ($scope.charIndex > $scope.currentSentences.length) {
          $scope.sentenceIndex++;
          if ($scope.sentenceIndex >= $scope.randomSentences.length) {
            $scope.sentenceIndex = 0;
          }
          $scope.charIndex = 0;
          $scope.currentSentences = $scope.randomSentences[$scope.sentenceIndex];
        }
      }
      $scope.animateText();
    }, 90);
  };

  $scope.animateText();


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
