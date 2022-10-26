"use strict";
//getWeather()
const appid = 'f477b3ea5b7d6c3e35e9f9fc5b9b03ef';
const backupWeatherIcon = 'https://openweathermap.org/img/wn/01d@2x.png';
const weatherTypes = {
    'clear sky': 'https://openweathermap.org/img/wn/01d@2x.png',
    'few clouds': 'https://openweathermap.org/img/wn/02d@2x.png',
    'overcast clouds': 'https://openweathermap.org/img/wn/02d@2x.png',
    'scattered clouds': 'https://openweathermap.org/img/wn/03d@2x.png',
    'broken clouds': 'https://openweathermap.org/img/wn/04d@2x.png',
    'shower rain': 'https://openweathermap.org/img/wn/09d@2x.png',
    'rain': 'https://openweathermap.org/img/wn/10d@2x.png',
    'thunderstorm': 'https://openweathermap.org/img/wn/11d@2x.png',
    'snow': 'https://openweathermap.org/img/wn/13d@2x.png',
    'mist': 'https://openweathermap.org/img/wn/50d@2x.png',
};
// TODO: Based on Postcode / location
async function retrieveData(postcode) {
    try {
        let codeResponse = await postcodeQuery(postcode);
        if ('error' in codeResponse) {
            return codeResponse;
        }
        else {
            return await latLongQuery(Number(filterLoop(codeResponse, 'lat')), Number(filterLoop(codeResponse, 'lon')));
        }
    }
    catch (error) {
        //let errorMessage = "Failed to connect to weather API"
        let errorMessage = "";
        if (error instanceof Error) {
            errorMessage = error.message;
        }
        console.log(errorMessage);
        //return {'error': errorMessage};
        return { 'error': '' };
    }
}
async function postcodeQuery(code) {
    // try the code as an eircode
    let ie_attempt = await apiService('https://api.openweathermap.org/geo/1.0/zip?zip=' + code + ',IE&appid=' + appid);
    if (ie_attempt != null) {
        return ie_attempt;
    }
    else {
        // otherwise, try it as a gb postcode
        let gb_attempt = await apiService('https://api.openweathermap.org/geo/1.0/zip?zip=' + code + ',GB&appid=' + appid);
        if (gb_attempt != null && 'lat' in gb_attempt) {
            return gb_attempt;
        }
        else {
            //console.log('not a valid IE or GB postcode');
            //return {'error': code + ' is not a valid IE or GB postcode'};
            return { 'error': '' };
        }
    }
}
function latLongQuery(lat, lon) {
    return apiService('https://api.openweathermap.org/data/2.5/weather?lat=' + lat + '&lon=' + lon + '&appid=' + appid).then(data => {
        if (data) {
            return data;
        }
        else {
            //console.log("No luck retrieving weather data");
            //return {'error': 'failed to retrieve weather data for ' + lat + ':' + lon};
            return { 'error': '' };
        }
    });
}
function mapWeatherType(weatherDescription) {
    const currentWeatherIcon = findWeatherIcon(weatherDescription);
    const weatherIconHolder = document.getElementById("weather-icon");
    if (weatherIconHolder)
        weatherIconHolder.src = currentWeatherIcon;
    //const {'clear sky': imgUrl} = weatherTypes
}
function findWeatherIcon(currentWeather) {
    let imgUrl = '';
    for (let [key, value] of Object.entries(weatherTypes)) {
        if (currentWeather.match(key)) {
            imgUrl = value;
        }
    }
    if (imgUrl == "")
        imgUrl = backupWeatherIcon;
    return imgUrl;
}
async function getWeather(postcode) {
    let response = await retrieveData(postcode);
    if ('error' in response) {
        //console.log('error retrieving weather data');
        //return '[error - ' + response['error'] + ']';
        return '[]';
    }
    else {
        //console.log(`returning ${temp} temperature`);
        return getWeatherDetails(response).toString();
    }
}
function getWeatherDetails(toProcess) {
    let filteredData = [];
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
        .then(handleResponse)
        .catch(error => console.log(error));
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
    for (let [key, value] of Object.entries(objectToReduce)) {
        if (key.includes(keySearched)) {
            return value;
        }
    }
}
