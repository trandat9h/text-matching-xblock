/* Javascript for TextMatchingXBlock. */

function TextMatchingXBlock(runtime, element, data) {
    function updateCount(result) {
        $('.count', element).text(result.count);
    }

    // Get Handler URL from XBlock runtime
    let matchOptionUrl = runtime.handlerUrl(element, 'match_option');
    let swapOptionsUrl = runtime.handlerUrl(element, 'swap_options');
    let submitUrl = runtime.handlerUrl(element, 'submit');

    // Assign event handler
    // $('p', element).click(function(eventObject) {
    //     $.ajax({
    //         type: "POST",
    //         url: handlerUrl,
    //         data: JSON.stringify({"hello": "world"}),
    //         success: updateCount
    //     });
    // });

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });

    function swapOptions(first_option_id, second_option_id) {

    }


    function matchOption(answerId, optionId) {

        function onUpdateChoiceSuccess(result) {

        }

        function onUpdateChoiceFailed(result) {

        }

        $.ajax({
            type: "POST",
            url: matchOptionUrl,
            data: JSON.stringify({
                "option_id": optionId,
                "answer_id": answerId
            }),
            success: onUpdateChoiceSuccess
        });
    }

    function swapOptions(first_option_id, second_option_id) {
        function onSwapOptionsSuccess() {

        }

        $.ajax({
            type: "POST",
            url: swapOptionsUrl,
            data: JSON.stringify({
                "first_option_id": first_option_id,
                "second_option_id": second_option_id,
            }),
            success: onSwapOptionsSuccess
        });
    }

    function UniqueDropzone() {
        let draggable = window.Draggable;
        console.debug("Init UniqueDropzone Javascript code ")
        let xblock_id = data.xblock_id
        console.debug(xblock_id)
        let containers = document.querySelectorAll(`#${xblock_id} .BlockLayout`);

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

        let originZoneId, originZoneType, targetZoneId, targetZoneType;

        // --- Drag start events --- //
        droppable.on('drag:start', (evt) => {
            console.debug("Drag starting!!")

            let origin = evt.originalSource.parentNode.dataset
            originZoneId = origin.dropzoneId;
            originZoneType = origin.dropzoneType;

        });

        // --- Drop stopped events --- //
        droppable.on('droppable:dropped', (evt) => {
            let targetDropzone = evt.dropzone.dataset;

            targetZoneId = targetDropzone.dropzoneId;
            targetZoneType = targetDropzone.dropzoneType;
            console.debug(targetZoneId)

            // TODO: Do some validation here

            // Handle student choice
            if (originZoneType === "Answer" && targetZoneType === "Option") {
                // Student remove current option
                console.debug("Student remove current option")
                matchOption(originZoneId, null)
            } else if (originZoneType === "Option" && targetZoneType === "Answer") {
                console.debug("Student select an option")
                matchOption(targetZoneId, originZoneId)
            } else if (originZoneType === "Answer" && targetZoneType == "Answer") {
                // Student try to match the option to another answer
                // TODO: Find a way to handle this atomically, for now just cancel this type of event
                console.debug("Student move the option to another answer.")
                swapOptions(originZoneId, targetZoneId)
            } else {
                console.error("Not implement this combination.")
            }
        });

        return droppable;
    }

    UniqueDropzone()
}
