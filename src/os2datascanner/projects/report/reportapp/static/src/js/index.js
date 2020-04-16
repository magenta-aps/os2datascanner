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
  $(this).toggleClass("is-active");
  $(this).siblings(tooltip).toggleClass("show");
})

function openMatchHandler() {
  $(tooltip).addClass("show");
}

function closeMatchHandler() {
  $(tooltip).removeClass("show");
}
// Handle matches, stop
