import '../css/master.scss';

// Copy Path function
new ClipboardJS(document.querySelectorAll('[data-clipboard-text]'));

// Handle matches, start
const button = $('.handle-match-button');
const buttonWidth = button.outerWidth(false);
const tooltip = $('.handle-match');

var offsetTop = 10

$(tooltip).css({
  marginTop: offsetTop,
  marginLeft: -buttonWidth/2
});

$(button).click(function() {
  console.log("click!");

  $(this).toggleClass("is-active");
  $(this).siblings(tooltip).toggleClass("show");
})

function openMatchHandler() {
  console.log("openMatchHandler");
  $(tooltip).addClass("show");
}

function closeMatchHandler() {
  console.log("closeMatchHandler");
  $(tooltip).removeClass("show");
}
// Handle matches, stop
