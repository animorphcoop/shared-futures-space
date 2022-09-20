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
//TODO: Rewrite endpoints to load dynamically based on user
var endpointDerry = 'https:api.openweathermap.org/data/2.5/weather?q=Derry,GB&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef';
var endpointDungloe = 'https:api.openweathermap.org/data/2.5/weather?q=Dungloe,IE&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef';
var endpointBelfast = 'https://api.openweathermap.org/data/2.5/weather?q=Belfast,GB&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef';
//TODO: Write postcode converter to lat & long, e.g. for Arranmore
//https://api.openweathermap.org/geo/1.0/zip?zip=F92,IE&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef
//https://api.openweathermap.org/data/2.5/weather?lat=54.95&lon=-7.7333&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef
//or North Belfast
//https://api.openweathermap.org/geo/1.0/zip?zip=BT13,GB&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef
//https://api.openweathermap.org/data/2.5/weather?lat=54.5833&lon=-5.9333&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef
var backupWeatherIcon = 'https://openweathermap.org/img/wn/01d@2x.png';
var weatherTypes = {
    'clear sky': 'https://openweathermap.org/img/wn/01d@2x.png',
    'few clouds': 'https://openweathermap.org/img/wn/02d@2x.png',
    'overcast clouds': 'https://openweathermap.org/img/wn/02d@2x.png',
    'scattered clouds': 'https://openweathermap.org/img/wn/03d@2x.png',
    'broken clouds': 'https://openweathermap.org/img/wn/04d@2x.png',
    'shower rain': 'https://openweathermap.org/img/wn/09d@2x.png',
    'rain': 'https://openweathermap.org/img/wn/10d@2x.png',
    'thunderstorm': 'https://openweathermap.org/img/wn/11d@2x.png',
    'snow': 'https://openweathermap.org/img/wn/13d@2x.png',
    'mist': 'https://openweathermap.org/img/wn/50d@2x.png'
};
// TODO: Based on Postcode / location
function retrieveData() {
    try {
        apiService(endpointBelfast).then(function (data) {
            if (data) {
                return data;
            }
            else {
                console.log("No luck retrieving weather data");
            }
        });
        return apiService(endpointBelfast);
    }
    catch (error) {
        var errorMessage = "Failed to connect to weather API";
        if (error instanceof Error) {
            errorMessage = error.message;
        }
        console.log(errorMessage);
    }
}
function mapWeatherType(weatherDescription) {
    var currentWeatherIcon = findWeatherIcon(weatherDescription);
    var weatherIconHolder = document.getElementById("weather-icon");
    if (weatherIconHolder)
        weatherIconHolder.src = currentWeatherIcon;
    //const {'clear sky': imgUrl} = weatherTypes
}
function findWeatherIcon(currentWeather) {
    var imgUrl = '';
    for (var _i = 0, _a = Object.entries(weatherTypes); _i < _a.length; _i++) {
        var _b = _a[_i], key = _b[0], value = _b[1];
        if (currentWeather.match(key)) {
            imgUrl = value;
        }
    }
    if (imgUrl == "")
        imgUrl = backupWeatherIcon;
    console.log("assigned ".concat(imgUrl));
    return imgUrl;
}
function getWeather() {
    return __awaiter(this, void 0, void 0, function () {
        var response;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, retrieveData()];
                case 1:
                    response = _a.sent();
                    console.log("returning ".concat(getWeatherDetails(response), " temperature"));
                    return [2 /*return*/, getWeatherDetails(response).toString()];
            }
        });
    });
}
function getWeatherDetails(toProcess) {
    var filteredData = [];
    filteredData.push(filterLoop(toProcess, "weather"));
    filteredData.push(filterLoop(toProcess, "main"));
    //issue with parsing data - interface convoluted to describe
    // @ts-ignore
    mapWeatherType(filterLoop(filteredData[0][0], "description").toString());
    // @ts-ignore
    return kelvinToCelsius(filterLoop(filteredData[1], "temp")).toString() + '°';
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
