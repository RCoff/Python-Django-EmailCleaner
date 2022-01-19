let dontShowMarkReadModal = false

function highlightRow(element) {
    let tableRow = document.getElementById(element.getAttribute('data-id'))
    if (element.checked) {
        tableRow.classList.add('table-primary')
    } else {
        tableRow.classList.remove('table-primary')
    }
}


function checkAllCheckboxes(element) {
    let tableRows = document.getElementById(element.getAttribute('data-id')).rows
    for (let row of tableRows) {
        let inputCheck = row.getElementsByTagName('input')[0]
        inputCheck.checked = element.checked
        highlightRow(inputCheck)
    }
}


function callModalOrMarkAsRead(button) {
    if (!dontShowMarkReadModal) {
        let markAsReadModal = document.getElementById('mark-read-modal')
        let modal = new bootstrap.Modal(markAsReadModal)
        let id = button.getAttribute('data-id')
        let sender = button.getAttribute('data-sender')
        let unread = button.getAttribute('data-unread')
        let modalText = markAsReadModal.querySelector('#mark-as-read-text')
        document.getElementById('mark-read-modal-confirm-btn').setAttribute('data-id', id)
        modalText.innerHTML = 'Mark <b>' + unread + '</b> emails from <b>' + sender + '</b> as read?'
        modal.show()
    } else {
        markAsRead(button.getAttribute('data-id'))
    }
}


function markAsRead(dataId) {
    // call the api and mark the email as read
    console.log('markAsRead called')
    let row = document.getElementById(dataId)
    // use fetch to call the api endpoint
    // while waiting for a response,
    //  change the 'mark as read' icon to a spinner
    //  if successful, fade the row out and show a 'success' toast message
    //  if unsuccessful, show a 'failure' toast message
    removeRow(dataId)
}


function removeRow(rowId) {
    document.getElementById(rowId).remove()
}
