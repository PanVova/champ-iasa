function validateSearchForm() {
    const query = document.querySelector('#input-query').value;
    const duration = document.querySelector('#input-duration').value;
    const alertSearch = document.querySelector('#alert-search');

    if (!query) {
        alertSearch.classList.remove('d-none');
        return false;
    }

    alertSearch.classList.add('d-none');
    window.location.href = '/search?q=' + encodeURIComponent(query) + '&duration=' + encodeURIComponent(duration);
    return false;
}