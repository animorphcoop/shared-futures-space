//getWeather()

/*document.getElementById('dash-weather').innerHTML = 'lol'

const weather = await parseData()

console.log(weather)*/

//TODO: Potentially look into geocoding requests to get more precise measurement
const endpointDerry = 'https:api.openweathermap.org/data/2.5/weather?q=Derry,GB&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef'
const endpointDungloe = 'https:api.openweathermap.org/data/2.5/weather?q=Dungloe,IE&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef'
const endpointBelfast = 'https://api.openweathermap.org/data/2.5/weather?q=Belfast,GB&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef'


const backupWeatherIcon = 'https://openweathermap.org/img/wn/01d@2x.png'
const weatherTypes = {
    'clear sky': 'https://openweathermap.org/img/wn/01d@2x.png',
    'few clouds': 'https://openweathermap.org/img/wn/02d@2x.png',
    'overcast clouds': 'https://openweathermap.org/img/wn/02d@2x.png', //added overcast though not featured in the main list: https://openweathermap.org/weather-conditions
    'scattered clouds': 'https://openweathermap.org/img/wn/03d@2x.png',
    'broken clouds': 'https://openweathermap.org/img/wn/04d@2x.png',
    'shower rain': 'https://openweathermap.org/img/wn/09d@2x.png',
    'rain': 'https://openweathermap.org/img/wn/10d@2x.png',
    'thunderstorm': 'https://openweathermap.org/img/wn/11d@2x.png',
    'snow': 'https://openweathermap.org/img/wn/13d@2x.png',
    'mist': 'https://openweathermap.org/img/wn/50d@2x.png',
}


// TODO: Based on Postcode / location
function retrieveData() {
    try {
        apiService(endpointBelfast).then(data => {
            if (data) {
                return data
            } else {
                console.log("No luck retrieving weather data")
            }

        })
        return apiService(endpointBelfast)
    } catch (error) {
        let errorMessage = "Failed to connect to weather API"
        if (error instanceof Error) {
            errorMessage = error.message;
        }
        console.log(errorMessage);


    }
}

function mapWeatherType(weatherDescription: string) {
    const currentWeatherIcon = findWeatherIcon(weatherDescription)
    const weatherIconHolder = <HTMLImageElement>document.getElementById("weather-icon")
    if (weatherIconHolder) weatherIconHolder.src = currentWeatherIcon
    //const {'clear sky': imgUrl} = weatherTypes


}

function findWeatherIcon(currentWeather: string) {
    let imgUrl = ''
    for (let [key, value] of Object.entries(weatherTypes)) {
        if (currentWeather.match(key)) {
            imgUrl = value
        }
    }
    if (imgUrl == "") imgUrl = backupWeatherIcon
    console.log(`assigned ${imgUrl}`)
    return imgUrl
}


async function getWeather() {

    let response = await retrieveData()
    console.log(`returning ${getWeatherDetails(response)} temperature`)
    return getWeatherDetails(response).toString()

}


function getWeatherDetails(toProcess: object) {
    let filteredData = []

    filteredData.push(filterLoop(toProcess, "weather"))
    filteredData.push(filterLoop(toProcess, "main"))

    //issue with parsing data - interface convoluted to describe
    // @ts-ignore
    mapWeatherType(filterLoop(filteredData[0][0], "description").toString())
    // @ts-ignore
    return kelvinToCelsius(filterLoop(filteredData[1], "temp")).toString() + '°'


}


function apiService(endpoint: string) {
    return fetch(endpoint)
        .then(handleResponse)
        .catch(error => console.log(error));
}


function handleResponse(response: any) {
    if (response.status === 204) {
        return "";
    } else if (response.status === 404) {
        return null;
    } else {
        return response.json()
    }
}


function kelvinToCelsius(kelvinTemp: string) {
    return Math.round((parseFloat(kelvinTemp) - 273.15) * 10) / 10
}

function filterLoop(objectToReduce: any, keySearched: string) {
    for (let [key, value] of Object.entries(objectToReduce)) {
        if (key.includes(keySearched)) {
            return value
        }

    }
}
