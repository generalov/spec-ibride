import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.js';
import './css/main.css';

$('#myModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var imgsrc = button.data('imgsrc');
    var modal = $(this);
    modal.find('.modal-body img').attr({src: imgsrc.replace('s.', 'w.')});
});
