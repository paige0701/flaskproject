/**
 * Created by Genus on 2016. 10. 14..
 */

$(document).ready(function() {
    //navbar toggle sidebar bootstrap
    var sideslider = $('[data-toggle=collapse-side]');
    var sel = sideslider.attr('data-target');
    var sel2 = sideslider.attr('data-target-2');
    sideslider.click(function(event){
        $(sel).toggleClass('in');
        $(sel2).toggleClass('out');
    });


    //scroll 위치에 따른 ui 변화
    //헤더 변화
    $(window).scroll(function (event) {
        var scroll = $(window).scrollTop();
        if (scroll>20){
            $('#kamper-global-header').addClass('kamper-minimize-header');
            $('#house-search-wrap').addClass('kamper-fixed-search-tab');
        }
        else{
            $('#kamper-global-header').removeClass('kamper-minimize-header');
            $('#house-search-wrap').removeClass('kamper-fixed-search-tab');

        }
    });
    $(".dropdown>a").on("click",function(){
        var dropdown_parent = $(this).parent('.dropdown');
        dropdown_parent.children(".dropdown-content").fadeToggle(250);
        if (dropdown_parent.hasClass('on')){
            console.error("NBB");
            dropdown_parent.removeClass('on');
        }
        else{
            console.error("on 안되어있는상태");
        dropdown_parent.addClass('on');

        }


        return false;
    });


});

