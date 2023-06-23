const draggable = window.Draggable;
function UniqueDropzone() {
    console.debug("Init UniqueDropzone Javascript code ")
    const containers = document.querySelectorAll('#UniqueDropzone .BlockLayout');

    if (containers.length === 0) {
        return false;
    }

    const droppable = new draggable.Droppable(containers, {
        draggable: '.Block--isDraggable',
        dropzone: '.BlockWrapper--isDropzone',
        mirror: {
            constrainDimensions: true,
        },
    });
    console.debug(droppable)
    let droppableOrigin;

    // --- Draggable events --- //
    droppable.on('drag:start', (evt) => {
        console.debug("Drag starting!!")
        droppableOrigin = evt.originalSource.parentNode.dataset.dropzone;
    });

    // TODO: This code can be removed since we are not currently support UniqueDropzone
    // droppable.on('droppable:dropped', (evt) => {
    //     if (droppableOrigin !== evt.dropzone.dataset.dropzone) {
    //         evt.cancel();
    //     }
    // });

    return droppable;
}

UniqueDropzone()
