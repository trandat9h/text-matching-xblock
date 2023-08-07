/* Javascript for TextMatchingXBlock. */

function TextMatchingXBlock(runtime, element, data) {
    let xblockId = data.xblock_id
    let responses = data.responses
    let learnerChoice = data.learner_choice
    let latestSubmittedChoice = data.latest_submitted_choice
    let learnerTempChoice = JSON.parse(JSON.stringify(learnerChoice))
    let maxAttempts = data.max_attempts
    let attemptsUsed = data.attempts_used
    let isGraded = data.is_graded
    let hasSubmittedAnswer = data.has_submitted_answer
    let weightScoreEarned = data.weight_score_earned
    let weightScorePossible = data.weight_score_possible

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
        // MUST-HAVE conditions for SUBMIT button to be enabled:
        // - Current attempt must have all prompts fulfilled
        // - Learner must have available retry (if max_retry is limited)


        // Only enable SUBMIT button in the following scenarios:
        // - Scenario 1
        //   + Learner has submitted once
        //   + New attempt if fulfilled AND different from the latest submission
        // - Scenario 2
        //   + Learner has NOT submitted anytime
        //   + New attempt is fulfilled


        let isEnabled = false
        const isAttemptFulfilled = (Object.keys(learnerTempChoice).length === Object.keys(responses).length)
        const canRetry = (maxAttempts === -1 || (attemptsUsed < maxAttempts))

        if (isAttemptFulfilled === true && canRetry === true) {
            if (hasSubmittedAnswer === true) {
                if (!isObjectsEqual(learnerTempChoice, latestSubmittedChoice))
                    isEnabled = true
            } else {
                isEnabled = true
            }
        }

        $('.submit', element).prop('disabled', !isEnabled)

        console.debug("Start check submit state!")
        console.debug(learnerTempChoice)

        console.debug(`is Equal: ${isEnabled}`)
    }

    function isObjectsEqual(obj1, obj2) {
        let isObjEqual = false;
        const obj1Keys = Object.keys(obj1).sort();
        const obj2Keys = Object.keys(obj2).sort();
        if (obj1Keys.length === obj2Keys.length) {
            const areEqual = obj1Keys.every((key, index) => {
                const objValue1 = obj1[key];
                const objValue2 = obj2[obj2Keys[index]];
                return objValue1 === objValue2;
            });
            if (areEqual) {
                isObjEqual = true;
            }
        }

        return isObjEqual
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
        $('.response-wrapper select.response-options', element).each(function () {
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

        hideAnswer()
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

    function getProgressMessage(_isGraded, _hasSubmittedAnswer, earned, possible) {
        let _progressMsg, _isGradedMsg
        if (_hasSubmittedAnswer === false)
            _progressMsg = `${possible} points possible`
        else
            _progressMsg = `${earned}/${possible} point`

        _isGradedMsg = _isGraded ? "(graded)" : "(ungraded)"

        return `${_progressMsg} ${_isGradedMsg}`
    }

    // Get Handler URL from XBlock runtime
    let saveUrl = runtime.handlerUrl(element, 'save_choice')
    let submitUrl = runtime.handlerUrl(element, 'submit');
    let showAnswerUrl = runtime.handlerUrl(element, 'show_answer')

    function onSubmitSuccess(response) {
        attemptsUsed++;
        let {result, weight_score_earned, weight_score_possible} = response

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
        if (maxAttempts !== -1)
            $('.submission-feedback', element).text(`You have used ${attemptsUsed} of ${maxAttempts} attempts.`)

        // Update progress message
        $('.problem-progress', element).text(
            getProgressMessage(
                isGraded,
                true,
                weight_score_earned,
                weight_score_possible,
            ))

        // Revert Submitting text message to Submit for next submission (if any)
        $('button.submit', element).find('span.submit-label').text('Submit')

        // Update temp choice and recheck Submit button status (in this case Submit button should always be disabled
        hasSubmittedAnswer = true
        latestSubmittedChoice = JSON.parse(JSON.stringify(learnerTempChoice))
        learnerChoice = JSON.parse(JSON.stringify(learnerTempChoice))
        checkSubmitState()
    }

    function onSaveSuccess(response) {
        learnerChoice = JSON.parse(JSON.stringify(learnerTempChoice))
        checkSubmitState()
    }

    // Handle Submit event
    $('button.submit', element).click(function (eventObject) {
        $(this).find('span.submit-label').text('Submitting')
        $(this).prop('disabled', true)
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

    // Handle Save event
    $('button.btn-save', element).click(function (eventObject) {
        $.ajax({
            type: "POST",
            url: saveUrl,
            data: JSON.stringify({
                'learner_choice': learnerTempChoice
            }),
            success: function () {
                $.ajax({
                    type: "POST",
                    url: saveUrl,
                    data: JSON.stringify({}),
                    success: onSaveSuccess
                });
            }
        })
    })

    // Handle remove all responses
    $('button.btn-reset', element).click(function(eventObject) {
        $('.matching-item-wrapper .btn-reset-response').each(function () {
            const promptId = $(this).data('prompt-id')
            if (learnerTempChoice[promptId] !== null)
                updateChoice(promptId, null)
            }
        )
    })

    function showAnswer(answer) {
        showAttemptCorrectness(answer)
        showCorrectAnswer(answer)
    }

    function showAttemptCorrectness(answer) {
        // Show learner attempt result by coloring green/red for correct/incorrect response
        $('.MatchingZone .matching-item-wrapper', element).each(function () {
            let isCorrect = false
            let promptId = $(this).data('prompt-id')
            let $response = $(this).find('.response-options')
            let responseId = $response.val()
            if (responseId === null)
                return

            if (answer[promptId] === responseId)
                isCorrect = true

            let resultCSSSelector = isCorrect === true ? "choice_correct" : "choice_incorrect"
            $response.addClass(resultCSSSelector)
        })
    }

    function showCorrectAnswer(answer) {
        // Show the correct response for each prompt
        $('.MatchingZone .matching-item-wrapper', element).each(function () {
            const promptId = $(this).data('prompt-id')
            const $answer = $(this).find('.answer-wrapper')
            $answer.append(`<p>${responses[answer[promptId]].text}</p>`)
        })
    }


    function hideAnswer() {
        $('.MatchingZone .matching-item-wrapper', element).each(function () {
            let promptId = $(this).data('prompt-id')
            let $response = $(this).find('.response-options')
            // Remove answer color (if learner has shown answer before)
            $response.removeClass('choice_correct choice_incorrect')

            $(this).find('.answer-wrapper').empty()
        })
    }

    $('.btn-show-answer', element).click(function () {
        $.ajax({
            type: "POST",
            url: showAnswerUrl,
            data: JSON.stringify({}),
            success: function (response) {
                showAnswer(response["answer"])
            },
        });
    })

    $(function ($) {
        // Add this class to parent class of Xblock to achieve CSS from OpenEdx Platform
        $('.problems-wrapper', element).parent().addClass('xmodule_display xmodule_ProblemBlock')

        // Update progress message
        $('.problem-progress', element).text(
            getProgressMessage(
                isGraded,
                hasSubmittedAnswer,
                weightScoreEarned,
                weightScorePossible,
            ))

        checkSubmitState()
        populateAvailableResponses()
    })
}
