"use strict";
//getWeather()
/*document.getElementById('dash-weather').innerHTML = 'lol'

const weather = await parseData()

console.log(weather)*/
//TODO: Potentially look into geocoding requests to get more precise measurement
const endpointDerry = 'https:api.openweathermap.org/data/2.5/weather?q=Derry,GB&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef';
const endpointDungloe = 'https:api.openweathermap.org/data/2.5/weather?q=Dungloe,IE&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef';
const endpointBelfast = 'https://api.openweathermap.org/data/2.5/weather?q=Belfast,GB&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef';
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
function retrieveData() {
    apiService(endpointBelfast).then(data => {
        if (data) {
            return data;
        }
        else {
            console.log('no luck retrieving weather data');
        }
    });
    return apiService(endpointBelfast);
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
    console.log(`assigned ${imgUrl}`);
    return imgUrl;
}
async function getWeather() {
    let response = await retrieveData();
    console.log(`returning ${getWeatherDetails(response)} temperature`);
    return getWeatherDetails(response).toString();
}
function getWeatherDetails(toProcess) {
    console.log(toProcess);
    let filteredData = [];
    filteredData.push(filterLoop(toProcess, "main"));
    filteredData.push(filterLoop(toProcess, "weather"));
    //document.getElementById('dash-weather').innerHTML = kelvinToCelsius(filterLoop(filteredData[0], "temp")).ToString()
    //return kelvinToCelsius(filterLoop(filteredData[0], whichOne))
    //let selected = []
    //selected.push(kelvinToCelsius(filterLoop(filteredData[0], "temp")).toString()+'°')
    //selected.push(filterLoop(filteredData[1][0], "main"))
    //selected.push(filterLoop(filteredData[1][0], "description"))
    //return selected
    mapWeatherType(filterLoop(filteredData[1][0], "description").toString());
    return kelvinToCelsius(filterLoop(filteredData[0], "temp")).toString() + '°';
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
