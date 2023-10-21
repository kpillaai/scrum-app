/* <!-- Drag and drop tasks reordering & sort --> */

// Connect tasks backlog area to taks sprint area
$(function() {
    $( "#board_TODO_sortable, #board_IN_PROGRESS_sortable, #board_DONE_sortable" ).sortable({
        connectWith: ".boardConnectedSortable"
    }).disableSelection();
} );

// Listen for tasks status TODO changes in sorting
$(function () { 
    $('#board_TODO_sortable').sortable({ 
        update: function (event, ui) { // on sort order changes
            var sort_order = $(this).sortable('toArray').toString(); // Get array on order of task Ids 
            $.post("/task/status/reorder/TODO", {"sort_order": sort_order}) // Send task order IDs array to server to reorder each task's task.status_order
        } 
    }); 
}); 
// Listen for tasks status IN_PROGRESS changes in sorting
$(function () { 
    $('#board_IN_PROGRESS_sortable').sortable({ 
        update: function (event, ui) { // on sort order changes
            var sort_order = $(this).sortable('toArray').toString(); // Get array on order of task Ids 
            $.post("/task/status/reorder/IN_PROGRESS", {"sort_order": sort_order}) // Send task order IDs array to server to reorder each task's task.status_order
        } 
    });
}); 
// Listen for tasks status DONE changes in sorting
$(function () { 
    $('#board_DONE_sortable').sortable({ 
        update: function (event, ui) { // on sort order changes
            var sort_order = $(this).sortable('toArray').toString(); // Get array on order of task Ids 
            $.post("/task/status/reorder/DONE", {"sort_order": sort_order}) // Send task order IDs array to server to reorder each task's task.status_order
        } 
    }); 
}); 
