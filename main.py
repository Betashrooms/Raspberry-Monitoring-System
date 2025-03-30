import machine
import network
import socket
import ujson  # MicroPython JSON library
import Pulse_Ox  # Assuming this has a function to read SPO2
import temp  # Assuming this has a function to read temperature

Green_LED = machine.Pin(15, machine.Pin.OUT)

# HTML Web Page
HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Patient Monitor</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; }
        .data-container { margin: 20px; font-size: 20px; }
        .status-button {
            background-color: green;
            color: white;
            padding: 15px;
            font-size: 18px;
            border: none;
            cursor: pointer;
        }
    </style>
    <script>
        function updateData() {
            fetch('/data')  // Request data from RP2040
            .then(response => response.json())
            .then(data => {
                document.getElementById("spo2").innerText = data.spo2 + "%";
                document.getElementById("temp").innerText = data.temperature + "°C";

                let button = document.getElementById("status-button");
                if (parseFloat(data.spo2) < 95 || parseFloat(data.spo2) > 100 || parseFloat(data.temperature) < 33 || parseFloat(data.temperature) > 39) {
                    button.style.backgroundColor = "red";
                    button.innerText = "Status: Abnormal";
                    button.disabled = false;
                    
                } else {
                    button.style.backgroundColor = "green";
                    button.innerText = "Status: Normal";
                    button.disabled = true;
                    
                }
            })
            .catch(error => console.error("Error fetching data:", error));
        }
        
        function resetAlert() {
            let button = document.getElementById("status-button");
            button.style.backgroundColor = "green";
            button.innerText = "Status: Normal";
            button.disabled = true;
        }
        
        setInterval(updateData, 2000);
    </script>
</head>
<body>
    <h1>Patient Vital Monitor</h1>
    <div class="data-container">
        <p>SPO2: <span id="spo2">--</span></p>
        <p>Temperature: <span id="temp">--</span></p>
    </div>
    <button id="status-button" class="status-button" onclick="resetAlert()" disabled>Status: Normal</button>
</body>
</html>'''

# Wi-Fi credentials
ssid = 'Local_Network'
password = 'Local_Only'

def get_sensor_data():
    """Get SPO2 and temperature readings from sensors."""
    spo2 = float(Pulse_Ox.Pulse_Ox())  # Replace with actual function
    temperature = float(temp.temp())  # Replace with actual function
    
        # LED Control based on sensor data
    if spo2 < 95 or spo2 > 100 or temperature < 33 or temperature > 39:
        Green_LED.value(1)  # Turn LED ON
    else:
        Green_LED.value(0)  # Turn LED OFF
        
    print(f"DEBUG: Raw SPO2 = {spo2}, Raw Temperature = {temperature}")  # Debugging output
    
    return {'spo2': spo2, 'temperature': temperature}


def application():
    """Sets up the web server on the RP2040."""
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    while not ap.active():
        pass  # Wait until the AP is active

    print("Access point created.")
    print(ap.ifconfig())  # Print IP address

    # Start the socket server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)

    try:
        while True:
            connection, address = s.accept()
            request = connection.recv(1024).decode()
            print("Request:", request)

            # Check if the request is for data
            if "GET /data" in request:
                sensor_data = get_sensor_data()
                
                print(sensor_data)
                
                response = "HTTP/1.1 200 OK\nContent-Type: application/json\n\n" + ujson.dumps(sensor_data)
            else:
                response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + HTML

            connection.sendall(response)
            connection.close()

    except Exception as err:
        print(f"Error: {err}")

    finally:
        s.close()
        ap.active(False)

if __name__ == "__main__":
    application()
