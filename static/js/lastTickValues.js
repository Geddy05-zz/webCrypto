/**
 * Created by geddy on 25/11/2016.
 */

function do_request(){
    element = document.getElementById("title")
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

    var change = (first /last ) * 100;
    if (change > 100){
        change = 100 - change;
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
            sentim = parseInt(tick.sentiment)
        }

        a.push({"date": tick.date,
                  "Twitter": tick.score,
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
                  "labelFrequency":2,
                  "minPeriod": "hh:mm",
                  "gridThickness": 0

              },
              "chartCursor": {
                "enabled": true,
                "categoryBalloonDateFormat": "JJ:NN"
              },
              "trendLines": [],
              "graphs": [
                {
                  "fillAlphas": 1,
                  "fillColors": "#90C695",
                  "id": "AmGraph-1",
                  "lineAlpha": 0,
                  "tabIndex": 0,
                  "title": "Reddit",
                  "valueField": "Reddit"
                },
                {
                  "fillAlphas": 1,
                  "fillColors": "#87D37C",
                  "id": "AmGraph-2",
                  "lineAlpha": 0,
                  "title": "Twitter",
                  "valueField": "Twitter"
                },
                {
                  "fillAlphas": 1,
                  "fillColors": "#C8F7C5",
                  "id": "AmGraph-3",
                  "lineThickness": 0,
                  "lineColor": "#C8F7C5",
                  "title": "News",
                  "valueField": "News"
                }
              ],
              "guides": [],
              "valueAxes": [
                {
                  "id": "ValueAxis-1",
                  "gridThickness": 0,
                  "stackType": "regular",
                  "tickLength": 0,
                  "title": ""
                }
              ],
              "allLabels": [],
              "balloon": {},
              "legend": {
                "enabled": true
              },
              "titles": [
                {
                  "id": "Title-1",
                  "size": 15,
                  "text": ""
                }
              ],
              "dataProvider":a
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
sentiment();
twitter();
