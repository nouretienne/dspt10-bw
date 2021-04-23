$(document).ready(function(){
        if(sessionStorage.getItem('last_song_entry')){
            $("#song_name").val(sessionStorage.getItem('last_song_entry'));
        }

        if(sessionStorage.getItem('last_artist_sel')){
            $('#artists_option').val(sessionStorage.getItem('last_artist_sel'));
        }

        $("#song_name").on("change",function(){
            sessionStorage.setItem('last_song_entry',$(this).val());
        });

        $('#artists_option').on('change', function(){
            sessionStorage.setItem('last_artist_sel',$(this).val());
        })
    });