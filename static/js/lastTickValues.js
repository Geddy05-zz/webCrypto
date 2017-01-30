/**
 * Created by geddy on 25/11/2016.
 */

function do_request(){
    element = document.getElementById("title");
    var text = element.innerText || element.textContent;
element.innerHTML = text;
    $.ajax({
        type: 'GET',
        url: '/get_last_tick_data',
        data: { "title": text},
        dataType: 'json',
        success: function (data) {
            updateScore(data);
            draw_live_ticks(data)
        }
    });
}

function twitter(){
    element = document.getElementById("title")
    var text = element.innerText || element.textContent;
           $.ajax({
        type: 'GET',
        url: '/twitter',
               data: { "coin": text},
        dataType: 'json',
        success: function (data) {
            // for (var x in data) {
            draw_live_twitter(data);
            // }
        }
    });
}

function ta(){
    element = document.getElementById("title")
    var text = element.innerText || element.textContent;
           $.ajax({
        type: 'GET',
        url: '/ta',
               data: { "coin": text},
        dataType: 'json',
        success: function (data) {
            // for (var x in data) {
            setArrow(data);
            // }
        }
       });
}

function setArrow(data){
    console.log(data);

    var up = document.getElementById("Layer_1");
    var down = document.getElementById("Layer_2");
    if (data){
        up.style.visibility = "visible" ;
        down.style.visibility = "hidden";
    }else{
        up.style.visibility = "hidden" ;
        down.style.visibility = "visible";
    }
}

function sentiment(){
    element = document.getElementById("title")
    var text = element.innerText || element.textContent;
           $.ajax({
        type: 'GET',
        url: '/sentiment',
               data: { "coin": text},
        dataType: 'json',
        success: function (data) {
            // for (var x in data) {
            draw_sentiment(data);
            // }
        }
    });
}

function updateScore(data) {
    var last = parseInt(data[data.length - 1].price_usd);
    var first = parseInt(data[0].price_usd);

    var change = (last /first ) * 100;
    if (change > 100){
        change = change - 100;
    }
    element = document.getElementById("score");
    element.innerHTML = change.toFixed(2)
}

function draw_sentiment(data){
           var a = [];

    for (var i = 0, len = data.length; i < len; i++) {
        var tick = data[i];
        var color = "red";

        if(tick.pos == "p"){
            color = "green"
        }

        a.push({"category": tick.event,
                "column-1": tick.percentage,
                "color": color});
    }

    AmCharts.makeChart("chart4div",
				{
					"type": "serial",
					"categoryField": "category",
                    	"rotate": true,
                    "color": "#FFFFFF",
					"startDuration": 1,
					"categoryAxis": {
						"gridPosition": "start",
                        "gridThickness": 0,
                        "axisColor": "#FFFFFF",
                        "axisAlpha": 0.5,
					},
						"trendLines": [
                            {
                                "balloonText": "",
                                "dashLength": 3,
                                "finalCategory": "Price Increase",
                                "finalValue": 11,
                                "id": "TrendLine-1",
                                "initialCategory": "Banned From Country",
                                "initialValue": 11,
                                "lineAlpha": 0.72,
                                "lineColor": "#FFFFFF",
                                "lineThickness": 2
                            }
                        ],
					"graphs": [
						{
							"colorField": "color",
							"fillAlphas": 1,
							"id": "AmGraph-1",
							"lineColorField": "#FFFFFF",
							"title": "graph 1",
							"type": "column",
							"valueField": "column-1",
                            "lineThickness": 0,
						}
					],
					"guides": [],
					"valueAxes": [
                        {
                          "id": "ValueAxis-1",
                          "stackType": "regular",
                          "tickLength": 0,
                          "title": "",
                          "gridThickness": 0,
                            "axisColor": "#FFFFFF",
                            "axisAlpha": 0.5,
                        }
                      ],
					"allLabels": [],
					"balloon": {},
					"titles": [
						{
							"id": "Title-1",
							"size": 15,
							"text": ""
						}
					],
					"dataProvider": a
				}
    );
}

function draw_live_twitter(data) {

        var a = [];

    for (var i = 0, len = data.length; i < len; i++) {
        var tick = data[i];
        var sentim = null;
        if(tick.sentiment != "NA"){
            sentim = tick.sentiment
        }

        a.push({"date": tick.date,
                  "Activity": tick.score,
                    "Sentiment": sentim })
    }
    console.log(a);
     AmCharts.makeChart("chart3div",
            {
              "type": "serial",
              "categoryField": "date",
              "dataDateFormat": "YYYY-MM-DD HH",
              "color": "#FFFFFF",
              "theme": "dark",
              "categoryAxis": {
                "labelFrequency":3,
                    "minPeriod": "hh:mm",
                    //"parseDates": true,
                    "gridThickness": 0

              },
              "chartCursor": {
                "enabled": true,
                "categoryBalloonDateFormat": "JJ:NN"
              },
              "trendLines": [],
              "graphs": [

                {
                  "fillAlphas": 0.0,
                  "fillColors": "#FFFFFF",
                  "gapPeriod": 0,
                  "id": "AmGraph-4",
                  "lineColor": "#C8F7C5",
                  "lineAlpha": 1,
                  "lineThickness": 5,
                  "title": "Activity",
                  "valueField": "Activity",
                    "valueAxis": "ValueAxis-1",
                },
                {
                  "fillAlphas": 0.0,
                  "fillColors": "#FFFFFF",
                  "gapPeriod": 0,
                  "id": "AmGraph-4",
                  "lineColor": "#87D37C",
                  "lineAlpha": 1,
                  "lineThickness": 5,
                  "title": "Sentiment",
                  "valueField": "Sentiment",
                    "valueAxis": "ValueAxis-2",
                }

              ],
              "guides": [],
              "valueAxes": [
                {
                  "id": "ValueAxis-1",
                  "stackType": "regular",
                  "tickLength": 0,
                  "title": "",
                  "gridThickness": 0,
                },
                {
                  "id": "ValueAxis-2",
                  "stackType": "regular",
                  "tickLength": 0,
                  "title": "",
                    "position": "right",
                  "gridThickness": 1,
                }
              ],
              "allLabels": [],
              "balloon": {},
              "legend": {
                "enabled": false
              },
              "titles": [
                {
                  "id": "Title-1",
                  "size": 15,
                  "text": ""
                }
              ],
              "dataProvider": a
            }
          );
}

function draw_live_ticks(data) {
    var a = [];

    for (var i = 0, len = data.length; i < len; i++) {
        var tick = data[i];
        a.push({"date": tick.last_updated,
                  "Price": tick.price_usd})
    }

    AmCharts.makeChart("chart2div",
            {
              "type": "serial",
              "categoryField": "date",
              "dataDateFormat": "YYYY-MM-DD HH",
              "color": "#FFFFFF",
              "theme": "dark",
              "categoryAxis": {
                  "labelFrequency":3,
                    "minPeriod": "hh:mm",
                    //"parseDates": true,
                    "gridThickness": 0

              },
              "chartCursor": {
                "enabled": true,
                "categoryBalloonDateFormat": "JJ:NN"
              },
              "trendLines": [],
              "graphs": [

                {
                  "fillAlphas": 0.0,
                  "fillColors": "#FFFFFF",
                  "gapPeriod": 0,
                  "id": "AmGraph-4",
                  "lineColor": "#C8F7C5",
                  "lineAlpha": 1,
                  "lineThickness": 5,
                  "title": "Price",
                  "valueField": "Price"
                }
              ],
              "guides": [],
              "valueAxes": [
                {
                  "id": "ValueAxis-1",
                  "stackType": "none",
                  "tickLength": 0.1,
                  "title": "",
                  "gridThickness": 0
                }
              ],
              "allLabels": [],
              "balloon": {},
              "legend": {
                "enabled": false
              },
              "titles": [
                {
                  "id": "Title-1",
                  "size": 15,
                  "text": ""
                }
              ],
              "dataProvider": a
            }
          );
}
do_request();
ta();
// sentiment();
twitter();
