$(document).ready(function () {
    console.log("Databases")

    $(function () {
        var button = $('#dropdb_mongo');
        button.click(function () {
            $.ajax({
                url: "/dropdb_mongo",
                // data: {},
                success: function (data) {
                    console.log(data.size);
                }
            });
        });
    });

    $(function () {
        var button = $('#count_mongo');
        button.click(function () {
            $.ajax({
                url: "/count_mongo",
                // data: {},
                success: function (data) {
                    console.log(data.size);
                    console.log(data.time , ' seconds');
                }
            });
        });
    });

    $(function () {
        var button = $('#dropdb_influx');
        button.click(function () {
            $.ajax({
                url: "/dropdb_influx",
                // data: {},
                success: function (data) {
                    console.log(data.message);
                }
            });
        });
    });

    $(function () {
        var button = $('#count_influx');
        button.click(function () {
            $.ajax({
                url: "/count_influx",
                // data: {},
                success: function (data) {
                    console.log(data.size);
                    console.log(data.time , ' seconds');
                }
            });
        });
    });


    $(function () {
        var button = $('#dropdb_pg');
        button.click(function () {
            $.ajax({
                url: "/dropdb_pg",
                // data: {},
                success: function (data) {
                    console.log(data.size);
                }
            });
        });
    });

    $(function () {
        var button = $('#count_pg');
        button.click(function () {
            $.ajax({
                url: "/count_pg",
                // data: {},
                success: function (data) {
                    console.log(data.size);
                    console.log(data.time , ' seconds');
                }
            });
        });
    });

});