//getWeather()

/*document.getElementById('dash-weather').innerHTML = 'lol'

const weather = await parseData()

console.log(weather)*/

function retireveData() {
    apiService('https://api.openweathermap.org/data/2.5/weather?q=Belfast,GB&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef').then(data => {
        if (data) {
            console.log(`result is ${data}`)
            return data
        } else {
            console.log('no luck')
        }

    })
    return apiService('https://api.openweathermap.org/data/2.5/weather?q=Belfast,GB&appid=f477b3ea5b7d6c3e35e9f9fc5b9b03ef')
}


async function getWeather() {
    let response = await retireveData()

    return getWeatherDetails(response).toString().split(',').join(' ')
}


function getWeatherDetails(toProcess) {
    console.log(toProcess)
    let filteredData = []
    filteredData.push(filterLoop(toProcess, "main"))
    filteredData.push(filterLoop(toProcess, "weather"))
    //document.getElementById('dash-weather').innerHTML = kelvinToCelsius(filterLoop(filteredData[0], "temp")).ToString()
    //return kelvinToCelsius(filterLoop(filteredData[0], whichOne))
    let selected = []
    selected.push(kelvinToCelsius(filterLoop(filteredData[0], "temp")).toString()+'°')
    selected.push(filterLoop(filteredData[1][0], "main"))
    console.log(selected[0])
    return selected


}


function apiService(endpoint) {
    return fetch(endpoint)
        .then(handleResponse)
        .catch(error => console.log(error));
}


function handleResponse(response) {
    if (response.status === 204) {
        return "";
    } else if (response.status === 404) {
        return null;
    } else {
        return response.json()
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
    return Math.round((parseFloat(kelvinTemp) - 273.15) * 10) / 10
}

function filterLoop(objectToReduce, keySearched) {
    for (let [key, value] of Object.entries(objectToReduce)) {
        if (key.includes(keySearched)) {
            return value
        }

    }
}
