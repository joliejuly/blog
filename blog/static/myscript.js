$(document).ready(function(){
  
  $('.test1.modal')
  .modal('attach events', '.test.button', 'show');

  setTimeout(function(){
    $('.message')
      .transition('slide down');  
  }, 1000);

  $('.ui.accordion')
    .accordion()
  ;
  
  $('.menu .item')
  .tab()
;
  
  $('.shiba_image')
  .transition('jiggle');
    
  $('.ui.dropdown')
  .dropdown()
;
});
