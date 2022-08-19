"use strict";
//getWeather()
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
/*document.getElementById('dash-weather').innerHTML = 'lol'

const weather = await parseData()

console.log(weather)*/
function retireveData() {
    apiService('https://api.openweathermap.org/data/2.5/weather?q=London,GB&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef').then(function (data) {
        if (data) {
            console.log("result is ".concat(data));
            return data;
        }
        else {
            console.log('no luck');
        }
    });
    return apiService('https://api.openweathermap.org/data/2.5/weather?q=London,GB&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef');
}
function getWeather() {
    return __awaiter(this, void 0, void 0, function () {
        var response;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, retireveData()];
                case 1:
                    response = _a.sent();
                    return [2 /*return*/, getWeatherDetails(response).toString().split(',').join(' ')];
            }
        });
    });
}
function getWeatherDetails(toProcess) {
    console.log(toProcess);
    var filteredData = [];
    filteredData.push(filterLoop(toProcess, "main"));
    filteredData.push(filterLoop(toProcess, "weather"));
    //document.getElementById('dash-weather').innerHTML = kelvinToCelsius(filterLoop(filteredData[0], "temp")).ToString()
    //return kelvinToCelsius(filterLoop(filteredData[0], whichOne))
    var selected = [];
    selected.push(kelvinToCelsius(filterLoop(filteredData[0], "temp")).toString() + '°');
    selected.push(filterLoop(filteredData[1][0], "main"));
    console.log(selected[0]);
    return selected;
}
function apiService(endpoint) {
    return fetch(endpoint)
        .then(handleResponse)["catch"](function (error) { return console.log(error); });
}
function handleResponse(response) {
    if (response.status === 204) {
        return "";
    }
    else if (response.status === 404) {
        return null;
    }
    else {
        return response.json();
    }
}
// Find info
/*function getWeather() {
    fetch('https://api.openweathermap.org/data/2.5/weather?q=Belfast,GB&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef').then(response => {
        return response.json()
    }).then(data => {
            console.log(data)
            let filteredData = []
            filteredData.push(filterLoop(data, "main"))
            filteredData.push(filterLoop(data, "weather"))
            return filteredData
        }
    ).then(filtered => {
        let selected = []
        selected.push(kelvinToCelsius(filterLoop(filtered[0], "temp")))
        selected.push(filterLoop(filtered[1][0], "main"))

        console.log(selected)
        return selected
        //RETURN TO TEMPLATE
    })

}*/
function kelvinToCelsius(kelvinTemp) {
    return Math.round((parseFloat(kelvinTemp) - 273.15) * 10) / 10;
}
function filterLoop(objectToReduce, keySearched) {
    for (var _i = 0, _a = Object.entries(objectToReduce); _i < _a.length; _i++) {
        var _b = _a[_i], key = _b[0], value = _b[1];
        if (key.includes(keySearched)) {
            return value;
        }
    }
}
