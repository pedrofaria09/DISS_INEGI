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

    $('a[name=delete_cluster]').on('click', function () {

        if (window.confirm("Do you really want to delete the cluster?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/delete_cluster',
                {
                    id: $(this).attr('data-id'),
                },
                function (data, status) {
                    location.reload();
                });
        }
    })

    $('a[name=delete_equipment]').on('click', function () {

        if (window.confirm("Do you really want to delete the equipment?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/delete_equipment',
                {
                    id: $(this).attr('data-id'),
                },
                function (data, status) {
                    location.reload();
                });
        }
    })

    $('a[name=delete_type]').on('click', function () {

        if (window.confirm("Do you really want to delete this type?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/delete_type',
                {
                    id: $(this).attr('data-id'),
                    typex: $(this).attr('data-type'),
                },
                function (data, status) {
                    location.reload();
                });
        }
    })

    $('a[name=delete_machine]').on('click', function () {

        if (window.confirm("Do you really want to delete the machine?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/delete_machine',
                {
                    id: $(this).attr('data-id'),
                },
                function (data, status) {
                    location.reload();
                });
        }
    })

    $('a[name=delete_conf_period]').on('click', function () {

        if (window.confirm("Do you really want to delete this Period?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/delete_conf_period',
                {
                    id: $(this).attr('data-id'),
                },
                function (data, status) {
                    location.reload();
                });
        }
    })

    $('a[name=delete_calibration]').on('click', function () {

        if (window.confirm("Do you really want to delete this Calibration?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/delete_calibration',
                {
                    id: $(this).attr('data-id'),
                },
                function (data, status) {
                    location.reload();
                });
        }
    })

    $('a[name=delete_associate_tower]').on('click', function () {

        if (window.confirm("Do you really want to delete this Association?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/delete_associate_tower',
                {
                    id: $(this).attr('data-id'),
                },
                function (data, status) {
                    location.reload();
                });
        }
    })

    $('a[name=delete_equipment_config]').on('click', function () {

        if (window.confirm("Do you really want to delete this Equipment Configuration?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/delete_equipment_config',
                {
                    id: $(this).attr('data-id'),
                },
                function (data, status) {
                    location.reload();
                });
        }
    })

    $('a[name=delete_status]').on('click', function () {

        if (window.confirm("Do you really want to delete this Status?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/delete_status',
                {
                    id: $(this).attr('data-id'),
                },
                function (data, status) {
                    location.reload();
                });
        }
    })

    $('a[name=delete_classification_period]').on('click', function () {

        if (window.confirm("Do you really want to delete the Classification Period?")) {
            var csrftoken = getCookie('csrftoken');
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });

            $.post('/delete_classification_period',
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