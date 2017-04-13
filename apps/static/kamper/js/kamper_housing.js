/**
 * Created by Genus on 2016. 10. 22..
 */
//console.warn(lng);
//console.warn(lat);


var map, marker, myLatlng, infowindow;
var initial_latlng;

//{#  처음 지도를 부르면 무조건 실행 되는 함수  #}
function googleInit(){
    //{# 처음 지도가 로딩 할 때 처음 텝이 active 하게 한다 #}
    $("#one").addClass("active");
    var mapOptions = {
        zoom: 15,
        center: myLatlng
    };
    //{# 지도 객체 초기화#}

    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);



}

//{#  처음 지도를 부르면 무조건 실행 되는 함수  #}
function googleInit(){
    //{# 처음 지도가 로딩 할 때 처음 텝이 active 하게 한다 #}
    $("#one").addClass("active");

    var mapOptions = {
        zoom: 15,
        center: myLatlng
    };
    // markers
    var mars = [];




    //{#          현재 보여지는 지도의 좌표(센터) 를 찾는다  #}
    initial_latlng= new google.maps.LatLng(lat, lng);
    console.log(lat);
    console.log(lng);
    console.log(initial_latlng)
    //myLatlng = new google.maps.LatLng({{ hh.addressLat }}, {{ hh.addressLong }});

    map  = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    var m = new  google.maps.event.addListener(map, 'idle', function() {
        // 지도에서 마커 삭제

        for (var i = 0; i < markers.length; i++) {
            markers[i].setMap(null);
        }
        var count = 0;
        count++;


        //{#                if(count > 1){#}
        //    {#                    marker.remove()#}
        //    {#                }#}



        //{#              현재 보여지고 있는 지도에서 대각선의 좌표를 찾는 작업  #}
        var bounds = map.getBounds();
        var sw = bounds.getSouthWest();
        var ne = bounds.getNorthEast();

        //{#                console.log("min sw lat: " + sw.lat());#}
        //{#                console.log(" min sw lon : "+sw.lng());#}
        //{#                console.log("min value of ne : "+ ne.lat());#}
        //{#                console.log("max value of ne : "+ ne.lng());#}

        sw_x = sw.lat();
        sw_y = sw.lng();
        ne_x = ne.lat();
        ne_y = ne.lng();

        var liii = {
            'sw_x':sw_x,
            'sw_y':sw_y,
            'ne_x':ne_x,
            'ne_y':ne_y

        }

        //{#                liii = JSON.stringify(liii);#}
        var list = document.getElementById("list");
        var content="";
        var contentString="";




        $.ajax({

            type: "GET",
            url: "/api/marker",
            data: liii,
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            success: function(data) {

                var base_detail_link = '/housing/detail/';

                for (var i = 0; i < data.result.length; i++) {
                    data.result[i], latLng = new google.maps.LatLng(data.result[i].latitude, data.result[i].longitude);

                    console.log("---------------");
                    var id = data.result[i].id
                    if ($(".list-group-item")) {
                        $(".list-group-item").empty();
                        var detail_link = base_detail_link + data.result[i].id;
                        content += "<a href='" +detail_link +"'><li class='list-group-item'><h4>" + (data.result[i].name) + "</h4>" + (data.result[i].address)+"번호"+(data.result[i].id)+ "<br/>" + (data.result[i].lowest_price)+ " WON" + "</li></a>";


                        $("#list").html(content);
                    } else {
                        var detail_link = base_detail_link + data.result[i].id;
                        content += "<a href='" +detail_link +"'><li class='list-group-item'><h4>" + (data.result[i].name) + "</h4>" + (data.result[i].address)+"번호"+(data.result[i].id)+ "<br/>" + (data.result[i].lowest_price)+ " WON" + "</li></a>";

                    }


                    marker = new google.maps.Marker({
                        position: latLng,
                        map: map,
                        title: data.result[i].name
                    });
                    markers.push(marker);
                    for (var i = 0; i < markers.length; i++) {
                        markers[i].setMap(map);
                    }


                    infowindow = new google.maps.InfoWindow({content: contentString});
                    infowindow.setContent(data.result[i].lowest_price);




                }
                infowindow.open(map, markers);

            }
            ,error:function(error){
                alert("error:"+error);}

        });


    })

};


//{#  sorting 할 때 불려지는 함수  #}
function arrange(num){

    if(num == 1){
        $("#two").removeClass("active");
        $("#three").removeClass("active");
        $("#one").addClass("active");
    }
    if(num == 2){
        $("#one").removeClass("active");
        $("#three").removeClass("active");
        $("#two").addClass("active");
    }
    if(num == 3){
        $("#one").removeClass("active");
        $("#two").removeClass("active");
        $("#three").addClass("active");
    }


    var content = "";

    var lat = myLatlng.lat();
    var lng = myLatlng.lng();

    var number = {
        'num':num,
        'sw_x':sw_x,
        'sw_y':sw_y,
        'ne_x':ne_x,
        'ne_y':ne_y,
        'lat':lat,
        'lng':lng

    }





    $.ajax({
        type: "GET",
        url: "/api/arrange",
        data: number,
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
        success: function(data) {
            var base_detail_link = '/housing/detail/';
            for( var i = 0 ; i < data.result.length; i++) {
                data.result[i], latLng = new google.maps.LatLng(data.result[i].latitude, data.result[i].longitude);
                if ($(".list-group-item")) {
                    $(".list-group-item").empty();
                    var detail_link = base_detail_link + data.result[i].id;
                    //{#                            var link_tag = document.createElement('a');#}
                    //{#                            link_tag.href=detail_link;#}
                    content += "<a href='" +detail_link +"'><li class='list-group-item'><h4>" + (data.result[i].name) + "</h4>" + (data.result[i].address)+"번호"+(data.result[i].id)+ "<br/>" + (data.result[i].lowest_price)+ " WON" + "</li></a>";
                    $("#list").html(content);
                } else {
                    detail_link = base_detail_link + data.result[i].id;
                    content += "<a href='" +detail_link +"'><li class='list-group-item'><h4>" + (data.result[i].name) + "</h4>" + (data.result[i].address)+"번호"+(data.result[i].id)+ "<br/>" + (data.result[i].lowest_price)+ " WON" + "</li></a>";
                    $("#list").html(content);

                }

/*

                {#----------------------------------------------------------------------------------------------------------#}
                {#                        여기서 부터 거리를 구하는 거임    #}

                {#                        var myLatlng = new google.maps.LatLng({{ hh.addressLat }}, {{ hh.addressLong }});#}
                {#                        var newlat = new google.maps.LatLng(data.result[i].latitude, data.result[i].longitude);#}
                {#                        var distance =  google.maps.geometry.spherical.computeDistanceBetween(myLatlng,newlat);#}
                {##}
                {#                        console.log(data.result[i].name);#}
                {#                        console.log(distance);#}

                {#                        # 콘손에 이렇게 거리(차) 가 나옴 실제로 숭실대에서 해피하우스가 제일 가까움#}
                {#                        Coco LivingTel#}
                {#                        274.2220230925835#}
                {#                        #}
                {#                        Happy House#}
                {#                        58.73221714012201#}
                {#                        #}
                {#                        Best House#}
                {#                        445.9821627072437#}

                {#----------------------------------------------------------------------------------------------------------#}

*/

            }
        } ,error:function(error){
            alert("error:"+error);}
    });

}

