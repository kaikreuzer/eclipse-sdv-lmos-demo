import kotlinx.coroutines.future.await
import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import org.slf4j.LoggerFactory

function(
    name = "get_telemetry_data",
    description = "Returns telemetry data from the vehicles.",
    params = types(
        string("query",
        """The InfluxDB v2 query, e.g. '|> range(start: -1h)'. Make sure to use 'range' always before any 'filter' or 'group' operation. if being asked for a current value, set range to a very small value, such as one minute.
        The available fields are: _start,_stop,_time,_value,_field,_measurement,trigger,vin
        The available '_field' values are: 'totalEngineHours', 'hrTotalVehicleDistance', 'grossCombinationVehicleWeight', 'ambientAirTemperature', 'tachographSpeed', 'engineSpeed', 'fuelLevel1', 'catalystFuelLevel', 'parkingBrakeSwitch', 'driver1WorkingState', 'driver2WorkingState', 'latitude', 'longitude'
        """)
    ),
) { (query) ->
    val body = "from(bucket: \"demo\") $query"

    val request = HttpRequest.newBuilder()
        .uri(URI.create("http://localhost:8086/api/v2/query?org=sdv"))
        .header("Authorization", "Token fms-backend-admin-token")
        .header("Content-Type", "application/vnd.flux")
        .POST(HttpRequest.BodyPublishers.ofString(body))
        .build()

    val response = HttpClient.newHttpClient()
        .sendAsync(request, HttpResponse.BodyHandlers.ofString())
        .toCompletableFuture()
        .await()

    if (response.statusCode() == 200) {
        response.body()
    } else {
        throw Exception("Failed to fetch telemetry data: ${response.statusCode()} - ${response.body()}")
    }
}