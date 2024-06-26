/*
 Copyright (C) 2016 Igor Soloduev <diahorver@gmail.com>

 This file is part of WikiCode.

 WikiCode is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 WikiCode is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with WikiCode.  If not, see <http://www.gnu.org/licenses/>.
 */

(function() {

  "use strict";

  //////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////
  //
  // H E L P E R    F U N C T I O N S
  //
  //////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////

  /**
   * Function to check if we clicked inside an element with a particular class
   * name.
   *
   * @param {Object} e The event
   * @param {String} className The class name to check against
   * @return {Boolean}
   */
  function clickInsideElement( e, className ) {
    var el = e.srcElement || e.target;

    if ( el.classList.contains(className) ) {
      return el;
    } else {
      while ( el = el.parentNode ) {
        if ( el.classList && el.classList.contains(className) ) {
          return el;
        }
      }
    }

    return false;
  }

  /**
   * Get's exact position of event.
   *
   * @param {Object} e The event passed in
   * @return {Object} Returns the x and y position
   */
  function getPosition(e) {
    var posx = 0;
    var posy = 0;

    if (!e) var e = window.event;

    if (e.pageX || e.pageY) {
      posx = e.pageX;
      posy = e.pageY;
    } else if (e.clientX || e.clientY) {
      posx = e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
      posy = e.clientY + document.body.scrollTop + document.documentElement.scrollTop;
    }

    return {
      x: posx,
      y: posy
    }
  }

  //////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////
  //
  // C O R E    F U N C T I O N S
  //
  //////////////////////////////////////////////////////////////////////////////
  //////////////////////////////////////////////////////////////////////////////

  /**
   * Variables.
   */
  var contextMenuClassName = "context-menu";
  var contextMenuItemClassName = "context-menu__item";
  var contextMenuLinkClassName = "context-menu__link";
  var contextMenuActive = "context-menu--active";

  var taskItemClassName = "task";
  var taskItemInContext;

  var clickCoords;
  var clickCoordsX;
  var clickCoordsY;

  var menu = document.querySelector("#context-menu");
  var menuItems = menu.querySelectorAll(".context-menu__item");
  var menuState = 0;
  var menuWidth;
  var menuHeight;
  var menuPosition;
  var menuPositionX;
  var menuPositionY;

  var windowWidth;
  var windowHeight;

  /**
   * Initialise our application's code.
   */
  function init() {
    contextListener();
    clickListener();
    keyupListener();
    resizeListener();
  }

  /**
   * Listens for contextmenu events.
   */
  function contextListener() {
    document.addEventListener( "contextmenu", function(e) {
      taskItemInContext = clickInsideElement( e, taskItemClassName );

      if ( taskItemInContext ) {
        e.preventDefault();
        toggleMenuOn();

        // Здесь необходимо выбрать какое контекстное меню отображать
        var str_line = ''+taskItemInContext.getAttribute("data-id");
        var type_elem = ''+taskItemInContext.getAttribute("type_elem");

        $('#jstree').jstree(true).deselect_all();
        $('#jstree').jstree(true).select_node(str_line);

        if(type_elem == "publ")
        {
          //Это конспект
          //Показываем нужные
          $("#lt-context-menu-3").attr("style", "");
          $("#lt-context-menu-3-0").attr("style", "");
          $("#lt-context-menu-3-1").attr("style", "");
          $("#lt-context-menu-1").attr("style", "");
          $("#lt-context-menu-6-1").attr("style", "");
          //Скрываем не нужные опции контекстного меню
          $("#lt-context-menu-4").attr("style", "display: none;");
          $("#lt-context-menu-5").attr("style", "display: none;");
          $("#lt-context-menu-5-5").attr("style", "display: none;");
          $("#lt-context-menu-6").attr("style", "display: none;");
          $("#lt-context-menu-7").attr("style", "display: none;");
          $("#lt-context-menu-8").attr("style", "display: none;");
          $("#lt-context-menu-9").attr("style", "display: none;");
          $("#lt-context-menu-10").attr("style", "display: none;");
          $("#lt-context-menu-4-1").attr("style", "display: none;");
        }
        else if(type_elem == "folder"){
            //Это папка
            //Скрываем не нужные опции контекстного меню
            $("#lt-context-menu-3").attr("style", "display: none;");
            $("#lt-context-menu-3-0").attr("style", "display: none;");
            $("#lt-context-menu-3-1").attr("style", "display: none;");
            $("#lt-context-menu-1").attr("style", "display: none;");
            $("#lt-context-menu-6-1").attr("style", "display: none;");
            $("#lt-context-menu-10").attr("style", "display: none;");
            $("#lt-context-menu-4-1").attr("style", "display: none;");
            //Показываем нужные
            $("#lt-context-menu-4").attr("style", "");
            $("#lt-context-menu-5").attr("style", "");
            $("#lt-context-menu-5-5").attr("style", "");
            $("#lt-context-menu-6").attr("style", "");
            $("#lt-context-menu-7").attr("style", "");
            $("#lt-context-menu-8").attr("style", "");
            $("#lt-context-menu-9").attr("style", "");
        }
        else if(type_elem == "group"){
            //Это группа
            //Скрываем не нужные опции контекстного меню
            $("#lt-context-menu-3").attr("style", "display: none;");
            $("#lt-context-menu-3-0").attr("style", "display: none;");
            $("#lt-context-menu-3-1").attr("style", "display: none;");
            $("#lt-context-menu-1").attr("style", "display: none;");
            $("#lt-context-menu-5-5").attr("style", "display: none;");
            $("#lt-context-menu-6-1").attr("style", "display: none;");
            $("#lt-context-menu-10").attr("style", "display: none;");
            $("#lt-context-menu-8").attr("style", "display: none;");
            //Показываем нужные
            $("#lt-context-menu-4-1").attr("style", "");
            $("#lt-context-menu-4").attr("style", "");
            $("#lt-context-menu-5").attr("style", "");
            $("#lt-context-menu-6").attr("style", "");
            $("#lt-context-menu-7").attr("style", "");
            $("#lt-context-menu-9").attr("style", "");
        }
        else if(type_elem == "saved") {
          //Это сохраненный конспект
          //Показываем нужные
          $("#lt-context-menu-3-0").attr("style", "");
          $("#lt-context-menu-1").attr("style", "");
          $("#lt-context-menu-10").attr("style", "");
          //Скрываем не нужные опции контекстного меню
          $("#lt-context-menu-3").attr("style", "display: none;");
          $("#lt-context-menu-3-1").attr("style", "display: none;");
          $("#lt-context-menu-4-1").attr("style", "display: none;");
          $("#lt-context-menu-4").attr("style", "display: none;");
          $("#lt-context-menu-5").attr("style", "display: none;");
          $("#lt-context-menu-6").attr("style", "display: none;");
          $("#lt-context-menu-6-1").attr("style", "display: none;");
          $("#lt-context-menu-7").attr("style", "display: none;");
          $("#lt-context-menu-8").attr("style", "display: none;");
          $("#lt-context-menu-9").attr("style", "display: none;");
        }
        else {
            //Это другой файл
        }

        positionMenu(e);
      } else {
        taskItemInContext = null;
        toggleMenuOff();
      }
    });
  }

  /**
   * Listens for click events.
   */
  function clickListener() {
    document.addEventListener( "click", function(e) {
      var clickeElIsLink = clickInsideElement( e, contextMenuLinkClassName );

      if ( clickeElIsLink ) {
        e.preventDefault();
        menuItemListener( clickeElIsLink );
      } else {
        var button = e.which || e.button;
        if ( button === 1 ) {
          toggleMenuOff();
        }
      }
    });
  }

  /**
   * Listens for keyup events.
   */
  function keyupListener() {
    window.onkeyup = function(e) {
      if ( e.keyCode === 27 ) {
        toggleMenuOff();
      }
    }
  }

  /**
   * Window resize event listener
   */
  function resizeListener() {
    window.onresize = function(e) {
      toggleMenuOff();
    };
  }

  /**
   * Turns the custom context menu on.
   */
  function toggleMenuOn() {
    if ( menuState !== 1 ) {
      menuState = 1;
      menu.classList.add( contextMenuActive );
    }
  }

  /**
   * Turns the custom context menu off.
   */
  function toggleMenuOff() {
    if ( menuState !== 0 ) {
      menuState = 0;
      menu.classList.remove( contextMenuActive );
    }
  }

  /**
   * Positions the menu properly.
   *
   * @param {Object} e The event
   */
  function positionMenu(e) {
    clickCoords = getPosition(e);
    clickCoordsX = clickCoords.x;
    clickCoordsY = clickCoords.y;

    menuWidth = menu.offsetWidth + 4;
    menuHeight = menu.offsetHeight + 4;

    windowWidth = window.innerWidth + window.scrollX;
    windowHeight = window.innerHeight + window.scrollY;

    if ( (windowWidth - clickCoordsX) < menuWidth ) {
      menu.style.left = clickCoordsX - menuWidth + "px";
    } else {
      menu.style.left = clickCoordsX + "px";
    }

    if ( (windowHeight - clickCoordsY) < menuHeight ) {
      menu.style.top = clickCoordsY - menuHeight + "px";
    } else {
      menu.style.top = clickCoordsY + "px";
    }
  }

  /**
   * Dummy action function that logs an action when a menu item link is clicked
   *
   * @param {HTMLElement} link The link that was clicked
   */
  function menuItemListener( link ) {
    console.log( "Task ID - " + taskItemInContext.getAttribute("data-id") + ", Task action - " + link.getAttribute("data-action"));
    toggleMenuOff();
  }

  /**
   * Run the app.
   */
  init();

})();