getWeather()

// Find info
function getWeather() {
    fetch('http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/350347?res=3hourly&key=1e0c30fb-cec9-497a-a29b-66b9f5a537a2').then(response => {
        return response.json()
    }).then(data => {
            console.log(data)
            console.log(typeof data)
            console.log(Object.keys(data))
            let keys = []

            for (let key in data) {
                if (data.hasOwnProperty(key)) {
                    keys.push(key)
                }
            }
            console.log(Object.values(data[keys[0]]))
            const locationData = Object.values(data[keys[0]])
            console.log(typeof locationData)
            let dataEntries = []
            locationData.forEach(entry => {
                dataEntries.push(entry)
            })
            const specificData = dataEntries[1]
            /*   specificData.forEach(item => {
                 console.log(item)
             })
             */
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
            // go figure https://hub.animorph.coop/f/243136
        }
    )

}