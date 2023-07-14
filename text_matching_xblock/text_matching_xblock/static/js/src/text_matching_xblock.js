/* Javascript for TextMatchingXBlock. */

function TextMatchingXBlock(runtime, element, data) {
    let xblockId = data.xblock_id;
    let responses = data.responses;
    let learnerChoice = data.learner_choice
    let learnerTempChoice = learnerChoice
    let maxAttempts = data.max_attempts

    // Bind onChange event listener to all select element
    $('.response-wrapper select', element).each(function () {
        $(this).change(function () {
            updateChoice(
                $(this).data("prompt-id"),
                $(this).val(),
            )
        })
    })

    // Bind remove event listener
    $('.matching-item-wrapper .btn-reset-response').each(function () {
        $(this).click(function () {
            const promptId = $(this).data('prompt-id')
            console.debug(`Learner has remove response of prompt: ${promptId}`)
            updateChoice(promptId, null)
        })
    })


    function checkSubmitState() {
        // Enable SUBMIT button when all prompts have responses for the first time
        // or some responses have changed since last submission.
        if (Object.keys(learnerTempChoice).length === Object.keys(responses).length)
            $('.submit', element).prop('disabled', false)
        else $('.submit', element).prop('disabled', true)
    }

    function populateAvailableResponses() {
        // filter available choice
        let selectedResponseIds = [], availableResponses = [];
        for (let promptId in learnerTempChoice)
            selectedResponseIds.push(learnerTempChoice[promptId])

        for (const response of Object.values(responses))
            if (!selectedResponseIds.includes(response.id)) {
                availableResponses.push(response)
            }

        // Populate these available responses to all dropdown options
        $('.response-wrapper select', element).each(function () {
            const promptId = $(this).data('prompt-id')
            if (promptId in learnerTempChoice) {
                $(this).find("option").remove()
                let selectedResponse = responses[learnerTempChoice[promptId]]
                $(this).append(
                    `<option value="${selectedResponse.id}" selected>${selectedResponse.text}</option>`
                )
            } else {
                // Leave the default option as the selected one
                $(this).find("option").remove()
                $(this).append(
                    `<option value="" selected disabled>Select your response</option>`
                )

            }

            for (let response of availableResponses)
                $(this).append(
                    `<option value="${response.id}">${response.text}</option>`
                );
        })
    }

    function updateChoice(promptId, responseId) {
        console.debug("New choice update!")
        console.debug(`Prompt ID: ${promptId}`)
        console.debug(`Response ID: ${responseId}`)
        if (responseId === null)
            delete learnerTempChoice[promptId]
        else
            learnerTempChoice[promptId] = responseId
        populateAvailableResponses()
        checkSubmitState()
    }

    // Get Handler URL from XBlock runtime
    let saveUrl = runtime.handlerUrl(element, 'save_choice')
    let submitUrl = runtime.handlerUrl(element, 'submit');

    function onSubmitSuccess(response) {
        let {result, weight_score_earned, weight_score_possible, attempts_used} = response

        let resultNotificationClassSelector, notificationMessage
        if (result === "correct") {
            resultNotificationClassSelector = "correct-answer"
            notificationMessage = "Correct"
        } else if (result === "incorrect") {
            resultNotificationClassSelector = "incorrect-answer"
            notificationMessage = "Incorrect"
        } else {
            resultNotificationClassSelector = "partially-correct-answer"
            notificationMessage = "Partial Correct"
        }

        resultNotificationClassSelector = `.notification.${resultNotificationClassSelector}`
        notificationMessage = `${notificationMessage} (${weight_score_earned}/${weight_score_possible} points)`
        // Show the result notification color section
        // Make sure all notification element is hidden first,
        // this is useful when learner re-score and the result has changed
        $('.notification', element).addClass("is-hidden")
        $(resultNotificationClassSelector, element).removeClass("is-hidden")

        // Update notification message
        $(`${resultNotificationClassSelector} > .notification-message`, element).text(notificationMessage)

        // Update submission feedback message
        $('.submission-feedback', element).text(`You have used ${attempts_used} of ${maxAttempts} atttempts.`)

        // TODO: Upgrade Progress later

    }

    // Handle learner submit event
    $('.submit', element).click(function (eventObject) {
        $.ajax({
            type: "POST",
            url: saveUrl,
            data: JSON.stringify({
                'learner_choice': learnerTempChoice
            }),
            success: function () {
                $.ajax({
                    type: "POST",
                    url: submitUrl,
                    data: JSON.stringify({}),
                    success: onSubmitSuccess
                });
            }
        });
    });

    $(function ($) {
        // Add this class to parent class of Xblock to achieve CSS from OpenEdx Platform
        $('.problems-wrapper', element).parent().addClass('xmodule_display xmodule_ProblemBlock')

        populateAvailableResponses()
        checkSubmitState()
    })
}
