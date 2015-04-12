var app = angular.module('app138', ['onsen.directives']);

if (localStorage.getItem("username") === null) {
  location.href = "/";
}

app.controller('chat', function($scope, $rootScope, $timeout, $http) {

  $scope.people = [];
  $scope.messages = [];

  $scope.init = function() {};

  $scope.api138 = new Api138({
    userID: localStorage["username"],
    host: '172.16.5.182',
    port: 8888,
    onMsgCallback: function(data) {
      if (data.type == "message") {
        $scope.messages.unshift(data);
      } else if (data.type == "neighbors") {
        $scope.people.unshift(data);
      }
      $scope.$apply();
    }
  });

  $scope.currentUser = localStorage.getItem("username");

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
    app.slidingMenu.setMainPage("page.html");
    $("#fieldMessage").addAttr("readonly");
    $scope.doAnimate = true;
    location.href('index.html');
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

  //$scope.animateText();

  $scope.sendMessage = function(field) {
    $("#fieldMessage").val("");
    if (field != "") {
      $scope.api138.sendMessage(field);
    }
  }
});
