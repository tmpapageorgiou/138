var app = angular.module('app138', ['onsen.directives']);

app.controller('chat', function($scope, $rootScope) {

  $scope.items = [{
      "from": "me",
      "msg": "Essa é a minha mensagem",
      "type": "message"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message"
    }, {
      "from": "me",
      "msg": "Essa é a minha mensagem",
      "type": "message"
    },

    {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message"
    }, {
      "from": "usuario",
      "msg": "Essa é a minha mensagem",
      "type": "message"
    },



  ];


  $scope.sendMessage = function(field) {
    $("#fieldMessage").val("");
    $scope.items.unshift({
      "from": "me",
      "msg": field,
      "type": "message"
    });
  }

});
