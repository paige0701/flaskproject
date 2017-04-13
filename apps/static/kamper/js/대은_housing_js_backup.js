//
///**
// * Created by Genus on 2016. 10. 23..
// */
//
//    <script type="text/javascript">
//
//        var map, marker, myLatlng, infowindow;
//
//        {#  처음 지도를 부르면 무조건 실행 되는 함수  #}
//        function googleInit(){
//
//            {# 처음 지도가 로딩 할 때 처음 텝이 active 하게 한다 #}
//            $("#one").addClass("active");
//
//
//            {# 현재 보여지는 지도의 좌표(센터) 를 찾는다 #}
//            myLatlng = new google.maps.LatLng({{ hh.addressLat }}, {{ hh.addressLong }});
//            var mapOptions = {
//                zoom: 15,
//                center: myLatlng
//            };
//            {# map 초기화 #}
//            map  = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
//
//            {# event listner 'idle' #}
//
//            google.maps.event.addListener(map, 'idle', function() {
//                {# 현재 보여지고 있는 지도에서 대각선의 좌표를 찾는 작업  #}
//                var bounds = map.getBounds();
//                var sw = bounds.getSouthWest();
//                var ne = bounds.getNorthEast();
//
//                {# var sw_x = sw.lat();#}
//                {# var sw_y = sw.lng();#}
//                {# var ne_x = ne.lat();#}
//                {# var ne_y = ne.lng();#}
//
//                var map_positions = {
//                    'sw_x':sw.lat(),
//                    'sw_y':sw.lng(),
//                    'ne_x':ne.lat(),
//                    'ne_y':ne.lng()
//                };
//                var list = document.getElementById("list");
//                var content="";
//
//                $.ajax({
//
//                    type: "GET",
//                    url: "/api/marker",
//                    data: map_positions,
//                    dataType: 'json',
//                    contentType: 'application/json;charset=UTF-8',
//                    success: function(data) {
//                        // link 추가
//                        var base_detail_link = '/housing/detail/';
//                        for (var i = 0; i < data.result.length; i++) {
//                            var house = data.result[i];
//
//                            var houseLatLng = new google.maps.LatLng(house.latitude, house.longitude);
//
//                            // list추가
//                            if ($(".list-group-item")) {
//                                $(".list-group-item").empty();
//                                var detail_link = base_detail_link + house.id;
//                                content += "<a href='" +detail_link +"'><li class='list-group-item'><h4>" + (data.result[i].name) + "</h4>" + (data.result[i].address)+"번호"+(data.result[i].id)+ "<br/>" + (data.result[i].lowest_price)+ " WON" + "</li></a>";
//                                $("#list").html(content);
//
//                            } else {
//                                var detail_link = base_detail_link + house.id;
//                                content += "<a href='" +detail_link +"'><li class='list-group-item'><h4>" + (data.result[i].name) + "</h4>" + (data.result[i].address)+"번호"+(data.result[i].id)+ "<br/>" + (data.result[i].lowest_price)+ " WON" + "</li></a>";
//                            }
//
//                            // marker 생성
//                            marker = new google.maps.Marker({
//                                position: houseLatLng,
//                                map: map,
//                                title: data.result[i].name
//                            });
//
//                            //지도에 info window 띄우기
//                            infowindow = new google.maps.InfoWindow();
//                            infowindow.setContent(house.lowest_price);
//                            infowindow.open(map, marker);
//                        }
//                    }
//                    ,error:function(error){
//                        alert("error:"+error);}
//                });
//            });
//        }
//
//
//
//        {#  sorting 할 때 불려지는 함수  #}
//        function arrange(num){
//
//            if(num == 1){
//                $("#two").removeClass("active");
//                $("#three").removeClass("active");
//                $("#one").addClass("active");
//            }
//            if(num == 2){
//                $("#one").removeClass("active");
//                $("#three").removeClass("active");
//                $("#two").addClass("active");
//            }
//            if(num == 3){
//                $("#one").removeClass("active");
//                $("#two").removeClass("active");
//                $("#three").addClass("active");
//            }
//
//
//            var content = "";
//
//            var lat = myLatlng.lat();
//            var lng = myLatlng.lng();
//
//            var number = {
//                'num':num,
//                'sw_x':sw_x,
//                'sw_y':sw_y,
//                'ne_x':ne_x,
//                'ne_y':ne_y,
//                'lat':lat,
//                'lng':lng
//
//            }
//
//
//
//
//
//            $.ajax({
//                type: "GET",
//                url: "/api/arrange",
//                data: number,
//                dataType: 'json',
//                contentType: 'application/json;charset=UTF-8',
//                success: function(data) {
//                    var base_detail_link = '/housing/detail/';
//                    for( var i = 0 ; i < data.result.length; i++) {
//                        data.result[i], latLng = new google.maps.LatLng(data.result[i].latitude, data.result[i].longitude);
//                        if ($(".list-group-item")) {
//                            $(".list-group-item").empty();
//                            var detail_link = base_detail_link + data.result[i].id;
//                            {#                            var link_tag = document.createElement('a');#}
//                            {#                            link_tag.href=detail_link;#}
//                            content += "<a href='" +detail_link +"'><li class='list-group-item'><h4>" + (data.result[i].name) + "</h4>" + (data.result[i].address)+"번호"+(data.result[i].id)+ "<br/>" + (data.result[i].lowest_price)+ " WON" + "</li></a>";
//                            $("#list").html(content);
//                        } else {
//                            detail_link = base_detail_link + data.result[i].id;
//                            content += "<a href='" +detail_link +"'><li class='list-group-item'><h4>" + (data.result[i].name) + "</h4>" + (data.result[i].address)+"번호"+(data.result[i].id)+ "<br/>" + (data.result[i].lowest_price)+ " WON" + "</li></a>";
//                            $("#list").html(content);
//
//                        }
//
//
//                        {#----------------------------------------------------------------------------------------------------------#}
//                        {#                        여기서 부터 거리를 구하는 거임    #}
//
//                        {#                        var myLatlng = new google.maps.LatLng({{ hh.addressLat }}, {{ hh.addressLong }});#}
//                        {#                        var newlat = new google.maps.LatLng(data.result[i].latitude, data.result[i].longitude);#}
//                        {#                        var distance =  google.maps.geometry.spherical.computeDistanceBetween(myLatlng,newlat);#}
//                        {##}
//                        {#                        console.log(data.result[i].name);#}
//                        {#                        console.log(distance);#}
//
//                        {#                        # 콘손에 이렇게 거리(차) 가 나옴 실제로 숭실대에서 해피하우스가 제일 가까움#}
//                        {#                        Coco LivingTel#}
//                        {#                        274.2220230925835#}
//                        {#                        #}
//                        {#                        Happy House#}
//                        {#                        58.73221714012201#}
//                        {#                        #}
//                        {#                        Best House#}
//                        {#                        445.9821627072437#}
//
//                        {#----------------------------------------------------------------------------------------------------------#}
//
//
//                    }
//                } ,error:function(error){
//                    alert("error:"+error);}
//            });
//
//        }
//    </script>
