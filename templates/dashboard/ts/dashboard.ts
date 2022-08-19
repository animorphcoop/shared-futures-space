getWeather()

// Find info
function getWeather() {
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
    })

}

function kelvinToCelsius(kelvinTemp){
    return Math.round((parseFloat(kelvinTemp) - 273.15) * 10) / 10
}

function filterLoop(objectToReduce, keySearched) {
    for (let [key, value] of Object.entries(objectToReduce)) {
        if (key.includes(keySearched)) {
            return value
        }

    }
}

/*

        const preferenceRank = Object.fromEntries(
            Object.entries(data).map(([key, { rank }]) => [rank, key])
        )
*/

/*
            let mainWeatherData = []
            let weatherType = []
            for (let [key, value] of Object.entries(data)) {
                //console.log(key, value);
                if (key.includes("main")) {
                    mainWeatherData.push(value)
                } else if (key.includes("weather")) {
                    weatherType.push(value)
                }
            }

            console.log(mainWeatherData)
            console.log(weatherType)
*/

/*            let keys = []

            for (let [key, value] in data) {
                console.log(key, value)
                if (data.hasOwnProperty(key)) {
                    keys.push(key)
                }
            }*/
/*            console.log(Object.values(data[keys[0]]))
            const locationData = Object.values(data[keys[0]])
            console.log(typeof locationData)
            let dataEntries = []
            locationData.forEach(entry => {
                dataEntries.push(entry)
            })
            const specificData = dataEntries[1]
            /!*   specificData.forEach(item => {
                 console.log(item)
             })
             *!/
            console.log(typeof specificData)
            let forecast = []
            for (let [key, value] of Object.entries(specificData)) {
                //console.log(key, value);
                if (key.includes("Location")) {
                    forecast.push(value)
                }
            }
            console.log(forecast)
            let forecastEntries = []

            for (let [key, value] of Object.entries(forecast)) {
                //console.log(value);
                forecastEntries.push(value)
            }

            console.log(forecastEntries[0])

            let forecastPeriods = []

            for (let [key, value] of Object.entries(forecastEntries[0])) {
                //console.log(key, value);
                if (key.includes("Period")) {
                    forecastPeriods.push(value)
                }
            }

            let firstDayForecast = []
            for (let [key, value] of Object.entries(forecastPeriods[0])) {
                if (key.includes("0")) {
                    firstDayForecast.push(value)
                }

            }
            console.log(firstDayForecast)


            let firstDayForecastSets = []
            for (let [key, value] of Object.entries(firstDayForecast[0])) {
                //console.log(key, value);
                if (key.includes("Rep")) {
                    firstDayForecastSets.push(value)
                }

            }
            console.log(firstDayForecastSets[0])


            let firstSetForecast = []
            for (let [key, value] of Object.entries(firstDayForecastSets[0])) {
                console.log(key, value);
                if (key.includes("0")) {
                    firstSetForecast.push(value)
                }

            }
            console.log(firstSetForecast[0])

            let weatherType = ''
            let temperature = ''

            for (let [key, value] of Object.entries(firstSetForecast[0])) {
                //console.log(key, value);
                if (key.includes("W")) {
                    weatherType = value
                } else if (key.includes("T")) {
                    temperature = value
                }

            }
            console.log(`weather type is ${weatherType}`)
            console.log(`temperature is ${temperature}`)
           */
