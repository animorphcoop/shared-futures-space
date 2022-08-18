"use strict";
getWeather();
// Find info
function getWeather() {
    fetch('http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/350347?res=3hourly&key=1e0c30fb-cec9-497a-a29b-66b9f5a537a2').then(function (response) {
        return response.json();
    }).then(function (data) {
        console.log(data);
        console.log(typeof data);
        console.log(Object.keys(data));
        var keys = [];
        for (var key in data) {
            if (data.hasOwnProperty(key)) {
                keys.push(key);
            }
        }
        console.log(Object.values(data[keys[0]]));
        var locationData = Object.values(data[keys[0]]);
        console.log(typeof locationData);
        var dataEntries = [];
        locationData.forEach(function (entry) {
            dataEntries.push(entry);
        });
        var specificData = dataEntries[1];
        /*   specificData.forEach(item => {
             console.log(item)
         })
         */
        console.log(typeof specificData);
        var forecast = [];
        for (var _i = 0, _a = Object.entries(specificData); _i < _a.length; _i++) {
            var _b = _a[_i], key = _b[0], value = _b[1];
            //console.log(key, value);
            if (key.includes("Location")) {
                forecast.push(value);
            }
        }
        console.log(forecast);
        var forecastEntries = [];
        for (var _c = 0, _d = Object.entries(forecast); _c < _d.length; _c++) {
            var _e = _d[_c], key = _e[0], value = _e[1];
            //console.log(value);
            forecastEntries.push(value);
        }
        console.log(forecastEntries[0]);
        var forecastPeriods = [];
        for (var _f = 0, _g = Object.entries(forecastEntries[0]); _f < _g.length; _f++) {
            var _h = _g[_f], key = _h[0], value = _h[1];
            //console.log(key, value);
            if (key.includes("Period")) {
                forecastPeriods.push(value);
            }
        }
        var firstDayForecast = [];
        for (var _j = 0, _k = Object.entries(forecastPeriods[0]); _j < _k.length; _j++) {
            var _l = _k[_j], key = _l[0], value = _l[1];
            if (key.includes("0")) {
                firstDayForecast.push(value);
            }
        }
        console.log(firstDayForecast);
        var firstDayForecastSets = [];
        for (var _m = 0, _o = Object.entries(firstDayForecast[0]); _m < _o.length; _m++) {
            var _p = _o[_m], key = _p[0], value = _p[1];
            //console.log(key, value);
            if (key.includes("Rep")) {
                firstDayForecastSets.push(value);
            }
        }
        console.log(firstDayForecastSets[0]);
        var firstSetForecast = [];
        for (var _q = 0, _r = Object.entries(firstDayForecastSets[0]); _q < _r.length; _q++) {
            var _s = _r[_q], key = _s[0], value = _s[1];
            console.log(key, value);
            if (key.includes("0")) {
                firstSetForecast.push(value);
            }
        }
        console.log(firstSetForecast[0]);
        var weatherType = '';
        var temperature = '';
        for (var _t = 0, _u = Object.entries(firstSetForecast[0]); _t < _u.length; _t++) {
            var _v = _u[_t], key = _v[0], value = _v[1];
            //console.log(key, value);
            if (key.includes("W")) {
                weatherType = value;
            }
            else if (key.includes("T")) {
                temperature = value;
            }
        }
        console.log("weather type is ".concat(weatherType));
        console.log("temperature is ".concat(temperature));
        // go figure https://hub.animorph.coop/f/243136
    });
}
