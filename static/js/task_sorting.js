/* <!-- Drag and drop tasks reordering & sort --> */

// Connect tasks backlog area to taks sprint area
$(function() {
    $( "#tasks_backlog_sortable, #tasks_sprint_sortable" ).sortable({
        connectWith: ".connectedSortable"
    }).disableSelection();
} );

// Listen for tasks backlog changes in sorting
$(function () { 
    $('#tasks_backlog_sortable').sortable({ 
        update: function (event, ui) { // on sort order changes
            var sort_order = $(this).sortable('toArray').toString(); // Get array on order of task Ids 
            $.post("/task/reorder/backlog", {"sort_order": sort_order}) // Send task order IDs array to server to reorder each task's task.order
        } 
    }); 
}); 
// Listen for tasks sprint changes in sorting
$(function () { 
    $('#tasks_sprint_sortable').sortable({ 
        update: function (event, ui) { // on sort order changes
            var sort_order = $(this).sortable('toArray').toString(); // Get array on order of task Ids 
            $.post("/task/reorder/sprint", {"sort_order": sort_order}) // Send task order IDs array to server to reorder each task's task.order
        } 
    }); 
}); 
