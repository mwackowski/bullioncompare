// popovers initialization - on hover
$('[data-toggle="popover-hover"]').popover({
    html: true,
    trigger: 'hover',
    // placement: 'top',
    content: function () { return '<img src="' + $(this).data('img') + '" width="200" />'; }
  });
  
  // popovers initialization - on click
  $('[data-toggle="popover-click"]').popover({
    html: true,
    trigger: 'click',
    // placement: 'top',
    content: function () { return '<img src="' + $(this).data('img') + '" />'; }
  });