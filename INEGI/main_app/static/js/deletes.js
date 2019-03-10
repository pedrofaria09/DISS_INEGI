$(function () {

    $('a[name=delete_tower]').on('click', function () {

        if (window.confirm("Do you really want to delete the tower?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/delete_tower',
                {
                    id: $(this).attr('data-id'),
                },
                function (data, status) {
                    location.reload();
                });
        }
    })

    $('a[name=delete_user]').on('click', function () {

        if (window.confirm("Do you really want to delete the user?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/delete_user',
                {
                    id: $(this).attr('data-id'),
                },
                function (data, status) {
                    location.reload();
                });
        }
    })

    $('a[name=ban_user]').on('click', function () {

        if (window.confirm("Do you really want to ban/activate the user?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/ban_user',
                {
                    id: $(this).attr('data-id'),
                },
                function (data, status) {
                    location.reload();
                });
        }
    })

});


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
        }
    return cookieValue;
}