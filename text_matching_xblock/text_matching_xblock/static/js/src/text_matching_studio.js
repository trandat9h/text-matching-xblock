function TextMatchingStudioXBlock(runtime, element, data) {
    let {settings} = data
    console.debug(settings)

    // Bind onChange event listener to setting with 'string' data type
    $('.field-data-control', element).each(function () {
        $(this).change(function () {
            const $wrapper = $(this).closest('li')
            const fieldType = $wrapper.data('cast')
            const fieldName = $wrapper.data('field-name')

            const fieldValue = $(this).val()
            if (fieldType === "string")
                settings[fieldName] = fieldValue
            else if (fieldType === "integer")
                settings[fieldName] = parseInt(fieldValue)
            else if (fieldType === "custom") {
                // Do nothing, this type will have its own handler
            } else {
                console.debug(`ERROR on parsing value ${fieldValue} of type ${fieldType} for field ${fieldValue}`)
            }

            console.debug(`Setting: ${fieldName} has new value: ${fieldValue}`)

            // TODO: Implement check any field has changed to enable/disable submit button
        })
    })


    // Handle prompt or response input change event handler
    function onMatchingItemChange() {
        const subfieldName = $(this).data('subfield-name')
        const $wrapper = $(this).closest('li')
        const itemIndex = $wrapper.index()

        settings.matching_items[itemIndex][subfieldName] = $(this).val()
    }

    $('.matching-item-row input.field-data-control', element).each(function () {
        $(this).change(onMatchingItemChange)
    })

    // Bind remove event handler to all 'remove' button of each item
    function removeMatchingItem(index) {
        const $wrapper = $(this).closest('li')
        const itemIndex = $wrapper.index()
        console.debug(settings)
        settings.matching_items.splice(itemIndex, 1)
        $wrapper.remove()
    }

    $('.btn-remove-item', element).each(function () {
        $(this).click(removeMatchingItem)
    })

    function onSubmitSuccess(response) {
        // TODO: Update savedSetting and disable submit button
    }

    // Studio submit event handler
    let studioSubmitUrl = runtime.handlerUrl(element, 'studio_submit');
    let getMatchingItemBlankTemplateUrl = runtime.handlerUrl(element, 'get_matching_item_template')
    $('.save-button', element).click(function (eventObject) {
        $.ajax({
            type: "POST",
            url: studioSubmitUrl,
            data: JSON.stringify(settings),
            success: onSubmitSuccess
        });
    });

    // Handle add new item event
    $('.btn-add-matching-item', element).click(function (eventObject) {
        console.debug("Learner has added new matching item")
        let _template = ''
        $.ajax({
            type: "POST",
            url: getMatchingItemBlankTemplateUrl,
            data: JSON.stringify({}),
            success: function (response) {
                _template = response.template
                settings.matching_items.push(
                    {
                        prompt: '',
                        response: '',
                    }
                )

                // Add new item element and assign remove event listener for this item

                $('.matching-items-wrapper', element).append(_template)

                const $matchingItem = $('.matching-item-row', element).last()
                $matchingItem.find('.btn-remove-item').click(removeMatchingItem)

                $matchingItem.find('input.field-data-control').each(function () {
                    $(this).change(onMatchingItemChange)
                })


            }
        })
    });


}
